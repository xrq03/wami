from __future__ import annotations

import numpy as np

from .gateway import WAMIGateway
from .shadow import PlanSample
from .tdg import build_tdg


def collect_alignment_scores(model, samples: list[PlanSample]) -> list[float]:
    scores: list[float] = []
    for sample in samples:
        intent_vec = model.encode_intent(sample.intent)
        for _, state in model.rollout(sample.intent, build_tdg(sample.plan)):
            scores.append(model.mine_score(intent_vec, state))
    return scores


def collect_plan_scores(model, samples: list[PlanSample]) -> list[float]:
    if not hasattr(model, "plan_score"):
        return []
    return [model.plan_score(sample.intent, sample.plan) for sample in samples]


def calibrate_gateway(
    model,
    samples: list[PlanSample],
    quantile: float = 0.05,
    margin: float = 0.02,
    use_action_prior: bool = True,
) -> WAMIGateway:
    benign = [sample for sample in samples if sample.label == 0] or samples
    scores = collect_alignment_scores(model, benign)
    plan_scores = collect_plan_scores(model, benign)
    if not scores:
        return WAMIGateway(model, use_action_prior=use_action_prior)
    threshold = float(np.quantile(scores, quantile) - margin)
    plan_threshold = float(np.quantile(plan_scores, quantile) - margin) if plan_scores else threshold
    return WAMIGateway(
        model,
        base_threshold=threshold,
        decay=0.0,
        use_action_prior=use_action_prior,
        plan_threshold=plan_threshold,
    )
