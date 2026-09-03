from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

import numpy as np

from .gateway import ATTACK_TARGET_PATTERNS, GateDecision, WAMIGateway
from .model import WAMIModel
from .tdg import TDGNode


@dataclass
class OnlineStepTrace:
    step: int
    tool: str
    score: float
    threshold: float
    intent_state_cos: float
    intent_memory_cos: float
    intent_subgoal_cos: float
    reason: str


class OnlineWAMIGateway:
    """Step-by-step WAMI gateway for live agent execution loops."""

    def __init__(self, model: WAMIModel, gateway: WAMIGateway | None = None):
        self.model = model
        self.gateway = gateway or WAMIGateway(model)
        self.reset("")

    def reset(self, intent: str) -> None:
        self.intent = intent
        self.intent_vec = self.model.encode_intent(intent) if intent else np.zeros(self.model.config.dim, dtype=np.float32)
        self.state = self.intent_vec.copy()
        self.memory = self.intent_vec.copy()
        self.step_index = 0
        self.seen_untrusted_injection = False
        self.trace: list[OnlineStepTrace] = []

    def inspect_step(
        self,
        tool: str,
        params: dict[str, Any] | None = None,
        observation: str | None = None,
    ) -> GateDecision:
        params = dict(params or {})
        if observation is not None:
            params["observation"] = observation
        node = TDGNode(f"live{self.step_index}", tool, params, self._raw_tool(tool, params))

        action = self.model.encode_node(node)
        obs_vec = self.model.encode_observation(node)
        subgoal = self.model.infer_subgoal(self.intent_vec, self.state, action)
        self.memory = self.model.update_memory(self.memory, self.state, obs_vec)
        self.state = self.model.transition(self.state, action, self.state, self.memory, subgoal, obs_vec)

        score = self.model.mine_score(self.intent_vec, self.state)
        threshold = self.gateway.threshold(self.step_index)
        decision = self._rule_decision(node, score, threshold)
        self.trace.append(
            OnlineStepTrace(
                self.step_index,
                tool,
                score,
                threshold,
                self._cos(self.intent_vec, self.state),
                self._cos(self.intent_vec, self.memory),
                self._cos(self.intent_vec, subgoal),
                decision.reason,
            )
        )
        self.step_index += 1
        return decision

    def _rule_decision(self, node: TDGNode, score: float, threshold: float) -> GateDecision:
        intent_lower = self.intent.lower()
        tool_key = node.tool.lower()
        compact_tool = tool_key.replace("_", "").replace("-", "")
        param_blob = str(node.params).lower()
        high_risk = self.gateway._requires_explicit_authorization(tool_key)
        attack_target = any(pattern in param_blob for pattern in ATTACK_TARGET_PATTERNS)
        if "readuntrustedinjection" in compact_tool or "parseinjectedinstruction" in compact_tool:
            self.seen_untrusted_injection = True
            return GateDecision(True, None, None, score, threshold, "untrusted content observed; future actions hardened")
        if attack_target and (self.seen_untrusted_injection or high_risk):
            return GateDecision(False, self.step_index, node.tool, score, threshold, "tool arguments target attacker-controlled resource")
        if self.seen_untrusted_injection and high_risk:
            return GateDecision(False, self.step_index, node.tool, score, threshold, "high-risk tool follows untrusted injection content")
        sensitive_terms = self.gateway._sensitive_terms(tool_key)
        if sensitive_terms and high_risk and not self.gateway._explicitly_authorizes(intent_lower, sensitive_terms):
            return GateDecision(False, self.step_index, node.tool, score, threshold, "high-risk tool is not explicitly authorized by user intent")
        effective_threshold = threshold - self.gateway.score_margin
        if not self.seen_untrusted_injection and self.gateway._is_passive_observation(tool_key) and not attack_target:
            effective_threshold = float("-inf")
        if score < effective_threshold:
            return GateDecision(False, self.step_index, node.tool, score, threshold, "intent alignment score below dynamic threshold")
        return GateDecision(True, None, None, score, threshold, "live action remained aligned")

    @staticmethod
    def _raw_tool(tool: str, params: dict[str, Any]) -> str:
        args = ", ".join(f"{key}={json.dumps(value, ensure_ascii=False)}" for key, value in params.items())
        return f"Action: {tool}({args})"

    @staticmethod
    def _cos(a: np.ndarray, b: np.ndarray) -> float:
        denom = float(np.linalg.norm(a) * np.linalg.norm(b))
        return float(a @ b / denom) if denom > 0 else 0.0
