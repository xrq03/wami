from __future__ import annotations

import json
from pathlib import Path

from .shadow import PlanSample


def load_llm_run_samples(path: str | Path, dangerous_only_as_attack: bool = True) -> list[PlanSample]:
    samples: list[PlanSample] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            if "error" in item:
                continue
            label = int(bool(item.get("dangerous_plan"))) if dangerous_only_as_attack else int(item.get("label", 0))
            samples.append(
                PlanSample(
                    intent=item.get("intent", ""),
                    plan=item.get("generated_plan", ""),
                    label=label,
                )
            )
    return samples

