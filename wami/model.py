from __future__ import annotations

from dataclasses import dataclass
import json
import numpy as np

from .embedding import HashingTextEncoder
from .tdg import TDG, TDGNode


@dataclass
class WAMIConfig:
    dim: int = 128
    seed: int = 7
    world_scale: float = 0.15
    learning_rate: float = 0.03
    l2: float = 1e-4
    memory_decay: float = 0.72
    subgoal_mix: float = 0.45
    observation_mix: float = 0.30
    world_learning_rate: float = 0.01
    world_margin: float = 0.15


def _sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30.0, 30.0)))


class WAMIModel:
    """Latent world model plus MINE-style critic."""

    def __init__(self, config: WAMIConfig | None = None):
        self.config = config or WAMIConfig()
        self.encoder = HashingTextEncoder(dim=self.config.dim, seed=self.config.seed)
        rng = np.random.default_rng(self.config.seed)
        d = self.config.dim
        self.w_state = rng.normal(0, self.config.world_scale / np.sqrt(d), (d, d)).astype(np.float32)
        self.w_action = rng.normal(0, self.config.world_scale / np.sqrt(d), (d, d)).astype(np.float32)
        self.w_memory = rng.normal(0, self.config.world_scale / np.sqrt(d), (d, d)).astype(np.float32)
        self.w_subgoal = rng.normal(0, self.config.world_scale / np.sqrt(d), (d, d)).astype(np.float32)
        self.w_observation = rng.normal(0, self.config.world_scale / np.sqrt(d), (d, d)).astype(np.float32)
        self.w_parent = rng.normal(0, self.config.world_scale / np.sqrt(d), (d, d)).astype(np.float32)
        self.b_state = np.zeros(d, dtype=np.float32)
        self.b_subgoal = np.zeros(d, dtype=np.float32)
        self.b_memory = np.zeros(d, dtype=np.float32)
        self.w_mi = rng.normal(0, 0.1 / np.sqrt(d), (d, d)).astype(np.float32)
        self.u_intent = np.zeros(d, dtype=np.float32)
        self.u_state = np.zeros(d, dtype=np.float32)
        self.bias = np.float32(0.0)

    def encode_intent(self, intent: str) -> np.ndarray:
        return self.encoder.encode(intent)

    def encode_node(self, node: TDGNode) -> np.ndarray:
        payload = f"{node.tool} {json.dumps(node.params, sort_keys=True, ensure_ascii=False)}"
        return self.encoder.encode(payload)

    def encode_observation(self, node: TDGNode) -> np.ndarray:
        observed = []
        for key in ("input", "content", "observation", "result", "body", "text", "url", "query"):
            value = node.params.get(key)
            if value is not None:
                observed.append(f"{key}={value}")
        payload = " ".join(observed) if observed else node.raw
        return self.encoder.encode(f"observation {payload}")

    def infer_subgoal(self, intent_vec: np.ndarray, state: np.ndarray, action: np.ndarray) -> np.ndarray:
        subgoal = np.tanh(
            self.config.subgoal_mix * intent_vec
            + (1.0 - self.config.subgoal_mix) * state
            + action @ self.w_subgoal
            + self.b_subgoal
        )
        return self._normalize(subgoal)

    def update_memory(self, memory: np.ndarray, state: np.ndarray, observation: np.ndarray) -> np.ndarray:
        proposal = np.tanh(state @ self.w_memory + observation @ self.w_observation + self.b_memory)
        updated = self.config.memory_decay * memory + (1.0 - self.config.memory_decay) * proposal
        return self._normalize(updated)

    def transition(
        self,
        state: np.ndarray,
        action: np.ndarray,
        parent_state: np.ndarray | None = None,
        memory: np.ndarray | None = None,
        subgoal: np.ndarray | None = None,
        observation: np.ndarray | None = None,
    ) -> np.ndarray:
        if parent_state is None:
            parent_state = np.zeros_like(state)
        if memory is None:
            memory = np.zeros_like(state)
        if subgoal is None:
            subgoal = state
        if observation is None:
            observation = np.zeros_like(state)
        mixed = (
            state @ self.w_state
            + action @ self.w_action
            + parent_state @ self.w_parent
            + memory @ self.w_memory
            + subgoal @ self.w_subgoal
            + self.config.observation_mix * (observation @ self.w_observation)
            + self.b_state
        )
        return self._normalize(np.tanh(mixed))

    def train_world_step(
        self,
        intent_vec: np.ndarray,
        positive: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray],
        negative: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    ) -> float:
        """Contrastively tune the cognitive sandbox transition.

        The positive tuple is a benign transition context and the negative tuple
        is a shadow-adversarial context. The update nudges world dynamics so the
        predicted positive next state stays closer to the user intent than the
        adversarial next state by a margin.
        """

        pos_state, pos_action, pos_parent, pos_memory, pos_observation = positive
        neg_state, neg_action, neg_parent, neg_memory, neg_observation = negative
        pos_subgoal = self.infer_subgoal(intent_vec, pos_state, pos_action)
        neg_subgoal = self.infer_subgoal(intent_vec, neg_state, neg_action)
        pos_next = self.transition(pos_state, pos_action, pos_parent, pos_memory, pos_subgoal, pos_observation)
        neg_next = self.transition(neg_state, neg_action, neg_parent, neg_memory, neg_subgoal, neg_observation)
        pos_score = float(intent_vec @ pos_next)
        neg_score = float(intent_vec @ neg_next)
        loss = max(0.0, self.config.world_margin - pos_score + neg_score)
        if loss <= 0:
            return 0.0

        lr = self.config.world_learning_rate
        pos_error = intent_vec - pos_next
        neg_error = neg_next - intent_vec
        self.w_state += lr * (np.outer(pos_state, pos_error) - np.outer(neg_state, neg_error))
        self.w_action += lr * (np.outer(pos_action, pos_error) - np.outer(neg_action, neg_error))
        self.w_parent += lr * (np.outer(pos_parent, pos_error) - np.outer(neg_parent, neg_error))
        self.w_memory += lr * (np.outer(pos_memory, pos_error) - np.outer(neg_memory, neg_error))
        self.w_subgoal += lr * (np.outer(pos_subgoal, pos_error) - np.outer(neg_subgoal, neg_error))
        self.w_observation += lr * (
            np.outer(pos_observation, pos_error) - np.outer(neg_observation, neg_error)
        )
        self.b_state += np.float32(lr) * (pos_error - neg_error)
        return float(loss)

    def rollout(self, intent: str, tdg: TDG) -> list[tuple[TDGNode, np.ndarray]]:
        intent_vec = self.encode_intent(intent)
        state = intent_vec
        memory = intent_vec
        states: dict[str, np.ndarray] = {}
        parents = tdg.parents()
        trajectory: list[tuple[TDGNode, np.ndarray]] = []
        for node in tdg.topological_order():
            parent_vecs = [states[p] for p in parents.get(node.id, []) if p in states]
            parent_state = np.mean(parent_vecs, axis=0) if parent_vecs else state
            action = self.encode_node(node)
            observation = self.encode_observation(node)
            subgoal = self.infer_subgoal(intent_vec, state, action)
            memory = self.update_memory(memory, state, observation)
            state = self.transition(state, action, parent_state, memory, subgoal, observation)
            states[node.id] = state
            trajectory.append((node, state))
        return trajectory

    def cognitive_rollout(self, intent: str, tdg: TDG) -> list[dict[str, np.ndarray | TDGNode | int]]:
        intent_vec = self.encode_intent(intent)
        state = intent_vec
        memory = intent_vec
        states: dict[str, np.ndarray] = {}
        parents = tdg.parents()
        trace: list[dict[str, np.ndarray | TDGNode | int]] = []
        for step, node in enumerate(tdg.topological_order()):
            parent_vecs = [states[p] for p in parents.get(node.id, []) if p in states]
            parent_state = np.mean(parent_vecs, axis=0) if parent_vecs else state
            action = self.encode_node(node)
            observation = self.encode_observation(node)
            subgoal = self.infer_subgoal(intent_vec, state, action)
            memory = self.update_memory(memory, state, observation)
            state = self.transition(state, action, parent_state, memory, subgoal, observation)
            states[node.id] = state
            trace.append(
                {
                    "step": step,
                    "node": node,
                    "state": state,
                    "memory": memory,
                    "subgoal": subgoal,
                    "observation": observation,
                    "action": action,
                    "parent_state": parent_state,
                }
            )
        return trace

    def encode_plan(self, plan: str) -> np.ndarray:
        return self.encoder.encode(plan)

    def plan_score(self, intent: str, plan: str) -> float:
        intent_vec = self.encode_intent(intent)
        return self.mine_score(intent_vec, self.encode_plan(plan))

    def mine_score(self, intent_vec: np.ndarray, state_vec: np.ndarray) -> float:
        return float(intent_vec @ self.w_mi @ state_vec + intent_vec @ self.u_intent + state_vec @ self.u_state + self.bias)

    @staticmethod
    def _normalize(vec: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def train_mine_step(self, intent: np.ndarray, positive: np.ndarray, negative: np.ndarray) -> float:
        lr = self.config.learning_rate
        pos_score = self.mine_score(intent, positive)
        neg_score = self.mine_score(intent, negative)
        pos_grad = _sigmoid(pos_score) - 1.0
        neg_grad = _sigmoid(neg_score)
        self.w_mi -= lr * (
            pos_grad * np.outer(intent, positive)
            + neg_grad * np.outer(intent, negative)
            + self.config.l2 * self.w_mi
        )
        self.u_intent -= lr * ((pos_grad + neg_grad) * intent + self.config.l2 * self.u_intent)
        self.u_state -= lr * (pos_grad * positive + neg_grad * negative + self.config.l2 * self.u_state)
        self.bias -= np.float32(lr * (pos_grad + neg_grad))
        return float(-np.log(_sigmoid(pos_score) + 1e-8) - np.log(1.0 - _sigmoid(neg_score) + 1e-8))

    def save(self, path: str) -> None:
        np.savez(
            path,
            config=np.array(
                [
                    self.config.dim,
                    self.config.seed,
                    self.config.world_scale,
                    self.config.learning_rate,
                    self.config.l2,
                    self.config.memory_decay,
                    self.config.subgoal_mix,
                    self.config.observation_mix,
                    self.config.world_learning_rate,
                    self.config.world_margin,
                ],
                dtype=np.float64,
            ),
            w_state=self.w_state,
            w_action=self.w_action,
            w_memory=self.w_memory,
            w_subgoal=self.w_subgoal,
            w_observation=self.w_observation,
            w_parent=self.w_parent,
            b_state=self.b_state,
            b_subgoal=self.b_subgoal,
            b_memory=self.b_memory,
            w_mi=self.w_mi,
            u_intent=self.u_intent,
            u_state=self.u_state,
            bias=np.array([self.bias], dtype=np.float32),
        )

    @classmethod
    def load(cls, path: str) -> "WAMIModel":
        data = np.load(path, allow_pickle=False)
        cfg_raw = data["config"]
        cfg_values = list(cfg_raw)
        defaults = [0.72, 0.45, 0.30, 0.01, 0.15]
        while len(cfg_values) < 10:
            cfg_values.append(defaults[len(cfg_values) - 5])
        model = cls(
            WAMIConfig(
                int(cfg_values[0]),
                int(cfg_values[1]),
                float(cfg_values[2]),
                float(cfg_values[3]),
                float(cfg_values[4]),
                float(cfg_values[5]),
                float(cfg_values[6]),
                float(cfg_values[7]),
                float(cfg_values[8]),
                float(cfg_values[9]),
            )
        )
        model.w_state = data["w_state"]
        model.w_action = data["w_action"]
        model.w_memory = data["w_memory"] if "w_memory" in data else model.w_memory
        model.w_subgoal = data["w_subgoal"] if "w_subgoal" in data else model.w_subgoal
        model.w_observation = data["w_observation"] if "w_observation" in data else model.w_observation
        model.w_parent = data["w_parent"] if "w_parent" in data else model.w_parent
        model.b_state = data["b_state"]
        model.b_subgoal = data["b_subgoal"] if "b_subgoal" in data else model.b_subgoal
        model.b_memory = data["b_memory"] if "b_memory" in data else model.b_memory
        model.w_mi = data["w_mi"]
        model.u_intent = data["u_intent"]
        model.u_state = data["u_state"]
        model.bias = np.float32(data["bias"][0])
        return model
