#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRAJECTORIES = ROOT / "benchmark" / "trajectories" / "llm_coding_agent_v0_trajectories.jsonl"
DEFAULT_ADMISSION = ROOT / "benchmark" / "admission_samples" / "llm_coding_agent_v0_admission_samples.jsonl"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(path)


def quantiles(values: list[float]) -> dict[str, float]:
    if not values:
        return {"min": 0.0, "median": 0.0, "mean": 0.0, "max": 0.0}
    return {
        "min": min(values),
        "median": median(values),
        "mean": mean(values),
        "max": max(values),
    }


def trajectory_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    token_rows = [row.get("token_usage") or {} for row in rows]
    total_prompt = sum(int(item.get("prompt_tokens") or 0) for item in token_rows)
    total_completion = sum(int(item.get("completion_tokens") or 0) for item in token_rows)
    total_tokens = sum(int(item.get("total_tokens") or 0) for item in token_rows)
    latencies = [float(row["model_latency_seconds"]) for row in rows if row.get("model_latency_seconds") is not None]
    successes = sum(1 for row in rows if row.get("success"))

    by_template: dict[str, dict[str, Any]] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row.get("template", "unknown")].append(row)

    for template, template_rows in sorted(grouped.items()):
        template_tokens = [
            int((row.get("token_usage") or {}).get("total_tokens") or 0)
            for row in template_rows
        ]
        by_template[template] = {
            "tasks": len(template_rows),
            "successes": sum(1 for row in template_rows if row.get("success")),
            "total_tokens": sum(template_tokens),
            "avg_tokens": mean(template_tokens) if template_tokens else 0.0,
        }

    return {
        "tasks": len(rows),
        "successes": successes,
        "success_rate": successes / len(rows) if rows else 0.0,
        "prompt_tokens": total_prompt,
        "completion_tokens": total_completion,
        "total_tokens": total_tokens,
        "avg_tokens_per_task": total_tokens / len(rows) if rows else 0.0,
        "avg_tokens_per_success": total_tokens / successes if successes else 0.0,
        "latency_seconds": {
            **quantiles(latencies),
            "total": sum(latencies),
        },
        "by_template": by_template,
    }


def admission_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    labels = Counter(row.get("label", "unknown") for row in rows)
    admitted = [row for row in rows if row.get("label") != "discard" and row.get("label") != "defer"]
    total_source_tokens = sum(int(row.get("total_tokens") or 0) for row in rows)
    admitted_source_tokens = sum(int(row.get("total_tokens") or 0) for row in admitted)

    return {
        "samples": len(rows),
        "label_counts": dict(sorted(labels.items())),
        "admitted_artifacts": len(admitted),
        "source_tokens_all_samples": total_source_tokens,
        "source_tokens_admitted_artifacts": admitted_source_tokens,
        "avg_source_tokens_per_sample": total_source_tokens / len(rows) if rows else 0.0,
        "avg_source_tokens_per_admitted_artifact": admitted_source_tokens / len(admitted) if admitted else 0.0,
        "artifacts": [
            {
                "sample_id": row.get("sample_id"),
                "label": row.get("label"),
                "cluster_name": row.get("cluster_name"),
                "num_trajectories": row.get("num_trajectories"),
                "success_rate": row.get("success_rate"),
                "total_tokens": row.get("total_tokens"),
                "avg_tokens": row.get("avg_tokens"),
            }
            for row in rows
        ],
    }


def break_even_summary(
    total_creation_tokens: int,
    admitted_artifacts: int,
    tokens_saved_per_artifact_use: float,
    expected_uses_per_future_task: float,
) -> dict[str, float]:
    saved_per_task = admitted_artifacts * tokens_saved_per_artifact_use * expected_uses_per_future_task
    return {
        "tokens_saved_per_artifact_use": tokens_saved_per_artifact_use,
        "expected_uses_per_future_task": expected_uses_per_future_task,
        "estimated_saved_tokens_per_future_task": saved_per_task,
        "break_even_future_tasks": total_creation_tokens / saved_per_task if saved_per_task > 0 else float("inf"),
        "break_even_uses_per_artifact": (total_creation_tokens / admitted_artifacts / tokens_saved_per_artifact_use)
        if admitted_artifacts and tokens_saved_per_artifact_use > 0
        else float("inf"),
    }


