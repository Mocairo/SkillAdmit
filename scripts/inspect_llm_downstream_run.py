#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = ROOT / "benchmark" / "downstream" / "llm_runs"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def short(text: str, max_chars: int = 1200) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...<truncated>..."


def summarize(rows: list[dict[str, Any]]) -> None:
    print("=" * 100)
    print("LLM downstream run summary")
    print("=" * 100)
    print(f"rows: {len(rows)}")

    by_strategy: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_strategy[row["strategy"]].append(row)

    print("\nBy strategy:")
    for strategy, items in sorted(by_strategy.items()):
        total_tokens = sum(int((item.get("model_usage") or {}).get("total_tokens") or 0) for item in items)
        successes = sum(1 for item in items if item["success"])
        negative = sum(1 for item in items if item.get("negative_transfer"))
        public_hidden = sum(1 for item in items if item.get("public_passed_hidden_failed"))
        adherence = sum(1 for item in items if item.get("artifact_adherence"))
        parse_errors = sum(1 for item in items if item.get("parse_error"))
        print(
            f"  {strategy}: {successes}/{len(items)} "
            f"rate={successes / len(items):.3f} "
            f"neg={negative} public_hidden={public_hidden} "
            f"adherence={adherence}/{len(items)} parse_errors={parse_errors} "
            f"tokens={total_tokens}"
        )

    print("\nBy strategy/template:")
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["strategy"], row["template"])].append(row)
    for (strategy, template), items in sorted(grouped.items()):
        successes = sum(1 for item in items if item["success"])
        public_hidden = sum(1 for item in items if item.get("public_passed_hidden_failed"))
        print(f"  {strategy} | {template}: {successes}/{len(items)} public_hidden={public_hidden}")

    print("\nUsed artifact counts:")
    for strategy, items in sorted(by_strategy.items()):
        counter = Counter(str((item.get("parsed_patch") or {}).get("used_artifact")) for item in items)
        print(f"  {strategy}: {dict(counter)}")


def print_failures(rows: list[dict[str, Any]], max_failures: int) -> None:
    failures = [row for row in rows if not row["success"]]
    print("\n" + "=" * 100)
    print(f"Failures: {len(failures)}")
    print("=" * 100)

    for row in failures[:max_failures]:
        patch = row.get("parsed_patch") or {}
        print("\n" + "-" * 100)
        print(f"task_id: {row['task_id']}")
        print(f"strategy: {row['strategy']}")
        print(f"template: {row['template']}")
        print(f"public_tests_passed: {row.get('public_tests_passed')}")
        print(f"public_passed_hidden_failed: {row.get('public_passed_hidden_failed')}")
        print(f"artifact_adherence: {row.get('artifact_adherence')}")
        print(f"used_artifact: {patch.get('used_artifact')}")
        print(f"files_seen: {row.get('files_seen')}")
        print("\ndiagnosis:")
        print(short(str(patch.get("diagnosis", "")), 800))
        print("\nnotes:")
        print(short(str(patch.get("notes", "")), 800))
        print("\napplied_edits:")
        print(json.dumps(row.get("applied_edits", []), ensure_ascii=False, indent=2))
        print("\nfinal stdout tail:")
        print(short(row.get("final_verifier", {}).get("stdout_tail", ""), 1200))
        print("\nfinal stderr tail:")
        print(short(row.get("final_verifier", {}).get("stderr_tail", ""), 1200))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-name")
    parser.add_argument("--path", type=Path)
    parser.add_argument("--max-failures", type=int, default=20)
    args = parser.parse_args()

    if not args.run_name and not args.path:
        raise SystemExit("Provide --run-name or --path")
    path = args.path or (RUN_ROOT / args.run_name / "trajectories.jsonl")
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        raise SystemExit(f"Missing trajectories file: {path}")

    rows = read_jsonl(path)
    summarize(rows)
    print_failures(rows, args.max_failures)


if __name__ == "__main__":
    main()
