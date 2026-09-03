"""WAMI torch 模型训练模块。

本文件使用自生成影子训练数据训练 WAMI 模型，使正常轨迹保持与用户目标对齐，使注入轨迹在风险步骤后对齐分数下降，并训练来源、敏感信息和目标漂移等辅助判断。"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Callable

import numpy as np

from .shadow import PlanSample, perturb_tdg, synthetic_samples, tdg_to_plan
from .tdg import build_tdg
from .torch_model import TorchWAMIModel


@dataclass
class TorchTrainStats:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""
    epoch: int
    loss: float
    mine_bound: float
    mi_gap: float
    world_loss: float = 0.0


def train_shadow_torch(
    model: TorchWAMIModel,
    samples: list[PlanSample] | None = None,
    epochs: int = 20,
    seed: int = 13,
    batch_size: int = 64,
    cosine_schedule: bool = False,
    use_labeled_negatives: bool = True,
    benign_weight: float = 1.5,
    supervised_gap_weight: float = 0.25,
    supervised_margin: float = 1.0,
    pairwise_weight: float = 0.35,
    pairwise_margin: float = 1.25,
    attack_recall_weight: float = 0.20,
    attack_target_score: float = -3.5,
    transition_weight: float = 0.25,
    auxiliary_weight: float = 0.20,
    provenance_weight: float = 0.15,
    slot_specific_weight: float = 0.15,
    subgoal_weight: float = 0.15,
    progress_callback: Callable[[TorchTrainStats], None] | None = None,
) -> list[TorchTrainStats]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    torch = model.torch
    samples = samples or synthetic_samples()
    positives = [sample for sample in samples if sample.label == 0] or samples
    labeled_negatives = [sample for sample in samples if sample.label == 1]
    attacks_by_intent: dict[str, list[PlanSample]] = {}
    for sample in labeled_negatives:
        attacks_by_intent.setdefault(sample.intent, []).append(sample)
    rng = random.Random(seed)
    optimizer = torch.optim.AdamW(
        model.net.parameters(),
        lr=model.config.learning_rate,
        weight_decay=model.config.weight_decay,
    )
    scheduler = (
        torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max(1, epochs))
        if cosine_schedule
        else None
    )
    stats: list[TorchTrainStats] = []
    for epoch in range(epochs):
        model.net.train()
        rng.shuffle(positives)
        losses: list[float] = []
        bounds: list[float] = []
        gaps: list[float] = []
        world_losses: list[float] = []
        for start in range(0, len(positives), batch_size):
            batch = positives[start : start + batch_size]
            pos_scores = []
            neg_scores = []
            labeled_attack_scores = []
            paired_losses = []
            transition_pos_scores = []
            transition_neg_scores = []
            aux_logits = []
            aux_labels = []
            provenance_logits = []
            provenance_labels = []
            slot_logits = []
            slot_labels = []
            subgoal_positive = []
            subgoal_negative = []
            pos_world_states = []
            neg_world_states = []
            intent_world = []
            for sample in batch:
                clean_tdg = build_tdg(sample.plan)
                corrupt = perturb_tdg(clean_tdg, seed=rng.randrange(10_000_000))
                corrupt_plan = tdg_to_plan(corrupt)
                intent_vec = model.tensor(model.encode_intent(sample.intent))
                pos_scores.append(model.net.score(intent_vec, model.tensor(model.encode_plan(sample.plan))))
                neg_scores.append(model.net.score(intent_vec, model.tensor(model.encode_plan(corrupt_plan))))
                pos_trace = model.cognitive_rollout_tensors(sample.intent, clean_tdg)
                neg_trace = model.cognitive_rollout_tensors(sample.intent, build_tdg(corrupt_plan))
                pos_states = [(item["node"], item["state"]) for item in pos_trace]
                neg_states = [(item["node"], item["state"]) for item in neg_trace]
                for (_, pos), (_, neg) in zip(pos_states, neg_states):
                    pos_scores.append(model.net.score(intent_vec, pos))
                    neg_scores.append(model.net.score(intent_vec, neg))
                    pos_world_states.append(pos)
                    neg_world_states.append(neg)
                    intent_world.append(intent_vec)
                for item in pos_trace:
                    transition_pos_scores.append(
                        model.net.transition_score(
                            intent_vec,
                            item["previous_state"],
                            item["action"],
                            item["observation"],
                            item["state"],
                        )
                    )
                    aux_logits.append(model.net.aux_logits(intent_vec, item["previous_state"], item["action"], item["observation"], item["state"]))
                    aux_labels.append(_aux_labels(item["node"].tool, str(item["node"].params), sample.label, seen_attack=False))
                    provenance_logits.append(
                        model.net.provenance_logits(
                            intent_vec,
                            item["action"],
                            item["observation"],
                            item["memory"],
                            item["state"],
                        )
                    )
                    provenance_labels.append(
                        _provenance_labels(
                            item["node"].tool,
                            str(item["node"].params),
                            sample.label,
                            seen_attack=False,
                        )
                    )
                    slot_logits.append(item["slots"].mean(dim=-1))
                    slot_labels.append(
                        _slot_labels(item["node"].tool, str(item["node"].params), sample.label, seen_attack=False)
                    )
                    subgoal_positive.append((intent_vec, item["subgoal"]))
                for item in neg_trace:
                    transition_neg_scores.append(
                        model.net.transition_score(
                            intent_vec,
                            item["previous_state"],
                            item["action"],
                            item["observation"],
                            item["state"],
                        )
                    )
                if use_labeled_negatives and labeled_negatives:
                    paired_attack = rng.choice(attacks_by_intent.get(sample.intent, labeled_negatives))
                    attack = paired_attack
                    attack_tdg = build_tdg(attack.plan)
                    attack_intent = model.tensor(model.encode_intent(attack.intent))
                    attack_plan_score = model.net.score(attack_intent, model.tensor(model.encode_plan(attack.plan)))
                    neg_scores.append(attack_plan_score)
                    labeled_attack_scores.append(attack_plan_score)
                    paired_losses.append(torch.nn.functional.relu(pairwise_margin - pos_scores[-1] + attack_plan_score))
                    attack_trace = model.cognitive_rollout_tensors(attack.intent, attack_tdg)
                    attack_states = [(item["node"], item["state"]) for item in attack_trace]
                    seen_attack_transition = False
                    for state_index, (attack_item, (_, attack_state)) in enumerate(zip(attack_trace, attack_states)):
                        attack_score = model.net.score(attack_intent, attack_state)
                        neg_scores.append(attack_score)
                        labeled_attack_scores.append(attack_score)
                        if _is_attack_transition(attack_item["node"].tool, seen_attack_transition):
                            seen_attack_transition = True
                            transition_neg_scores.append(
                                model.net.transition_score(
                                    attack_intent,
                                    attack_item["previous_state"],
                                    attack_item["action"],
                                    attack_item["observation"],
                                    attack_item["state"],
                                )
                            )
                        aux_logits.append(
                            model.net.aux_logits(
                                attack_intent,
                                attack_item["previous_state"],
                                attack_item["action"],
                                attack_item["observation"],
                                attack_item["state"],
                            )
                        )
                        aux_labels.append(
                            _aux_labels(
                                attack_item["node"].tool,
                                str(attack_item["node"].params),
                                attack.label,
                                seen_attack=seen_attack_transition,
                            )
                        )
                        provenance_logits.append(
                            model.net.provenance_logits(
                                attack_intent,
                                attack_item["action"],
                                attack_item["observation"],
                                attack_item["memory"],
                                attack_item["state"],
                            )
                        )
                        provenance_labels.append(
                            _provenance_labels(
                                attack_item["node"].tool,
                                str(attack_item["node"].params),
                                attack.label,
                                seen_attack=seen_attack_transition,
                            )
                        )
                        slot_logits.append(attack_item["slots"].mean(dim=-1))
                        slot_labels.append(
                            _slot_labels(
                                attack_item["node"].tool,
                                str(attack_item["node"].params),
                                attack.label,
                                seen_attack=seen_attack_transition,
                            )
                        )
                        subgoal_negative.append((attack_intent, attack_item["subgoal"]))
                        if state_index < len(pos_states):
                            pos_state_score = model.net.score(intent_vec, pos_states[state_index][1])
                            paired_losses.append(torch.nn.functional.relu(pairwise_margin - pos_state_score + attack_score))
            if not pos_scores:
                continue
            pos = torch.stack(pos_scores)
            neg = torch.stack(neg_scores)
            mine_bound = pos.mean() - torch.logsumexp(neg, dim=0) + np.log(max(1, neg.numel()))
            logistic_loss = benign_weight * torch.nn.functional.softplus(-pos).mean() + torch.nn.functional.softplus(neg).mean()
            if labeled_attack_scores:
                attack_scores = torch.stack(labeled_attack_scores)
                supervised_gap = torch.nn.functional.relu(supervised_margin - pos.mean() + attack_scores.mean())
                attack_suppression = torch.nn.functional.softplus(attack_scores).mean()
                supervised_loss = supervised_gap + attack_suppression
                attack_recall_loss = torch.nn.functional.relu(attack_scores - attack_target_score).mean()
            else:
                supervised_loss = torch.tensor(0.0, device=model.config.device)
                attack_recall_loss = torch.tensor(0.0, device=model.config.device)
            if paired_losses:
                pairwise_loss = torch.stack(paired_losses).mean()
            else:
                pairwise_loss = torch.tensor(0.0, device=model.config.device)
            if transition_pos_scores and transition_neg_scores:
                transition_pos = torch.stack(transition_pos_scores)
                transition_neg = torch.stack(transition_neg_scores)
                transition_loss = (
                    torch.nn.functional.softplus(-transition_pos).mean()
                    + torch.nn.functional.softplus(transition_neg).mean()
                )
            else:
                transition_loss = torch.tensor(0.0, device=model.config.device)
            if aux_logits:
                source_logits = torch.stack([item[0] for item in aux_logits])
                drift_logits = torch.stack([item[1] for item in aux_logits])
                sink_logits = torch.stack([item[2] for item in aux_logits])
                labels = torch.tensor(aux_labels, dtype=torch.float32, device=model.config.device)
                source_loss = torch.nn.functional.binary_cross_entropy_with_logits(source_logits, labels[:, 0])
                drift_loss = torch.nn.functional.binary_cross_entropy_with_logits(drift_logits, labels[:, 1])
                sink_auth_loss = torch.nn.functional.binary_cross_entropy_with_logits(sink_logits, labels[:, 2])
                auxiliary_loss = source_loss + drift_loss + sink_auth_loss
            else:
                auxiliary_loss = torch.tensor(0.0, device=model.config.device)
            if provenance_logits:
                provenance_pred = torch.stack(provenance_logits)
                provenance_target = torch.tensor(provenance_labels, dtype=torch.float32, device=model.config.device)
                provenance_loss = torch.nn.functional.binary_cross_entropy_with_logits(
                    provenance_pred,
                    provenance_target,
                )
            else:
                provenance_loss = torch.tensor(0.0, device=model.config.device)
            if slot_logits:
                slot_pred = torch.stack(slot_logits)
                slot_target = torch.tensor(slot_labels, dtype=torch.float32, device=model.config.device)
                slot_specific_loss = torch.nn.functional.binary_cross_entropy_with_logits(slot_pred, slot_target)
            else:
                slot_specific_loss = torch.tensor(0.0, device=model.config.device)
            if subgoal_positive and subgoal_negative:
                pos_sim = torch.stack([(intent * subgoal).sum(-1) for intent, subgoal in subgoal_positive])
                neg_sim = torch.stack([(intent * subgoal).sum(-1) for intent, subgoal in subgoal_negative])
                subgoal_loss = torch.nn.functional.relu(0.35 - pos_sim.mean() + neg_sim.mean())
            else:
                subgoal_loss = torch.tensor(0.0, device=model.config.device)
            if pos_world_states:
                intents = torch.stack(intent_world)
                positive_states = torch.stack(pos_world_states)
                negatives = torch.stack(neg_world_states)
                logits = intents @ positive_states.T / 0.07
                labels = torch.arange(logits.shape[0], device=model.config.device)
                infonce = torch.nn.functional.cross_entropy(logits, labels)
                margin = torch.nn.functional.relu(0.15 - (intents * positive_states).sum(-1) + (intents * negatives).sum(-1)).mean()
                world_loss = infonce + margin
            else:
                world_loss = torch.tensor(0.0, device=model.config.device)
            variance_penalty = 0.01 * (pos.var(unbiased=False) + neg.var(unbiased=False))
            loss = (
                logistic_loss
                - 0.1 * mine_bound
                + 0.2 * world_loss
                + supervised_gap_weight * supervised_loss
                + pairwise_weight * pairwise_loss
                + attack_recall_weight * attack_recall_loss
                + transition_weight * transition_loss
                + auxiliary_weight * auxiliary_loss
                + provenance_weight * provenance_loss
                + slot_specific_weight * slot_specific_loss
                + subgoal_weight * subgoal_loss
                + variance_penalty
            )
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.net.parameters(), 1.0)
            optimizer.step()
            losses.append(float(loss.detach().cpu()))
            bounds.append(float(mine_bound.detach().cpu()))
            gaps.append(float((pos.mean() - neg.mean()).detach().cpu()))
            world_losses.append(float(world_loss.detach().cpu()))
        if scheduler is not None:
            scheduler.step()
        stat = TorchTrainStats(
            epoch=epoch + 1,
            loss=float(np.mean(losses)) if losses else 0.0,
            mine_bound=float(np.mean(bounds)) if bounds else 0.0,
            mi_gap=float(np.mean(gaps)) if gaps else 0.0,
            world_loss=float(np.mean(world_losses)) if world_losses else 0.0,
        )
        stats.append(stat)
        if progress_callback is not None:
            progress_callback(stat)
    return stats


def _is_attack_transition(tool: str, seen_attack_transition: bool) -> bool:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    compact = tool.lower().replace("_", "").replace("-", "")
    starts_attack = "parseinjectedinstruction" in compact or "readuntrustedinjection" in compact
    return seen_attack_transition or starts_attack


def _aux_labels(tool: str, params: str, label: int, seen_attack: bool) -> tuple[float, float, float]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    compact = tool.lower().replace("_", "").replace("-", "")
    blob = f"{tool} {params}".lower()
    external = any(
        key in compact or key in blob
        for key in (
            "readtoolresponse",
            "readcontext",
            "readuntrustedinjection",
            "parseinjectedinstruction",
            "webbrowsernavigateto",
            "readimagetext",
            "gmailreademail",
            "readchannelmessages",
        )
    )
    sink = any(
        key in compact
        for key in (
            "send",
            "email",
            "transfer",
            "execute",
            "exfiltrate",
            "revealsecret",
            "upload",
            "share",
            "scheduleddeviceaction",
        )
    )
    authorized = sink and ("authorization" in blob or "approved" in blob or "user requested" in blob or "user intent" in blob)
    drift = label == 1 and (seen_attack or sink)
    sink_auth = 1.0 if (sink and authorized) or not sink else 0.0
    return float(external), float(drift), float(sink_auth)


def _provenance_labels(tool: str, params: str, label: int, seen_attack: bool) -> tuple[float, float, float, float]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    compact = tool.lower().replace("_", "").replace("-", "")
    blob = f"{tool} {params}".lower()
    external = any(
        key in compact or key in blob
        for key in (
            "readtoolresponse",
            "readcontext",
            "readuntrustedinjection",
            "parseinjectedinstruction",
            "webbrowsernavigateto",
            "readimagetext",
            "gmailreademail",
            "readchannelmessages",
        )
    )
    sensitive = any(
        key in compact or key in blob
        for key in (
            "secret",
            "password",
            "credential",
            "address",
            "phone",
            "payment",
            "account",
            "savedaddresses",
            "patient",
        )
    )
    sink = any(
        key in compact
        for key in (
            "send",
            "email",
            "transfer",
            "execute",
            "exfiltrate",
            "revealsecret",
            "upload",
            "share",
            "scheduleddeviceaction",
        )
    )
    trusted = not external and not seen_attack
    untrusted = external or seen_attack
    instruction = (label == 1 and seen_attack) or "instruction" in blob
    sensitive_memory = sensitive or (label == 1 and sink)
    return float(trusted), float(untrusted), float(instruction), float(sensitive_memory)


def _slot_labels(tool: str, params: str, label: int, seen_attack: bool) -> tuple[float, float, float, float]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    compact = tool.lower().replace("_", "").replace("-", "")
    blob = f"{tool} {params}".lower()
    external = any(key in compact or key in blob for key in ("readtoolresponse", "readcontext", "readuntrusted", "parseinjected", "web", "gmailread"))
    sink = any(key in compact for key in ("send", "email", "transfer", "execute", "exfiltrate", "reveal", "upload", "share"))
    sensitive = any(key in compact or key in blob for key in ("address", "secret", "account", "payment", "password", "patient", "private"))
    trusted = (not external and not seen_attack) or "authorization" in blob or "approved" in blob
    untrusted = external or seen_attack
    instruction = (label == 1 and seen_attack) or "parseinjected" in compact
    sensitive_slot = sensitive or (label == 1 and sink)
    return float(trusted), float(untrusted), float(instruction), float(sensitive_slot)
