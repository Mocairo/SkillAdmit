#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TRAJ = ROOT / "benchmark" / "trajectories" / "llm_coding_agent_v0_trajectories.jsonl"
OUT = ROOT / "benchmark" / "clusters" / "llm_coding_agent_v0_clusters.json"


CLUSTER_META = {
    "T1_missing_third_party_package": {
        "cluster_id": "llm_cluster_t1_missing_import_removed",
        "cluster_name": "Missing dependency import removed as unused",
        "note": (
            "The original task template represented missing external dependencies, "
            "but the LLM often solved these tasks by removing unused imports. "
            "This should be treated as a real observed agent repair pattern, not the original seed assumption."
        ),
    },
    "T2_local_module_mistaken_as_missing_package": {
        "cluster_id": "llm_cluster_t2_local_module",
        "cluster_name": "Local module import repaired",
        "note": "The LLM repaired local module import failures by changing imports to package-relative or package-qualified forms.",
    },
    "T3_relative_import_executed_as_script": {
        "cluster_id": "llm_cluster_t3_relative_import_script",
        "cluster_name": "Relative import repaired for script execution",
        "note": "The LLM repaired relative import script-mode failures by aligning import style with direct script execution.",
    },
    "T4_wrong_current_working_directory": {
        "cluster_id": "llm_cluster_t4_wrong_cwd",
        "cluster_name": "CWD-sensitive path repaired",
        "note": "The LLM repaired cwd-sensitive file access by anchoring paths more robustly.",
    },
    "T5_broken_package_structure": {
        "cluster_id": "llm_cluster_t5_broken_package_import",
        "cluster_name": "Package-internal bare import repaired",
        "note": "The LLM repaired package-internal bare imports using relative imports.",
    },
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    rows = load_jsonl(TRAJ)
    grouped = defaultdict(list)

    for row in rows:
        grouped[row["template"]].append(row)

    clusters = []

    for template, items in sorted(grouped.items()):
        meta = CLUSTER_META[template]
        successes = sum(1 for item in items if item["success"])
        total_tokens = sum(
            item.get("token_usage", {}).get("total_tokens") or 0
            for item in items
        )

        cluster = {
            "cluster_id": meta["cluster_id"],
            "cluster_name": meta["cluster_name"],
            "family": "python_import_debug",
            "template": template,
            "source": "llm_coding_agent_v0",
            "agent": "llm_coding_agent_v0",
            "model": items[0].get("model") if items else None,
            "note": meta["note"],
            "trajectory_ids": [item["trajectory_id"] for item in items],
            "task_ids": [item["task_id"] for item in items],
            "successes": successes,
            "num_trajectories": len(items),
            "success_rate": successes / len(items) if items else 0.0,
            "total_tokens": total_tokens,
            "avg_tokens": total_tokens / len(items) if items else None,
            "experience_cluster": [
                {
                    "task_id": item["task_id"],
                    "success": item["success"],
                    "observation": item["trajectory_summary"]["observation"],
                    "diagnosis": item["trajectory_summary"]["diagnosis"],
                    "fix_pattern": item["trajectory_summary"]["fix_pattern"],
                    "notes": item["trajectory_summary"]["notes"],
                    "validation": item["trajectory_summary"]["validation"],
                    "applied_edits": item.get("applied_edits", []),
                    "token_usage": item.get("token_usage", {}),
                }
                for item in items
            ],
        }
        clusters.append(cluster)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(clusters, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(clusters)} LLM clusters to {OUT}")


if __name__ == "__main__":
    main()
