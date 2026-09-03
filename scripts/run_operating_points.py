from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run predefined WAMI operating points.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--val-data", required=True)
    parser.add_argument("--test-data", action="append", required=True)
    parser.add_argument("--prefix", default="data/operating_point")
    parser.add_argument("--points", default="-4.75,-4.5,-4.0,-3.5")
    args = parser.parse_args()

    for tau_text in args.points.split(","):
        tau = tau_text.strip()
        out = f"{args.prefix}_tau{tau.replace('-', 'm').replace('.', 'p')}"
        cmd = [
            sys.executable,
            "scripts/run_paper_mine_gateway.py",
            "--model",
            args.model,
            "--val-data",
            args.val_data,
            "--candidate-count",
            "1",
            "--tau-init",
            tau,
            "--candidate-radius",
            "0",
            "--use-transition-mine",
            "--transition-fusion",
            "0.35",
            "--use-auxiliary-heads",
            "--auxiliary-fusion",
            "0.10",
            "--output-md",
            out + ".md",
            "--output-csv",
            out + ".csv",
        ]
        for path in args.test_data:
            cmd.extend(["--test-data", path])
        print("running", " ".join(cmd), flush=True)
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
