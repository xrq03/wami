from __future__ import annotations

from dataclasses import dataclass
import time

from .evaluate import Metrics, evaluate_gateway
from .gateway import WAMIGateway
from .shadow import PlanSample


@dataclass
class AblationResult:
    name: str
    metrics: Metrics
    latency_ms: float


def benchmark_gateway(gateway: WAMIGateway, samples: list[PlanSample]) -> tuple[Metrics, float]:
    start = time.perf_counter()
    metrics = evaluate_gateway(gateway, samples)
    elapsed_ms = (time.perf_counter() - start) * 1000.0 / max(1, len(samples))
    return metrics, elapsed_ms


def run_ablation(model, samples: list[PlanSample]) -> list[AblationResult]:
    variants = [
        ("WAMI Full", WAMIGateway(model, use_action_prior=True)),
        ("w/o Action Prior", WAMIGateway(model, use_action_prior=False)),
        ("Loose Threshold", WAMIGateway(model, base_threshold=-0.25, use_action_prior=True)),
        ("Strict Threshold", WAMIGateway(model, base_threshold=0.05, use_action_prior=True)),
    ]
    results = []
    for name, gateway in variants:
        metrics, latency = benchmark_gateway(gateway, samples)
        results.append(AblationResult(name, metrics, latency))
    return results

