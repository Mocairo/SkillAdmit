#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLUSTERS = ROOT / "benchmark" / "clusters" / "seed_clusters_with_artifacts.json"
OUT = ROOT / "benchmark" / "admission_samples" / "seed_admission_samples.jsonl"


LABELS = {
    "cluster_t1_missing_third_party": {
        "label": "defer",
        "label_rationale": (
            "The cluster contains real third-party dependency cases, but the candidate skill "
            "is risky if admitted too broadly. More negative-transfer validation is needed "
            "before turning this into a procedural skill."
        ),
    },
    "cluster_t2_local_module": {
        "label": "distill_into_skill",
        "label_rationale": (
            "The cluster shows a stable and reusable diagnostic procedure: check whether a "
            "missing module is local before treating it as an external dependency."
        ),
    },
    "cluster_t3_relative_import_script": {
        "label": "distill_into_skill",
        "label_rationale": (
            "The cluster supports a reusable procedure for diagnosing script-mode versus "
            "package-mode import failures."
        ),
    },
    "cluster_t4_wrong_cwd": {
        "label": "distill_into_skill",
        "label_rationale": (
            "The cluster supports a reusable procedure for checking cwd-sensitive path and "
            "import failures."
        ),
    },
    "cluster_t5_broken_package_import": {
        "label": "distill_into_skill",
        "label_rationale": (
            "The cluster supports a reusable procedure for package-internal import failures "
            "and provides negative-transfer evidence against blind dependency installation."
        ),
    },
}


def main() -> None:
    clusters = json.loads(CLUSTERS.read_text(encoding="utf-8"))
    rows = []

    for cluster in clusters:
        cluster_id = cluster["cluster_id"]
        label_info = LABELS[cluster_id]

        row = {
            "sample_id": f"sample_{cluster_id}",
            "source": "seed_cluster_v0",
            "family": cluster["family"],
            "cluster_id": cluster_id,
            "cluster_name": cluster["cluster_name"],
            "task_ids": cluster["task_ids"],
            "experience_cluster": cluster["experience_cluster"],
            "candidate_memory": cluster["candidate_memory"],
            "candidate_skill": cluster["candidate_skill"],
            "candidate_rule": cluster["candidate_rule"],
            "label": label_info["label"],
            "label_rationale": label_info["label_rationale"],
            "available_actions": [
                "discard",
                "store_as_memory",
                "distill_into_skill",
                "promote_to_rule",
                "defer",
            ],
        }
        rows.append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )

    print(f"Wrote {len(rows)} admission samples to {OUT}")


if __name__ == "__main__":
    main()
