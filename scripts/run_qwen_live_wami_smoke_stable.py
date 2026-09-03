

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import run_qwen_full_live_wami_runtime as live
from wami.datasets import load_plan_samples


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """命令行入口。
    
    函数负责解析运行参数、加载数据集和模型配置、调用核心评估流程，并把结果写入 CSV、Markdown 或详情文件。你在 PyCharm 中运行对应脚本时，实际进入的就是这个函数。"""
    parser = argparse.ArgumentParser(description="Stable small qwen2.5 live agent WAMI smoke runner.")
    parser.add_argument("--dataset", choices=["InjecAgent", "BIPIA", "AgentDojo"], default="InjecAgent")
    parser.add_argument("--model", default="qwen2.5:7b-instruct")
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument("--attack-limit", type=int, default=5)
    parser.add_argument("--benign-limit", type=int, default=5)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--benign-offset", type=int, default=0)
    parser.add_argument("--max-steps", type=int, default=5)
    parser.add_argument("--planner-mode", default="max-directive-parser")
    parser.add_argument("--planner-max-tokens", type=int, default=80)
    parser.add_argument("--planner-timeout-sec", type=int, default=60)
    parser.add_argument("--bootstrap-first-observation", action="store_true")
    parser.add_argument("--model-a", default="wami_paper_strict_shadowv2_b70_e3_cuda.pt")
    parser.add_argument("--tau-a", type=float, default=-5.85)
    parser.add_argument("--model-b", default="wami_paper_strict_shadowv3_targeted_e2_cuda.pt")
    parser.add_argument("--tau-b", type=float, default=-3.75)
    parser.add_argument("--ensemble-mode", choices=["or", "and"], default="or")
    parser.add_argument("--output-csv", default="data/qwen_live_wami_smoke_stable.csv")
    parser.add_argument("--output-md", default="data/qwen_live_wami_smoke_stable.md")
    args = parser.parse_args()

    data_path = {
        "InjecAgent": ROOT / "data" / "injecagent_wami.jsonl",
        "BIPIA": ROOT / "data" / "bipia_wami.jsonl",
        "AgentDojo": ROOT / "data" / "agentdojo_wami.jsonl",
    }[args.dataset]
    samples = load_plan_samples(data_path)
    selected = live.select_samples(samples, args.attack_limit, args.benign_limit, args.offset, args.benign_offset)

    gateway_args = argparse.Namespace(
        model_a=args.model_a,
        tau_a=args.tau_a,
        model_b=args.model_b,
        tau_b=args.tau_b,
        ensemble_mode=args.ensemble_mode,
        risk_margin=0.0,
        passive_margin=0.15,
        use_runtime_flow_check=False,
        strict_side_effect_flow=False,
    )
    gateway = live.build_gateway(gateway_args)
    client = live.OllamaChatClient(
        args.model,
        args.ollama_url,
        temperature=0.0,
        max_tokens=args.planner_max_tokens,
        timeout_sec=args.planner_timeout_sec,
    )

    rows = []
    for pos, (index, sample) in enumerate(selected, start=1):
        start = time.perf_counter()
        row = live.run_one(
            args.dataset,
            index,
            sample,
            client,
            args.model,
            gateway,
            args.max_steps,
            False,
            args.planner_mode,
            False,
            args.bootstrap_first_observation,
            0,
            False,
        )
        rows.append(row)
        print(
            f"[{pos}/{len(selected)}] idx={index} label={sample.label} blocked={row.blocked} "
            f"risk={row.risky_actions} blocked_risk={row.risky_actions_blocked} "
            f"steps={row.executed_steps} latency={row.latency_ms:.1f}ms elapsed={time.perf_counter()-start:.1f}s",
            flush=True,
        )

    summary = live.summarize(args.dataset, args.model, rows, "ollama-stable")
    out_csv = ROOT / args.output_csv
    out_md = ROOT / args.output_md
    live.write_outputs(summary, rows, out_md, out_csv, trace_detail_limit=10)
    print(live.format_summary(summary))
    print(f"saved {out_csv}")
    print(f"saved {out_md}")


if __name__ == "__main__":
    main()
