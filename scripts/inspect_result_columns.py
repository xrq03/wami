from __future__ import annotations

from pathlib import Path

import pandas as pd


FILES = [
    "data/qwen25_7b_ollama_full_live_wami_injecagent_full.csv",
    "data/qwen25_7b_ollama_full_live_wami_bipia_full.csv",
    "data/qwen25_7b_ollama_full_live_wami_agentdojo_full.csv",
    "data/webagentguard_final_action_fidelity_operating_point.csv",
    "data/webagentguard_qwen25_action_fidelity_full_random25x25_3datasets.csv",
    "data/guardreasoner_vl_eco3b_4bit_response_random50x50_3datasets_details.csv",
    "data/bookagent_constraint_verifier_full.csv",
    "data/agentdojo_official_detector_wami_datasets_full.csv",
    "data/toolemu_sandbox_style_table2_full_tau7_details.csv",
    "data/llamaguard3_ollama_pc100_details.csv",
]


def main() -> None:
    for name in FILES:
        path = Path(name)
        print("---", name, path.exists(), path.stat().st_size if path.exists() else "")
        if not path.exists():
            continue
        try:
            df = pd.read_csv(path)
        except Exception as exc:
            print("ERR", exc)
            continue
        print(df.shape)
        print(list(df.columns))
        print(df.head(2).to_string(max_cols=18, max_colwidth=90))


if __name__ == "__main__":
    main()
