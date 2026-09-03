from __future__ import annotations

from dataclasses import dataclass

from .evaluate import evaluate_gateway
from .gateway import WAMIGateway
from .shadow import PlanSample


@dataclass
class GreedyCalibrationResult:
    base_threshold: float
    plan_threshold: float
    score_margin: float
    ir: float
    fpr: float
    acc: float


def greedy_calibrate_gateway(
    model,
    validation_samples: list[PlanSample],
    tau_init: float = 0.15,
    target_fpr: float = 0.02,
    candidate_radius: float = 2.0,
    candidate_count: int = 81,
    use_action_prior: bool = True,
    use_plan_mine: bool = True,
) -> tuple[WAMIGateway, GreedyCalibrationResult]:
    """Greedy validation calibration for the paper-strict threshold path.

    The final paper states that tau is initialized to 0.15 and then calibrated
    on validation data by greedy search. This routine searches nearby threshold
    values and picks the highest IR among candidates whose FPR is under the
    requested target. If none satisfy the target, it picks the best accuracy.
    """

    if candidate_count < 2:
        candidates = [tau_init]
    else:
        step = (candidate_radius * 2.0) / (candidate_count - 1)
        candidates = [tau_init - candidate_radius + i * step for i in range(candidate_count)]
    best_gateway = None
    best_result = None
    feasible = []
    all_results = []
    for threshold in candidates:
        gateway = WAMIGateway(
            model,
            base_threshold=threshold,
            decay=0.02,
            use_action_prior=use_action_prior,
            use_plan_mine=use_plan_mine,
            plan_threshold=threshold,
        )
        metrics = evaluate_gateway(gateway, validation_samples)
        result = GreedyCalibrationResult(
            base_threshold=threshold,
            plan_threshold=threshold,
            score_margin=0.0,
            ir=metrics.interception_rate,
            fpr=metrics.false_positive_rate,
            acc=metrics.accuracy,
        )
        all_results.append((gateway, result))
        if result.fpr <= target_fpr:
            feasible.append((gateway, result))
    if feasible:
        best_gateway, best_result = max(feasible, key=lambda item: (item[1].ir, item[1].acc, -item[1].fpr))
    else:
        best_gateway, best_result = max(all_results, key=lambda item: (item[1].acc, item[1].ir, -item[1].fpr))
    return best_gateway, best_result
