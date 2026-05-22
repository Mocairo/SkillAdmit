#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "benchmark" / "admission_samples" / "v4_blind_admission_samples.jsonl"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_controller(module_name: str) -> Any:
    module = importlib.import_module(module_name)
    return module.RuleBasedSkillAdmitController()


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--controller-module", required=True)
    parser.add_argument("--samples", type=Path, action="append")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    sample_paths = args.samples or [DEFAULT_SAMPLES]
    controller = load_controller(args.controller_module)

    all_predictions: list[dict[str, Any]] = []
    failed_files = 0

    for path in sample_paths:
        samples = load_jsonl(path)
        correct = 0
        confusion: dict[str, Counter[str]] = defaultdict(Counter)
        file_predictions: list[dict[str, Any]] = []

        for sample in samples:
            decision = controller.predict(sample)
            gold = sample["label"]
            pred = decision.prediction
            is_correct = gold == pred
            correct += int(is_correct)
            confusion[gold][pred] += 1

            file_predictions.append(
                {
                    "sample_file": display_path(path),
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
        if correct != len(samples):
            failed_files += 1

        print("=" * 100)
        print(f"controller: {args.controller_module}")
        print(f"samples:    {display_path(path)}")
        print(f"total:      {len(samples)}")
        print(f"correct:    {correct}")
        print(f"accuracy:   {accuracy:.3f}")
        print("confusion:")
        for gold in sorted(confusion):
            print(f"  gold={gold}")
            for pred, count in sorted(confusion[gold].items()):
                print(f"    pred={pred}: {count}")

        errors = [row for row in file_predictions if not row["correct"]]
        print(f"errors:    {len(errors)}")
        for row in errors[:30]:
            print(
                f"  {row['sample_id']}: "
                f"gold={row['gold']} pred={row['pred']} "
                f"cluster={row['cluster_name']}"
            )

        all_predictions.extend(file_predictions)

    print("=" * 100)
    print(f"checked_files: {len(sample_paths)}")
    print(f"failed_files:  {failed_files}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in all_predictions),
            encoding="utf-8",
        )
        print(f"Wrote predictions to {args.output}")


if __name__ == "__main__":
    main()
