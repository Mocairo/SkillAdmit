#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRAJ = ROOT / "benchmark" / "agent_runs" / "llm_coding_agent_v0" / "trajectories.jsonl"


def load_rows() -> list[dict]:
    return [json.loads(line) for line in TRAJ.read_text(encoding="utf-8").splitlines() if line.strip()]


def clip(text: str | None, limit: int = 3000) -> str:
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...<truncated>..."


def main() -> None:
    rows = load_rows()

    total = len(rows)
    passed = sum(1 for row in rows if row["success"])
    print("=" * 100)
    print("LLM run summary")
    print("=" * 100)
    print(f"total:   {total}")
    print(f"passed:  {passed}")
    print(f"failed:  {total - passed}")
    print(f"success_rate: {passed / total:.3f}" if total else "success_rate: 0.000")

    by_template = defaultdict(list)
    for row in rows:
        by_template[row["template"]].append(row)

    print("\nBy template:")
    for template, items in sorted(by_template.items()):
        ok = sum(1 for item in items if item["success"])
        print(f"  {template}: {ok}/{len(items)}")

    parse_errors = Counter(row["parse_error"] for row in rows if row.get("parse_error"))
    print("\nParse errors:")
    if parse_errors:
        for err, count in parse_errors.items():
            print(f"  {count}x {err}")
    else:
        print("  none")

    failed_rows = [row for row in rows if not row["success"]]

    print("\n" + "=" * 100)
    print("Failed samples")
    print("=" * 100)

    for row in failed_rows:
        print(f"\ntask_id: {row['task_id']}")
        print(f"template: {row['template']}")
        print(f"parse_error: {row.get('parse_error')}")
        print(f"initial_returncode: {row['initial_returncode']}")
        print(f"final_returncode: {row['final_returncode']}")

        print("\nraw_model_response:")
        print("-" * 100)
        print(clip(row.get("raw_model_response"), 4000))

        print("\nparsed_patch:")
        print("-" * 100)
        print(json.dumps(row.get("parsed_patch"), indent=2, ensure_ascii=False))

        print("\napplied_edits:")
        print("-" * 100)
        print(json.dumps(row.get("applied_edits"), indent=2, ensure_ascii=False))

        print("\nfinal stdout_tail:")
        print("-" * 100)
        print(clip(row.get("final_verifier", {}).get("stdout_tail"), 2000))

        print("\nfinal stderr_tail:")
        print("-" * 100)
        print(clip(row.get("final_verifier", {}).get("stderr_tail"), 2000))


if __name__ == "__main__":
    main()
