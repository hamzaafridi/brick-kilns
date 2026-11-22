#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from brick_kilns.build_map import build_web
from brick_kilns.detect import detect
from brick_kilns.ground_truth import ingest_paqi
from brick_kilns.train import train_and_eval


def main():
    parser = argparse.ArgumentParser(description="Lahore brick kiln end-to-end pipeline")
    parser.add_argument(
        "--steps",
        default="all",
        help="Comma list: gt,train,detect,map,all",
    )
    args = parser.parse_args()
    steps = {s.strip() for s in args.steps.split(",")}
    if "all" in steps:
        steps = {"gt", "train", "detect", "map"}

    summary = {}
    if "gt" in steps:
        print("=== Ground truth (PAQI) ===")
        summary["ground_truth"] = ingest_paqi()
        print(json.dumps(summary["ground_truth"], indent=2))

    if "train" in steps:
        print("=== Train ===")
        summary["train"] = train_and_eval()

    if "detect" in steps:
        print("=== Detect ===")
        summary["detect"] = detect()

    if "map" in steps:
        print("=== Build map ===")
        path = build_web()
        summary["map"] = str(path)
        print(f"Open {path}")

    (ROOT / "data" / "outputs" / "pipeline_summary.json").write_text(
        json.dumps(summary, indent=2, default=str)
    )
    print("Done.")


if __name__ == "__main__":
    main()