def render_markdown(summary: dict[str, Any]) -> str:
    traj = summary["trajectory_summary"]
    adm = summary["admission_summary"]
    be = summary["break_even"]

    lines = [
        "# SkillAdmit Cost Summary",
        "",
        "This report summarizes observed token and latency cost from the current real LLM trajectory run.",
        "",
        "## Inputs",
        "",
        f"- trajectories: `{summary['trajectory_file']}`",
        f"- admission samples: `{summary['admission_file']}`",
        "",
        "## LLM Trajectory Cost",
        "",
        f"- tasks: {traj['tasks']}",
        f"- successes: {traj['successes']}",
        f"- success_rate: {traj['success_rate']:.3f}",
        f"- prompt_tokens: {traj['prompt_tokens']}",
        f"- completion_tokens: {traj['completion_tokens']}",
        f"- total_tokens: {traj['total_tokens']}",
        f"- avg_tokens_per_task: {traj['avg_tokens_per_task']:.1f}",
        f"- avg_tokens_per_success: {traj['avg_tokens_per_success']:.1f}",
        f"- total_model_latency_seconds: {traj['latency_seconds']['total']:.3f}",
        f"- avg_model_latency_seconds: {traj['latency_seconds']['mean']:.3f}",
        "",
        "## Cost By Template",
        "",
        "| template | tasks | successes | total_tokens | avg_tokens |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for template, item in traj["by_template"].items():
        lines.append(
            f"| {template} | {item['tasks']} | {item['successes']} | "
            f"{item['total_tokens']} | {item['avg_tokens']:.1f} |"
        )

    lines.extend(
        [
            "",
            "## Admission Artifact Cost",
            "",
            f"- admission_samples: {adm['samples']}",
            f"- admitted_artifacts: {adm['admitted_artifacts']}",
            f"- source_tokens_all_samples: {adm['source_tokens_all_samples']}",
            f"- source_tokens_admitted_artifacts: {adm['source_tokens_admitted_artifacts']}",
            f"- avg_source_tokens_per_admitted_artifact: {adm['avg_source_tokens_per_admitted_artifact']:.1f}",
            "",
            "## Break-Even Estimate",
            "",
            "This estimate is parameterized. It is not a measured downstream result yet.",
            "",
            f"- tokens_saved_per_artifact_use: {be['tokens_saved_per_artifact_use']:.1f}",
            f"- expected_uses_per_future_task: {be['expected_uses_per_future_task']:.2f}",
            f"- estimated_saved_tokens_per_future_task: {be['estimated_saved_tokens_per_future_task']:.1f}",
            f"- break_even_future_tasks: {be['break_even_future_tasks']:.2f}",
            f"- break_even_uses_per_artifact: {be['break_even_uses_per_artifact']:.2f}",
            "",
            "## Caveat",
            "",
            "This is only an accounting report. A paper result still needs measured downstream reuse, not just assumed savings.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trajectories", type=Path, default=DEFAULT_TRAJECTORIES)
    parser.add_argument("--admission-samples", type=Path, default=DEFAULT_ADMISSION)
    parser.add_argument("--tokens-saved-per-artifact-use", type=float, default=500.0)
    parser.add_argument("--expected-uses-per-future-task", type=float, default=1.0)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    args = parser.parse_args()

    trajectories = load_jsonl(args.trajectories)
    admissions = load_jsonl(args.admission_samples)
    traj_summary = trajectory_summary(trajectories)
    adm_summary = admission_summary(admissions)
    be_summary = break_even_summary(
        traj_summary["total_tokens"],
        adm_summary["admitted_artifacts"],
        args.tokens_saved_per_artifact_use,
        args.expected_uses_per_future_task,
    )

    summary = {
        "trajectory_file": display_path(args.trajectories),
        "admission_file": display_path(args.admission_samples),
        "trajectory_summary": traj_summary,
        "admission_summary": adm_summary,
        "break_even": be_summary,
    }

    print("Trajectory cost")
    print(f"  tasks: {traj_summary['tasks']}")
    print(f"  successes: {traj_summary['successes']}")
    print(f"  total_tokens: {traj_summary['total_tokens']}")
    print(f"  avg_tokens_per_task: {traj_summary['avg_tokens_per_task']:.1f}")
    print(f"  total_latency_seconds: {traj_summary['latency_seconds']['total']:.3f}")
    print("Admission artifacts")
    print(f"  admitted_artifacts: {adm_summary['admitted_artifacts']}")
    print(f"  avg_source_tokens_per_admitted_artifact: {adm_summary['avg_source_tokens_per_admitted_artifact']:.1f}")
    print("Break-even estimate")
    print(f"  estimated_saved_tokens_per_future_task: {be_summary['estimated_saved_tokens_per_future_task']:.1f}")
    print(f"  break_even_future_tasks: {be_summary['break_even_future_tasks']:.2f}")

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote JSON report to {args.output_json}")

    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(render_markdown(summary), encoding="utf-8")
        print(f"Wrote Markdown report to {args.output_md}")


if __name__ == "__main__":
    main()
