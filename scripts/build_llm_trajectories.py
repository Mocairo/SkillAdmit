#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "benchmark" / "agent_runs" / "llm_coding_agent_v0" / "trajectories.jsonl"
OUT = ROOT / "benchmark" / "trajectories" / "llm_coding_agent_v0_trajectories.jsonl"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def summarize_edits(row: dict[str, Any]) -> str:
    edits = row.get("applied_edits") or []
    if not edits:
        return "No edits were applied."

    parts = []
    for edit in edits:
        parts.append(
            f"{edit.get('path')} changed={edit.get('changed')} size={edit.get('new_size')}"
        )
    return "; ".join(parts)


def get_patch_field(row: dict[str, Any], key: str) -> str:
    patch = row.get("parsed_patch")
    if isinstance(patch, dict):
        value = patch.get(key, "")
        if isinstance(value, str):
            return value
    return ""


def main() -> None:
    rows = load_jsonl(IN)
    out_rows = []

    for row in rows:
        usage = row.get("model_usage") or {}

        out = {
            "trajectory_id": row["trajectory_id"],
            "task_id": row["task_id"],
            "family": row["family"],
            "template": row["template"],
            "agent": row["agent"],
            "model": row["model"],
            "source": "llm_coding_agent_v0",
            "success": row["success"],
            "initial_returncode": row["initial_returncode"],
            "final_returncode": row["final_returncode"],
            "token_usage": {
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
            },
            "model_latency_seconds": row.get("model_latency_seconds"),
            "files_seen": row.get("files_seen", []),
            "applied_edits": row.get("applied_edits", []),
            "trajectory_summary": {
                "observation": row.get("initial_verifier", {}).get("stdout_tail", "")[-1200:],
                "diagnosis": get_patch_field(row, "diagnosis"),
                "fix_pattern": summarize_edits(row),
                "notes": get_patch_field(row, "notes"),
                "validation": "Verifier passed after patch." if row["success"] else "Verifier failed after patch.",
            },
            "artifact_evidence": {
                "memory_signal": get_patch_field(row, "diagnosis"),
                "skill_signal": get_patch_field(row, "notes") or summarize_edits(row),
                "rule_signal": "Check whether the error is caused by dependency, local import, launch mode, cwd, or package structure before applying a generic fix.",
            },
        }
        out_rows.append(out)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in out_rows),
        encoding="utf-8",
    )

    print(f"Wrote {len(out_rows)} LLM trajectory summaries to {OUT}")


if __name__ == "__main__":
    main()
