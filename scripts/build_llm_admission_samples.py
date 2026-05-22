#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLUSTERS = ROOT / "benchmark" / "clusters" / "llm_coding_agent_v0_clusters_with_artifacts.json"
OUT = ROOT / "benchmark" / "admission_samples" / "llm_coding_agent_v0_admission_samples.jsonl"


def main() -> None:
    clusters = json.loads(CLUSTERS.read_text(encoding="utf-8"))
    rows = []

    for cluster in clusters:
        row = {
            "sample_id": f"sample_{cluster['cluster_id']}",
            "source": "llm_coding_agent_v0_cluster",
            "family": cluster["family"],
            "agent": cluster["agent"],
            "model": cluster["model"],
            "cluster_id": cluster["cluster_id"],
            "cluster_name": cluster["cluster_name"],
            "template": cluster["template"],
            "task_ids": cluster["task_ids"],
            "trajectory_ids": cluster["trajectory_ids"],
            "num_trajectories": cluster["num_trajectories"],
            "success_rate": cluster["success_rate"],
            "total_tokens": cluster["total_tokens"],
            "avg_tokens": cluster["avg_tokens"],
            "experience_cluster": cluster["experience_cluster"],
            "candidate_memory": cluster["candidate_memory"],
            "candidate_skill": cluster["candidate_skill"],
            "candidate_rule": cluster["candidate_rule"],
            "label": cluster["label"],
            "label_rationale": cluster["label_rationale"],
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

    print(f"Wrote {len(rows)} LLM admission samples to {OUT}")


if __name__ == "__main__":
    main()
