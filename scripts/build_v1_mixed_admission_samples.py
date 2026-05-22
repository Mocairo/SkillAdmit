#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

INPUTS = [
    ROOT / "benchmark" / "admission_samples" / "llm_coding_agent_v0_admission_samples.jsonl",
    ROOT / "benchmark" / "admission_samples" / "curated_non_skill_v1_admission_samples.jsonl",
]

OUT = ROOT / "benchmark" / "admission_samples" / "v1_mixed_admission_samples.jsonl"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    rows = []
    seen = set()

    for path in INPUTS:
        for row in load_jsonl(path):
            sample_id = row["sample_id"]
            if sample_id in seen:
                raise ValueError(f"Duplicate sample_id: {sample_id}")
            seen.add(sample_id)
            rows.append(row)

    OUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )

    counts = Counter(row["label"] for row in rows)

    print(f"Wrote {len(rows)} mixed admission samples to {OUT}")
    print("label_counts:")
    for label, count in sorted(counts.items()):
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
