from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .shadow import PlanSample


def load_flexible_jsonl(path: str | Path) -> list[PlanSample]:
    """Load WAMI, InjecAgent-like, or BIPIA-like JSONL into PlanSample rows.

    Supported keys are intentionally broad because public agent-safety datasets
    often use different field names for the same concepts.
    """
    samples: list[PlanSample] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            samples.append(_coerce_item(item))
    return samples


def load_flexible_json(path: str | Path) -> list[PlanSample]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = data if isinstance(data, list) else data.get("data", data.get("examples", []))
    return [_coerce_item(row) for row in rows]


def _first(item: dict[str, Any], keys: tuple[str, ...], default: str = "") -> str:
    for key in keys:
        value = item.get(key)
        if value is not None:
            return str(value)
    return default


def _coerce_item(item: dict[str, Any]) -> PlanSample:
    intent = _first(
        item,
        (
            "intent",
            "user_intent",
            "user_instruction",
            "instruction",
            "goal",
            "query",
            "task",
        ),
    )
    plan = _first(item, ("plan", "trajectory", "actions", "tool_calls", "response", "agent_plan"))
    if isinstance(item.get("actions"), list):
        plan = "\n".join(str(action) for action in item["actions"])
    label_raw = item.get("label", item.get("is_attack", item.get("attack", item.get("malicious", 0))))
    if isinstance(label_raw, str):
        label = 1 if label_raw.lower() in {"1", "true", "attack", "malicious", "unsafe", "injected"} else 0
    else:
        label = int(bool(label_raw))
    return PlanSample(intent=intent, plan=plan, label=label)

