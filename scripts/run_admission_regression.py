#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from skilladmit.controllers.rule_based_controller import RuleBasedSkillAdmitController


ROOT = Path(__file__).resolve().parents[1]


# Regression data includes every sample set that has already been used for
# controller development. The current blind set is intentionally excluded.
DEFAULT_SAMPLE_FILES = [
    ROOT / "benchmark" / "admission_samples" / "seed_admission_samples.jsonl",
    ROOT / "benchmark" / "admission_samples" / "llm_coding_agent_v0_admission_samples.jsonl",
    ROOT / "benchmark" / "admission_samples" / "v0_mixed_admission_samples.jsonl",
    ROOT / "benchmark" / "admission_samples" / "v1_mixed_admission_samples.jsonl",
    ROOT / "benchmark" / "admission_samples" / "v2_heldout_admission_samples.jsonl",
    ROOT / "benchmark" / "admission_samples" / "v3_heldout_admission_samples.jsonl",
    ROOT / "benchmark" / "admission_samples" / "v4_blind_admission_samples.jsonl",
    ROOT / "benchmark" / "admission_samples" / "v5_blind_admission_samples.jsonl",
    ROOT / "benchmark" / "admission_samples" / "v6_blind_admission_samples.jsonl",
]


@dataclass
class EvalResult:
    path: Path
    total: int
    correct: int
    errors: list[tuple[str, str, str]]
    confusion: dict[str, Counter[str]]

    @property
    def accuracy(self) -> float:
        if self.total == 0:
            return 0.0
        return self.correct / self.total


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def evaluate_file(path: Path) -> EvalResult:
    controller = RuleBasedSkillAdmitController()
    samples = load_jsonl(path)

    correct = 0
    errors: list[tuple[str, str, str]] = []
    confusion: dict[str, Counter[str]] = defaultdict(Counter)

    for sample in samples:
        gold = sample["label"]
        decision = controller.predict(sample)
        pred = decision.prediction
        confusion[gold][pred] += 1
        if gold == pred:
            correct += 1
        else:
            errors.append((sample["sample_id"], gold, pred))

    return EvalResult(
        path=path,
        total=len(samples),
        correct=correct,
        errors=errors,
        confusion=dict(confusion),
    )


def print_result(result: EvalResult) -> None:
    rel_path = result.path.relative_to(ROOT)
    print("=" * 100)
    print(str(rel_path))
    print(f"samples:  {result.total}")
    print(f"correct:  {result.correct}")
    print(f"accuracy: {result.accuracy:.3f}")

    if result.errors:
        print("errors:")
        for sample_id, gold, pred in result.errors:
            print(f"  {sample_id}: gold={gold} pred={pred}")
    else:
        print("errors:   none")

    print("confusion:")
    for gold in sorted(result.confusion):
        preds = result.confusion[gold]
        rendered = ", ".join(f"{pred}={count}" for pred, count in sorted(preds.items()))
        print(f"  {gold}: {rendered}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--samples",
        type=Path,
        action="append",
        help="Optional JSONL admission sample file. Can be provided multiple times.",
    )
    parser.add_argument(
        "--min-accuracy",
        type=float,
        default=1.0,
        help="Exit with code 1 if any evaluated file is below this accuracy.",
    )
    args = parser.parse_args()

    paths = args.samples or DEFAULT_SAMPLE_FILES
    missing = [path for path in paths if not path.exists()]
    if missing:
        for path in missing:
            print(f"missing sample file: {path}")
        raise SystemExit(2)

    results = [evaluate_file(path) for path in paths]
    for result in results:
        print_result(result)

    failed = [result for result in results if result.accuracy < args.min_accuracy]
    print("=" * 100)
    print(f"checked_files: {len(results)}")
    print(f"min_accuracy:  {args.min_accuracy:.3f}")
    print(f"passed_files:  {len(results) - len(failed)}")
    print(f"failed_files:  {len(failed)}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
