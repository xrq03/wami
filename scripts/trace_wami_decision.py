from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wami.gateway import ATTACK_TARGET_PATTERNS, WAMIGateway
from wami.model import WAMIModel
from wami.tdg import analyze_tdg_security, build_tdg
from wami.training import load_jsonl


def cosine(a, b) -> float:
    denom = float((a @ a) ** 0.5 * (b @ b) ** 0.5)
    return float(a @ b / denom) if denom > 0 else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/agentdojo_wami.jsonl")
    parser.add_argument("--model", default="wami_agentdojo_final_tuned_e5.npz")
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--label", type=int, choices=[0, 1], default=1)
    parser.add_argument("--base-threshold", type=float, default=-0.05)
    parser.add_argument("--decay", type=float, default=0.02)
    parser.add_argument("--score-margin", type=float, default=0.0)
    parser.add_argument("--use-plan-mine", action="store_true")
    args = parser.parse_args()

    samples = [sample for sample in load_jsonl(args.data) if sample.label == args.label]
    if not samples:
        raise SystemExit(f"no samples with label={args.label} in {args.data}")
    sample = samples[args.index]
    model = WAMIModel.load(args.model) if Path(args.model).exists() else WAMIModel()
    gateway = WAMIGateway(
        model=model,
        base_threshold=args.base_threshold,
        decay=args.decay,
        score_margin=args.score_margin,
        use_plan_mine=args.use_plan_mine,
    )

    started = time.perf_counter()
    print("=== WAMI Decision Trace ===")
    print(f"data: {args.data}")
    print(f"model: {args.model if Path(args.model).exists() else 'fresh random WAMIModel'}")
    print(f"sample_index_with_label_{args.label}: {args.index}")
    print(f"label: {sample.label} ({'attack' if sample.label == 1 else 'benign'})")
    print(f"base_threshold: {gateway.base_threshold}")
    print(f"decay: {gateway.decay}")
    print(f"score_margin: {gateway.score_margin}")
    print()

    print("[1] User Intent")
    print(sample.intent)
    print()

    print("[2] Candidate Agent Plan")
    print(sample.plan)
    print()

    tdg = build_tdg(sample.plan)
    print("[3] Tool Dependency Graph")
    print(f"nodes: {len(tdg.nodes)}")
    for node in tdg.nodes:
        print(f"  - {node.id}: tool={node.tool}")
        print(f"    raw={node.raw}")
        print(f"    params={json.dumps(node.params, ensure_ascii=False)}")
    print(f"edges: {tdg.edges if tdg.edges else 'none'}")
    print(f"topological_order: {[node.id for node in tdg.topological_order()]}")
    print()

    security = analyze_tdg_security(tdg)
    print("[3b] Enhanced TDG Security/Data-Flow Analysis")
    for node_id in security.tool_order:
        info = security.nodes[node_id]
        print(
            f"  - {node_id}: external={info.external_observation} "
            f"untrusted_source={info.untrusted_source} sensitive_source={info.sensitive_source} "
            f"tainted={info.tainted} sensitive={info.sensitive} sink={info.sink}"
        )
        if info.memory_reads:
            print(f"    memory_reads={info.memory_reads}")
    for kind in ("data", "order", "memory", "taint", "sensitive"):
        edges = security.edges_by_kind(kind)
        if edges:
            print(f"  {kind}_edges: {[f'{e.src}->{e.dst}' for e in edges]}")
    print(f"  untrusted_paths_to_sinks: {security.untrusted_paths if security.untrusted_paths else 'none'}")
    print(f"  sensitive_flows_to_sinks: {security.sensitive_flows if security.sensitive_flows else 'none'}")
    print()

    intent_lower = sample.intent.lower()
    plan_lower = sample.plan.lower()
    intent_vec = model.encode_intent(sample.intent)

    print("[4] Plan-Level Rule Checks")
    adopts_injection = gateway._appears_to_adopt_injection(intent_lower, plan_lower)
    print(f"appears_to_adopt_external_injection: {adopts_injection}")
    if args.use_plan_mine:
        plan_score = model.plan_score(sample.intent, sample.plan)
        print(f"plan_mine_score: {plan_score:.6f}")
        print(f"plan_threshold: {gateway.plan_threshold:.6f}")
        print(f"plan_level_block: {plan_score < gateway.plan_threshold}")
    print()

    print("[5] Step-by-Step Rollout")
    seen_untrusted_injection = False
    final_reason = "trajectory remained aligned"
    final_allowed = True
    final_step = None
    final_tool = None
    final_score = 0.0
    final_threshold = gateway.threshold(0)

    cognitive_trace = model.cognitive_rollout(sample.intent, tdg)
    for item in cognitive_trace:
        step = int(item["step"])
        node = item["node"]
        state = item["state"]
        memory = item["memory"]
        subgoal = item["subgoal"]
        observation = item["observation"]
        action = item["action"]
        score = model.mine_score(intent_vec, state)
        threshold = gateway.threshold(step)
        effective_threshold = threshold - gateway.score_margin
        tool_key = node.tool.lower()
        compact_tool = tool_key.replace("_", "").replace("-", "")
        params_blob = str(node.params).lower()
        sensitive_terms = gateway._sensitive_terms(tool_key)
        high_risk = gateway._requires_explicit_authorization(tool_key)
        explicit_authorized = gateway._explicitly_authorizes(intent_lower, sensitive_terms or ())
        attack_target = any(pattern in params_blob for pattern in ATTACK_TARGET_PATTERNS)
        overlap = gateway._intent_tool_overlap(intent_lower, node.tool)
        passive_observation = gateway._is_passive_observation(tool_key)
        if (
            gateway.use_action_prior
            and not seen_untrusted_injection
            and passive_observation
            and not attack_target
        ):
            effective_threshold = float("-inf")
        elif gateway.use_action_prior and not seen_untrusted_injection and not attack_target and overlap > 0:
            effective_threshold -= 0.35

        print(f"step {step}: node={node.id} tool={node.tool}")
        print(f"  params={json.dumps(node.params, ensure_ascii=False)}")
        print(f"  mine_score={score:.6f}")
        print(f"  sandbox_intent_state_cos={cosine(intent_vec, state):+.6f}")
        print(f"  sandbox_intent_memory_cos={cosine(intent_vec, memory):+.6f}")
        print(f"  sandbox_intent_subgoal_cos={cosine(intent_vec, subgoal):+.6f}")
        print(f"  sandbox_action_observation_cos={cosine(action, observation):+.6f}")
        print(f"  dynamic_threshold={threshold:.6f}")
        print(f"  effective_threshold={effective_threshold:.6f}")
        print(f"  sensitive_terms={sensitive_terms}")
        print(f"  high_risk_tool={high_risk}")
        print(f"  explicitly_authorized_by_user={explicit_authorized}")
        print(f"  intent_tool_overlap={overlap}")
        print(f"  passive_observation={passive_observation}")
        print(f"  attack_target_in_args={attack_target}")
        print(f"  seen_untrusted_injection_before_step={seen_untrusted_injection}")

        if "readuntrustedinjection" in compact_tool or "parseinjectedinstruction" in compact_tool:
            seen_untrusted_injection = True
            print("  rule: marks future steps as following untrusted injection content")
            print("  decision_at_step=continue")
            continue
        if attack_target and (seen_untrusted_injection or high_risk):
            final_allowed = False
            final_reason = "tool arguments target attacker-controlled resource"
        elif seen_untrusted_injection and high_risk:
            final_allowed = False
            final_reason = "high-risk tool follows untrusted injection content"
        elif sensitive_terms and high_risk and not explicit_authorized:
            final_allowed = False
            final_reason = "high-risk tool is not explicitly authorized by user intent"
        elif score < effective_threshold:
            final_allowed = False
            final_reason = "intent alignment score below dynamic threshold"

        final_step = step
        final_tool = node.tool
        final_score = score
        final_threshold = threshold
        if not final_allowed:
            print(f"  decision_at_step=BLOCK")
            print(f"  block_reason={final_reason}")
            break
        print("  decision_at_step=continue")

    if adopts_injection:
        final_allowed = False
        final_step = None
        final_tool = None
        final_score = 0.0
        final_threshold = gateway.threshold(0)
        final_reason = "plan text appears to adopt an external injection instruction"

    decision = gateway.inspect(sample.intent, sample.plan)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    print()
    print("[6] Final Decision")
    print(f"manual_trace_allowed: {final_allowed}")
    print(f"manual_trace_block_step: {final_step}")
    print(f"manual_trace_block_tool: {final_tool}")
    print(f"manual_trace_score: {final_score:.6f}")
    print(f"manual_trace_threshold: {final_threshold:.6f}")
    print(f"manual_trace_reason: {final_reason}")
    print()
    print("[7] Gateway.inspect Cross-Check")
    print(f"gateway_allowed: {decision.allowed}")
    print(f"gateway_step: {decision.step}")
    print(f"gateway_tool: {decision.tool}")
    print(f"gateway_score: {decision.score:.6f}")
    print(f"gateway_threshold: {decision.threshold:.6f}")
    print(f"gateway_reason: {decision.reason}")
    print()
    print(f"trace_elapsed_ms: {elapsed_ms:.3f}")


if __name__ == "__main__":
    main()
