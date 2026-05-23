#!/usr/bin/env python3
"""Export model-transfer downstream evidence for hard_v3 and hard_v4.

What this file does:
  Reads the predeclared hard_v3/hard_v4 transfer-model run directories and
  writes a compact evidence package with primary strategy rows, selected-vs-
  baseline deltas, context deltas, forced-bad aggregate evidence, source
  hashes, and explicit claim boundaries.

Why it is needed:
  The model-transfer protocol is a pre-run registration artifact. Once the
  second-model runs finish, this script turns their completed summaries into
  evidence while keeping the interpretation narrow: model sensitivity and
  negative-transfer replication, not universal selected superiority.

Inputs:
  benchmark/downstream/llm_runs/llm_downstream_hard_v3_transfer_mimo_v2_5_*/
  benchmark/downstream/llm_runs/llm_downstream_hard_v4_transfer_mimo_v2_5_*/
  benchmark/downstream/reports/model_transfer_replication_protocol.json

Outputs:
  benchmark/downstream/reports/model_transfer_evidence_package.json
  benchmark/downstream/reports/model_transfer_evidence_package.md
  benchmark/downstream/reports/model_transfer_evidence_package.tex

Who runs it:
  Researchers or Codex sessions after the predeclared transfer-model matrix has
  completed, before adding any model-transfer claim to paper-facing summaries.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = ROOT / "benchmark" / "downstream" / "llm_runs"
REPORT_DIR = ROOT / "benchmark" / "downstream" / "reports"

DEFAULT_PROTOCOL = REPORT_DIR / "model_transfer_replication_protocol.json"
DEFAULT_JSON = REPORT_DIR / "model_transfer_evidence_package.json"
DEFAULT_MD = REPORT_DIR / "model_transfer_evidence_package.md"
DEFAULT_TEX = REPORT_DIR / "model_transfer_evidence_package.tex"

TRANSFER_MODEL = "mimo-v2.5"
BASELINE_MODEL_LABEL = "mimo-v2.5-pro"

DISPLAY = {
    "no_experience": "No experience",
    "skilladmit_selected": "SkillAdmit-selected",
    "skilladmit_selected_with_precondition_context": "Selected + tree + preconditions",
    "skilladmit_selected_with_precondition_only": "Selected + preconditions only",
    "raw_memory": "Raw memory",
    "distilled_skills_all": "All distilled skills",
    "bad_dependency_rule": "Bad dependency rule",
    "promoted_rules": "Promoted rules",
    "forced_bad_artifact": "Forced bad artifact",
}

RUN_SPECS = [
    {
        "run_id": "MT1_hard_v3_tree",
        "suite": "hard_v3",
        "setting": "tree-aware",
        "run_name": "llm_downstream_hard_v3_transfer_mimo_v2_5_tree_30x8",
        "expected_rows": 240,
        "expected_tasks": 30,
        "strategies": [
            "no_experience",
            "skilladmit_selected",
            "skilladmit_selected_with_precondition_context",
            "raw_memory",
            "distilled_skills_all",
            "promoted_rules",
            "bad_dependency_rule",
            "forced_bad_artifact",
        ],
    },
    {
        "run_id": "MT2_hard_v3_strict",
        "suite": "hard_v3",
        "setting": "strict visible",
        "run_name": "llm_downstream_hard_v3_transfer_mimo_v2_5_strict_30x8",
        "expected_rows": 240,
        "expected_tasks": 30,
        "strategies": [
            "no_experience",
            "skilladmit_selected",
            "skilladmit_selected_with_precondition_only",
            "raw_memory",
            "distilled_skills_all",
            "promoted_rules",
            "bad_dependency_rule",
            "forced_bad_artifact",
        ],
    },
    {
        "run_id": "MT3_hard_v4_tree",
        "suite": "hard_v4",
        "setting": "tree-aware",
        "run_name": "llm_downstream_hard_v4_transfer_mimo_v2_5_tree_24x8",
        "expected_rows": 192,
        "expected_tasks": 24,
        "strategies": [
            "no_experience",
            "skilladmit_selected",
            "skilladmit_selected_with_precondition_context",
            "raw_memory",
            "distilled_skills_all",
            "promoted_rules",
            "bad_dependency_rule",
            "forced_bad_artifact",
        ],
    },
    {
        "run_id": "MT4_hard_v4_strict",
        "suite": "hard_v4",
        "setting": "strict visible",
        "run_name": "llm_downstream_hard_v4_transfer_mimo_v2_5_strict_24x8",
        "expected_rows": 192,
        "expected_tasks": 24,
        "strategies": [
            "no_experience",
            "skilladmit_selected",
            "skilladmit_selected_with_precondition_only",
            "raw_memory",
            "distilled_skills_all",
            "promoted_rules",
            "bad_dependency_rule",
            "forced_bad_artifact",
        ],
    },
]

CLAIM_BOUNDARY = {
    "supported": [
        (
            "The predeclared transfer matrix completed with model mimo-v2.5: "
            "hard_v3 and hard_v4, tree-aware and strict visible-file settings, "
            "864 total strategy-task rows, and zero parse errors."
        ),
        (
            "Forced bad artifacts replicate as systematic negative transfer under "
            "the transfer model: 0/108 success with 108 public-pass/hidden-fail cases."
        ),
        (
            "SkillAdmit-selected is model-sensitive rather than universally dominant: "
            "it ties no_experience in hard_v3 tree-aware, improves by one task in "
            "hard_v3 strict and hard_v4 tree-aware, and improves by three tasks in "
            "hard_v4 strict for this transfer model."
        ),
        (
            "Precondition context is not a universal replacement for ordinary selected "
            "context: strict precondition-only ties selected in hard_v3 and trails it "
            "in hard_v4 for this transfer model."
        ),
        (
            "Bad-dependency-rule success remains hard to interpret without artifact "
            "adherence: adherence is low in every transfer setting."
        ),
    ],
    "not_supported": [
        "Do not claim model-general SkillAdmit-selected superiority from one transfer model.",
        "Do not claim SkillAdmit-selected token savings; token deltas are mixed and protocol-dependent.",
        "Do not claim precondition-only replaces repository-tree context.",
        "Do not treat raw memory or all-skills as deployable admission policies.",
        "Do not tune hard_v3 or hard_v4 prompts, tasks, strategies, or hidden verifiers from these outcomes.",
        "Do not cite the pre-run protocol as model-performance evidence; cite this evidence package instead.",
    ],
}


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> str:
    resolved = resolve(path)
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(resolve(path).read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in resolve(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with resolve(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def source_info(path: Path) -> dict[str, Any]:
    resolved = resolve(path)
    stat = resolved.stat()
    return {
        "path": display_path(resolved),
        "size_bytes": stat.st_size,
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        "sha256": sha256_file(resolved),
    }


def ratio(successes: int, tasks: int) -> str:
    return f"{successes}/{tasks}"


def run_dir(run_root: Path, run_name: str) -> Path:
    return resolve(run_root) / run_name


def load_run(run_root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    directory = run_dir(run_root, spec["run_name"])
    summary_path = directory / "summary.json"
    trajectories_path = directory / "trajectories.jsonl"
    summary = read_json(summary_path)
    trajectories = read_jsonl(trajectories_path)
    return {
        "spec": spec,
        "run_dir": directory,
        "summary": summary,
        "trajectories": trajectories,
        "summary_path": summary_path,
        "trajectories_path": trajectories_path,
    }


def row_models(summary: dict[str, Any], trajectories: list[dict[str, Any]]) -> list[str]:
    models = summary.get("models")
    if isinstance(models, list) and models:
        return sorted(str(model) for model in models)
    return sorted({str(row.get("model")) for row in trajectories if row.get("model")})


def build_run_summaries(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for run in runs:
        spec = run["spec"]
        summary = run["summary"]
        trajectories = run["trajectories"]
        rows.append(
            {
                "run_id": spec["run_id"],
                "suite": spec["suite"],
                "setting": spec["setting"],
                "run_name": spec["run_name"],
                "models": row_models(summary, trajectories),
                "total_rows": summary.get("total_rows"),
                "expected_rows": spec["expected_rows"],
                "expected_tasks_per_strategy": spec["expected_tasks"],
                "parse_errors": sum(
                    int(item.get("parse_errors", 0))
                    for item in summary.get("strategies", {}).values()
                ),
                "source_files": {
                    "summary": source_info(run["summary_path"]),
                    "trajectories": source_info(run["trajectories_path"]),
                },
            }
        )
    return rows


def build_primary_strategy_table(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for run in runs:
        spec = run["spec"]
        summary = run["summary"]
        trajectories = run["trajectories"]
        by_strategy: dict[str, list[dict[str, Any]]] = {}
        for item in trajectories:
            by_strategy.setdefault(str(item.get("strategy")), []).append(item)
        models = row_models(summary, trajectories)
        for strategy in spec["strategies"]:
            item = summary["strategies"][strategy]
            strategy_items = by_strategy.get(strategy, [])
            rows.append(
                {
                    "run_id": spec["run_id"],
                    "suite": spec["suite"],
                    "setting": spec["setting"],
                    "run_name": spec["run_name"],
                    "strategy": strategy,
                    "display_strategy": DISPLAY.get(strategy, strategy),
                    "model": ",".join(models),
                    "success": ratio(item["successes"], item["tasks"]),
                    "successes": item["successes"],
                    "tasks": item["tasks"],
                    "success_rate": round(float(item.get("success_rate", 0.0)), 4),
                    "negative_transfer": item.get("negative_transfer", 0),
                    "public_passed_hidden_failed": item.get("public_passed_hidden_failed", 0),
                    "artifact_adherence": item.get("artifact_adherence", 0),
                    "parse_errors": item.get("parse_errors", 0),
                    "total_tokens": item.get("total_tokens", 0),
                    "avg_tokens": round(float(item.get("avg_tokens", 0.0)), 2),
                    "included_repo_tree_rows": sum(1 for row in strategy_items if row.get("included_repo_tree")),
                    "visible_file_rows": sum(1 for row in strategy_items if row.get("used_task_visible_files")),
                }
            )
    return rows


def row_index(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str], dict[str, Any]]:
    return {(row["suite"], row["setting"], row["strategy"]): row for row in rows}


def delta(left: dict[str, Any], right: dict[str, Any]) -> dict[str, int]:
    return {
        "success_delta": int(left["successes"]) - int(right["successes"]),
        "token_delta": int(left["total_tokens"]) - int(right["total_tokens"]),
    }


def selected_comparison_table(primary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = row_index(primary_rows)
    specs = [
        ("hard_v3", "tree-aware"),
        ("hard_v3", "strict visible"),
        ("hard_v4", "tree-aware"),
        ("hard_v4", "strict visible"),
    ]
    out = []
    for suite, setting in specs:
        selected = rows[(suite, setting, "skilladmit_selected")]
        no_exp = rows[(suite, setting, "no_experience")]
        out.append(
            {
                "suite": suite,
                "setting": setting,
                "model": selected["model"],
                "selected_success": selected["success"],
                "baseline_success": no_exp["success"],
                "selected_tokens": selected["total_tokens"],
                "baseline_tokens": no_exp["total_tokens"],
                **delta(selected, no_exp),
            }
        )
    return out


def context_comparison_table(primary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = row_index(primary_rows)
    specs = [
        (
            "hard_v3",
            "tree-aware",
            "tree precondition context vs selected",
            "skilladmit_selected_with_precondition_context",
            "skilladmit_selected",
        ),
        (
            "hard_v4",
            "tree-aware",
            "tree precondition context vs selected",
            "skilladmit_selected_with_precondition_context",
            "skilladmit_selected",
        ),
        (
            "hard_v3",
            "strict visible",
            "strict precondition-only vs selected",
            "skilladmit_selected_with_precondition_only",
            "skilladmit_selected",
        ),
        (
            "hard_v4",
            "strict visible",
            "strict precondition-only vs selected",
            "skilladmit_selected_with_precondition_only",
            "skilladmit_selected",
        ),
        (
            "hard_v3",
            "strict visible",
            "strict precondition-only vs no_experience",
            "skilladmit_selected_with_precondition_only",
            "no_experience",
        ),
        (
            "hard_v4",
            "strict visible",
            "strict precondition-only vs no_experience",
            "skilladmit_selected_with_precondition_only",
            "no_experience",
        ),
    ]
    out = []
    for suite, setting, comparison, left_strategy, right_strategy in specs:
        left = rows[(suite, setting, left_strategy)]
        right = rows[(suite, setting, right_strategy)]
        out.append(
            {
                "suite": suite,
                "setting": setting,
                "comparison": comparison,
                "model": left["model"],
                "left_strategy": left_strategy,
                "left_success": left["success"],
                "left_tokens": left["total_tokens"],
                "right_strategy": right_strategy,
                "right_success": right["success"],
                "right_tokens": right["total_tokens"],
                **delta(left, right),
            }
        )
    return out


def forced_bad_summary(primary_rows: list[dict[str, Any]]) -> dict[str, Any]:
    forced_rows = [row for row in primary_rows if row["strategy"] == "forced_bad_artifact"]
    by_setting = []
    for row in forced_rows:
        by_setting.append(
            {
                "suite": row["suite"],
                "setting": row["setting"],
                "model": row["model"],
                "success": row["success"],
                "successes": row["successes"],
                "tasks": row["tasks"],
                "negative_transfer": row["negative_transfer"],
                "public_passed_hidden_failed": row["public_passed_hidden_failed"],
            }
        )
    total_tasks = sum(int(row["tasks"]) for row in forced_rows)
    total_successes = sum(int(row["successes"]) for row in forced_rows)
    total_public_hidden = sum(int(row["public_passed_hidden_failed"]) for row in forced_rows)
    total_negative_transfer = sum(int(row["negative_transfer"]) for row in forced_rows)
    return {
        "by_setting": by_setting,
        "total_success": ratio(total_successes, total_tasks),
        "total_successes": total_successes,
        "total_tasks": total_tasks,
        "total_public_passed_hidden_failed": total_public_hidden,
        "total_negative_transfer": total_negative_transfer,
        "replicated_systematic_negative_transfer": (
            total_tasks == 108
            and total_successes == 0
            and total_public_hidden == 108
            and total_negative_transfer == 108
        ),
    }


def artifact_adherence_table(primary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tracked = {
        "bad_dependency_rule",
        "distilled_skills_all",
        "forced_bad_artifact",
        "promoted_rules",
        "raw_memory",
        "skilladmit_selected",
        "skilladmit_selected_with_precondition_context",
        "skilladmit_selected_with_precondition_only",
    }
    rows = []
    for row in primary_rows:
        if row["strategy"] not in tracked:
            continue
        tasks = int(row["tasks"])
        adherence = int(row["artifact_adherence"])
        rows.append(
            {
                "suite": row["suite"],
                "setting": row["setting"],
                "strategy": row["strategy"],
                "display_strategy": row["display_strategy"],
                "success": row["success"],
                "artifact_adherence": f"{adherence}/{tasks}",
                "adherence_rate": round(adherence / tasks, 4) if tasks else 0.0,
                "public_passed_hidden_failed": row["public_passed_hidden_failed"],
            }
        )
    return rows


def failure_taxonomy(runs: list[dict[str, Any]]) -> dict[str, Any]:
    by_suite_setting_strategy_template: Counter[tuple[str, str, str, str]] = Counter()
    public_hidden_by_strategy: Counter[str] = Counter()
    negative_transfer_by_strategy: Counter[str] = Counter()
    non_forced_failures_by_strategy: Counter[str] = Counter()

    for run in runs:
        spec = run["spec"]
        for row in run["trajectories"]:
            if row.get("success"):
                continue
            strategy = str(row.get("strategy"))
            template = str(row.get("template"))
            key = (spec["suite"], spec["setting"], strategy, template)
            by_suite_setting_strategy_template[key] += 1
            strategy_key = f"{spec['suite']}::{spec['setting']}::{strategy}"
            if row.get("public_passed_hidden_failed"):
                public_hidden_by_strategy[strategy_key] += 1
            if row.get("negative_transfer"):
                negative_transfer_by_strategy[strategy_key] += 1
            if strategy != "forced_bad_artifact":
                non_forced_failures_by_strategy[strategy_key] += 1

    return {
        "non_forced_failures_by_strategy": dict(sorted(non_forced_failures_by_strategy.items())),
        "public_passed_hidden_failed_by_strategy": dict(sorted(public_hidden_by_strategy.items())),
        "negative_transfer_by_strategy": dict(sorted(negative_transfer_by_strategy.items())),
        "by_suite_setting_strategy_template": [
            {
                "suite": suite,
                "setting": setting,
                "strategy": strategy,
                "template": template,
                "failures": count,
            }
            for (suite, setting, strategy, template), count in sorted(by_suite_setting_strategy_template.items())
        ],
    }


def derived_claims(
    selected_rows: list[dict[str, Any]],
    context_rows: list[dict[str, Any]],
    forced_summary: dict[str, Any],
    primary_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    selected_success_deltas = {
        f"{row['suite']}_{row['setting'].replace(' ', '_')}_selected_success_delta_vs_no_experience": row[
            "success_delta"
        ]
        for row in selected_rows
    }
    selected_token_deltas = {
        f"{row['suite']}_{row['setting'].replace(' ', '_')}_selected_token_delta_vs_no_experience": row[
            "token_delta"
        ]
        for row in selected_rows
    }
    context_success_deltas = {
        f"{row['suite']}_{row['setting'].replace(' ', '_')}_{row['comparison'].replace(' ', '_').replace('-', '_')}": row[
            "success_delta"
        ]
        for row in context_rows
    }
    context_token_deltas = {
        f"{row['suite']}_{row['setting'].replace(' ', '_')}_{row['comparison'].replace(' ', '_').replace('-', '_')}": row[
            "token_delta"
        ]
        for row in context_rows
    }
    bad_dependency_adherence = {
        f"{row['suite']}_{row['setting'].replace(' ', '_')}": f"{row['artifact_adherence']}/{row['tasks']}"
        for row in primary_rows
        if row["strategy"] == "bad_dependency_rule"
    }
    return {
        "selected_success_delta_values": selected_success_deltas,
        "selected_token_delta_values": selected_token_deltas,
        "selected_superiority_consistent": all(value > 0 for value in selected_success_deltas.values()),
        "selected_token_savings_consistent": all(value < 0 for value in selected_token_deltas.values()),
        "context_success_delta_values": context_success_deltas,
        "context_token_delta_values": context_token_deltas,
        "bad_dependency_adherence_values": bad_dependency_adherence,
        "forced_bad_total_success": forced_summary["total_success"],
        "forced_bad_total_tasks": forced_summary["total_tasks"],
        "forced_bad_total_public_passed_hidden_failed": forced_summary[
            "total_public_passed_hidden_failed"
        ],
        "forced_bad_negative_transfer_replicated": forced_summary[
            "replicated_systematic_negative_transfer"
        ],
    }


def protocol_source(protocol_path: Path, protocol: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": display_path(protocol_path),
        "sha256": sha256_file(protocol_path),
        "generated_at_utc": protocol.get("generated_at_utc"),
        "protocol_id": protocol.get("protocol_id"),
        "expected_total_rows": protocol.get("expected_total_rows"),
        "transfer_model": protocol.get("transfer_model"),
    }


def build_package(run_root: Path, protocol_path: Path) -> dict[str, Any]:
    protocol = read_json(protocol_path)
    runs = [load_run(run_root, spec) for spec in RUN_SPECS]
    primary_rows = build_primary_strategy_table(runs)
    selected_rows = selected_comparison_table(primary_rows)
    context_rows = context_comparison_table(primary_rows)
    forced_summary = forced_bad_summary(primary_rows)
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Model-transfer evidence package for the predeclared hard_v3/hard_v4 "
            "replication matrix. This is post-run evidence, not prompt tuning."
        ),
        "transfer_model": TRANSFER_MODEL,
        "baseline_model_label": BASELINE_MODEL_LABEL,
        "protocol_source": protocol_source(protocol_path, protocol),
        "run_summaries": build_run_summaries(runs),
        "primary_strategy_table": primary_rows,
        "selected_comparison_table": selected_rows,
        "context_comparison_table": context_rows,
        "forced_bad_summary": forced_summary,
        "artifact_adherence_table": artifact_adherence_table(primary_rows),
        "failure_taxonomy": failure_taxonomy(runs),
        "derived_claims": derived_claims(selected_rows, context_rows, forced_summary, primary_rows),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def assert_current_model_transfer(package: dict[str, Any]) -> None:
    if package["transfer_model"] != TRANSFER_MODEL:
        raise AssertionError("transfer model label changed")
    if package["baseline_model_label"] != BASELINE_MODEL_LABEL:
        raise AssertionError("baseline model label changed")
    if len(package["primary_strategy_table"]) != 32:
        raise AssertionError("primary strategy row count changed")
    if len(package["selected_comparison_table"]) != 4:
        raise AssertionError("selected comparison row count changed")
    if len(package["context_comparison_table"]) != 6:
        raise AssertionError("context comparison row count changed")

    for run in package["run_summaries"]:
        if run["total_rows"] != run["expected_rows"]:
            raise AssertionError(f"{run['run_name']}: incomplete row count")
        if run["parse_errors"] != 0:
            raise AssertionError(f"{run['run_name']}: parse errors changed")
        if run["models"] != [TRANSFER_MODEL]:
            raise AssertionError(f"{run['run_name']}: unexpected models {run['models']}")

    primary = {
        (row["suite"], row["setting"], row["strategy"]): row
        for row in package["primary_strategy_table"]
    }
    expected_success = {
        ("hard_v3", "tree-aware", "no_experience"): "29/30",
        ("hard_v3", "tree-aware", "skilladmit_selected"): "29/30",
        ("hard_v3", "tree-aware", "skilladmit_selected_with_precondition_context"): "29/30",
        ("hard_v3", "tree-aware", "raw_memory"): "30/30",
        ("hard_v3", "tree-aware", "distilled_skills_all"): "28/30",
        ("hard_v3", "tree-aware", "promoted_rules"): "29/30",
        ("hard_v3", "tree-aware", "bad_dependency_rule"): "29/30",
        ("hard_v3", "tree-aware", "forced_bad_artifact"): "0/30",
        ("hard_v3", "strict visible", "no_experience"): "28/30",
        ("hard_v3", "strict visible", "skilladmit_selected"): "29/30",
        ("hard_v3", "strict visible", "skilladmit_selected_with_precondition_only"): "29/30",
        ("hard_v3", "strict visible", "raw_memory"): "30/30",
        ("hard_v3", "strict visible", "distilled_skills_all"): "29/30",
        ("hard_v3", "strict visible", "promoted_rules"): "26/30",
        ("hard_v3", "strict visible", "bad_dependency_rule"): "29/30",
        ("hard_v3", "strict visible", "forced_bad_artifact"): "0/30",
        ("hard_v4", "tree-aware", "no_experience"): "23/24",
        ("hard_v4", "tree-aware", "skilladmit_selected"): "24/24",
        ("hard_v4", "tree-aware", "skilladmit_selected_with_precondition_context"): "24/24",
        ("hard_v4", "tree-aware", "raw_memory"): "24/24",
        ("hard_v4", "tree-aware", "distilled_skills_all"): "24/24",
        ("hard_v4", "tree-aware", "promoted_rules"): "24/24",
        ("hard_v4", "tree-aware", "bad_dependency_rule"): "21/24",
        ("hard_v4", "tree-aware", "forced_bad_artifact"): "0/24",
        ("hard_v4", "strict visible", "no_experience"): "18/24",
        ("hard_v4", "strict visible", "skilladmit_selected"): "21/24",
        ("hard_v4", "strict visible", "skilladmit_selected_with_precondition_only"): "20/24",
        ("hard_v4", "strict visible", "raw_memory"): "18/24",
        ("hard_v4", "strict visible", "distilled_skills_all"): "19/24",
        ("hard_v4", "strict visible", "promoted_rules"): "20/24",
        ("hard_v4", "strict visible", "bad_dependency_rule"): "18/24",
        ("hard_v4", "strict visible", "forced_bad_artifact"): "0/24",
    }
    for key, expected in expected_success.items():
        actual = primary[key]["success"]
        if actual != expected:
            raise AssertionError(f"{key}: expected {expected}, got {actual}")

    expected_adherence = {
        ("hard_v3", "tree-aware", "bad_dependency_rule"): 9,
        ("hard_v3", "strict visible", "bad_dependency_rule"): 10,
        ("hard_v4", "tree-aware", "bad_dependency_rule"): 6,
        ("hard_v4", "strict visible", "bad_dependency_rule"): 12,
    }
    for key, expected in expected_adherence.items():
        actual = primary[key]["artifact_adherence"]
        if actual != expected:
            raise AssertionError(f"{key}: expected adherence {expected}, got {actual}")

    selected = {
        (row["suite"], row["setting"]): row
        for row in package["selected_comparison_table"]
    }
    expected_selected = {
        ("hard_v3", "tree-aware"): ("29/30", "29/30", 0, -5242),
        ("hard_v3", "strict visible"): ("29/30", "28/30", 1, 1698),
        ("hard_v4", "tree-aware"): ("24/24", "23/24", 1, 3861),
        ("hard_v4", "strict visible"): ("21/24", "18/24", 3, 422),
    }
    for key, expected in expected_selected.items():
        row = selected[key]
        actual = (
            row["selected_success"],
            row["baseline_success"],
            row["success_delta"],
            row["token_delta"],
        )
        if actual != expected:
            raise AssertionError(f"{key}: expected {expected}, got {actual}")

    context = {
        (row["suite"], row["setting"], row["comparison"]): row
        for row in package["context_comparison_table"]
    }
    expected_context = {
        ("hard_v3", "tree-aware", "tree precondition context vs selected"): (0, 6864),
        ("hard_v4", "tree-aware", "tree precondition context vs selected"): (0, 2840),
        ("hard_v3", "strict visible", "strict precondition-only vs selected"): (0, 15972),
        ("hard_v4", "strict visible", "strict precondition-only vs selected"): (-1, 10925),
        ("hard_v3", "strict visible", "strict precondition-only vs no_experience"): (1, 17670),
        ("hard_v4", "strict visible", "strict precondition-only vs no_experience"): (2, 11347),
    }
    for key, expected in expected_context.items():
        row = context[key]
        actual = (row["success_delta"], row["token_delta"])
        if actual != expected:
            raise AssertionError(f"{key}: expected {expected}, got {actual}")

    forced = package["forced_bad_summary"]
    expected_forced = {
        "total_success": "0/108",
        "total_successes": 0,
        "total_tasks": 108,
        "total_public_passed_hidden_failed": 108,
        "total_negative_transfer": 108,
        "replicated_systematic_negative_transfer": True,
    }
    for key, expected in expected_forced.items():
        actual = forced[key]
        if actual != expected:
            raise AssertionError(f"forced {key}: expected {expected}, got {actual}")

    derived = package["derived_claims"]
    if derived["selected_superiority_consistent"] is not False:
        raise AssertionError("selected superiority should not be marked consistent")
    if derived["selected_token_savings_consistent"] is not False:
        raise AssertionError("selected token savings should not be marked consistent")
    if derived["forced_bad_negative_transfer_replicated"] is not True:
        raise AssertionError("forced bad replication flag changed")

    rendered = render_markdown(package)
    required_phrases = [
        "0/108",
        "mimo-v2.5",
        "Do not claim model-general SkillAdmit-selected superiority",
        "hard_v4",
        "strict visible",
    ]
    for phrase in required_phrases:
        if phrase not in rendered:
            raise AssertionError(f"missing rendered phrase: {phrase}")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def render_markdown(package: dict[str, Any]) -> str:
    primary_rows = [
        [
            row["suite"],
            row["setting"],
            row["display_strategy"],
            row["model"],
            row["success"],
            row["negative_transfer"],
            row["public_passed_hidden_failed"],
            f"{row['artifact_adherence']}/{row['tasks']}",
            row["total_tokens"],
        ]
        for row in package["primary_strategy_table"]
    ]
    selected_rows = [
        [
            row["suite"],
            row["setting"],
            row["selected_success"],
            row["baseline_success"],
            row["success_delta"],
            row["token_delta"],
        ]
        for row in package["selected_comparison_table"]
    ]
    context_rows = [
        [
            row["suite"],
            row["setting"],
            row["comparison"],
            row["left_success"],
            row["right_success"],
            row["success_delta"],
            row["token_delta"],
        ]
        for row in package["context_comparison_table"]
    ]
    forced_rows = [
        [
            row["suite"],
            row["setting"],
            row["success"],
            row["negative_transfer"],
            row["public_passed_hidden_failed"],
        ]
        for row in package["forced_bad_summary"]["by_setting"]
    ]
    adherence_rows = [
        [
            row["suite"],
            row["setting"],
            row["display_strategy"],
            row["success"],
            row["artifact_adherence"],
            row["adherence_rate"],
            row["public_passed_hidden_failed"],
        ]
        for row in package["artifact_adherence_table"]
    ]
    run_rows = [
        [
            row["run_id"],
            row["run_name"],
            ",".join(row["models"]),
            row["total_rows"],
            row["expected_rows"],
            row["parse_errors"],
            f"`{row['source_files']['summary']['sha256'][:16]}`",
            f"`{row['source_files']['trajectories']['sha256'][:16]}`",
        ]
        for row in package["run_summaries"]
    ]
    derived_rows = [
        [key, json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value]
        for key, value in sorted(package["derived_claims"].items())
    ]
    supported = "\n".join(f"- {claim}" for claim in package["claim_boundary"]["supported"])
    not_supported = "\n".join(f"- {claim}" for claim in package["claim_boundary"]["not_supported"])
    return "\n\n".join(
        [
            "# Model-Transfer Evidence Package",
            f"Generated at UTC: `{package['generated_at_utc']}`",
            package["purpose"],
            (
                f"Transfer model: `{package['transfer_model']}`. Baseline model label for "
                f"later cross-model synthesis: `{package['baseline_model_label']}`."
            ),
            "## Run Completion",
            md_table(
                [
                    "run_id",
                    "run_name",
                    "models",
                    "rows",
                    "expected",
                    "parse_errors",
                    "summary_sha256",
                    "trajectories_sha256",
                ],
                run_rows,
            ),
            "## Primary Strategy Table",
            md_table(
                [
                    "suite",
                    "setting",
                    "strategy",
                    "model",
                    "success",
                    "neg",
                    "public_hidden",
                    "adherence",
                    "tokens",
                ],
                primary_rows,
            ),
            "## Selected Versus No Experience",
            md_table(
                [
                    "suite",
                    "setting",
                    "selected",
                    "no_experience",
                    "success_delta",
                    "token_delta",
                ],
                selected_rows,
            ),
            "## Context Comparisons",
            md_table(
                [
                    "suite",
                    "setting",
                    "comparison",
                    "left_success",
                    "right_success",
                    "success_delta",
                    "token_delta",
                ],
                context_rows,
            ),
            "## Forced Bad Artifact Aggregate",
            md_table(["suite", "setting", "success", "negative_transfer", "public_hidden"], forced_rows),
            (
                f"Total: `{package['forced_bad_summary']['total_success']}` success, "
                f"`{package['forced_bad_summary']['total_public_passed_hidden_failed']}` "
                "public-pass/hidden-fail cases."
            ),
            "## Artifact Adherence",
            md_table(
                ["suite", "setting", "strategy", "success", "adherence", "adherence_rate", "public_hidden"],
                adherence_rows,
            ),
            "## Derived Claim Flags",
            md_table(["flag", "value"], derived_rows),
            "## Supported Claims",
            supported,
            "## Unsupported Claims",
            not_supported,
            "## Protocol Source",
            md_table(
                ["field", "value"],
                [
                    ["path", f"`{package['protocol_source']['path']}`"],
                    ["sha256", f"`{package['protocol_source']['sha256'][:16]}`"],
                    ["protocol_id", package["protocol_source"].get("protocol_id")],
                    ["expected_total_rows", package["protocol_source"].get("expected_total_rows")],
                ],
            ),
            "",
        ]
    )


def tex_escape(value: Any) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def render_latex(package: dict[str, Any]) -> str:
    lines = [
        "% Auto-generated by scripts/export_model_transfer_evidence_package.py",
        "\\begin{tabular}{lllrrrr}",
        "\\hline",
        "Suite & Setting & Strategy & Success & Neg. & Pub./hid. & Tokens \\\\",
        "\\hline",
    ]
    for row in package["primary_strategy_table"]:
        lines.append(
            " & ".join(
                [
                    tex_escape(row["suite"]),
                    tex_escape(row["setting"]),
                    tex_escape(row["display_strategy"]),
                    tex_escape(row["success"]),
                    str(row["negative_transfer"]),
                    str(row["public_passed_hidden_failed"]),
                    str(row["total_tokens"]),
                ]
            )
            + " \\\\"
        )
    lines.extend(["\\hline", "\\end{tabular}", "", "% Model-transfer derived claim flags:"])
    for key, value in sorted(package["derived_claims"].items()):
        lines.append(f"% {tex_escape(key)} = {tex_escape(value)}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(package: dict[str, Any], json_path: Path, md_path: Path, tex_path: Path) -> None:
    json_path = resolve(json_path)
    md_path = resolve(md_path)
    tex_path = resolve(tex_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(package), encoding="utf-8")
    tex_path.write_text(render_latex(package), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX)
    parser.add_argument(
        "--assert-current-model-transfer",
        action="store_true",
        help="Assert the current mimo-v2.5 transfer evidence values and invariants.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    package = build_package(args.run_root, args.protocol)
    if args.assert_current_model_transfer:
        assert_current_model_transfer(package)
    write_outputs(package, args.json_out, args.md_out, args.tex_out)
    print(f"primary_rows: {len(package['primary_strategy_table'])}")
    print(f"selected_rows: {len(package['selected_comparison_table'])}")
    print(f"context_rows: {len(package['context_comparison_table'])}")
    print(f"forced_bad_total_success: {package['forced_bad_summary']['total_success']}")
    print(f"forced_bad_public_hidden: {package['forced_bad_summary']['total_public_passed_hidden_failed']}")
    print(f"wrote_json: {display_path(args.json_out)}")
    print(f"wrote_md: {display_path(args.md_out)}")
    print(f"wrote_tex: {display_path(args.tex_out)}")


if __name__ == "__main__":
    main()
