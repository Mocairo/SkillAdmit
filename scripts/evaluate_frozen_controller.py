#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from skilladmit.controllers.rule_based_controller_v3_frozen import RuleBasedSkillAdmitController


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "benchmark" / "admission_samples" / "v4_blind_admission_samples.jsonl"
DEFAULT_OUTPUT = ROOT / "benchmark" / "admission_samples" / "v4_frozen_controller_predictions.jsonl"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-output", action="store_true")
    args = parser.parse_args()

    samples = load_jsonl(args.samples)
    controller = RuleBasedSkillAdmitController()

    correct = 0
    confusion: dict[str, Counter[str]] = defaultdict(Counter)
    predictions: list[dict[str, Any]] = []

    for sample in samples:
        decision = controller.predict(sample)
        gold = sample["label"]
        pred = decision.prediction
        is_correct = gold == pred

        correct += int(is_correct)
        confusion[gold][pred] += 1
        predictions.append(
            {
                "sample_id": sample["sample_id"],
                "cluster_id": sample["cluster_id"],
                "cluster_name": sample["cluster_name"],
                "gold": gold,
                "pred": pred,
                "correct": is_correct,
                "scores": decision.scores,
                "reason": decision.reason,
            }
        )

    accuracy = correct / len(samples) if samples else 0.0

    print("=" * 100)
    print("Frozen controller evaluation")
    print("=" * 100)
    print(f"samples:  {len(samples)}")
    print(f"correct:  {correct}")
    print(f"accuracy: {accuracy:.3f}")
    print()
    print("Confusion:")
    for gold in sorted(confusion):
        print(f"  gold={gold}")
        for pred, count in sorted(confusion[gold].items()):
            print(f"    pred={pred}: {count}")

    errors = [row for row in predictions if not row["correct"]]
    print()
    print(f"errors: {len(errors)}")
    for row in errors:
        print(
            f"  {row['sample_id']}: "
            f"gold={row['gold']} pred={row['pred']} "
            f"cluster={row['cluster_name']}"
        )

    if not args.no_output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in predictions),
            encoding="utf-8",
        )
        print()
        print(f"Wrote predictions to {args.output}")


if __name__ == "__main__":
    main()
