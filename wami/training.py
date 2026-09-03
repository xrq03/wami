from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import random
from collections import defaultdict

import numpy as np

from .model import WAMIModel
from .shadow import PlanSample, perturb_tdg, synthetic_samples, tdg_to_plan
from .tdg import build_tdg


@dataclass
class TrainStats:
    epoch: int
    loss: float
    mi_gap: float
    world_loss: float = 0.0


def load_jsonl(path: str | Path) -> list[PlanSample]:
    samples: list[PlanSample] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            samples.append(PlanSample(item["intent"], item["plan"], int(item.get("label", 0))))
    return samples


def _states(model: WAMIModel, intent: str, plan: str) -> list[np.ndarray]:
    tdg = build_tdg(plan)
    trajectory = model.rollout(intent, tdg)
    if trajectory:
        return [state for _, state in trajectory]
    return [model.encode_intent(intent)]


def _transition_contexts(model: WAMIModel, intent: str, plan: str):
    tdg = build_tdg(plan)
    intent_vec = model.encode_intent(intent)
    state = intent_vec
    memory = intent_vec
    states: dict[str, np.ndarray] = {}
    parents = tdg.parents()
    contexts = []
    for node in tdg.topological_order():
        parent_vecs = [states[p] for p in parents.get(node.id, []) if p in states]
        parent_state = np.mean(parent_vecs, axis=0) if parent_vecs else state
        action = model.encode_node(node)
        observation = model.encode_observation(node)
        memory = model.update_memory(memory, state, observation)
        contexts.append((state, action, parent_state, memory, observation))
        subgoal = model.infer_subgoal(intent_vec, state, action)
        state = model.transition(state, action, parent_state, memory, subgoal, observation)
        states[node.id] = state
    return contexts


def train_shadow(
    model: WAMIModel,
    samples: list[PlanSample] | None = None,
    epochs: int = 20,
    seed: int = 13,
) -> list[TrainStats]:
    rng = random.Random(seed)
    samples = samples or synthetic_samples()
    positive_samples = [sample for sample in samples if sample.label == 0] or samples
    attack_bank: dict[str, list[PlanSample]] = defaultdict(list)
    for sample in samples:
        if sample.label == 1:
            attack_bank[sample.intent].append(sample)
    stats: list[TrainStats] = []
    for epoch in range(epochs):
        rng.shuffle(positive_samples)
        losses: list[float] = []
        gaps: list[float] = []
        world_losses: list[float] = []
        for sample in positive_samples:
            clean_tdg = build_tdg(sample.plan)
            bank = attack_bank.get(sample.intent, [])
            intent = model.encode_intent(sample.intent)
            if bank and rng.random() < 0.75:
                neg_plan = rng.choice(bank).plan
            else:
                corrupt_tdg = perturb_tdg(clean_tdg, seed=rng.randrange(10_000_000))
                neg_plan = tdg_to_plan(corrupt_tdg)
            plan_loss = model.train_mine_step(intent, model.encode_plan(sample.plan), model.encode_plan(neg_plan))
            losses.append(plan_loss)
            gaps.append(model.plan_score(sample.intent, sample.plan) - model.plan_score(sample.intent, neg_plan))
            pos_states = _states(model, sample.intent, sample.plan)
            neg_states = _states(model, sample.intent, neg_plan)
            pos_contexts = _transition_contexts(model, sample.intent, sample.plan)
            neg_contexts = _transition_contexts(model, sample.intent, neg_plan)
            for pos_context, neg_context in zip(pos_contexts, neg_contexts):
                world_losses.append(model.train_world_step(intent, pos_context, neg_context))
            for pos, neg in zip(pos_states, neg_states):
                loss = model.train_mine_step(intent, pos, neg)
                losses.append(loss)
                gaps.append(model.mine_score(intent, pos) - model.mine_score(intent, neg))
        stats.append(
            TrainStats(
                epoch + 1,
                float(np.mean(losses)),
                float(np.mean(gaps)),
                float(np.mean(world_losses)) if world_losses else 0.0,
            )
        )
    return stats
