"""WAMI 可训练 latent/world model 模块。

本文件实现用户意图、工具动作、工具返回内容编码，变换器、门控循环单元、槽位记忆状态更新，MINE 分数头和来源感知辅助头。它是 WAMI 从工程规则走向可训练算法的核心。"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from .embedding import HashingTextEncoder
from .tdg import TDG, TDGNode

if TYPE_CHECKING:
    import torch


@dataclass
class TorchWAMIConfig:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""
    dim: int = 256
    hidden_dim: int = 512
    layers: int = 2
    heads: int = 4
    dropout: float = 0.1
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    seed: int = 7
    device: str = "cpu"
    use_slot_memory: bool = True

    @classmethod
    def paper_strict(cls, device: str = "cpu", seed: int = 7) -> "TorchWAMIConfig":
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""

        return cls(
            dim=1024,
            hidden_dim=1024,
            layers=4,
            heads=8,
            dropout=0.1,
            learning_rate=2e-4,
            weight_decay=1e-4,
            seed=seed,
            device=device,
        )


def _require_torch():
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    try:
        import torch
        import torch.nn as nn
        import torch.nn.functional as F
    except ImportError as exc:
        raise ImportError(
            "TorchWAMIModel requires PyTorch. Install it with "
            "`pip install torch` or run `uv run --with torch ...`."
        ) from exc
    return torch, nn, F


class ResidualBlock:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""
    def __new__(cls, dim: int, hidden_dim: int, dropout: float):
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        torch, nn, _ = _require_torch()

        class _Block(nn.Module):
            """类说明。
            
            这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""
            def __init__(self) -> None:
                """函数说明。
                
                这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
                super().__init__()
                self.net = nn.Sequential(
                    nn.LayerNorm(dim),
                    nn.Linear(dim, hidden_dim),
                    nn.GELU(),
                    nn.Dropout(dropout),
                    nn.Linear(hidden_dim, dim),
                )

            def forward(self, x: torch.Tensor) -> torch.Tensor:
                """函数说明。
                
                这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
                return x + self.net(x)

        return _Block()


