#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRAJ = ROOT / "benchmark" / "trajectories" / "seed_trajectories.jsonl"
OUT = ROOT / "benchmark" / "clusters" / "seed_clusters.json"


CLUSTER_META = {
    "T1_missing_third_party_package": {
        "cluster_id": "cluster_t1_missing_third_party",
        "cluster_name": "Missing third-party dependency",
        "expected_primary_action": "defer",
        "note": "Useful only after confirming the module is truly external; risky if generalized to all ModuleNotFoundError cases.",
    },
    "T2_local_module_mistaken_as_missing_package": {
        "cluster_id": "cluster_t2_local_module",
        "cluster_name": "Local module mistaken as missing package",
        "expected_primary_action": "distill_into_skill",
        "note": "Strong negative-transfer evidence against blindly installing missing module names.",
    },
    "T3_relative_import_executed_as_script": {
        "cluster_id": "cluster_t3_relative_import_script",
        "cluster_name": "Relative import executed as script",
        "expected_primary_action": "distill_into_skill",
        "note": "Stable diagnostic procedure around script mode versus package mode.",
    },
    "T4_wrong_current_working_directory": {
        "cluster_id": "cluster_t4_wrong_cwd",
        "cluster_name": "Wrong current working directory",
        "expected_primary_action": "distill_into_skill",
        "note": "Stable diagnostic procedure around cwd-sensitive paths and imports.",
    },
    "T5_broken_package_structure": {
        "cluster_id": "cluster_t5_broken_package_import",
        "cluster_name": "Broken package-qualified import",
        "expected_primary_action": "distill_into_skill",
        "note": "Stable package-structure import pattern; also supports a general rule against blind pip install.",
    },
}


def main() -> None:
    grouped = defaultdict(list)

    for line in TRAJ.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        grouped[row["template"]].append(row)

    clusters = []

    for template, rows in sorted(grouped.items()):
        meta = CLUSTER_META[template]
        cluster = {
            "cluster_id": meta["cluster_id"],
            "cluster_name": meta["cluster_name"],
            "family": "python_import_debug",
            "template": template,
            "expected_primary_action": meta["expected_primary_action"],
            "note": meta["note"],
            "trajectory_ids": [row["trajectory_id"] for row in rows],
            "task_ids": [row["task_id"] for row in rows],
            "experience_cluster": [
                {
                    "task_id": row["task_id"],
                    "observation": row["trajectory_summary"]["observation"],
                    "diagnosis": row["trajectory_summary"]["diagnosis"],
                    "fix_pattern": row["trajectory_summary"]["fix_pattern"],
                    "risk": row["trajectory_summary"]["risk"],
                }
                for row in rows
            ],
        }
        clusters.append(cluster)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(clusters, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(clusters)} clusters to {OUT}")


if __name__ == "__main__":
    main()
