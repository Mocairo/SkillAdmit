from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from skilladmit.controllers.rule_based_controller import RuleBasedSkillAdmitController


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SAMPLES = ROOT / "benchmark" / "admission_samples" / "seed_admission_samples.jsonl"


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES)
    args = parser.parse_args()

    samples = load_jsonl(args.samples)
    controller = RuleBasedSkillAdmitController()

    correct = 0
    confusion = defaultdict(Counter)

    print("=" * 100)
    print("Per-sample predictions")
    print("=" * 100)

    for sample in samples:
        decision = controller.predict(sample)
        gold = sample["label"]
        pred = decision.prediction
        is_correct = pred == gold

        correct += int(is_correct)
        confusion[gold][pred] += 1

        print(f"sample_id: {sample['sample_id']}")
        print(f"cluster:   {sample['cluster_name']}")
        print(f"gold:      {gold}")
        print(f"pred:      {pred}")
        print(f"correct:   {is_correct}")
        print(f"reason:    {decision.reason}")
        print(f"scores:    {json.dumps(decision.scores, ensure_ascii=False, sort_keys=True)}")
        print("-" * 100)

    total = len(samples)
    accuracy = correct / total if total else 0.0

    print("=" * 100)
    print("Summary")
    print("=" * 100)
    print(f"samples:  {total}")
    print(f"correct:  {correct}")
    print(f"accuracy: {accuracy:.3f}")

    print("\nConfusion:")
    for gold, preds in sorted(confusion.items()):
        print(f"  gold={gold}")
        for pred, count in sorted(preds.items()):
            print(f"    pred={pred}: {count}")


if __name__ == "__main__":
    main()