class _TorchWAMINet:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""
    def __new__(cls, config: TorchWAMIConfig):
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        torch, nn, F = _require_torch()

        class _Net(nn.Module):
            """类说明。
            
            这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""
            def __init__(self) -> None:
                """函数说明。
                
                这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
                super().__init__()
                d = config.dim
                self.intent_proj = nn.Sequential(
                    nn.LayerNorm(d),
                    nn.Linear(d, d),
                    nn.GELU(),
                    ResidualBlock(d, config.hidden_dim, config.dropout),
                )
                self.action_proj = nn.Sequential(
                    nn.LayerNorm(d),
                    nn.Linear(d, d),
                    nn.GELU(),
                    ResidualBlock(d, config.hidden_dim, config.dropout),
                )
                self.observation_proj = nn.Sequential(
                    nn.LayerNorm(d),
                    nn.Linear(d, d),
                    nn.GELU(),
                    ResidualBlock(d, config.hidden_dim, config.dropout),
                )
                self.memory_cell = nn.GRUCell(d * 2, d)
                self.slot_gate = nn.Sequential(
                    nn.LayerNorm(d * 3),
                    nn.Linear(d * 3, config.hidden_dim // 2),
                    nn.GELU(),
                    nn.Linear(config.hidden_dim // 2, 4),
                )
                self.slot_update = nn.Sequential(
                    nn.LayerNorm(d * 3),
                    nn.Linear(d * 3, d),
                    nn.Tanh(),
                )
                self.slot_fusion = nn.Sequential(
                    nn.LayerNorm(d * 5),
                    nn.Linear(d * 5, d),
                    nn.GELU(),
                    ResidualBlock(d, config.hidden_dim, config.dropout),
                )
                self.subgoal_head = nn.Sequential(
                    nn.LayerNorm(d * 3),
                    nn.Linear(d * 3, config.hidden_dim),
                    nn.GELU(),
                    nn.Dropout(config.dropout),
                    nn.Linear(config.hidden_dim, d),
                )
                encoder_layer = nn.TransformerEncoderLayer(
                    d_model=d,
                    nhead=config.heads,
                    dim_feedforward=config.hidden_dim,
                    dropout=config.dropout,
                    batch_first=True,
                    activation="gelu",
                    norm_first=True,
                )
                self.world = nn.TransformerEncoder(encoder_layer, num_layers=config.layers)
                self.transition = nn.Sequential(
                    nn.LayerNorm(d * 5),
                    nn.Linear(d * 5, config.hidden_dim),
                    nn.GELU(),
                    nn.Dropout(config.dropout),
                    nn.Linear(config.hidden_dim, d),
                )
                self.mine = nn.Sequential(
                    nn.LayerNorm(d * 4),
                    nn.Linear(d * 4, config.hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(config.dropout),
                    nn.Linear(config.hidden_dim, config.hidden_dim // 2),
                    nn.ReLU(),
                    nn.Linear(config.hidden_dim // 2, 1),
                )
                self.transition_mine = nn.Sequential(
                    nn.LayerNorm(d * 5),
                    nn.Linear(d * 5, config.hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(config.dropout),
                    nn.Linear(config.hidden_dim, config.hidden_dim // 2),
                    nn.ReLU(),
                    nn.Linear(config.hidden_dim // 2, 1),
                )
                self.source_head = nn.Sequential(
                    nn.LayerNorm(d * 3),
                    nn.Linear(d * 3, config.hidden_dim // 2),
                    nn.GELU(),
                    nn.Dropout(config.dropout),
                    nn.Linear(config.hidden_dim // 2, 1),
                )
                self.drift_head = nn.Sequential(
                    nn.LayerNorm(d * 5),
                    nn.Linear(d * 5, config.hidden_dim // 2),
                    nn.GELU(),
                    nn.Dropout(config.dropout),
                    nn.Linear(config.hidden_dim // 2, 1),
                )
                self.sink_auth_head = nn.Sequential(
                    nn.LayerNorm(d * 4),
                    nn.Linear(d * 4, config.hidden_dim // 2),
                    nn.GELU(),
                    nn.Dropout(config.dropout),
                    nn.Linear(config.hidden_dim // 2, 1),
                )
                # 名称必须与已发布权重的 provenance_head 键一致。
                self.provenance_head = nn.Sequential(
                    nn.LayerNorm(d * 4),
                    nn.Linear(d * 4, config.hidden_dim // 2),
                    nn.GELU(),
                    nn.Dropout(config.dropout),
                    nn.Linear(config.hidden_dim // 2, 4),
                )

            def next_state(
                self,
                current: torch.Tensor,
                action: torch.Tensor,
                parent: torch.Tensor,
                observation: torch.Tensor,
                memory: torch.Tensor,
                slots: torch.Tensor | None,
                history: torch.Tensor | None,
            ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
                """函数说明。
                
                这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
                current = self.intent_proj(current)
                action = self.action_proj(action)
                parent = self.intent_proj(parent)
                observation = self.observation_proj(observation)
                memory = F.normalize(self.memory_cell(torch.cat([current, observation], dim=-1), memory), dim=-1)
                if not config.use_slot_memory:
                    slot_summary = memory
                    slots = memory.unsqueeze(0).repeat(4, 1) if slots is None else slots
                elif slots is None:
                    slots = memory.unsqueeze(0).repeat(4, 1)
                    slot_features = torch.cat([current, action, observation], dim=-1)
                    gates = torch.sigmoid(self.slot_gate(slot_features))
                    update = self.slot_update(slot_features)
                    slots = F.normalize((1.0 - gates.unsqueeze(-1)) * slots + gates.unsqueeze(-1) * update.unsqueeze(0), dim=-1)
                    slot_summary = self.slot_fusion(torch.cat([memory, slots.reshape(-1)], dim=-1))
                else:
                    slot_features = torch.cat([current, action, observation], dim=-1)
                    gates = torch.sigmoid(self.slot_gate(slot_features))
                    update = self.slot_update(slot_features)
                    slots = F.normalize((1.0 - gates.unsqueeze(-1)) * slots + gates.unsqueeze(-1) * update.unsqueeze(0), dim=-1)
                    slot_summary = self.slot_fusion(torch.cat([memory, slots.reshape(-1)], dim=-1))
                subgoal = torch.tanh(self.subgoal_head(torch.cat([current, action, memory], dim=-1)))
                subgoal = F.normalize(subgoal, dim=-1)
                if history is None:
                    context = current
                else:
                    encoded = self.world(history.unsqueeze(0)).squeeze(0)
                    context = encoded[-1]
                state = torch.tanh(self.transition(torch.cat([context, action, parent, slot_summary, subgoal], dim=-1)))
                return F.normalize(state, dim=-1), memory, subgoal, slots

            def score(self, intent: torch.Tensor, state: torch.Tensor) -> torch.Tensor:
                """函数说明。
                
                这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
                features = torch.cat([intent, state, intent * state, torch.abs(intent - state)], dim=-1)
                return self.mine(features).squeeze(-1)

            def transition_score(
                self,
                intent: torch.Tensor,
                previous: torch.Tensor,
                action: torch.Tensor,
                observation: torch.Tensor,
                state: torch.Tensor,
            ) -> torch.Tensor:
                """函数说明。
                
                这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
                delta = state - previous
                features = torch.cat([intent, previous, action, observation, delta], dim=-1)
                return self.transition_mine(features).squeeze(-1)

            def aux_logits(
                self,
                intent: torch.Tensor,
                previous: torch.Tensor,
                action: torch.Tensor,
                observation: torch.Tensor,
                state: torch.Tensor,
            ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
                """函数说明。
                
                这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
                delta = state - previous
                source = self.source_head(torch.cat([state, observation, state * observation], dim=-1)).squeeze(-1)
                drift = self.drift_head(torch.cat([intent, previous, action, observation, delta], dim=-1)).squeeze(-1)
                sink_auth = self.sink_auth_head(torch.cat([intent, action, state, intent * action], dim=-1)).squeeze(-1)
                return source, drift, sink_auth

            def provenance_logits(
                self,
                intent: torch.Tensor,
                action: torch.Tensor,
                observation: torch.Tensor,
                memory: torch.Tensor,
                state: torch.Tensor,
            ) -> torch.Tensor:
                """函数说明。
                
                这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
                return self.provenance_head(torch.cat([intent, action, observation, memory + state], dim=-1))

        return _Net()


class TorchWAMIModel:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""

    def __init__(self, config: TorchWAMIConfig | None = None):
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        torch, _, _ = _require_torch()
        self.config = config or TorchWAMIConfig()
        torch.manual_seed(self.config.seed)
        self.torch = torch
        self.encoder = HashingTextEncoder(dim=self.config.dim, seed=self.config.seed)
        self.net = _TorchWAMINet(self.config).to(self.config.device)

    def encode_intent(self, intent: str) -> np.ndarray:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        return self.encoder.encode(intent)

    def encode_node(self, node: TDGNode) -> np.ndarray:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        payload = f"{node.tool} {json.dumps(node.params, sort_keys=True, ensure_ascii=False)}"
        return self.encoder.encode(payload)

    def encode_observation(self, node: TDGNode) -> np.ndarray:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        observed = []
        for key in ("input", "content", "observation", "result", "body", "text", "url", "query"):
            value = node.params.get(key)
            if value is not None:
                observed.append(f"{key}={value}")
        payload = " ".join(observed) if observed else node.raw
        return self.encoder.encode(f"observation {payload}")

    def tensor(self, array: np.ndarray):
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        return self.torch.tensor(array, dtype=self.torch.float32, device=self.config.device)

    def rollout_tensors(self, intent: str, tdg: TDG):
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        torch = self.torch
        state = self.tensor(self.encode_intent(intent))
        memory = state
        slots = None
        states: dict[str, torch.Tensor] = {}
        parents = tdg.parents()
        trajectory = []
        history = None
        for node in tdg.topological_order():
            previous = state
            parent_vecs = [states[p] for p in parents.get(node.id, []) if p in states]
            parent = torch.stack(parent_vecs).mean(dim=0) if parent_vecs else state
            action = self.tensor(self.encode_node(node))
            observation = self.tensor(self.encode_observation(node))
            state, memory, _subgoal, slots = self.net.next_state(state, action, parent, observation, memory, slots, history)
            history = state.unsqueeze(0) if history is None else torch.cat([history, state.unsqueeze(0)], dim=0)
            states[node.id] = state
            trajectory.append((node, state))
        return trajectory

    def cognitive_rollout_tensors(self, intent: str, tdg: TDG):
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        torch = self.torch
        intent_vec = self.tensor(self.encode_intent(intent))
        state = intent_vec
        memory = intent_vec
        slots = None
        states: dict[str, torch.Tensor] = {}
        parents = tdg.parents()
        trace = []
        history = None
        for step, node in enumerate(tdg.topological_order()):
            previous = state
            parent_vecs = [states[p] for p in parents.get(node.id, []) if p in states]
            parent = torch.stack(parent_vecs).mean(dim=0) if parent_vecs else state
            action = self.tensor(self.encode_node(node))
            observation = self.tensor(self.encode_observation(node))
            state, memory, subgoal, slots = self.net.next_state(state, action, parent, observation, memory, slots, history)
            history = state.unsqueeze(0) if history is None else torch.cat([history, state.unsqueeze(0)], dim=0)
            states[node.id] = state
            trace.append(
                {
                    "step": step,
                    "node": node,
                    "state": state,
                    "memory": memory,
                    "slots": slots,
                    "subgoal": subgoal,
                    "observation": observation,
                    "action": action,
                    "previous_state": previous,
                    "parent_state": parent,
                }
            )
        return trace

    def cognitive_rollout(self, intent: str, tdg: TDG) -> list[dict]:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        self.net.eval()
        with self.torch.no_grad():
            out = []
            for item in self.cognitive_rollout_tensors(intent, tdg):
                converted = dict(item)
                for key in ("state", "memory", "slots", "subgoal", "observation", "action", "previous_state", "parent_state"):
                    converted[key] = converted[key].detach().cpu().numpy()
                out.append(converted)
            return out

    def rollout(self, intent: str, tdg: TDG) -> list[tuple[TDGNode, np.ndarray]]:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        self.net.eval()
        with self.torch.no_grad():
            return [(node, state.detach().cpu().numpy()) for node, state in self.rollout_tensors(intent, tdg)]

    def encode_plan(self, plan: str) -> np.ndarray:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        return self.encoder.encode(plan)

    def plan_score(self, intent: str, plan: str) -> float:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        return self.mine_score(self.encode_intent(intent), self.encode_plan(plan))

    def mine_score(self, intent_vec: np.ndarray, state_vec: np.ndarray) -> float:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        self.net.eval()
        with self.torch.no_grad():
            intent = self.tensor(intent_vec)
            state = self.tensor(state_vec)
            return float(self.net.score(intent, state).detach().cpu())

    def transition_score(
        self,
        intent_vec: np.ndarray,
        previous_vec: np.ndarray,
        action_vec: np.ndarray,
        observation_vec: np.ndarray,
        state_vec: np.ndarray,
    ) -> float:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        self.net.eval()
        with self.torch.no_grad():
            return float(
                self.net.transition_score(
                    self.tensor(intent_vec),
                    self.tensor(previous_vec),
                    self.tensor(action_vec),
                    self.tensor(observation_vec),
                    self.tensor(state_vec),
                )
                .detach()
                .cpu()
            )

    def aux_scores(
        self,
        intent_vec: np.ndarray,
        previous_vec: np.ndarray,
        action_vec: np.ndarray,
        observation_vec: np.ndarray,
        state_vec: np.ndarray,
    ) -> tuple[float, float, float]:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        self.net.eval()
        with self.torch.no_grad():
            logits = self.net.aux_logits(
                self.tensor(intent_vec),
                self.tensor(previous_vec),
                self.tensor(action_vec),
                self.tensor(observation_vec),
                self.tensor(state_vec),
            )
            return tuple(float(logit.detach().cpu()) for logit in logits)

    def provenance_scores(
        self,
        intent_vec: np.ndarray,
        action_vec: np.ndarray,
        observation_vec: np.ndarray,
        memory_vec: np.ndarray,
        state_vec: np.ndarray,
    ) -> tuple[float, float, float, float]:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        self.net.eval()
        with self.torch.no_grad():
            logits = self.net.provenance_logits(
                self.tensor(intent_vec),
                self.tensor(action_vec),
                self.tensor(observation_vec),
                self.tensor(memory_vec),
                self.tensor(state_vec),
            )
            return tuple(float(logit.detach().cpu()) for logit in logits)

    def save(self, path: str | Path) -> None:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        self.torch.save({"config": self.config.__dict__, "state_dict": self.net.state_dict()}, path)

    @classmethod
    def load(cls, path: str | Path) -> "TorchWAMIModel":
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        torch, _, _ = _require_torch()
        data = torch.load(path, map_location="cpu")
        config = TorchWAMIConfig(**data["config"])
        config.use_slot_memory = any(key.startswith("slot_gate.") for key in data["state_dict"])
        model = cls(config)
        model.net.load_state_dict(data["state_dict"], strict=False)
        return model
