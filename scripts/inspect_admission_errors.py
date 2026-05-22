#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from skilladmit.controllers.rule_based_controller import RuleBasedSkillAdmitController


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "benchmark" / "admission_samples" / "v1_mixed_admission_samples.jsonl"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def clip(text: str, limit: int = 900) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...<truncated>..."


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES)
    args = parser.parse_args()

    samples = load_jsonl(args.samples)
    controller = RuleBasedSkillAdmitController()

    errors = []
    for sample in samples:
        decision = controller.predict(sample)
        gold = sample["label"]
        pred = decision.prediction
        if gold != pred:
            errors.append((sample, decision))

    print(f"samples: {len(samples)}")
    print(f"errors: {len(errors)}")

    for sample, decision in errors:
        print("=" * 100)
        print(f"sample_id: {sample['sample_id']}")
        print(f"cluster:   {sample['cluster_name']}")
        print(f"gold:      {sample['label']}")
        print(f"pred:      {decision.prediction}")
        print(f"reason:    {decision.reason}")
        print(f"scores:    {json.dumps(decision.scores, ensure_ascii=False, sort_keys=True)}")
        print(f"tags:      {','.join(sample.get('tags', []))}")
        print()
        print("label_rationale:")
        print(clip(sample.get("label_rationale", "")))
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
            print("observation:", clip(str(item.get("observation", "")), 400))
            print("diagnosis:  ", clip(str(item.get("diagnosis", "")), 400))
            print("fix_pattern:", clip(str(item.get("fix_pattern", "")), 400))
            print("risk:       ", clip(str(item.get("risk", "")), 400))


if __name__ == "__main__":
    main()
