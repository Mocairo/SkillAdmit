#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "benchmark" / "admission_samples" / "v4_blind_admission_samples.jsonl"
DEFAULT_PREDICTIONS = ROOT / "benchmark" / "admission_samples" / "v4_frozen_controller_predictions.jsonl"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def clip(text: str, limit: int = 700) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...<truncated>..."


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES)
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PREDICTIONS)
    args = parser.parse_args()

    samples = {row["sample_id"]: row for row in load_jsonl(args.samples)}
    predictions = load_jsonl(args.predictions)
    errors = [row for row in predictions if not row["correct"]]

    print(f"samples: {len(predictions)}")
    print(f"errors: {len(errors)}")

    for pred_row in errors:
        sample = samples[pred_row["sample_id"]]
        print("=" * 100)
        print(f"sample_id: {sample['sample_id']}")
        print(f"cluster:   {sample['cluster_name']}")
        print(f"gold:      {pred_row['gold']}")
        print(f"pred:      {pred_row['pred']}")
        print(f"reason:    {pred_row['reason']}")
        print(f"scores:    {json.dumps(pred_row['scores'], ensure_ascii=False, sort_keys=True)}")
        print()
        print("label_rationale:")
        print(clip(sample.get("label_rationale", "")))
        print()
        print("candidate_memory:")
        print(clip(sample.get("candidate_memory", "")))
        print()
        print("candidate_skill:")
        print(json.dumps(sample.get("candidate_skill", {}), indent=2, ensure_ascii=False))
        print()
        print("candidate_rule:")
        print(clip(sample.get("candidate_rule", "")))
        print()
        print("experience_cluster:")
        for item in sample.get("experience_cluster", []):
            print("-" * 80)
            print(f"task_id: {item.get('task_id')}")
            print("observation:", clip(str(item.get("observation", "")), 350))
            print("diagnosis:  ", clip(str(item.get("diagnosis", "")), 350))
            print("fix_pattern:", clip(str(item.get("fix_pattern", "")), 350))
            print("risk:       ", clip(str(item.get("risk", "")), 350))


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        raise SystemExit(0)
