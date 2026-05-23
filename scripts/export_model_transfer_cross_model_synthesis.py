#!/usr/bin/env python3
"""Export cross-model synthesis for SkillAdmit downstream validation.

What this file does:
  Combines the original hard_v3/hard_v4 evidence packages with the
  model-transfer evidence package and exports a cross-model comparison table:
  per-strategy outcomes, selected-vs-no-experience deltas, context deltas,
  forced-bad replication, and explicit claim boundaries.

Why it is needed:
  A second model is useful only if its results are interpreted against the
  frozen baseline evidence. This script separates replicated findings
  (especially forced bad artifacts) from model-sensitive findings (such as
  hard_v4 strict selected-vs-no-experience).

Inputs:
  benchmark/downstream/reports/hard_v3_evidence_package.json
  benchmark/downstream/reports/hard_v4_evidence_package.json
  benchmark/downstream/reports/model_transfer_evidence_package.json

Outputs:
  benchmark/downstream/reports/model_transfer_cross_model_synthesis.json
  benchmark/downstream/reports/model_transfer_cross_model_synthesis.md
  benchmark/downstream/reports/model_transfer_cross_model_synthesis.tex

Who runs it:
  Researchers or Codex sessions after regenerating either the baseline
  hard_v3/hard_v4 evidence packages or the model-transfer evidence package.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "benchmark" / "downstream" / "reports"

DEFAULT_HARD_V3_PACKAGE = REPORT_DIR / "hard_v3_evidence_package.json"
DEFAULT_HARD_V4_PACKAGE = REPORT_DIR / "hard_v4_evidence_package.json"
DEFAULT_TRANSFER_PACKAGE = REPORT_DIR / "model_transfer_evidence_package.json"
DEFAULT_JSON = REPORT_DIR / "model_transfer_cross_model_synthesis.json"
DEFAULT_MD = REPORT_DIR / "model_transfer_cross_model_synthesis.md"
DEFAULT_TEX = REPORT_DIR / "model_transfer_cross_model_synthesis.tex"

BASELINE_MODEL_LABEL = "mimo-v2.5-pro"
TRANSFER_MODEL_LABEL = "mimo-v2.5"

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

SETTING_SPECS = [
    {
        "suite": "hard_v3",
        "setting": "tree-aware",
        "baseline_run": "llm_downstream_hard_v3_tree_core_30x2",
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
        "suite": "hard_v3",
        "setting": "strict visible",
        "baseline_run": "llm_downstream_hard_v3_strict_30x8",
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
        "suite": "hard_v4",
        "setting": "tree-aware",
        "baseline_run": "llm_downstream_hard_v4_tree_24x8",
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
        "suite": "hard_v4",
        "setting": "strict visible",
        "baseline_run": "llm_downstream_hard_v4_strict_24x8",
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
            "Forced bad artifacts replicate across the two-model hard_v3/hard_v4 "
            "comparison: baseline 0/108 and transfer 0/108, with 216 total "
            "public-pass/hidden-fail cases."
        ),
        (
            "The hard_v3 selected-vs-no-experience pattern is stable across the two "
            "models: tree-aware ties at 29/30, and strict visible-file selected is "
            "+1 task over no_experience."
        ),
        (
            "The hard_v4 strict selected comparison is model-sensitive: baseline "
            "selected trails no_experience by two tasks, while transfer selected "
            "beats no_experience by three tasks."
        ),
        (
            "Precondition-only is not model-general selected improvement: it is +1 "
            "over selected in both baseline strict settings, but ties or trails "
            "selected for the transfer model."
        ),
    ],
    "not_supported": [
        "Do not claim model-general SkillAdmit-selected superiority.",
        "Do not claim selected token savings across models.",
        "Do not claim precondition-only generally replaces repository context.",
        "Do not use model-transfer results to retune hard_v3 or hard_v4.",
        "Do not treat the second model as a new clean task boundary; it is a model-transfer replication over frozen tasks.",
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(resolve(path).read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with resolve(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def source_package(name: str, path: Path, package: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "path": display_path(path),
        "sha256": sha256_file(path),
        "generated_at_utc": package.get("generated_at_utc"),
    }


def find_baseline_row(package: dict[str, Any], run_name: str, strategy: str) -> dict[str, Any]:
    for row in package["primary_strategy_table"]:
        if row["run_name"] == run_name and row["strategy"] == strategy:
            return row
    raise KeyError(f"Missing baseline row: {run_name}/{strategy}")


def find_transfer_row(package: dict[str, Any], suite: str, setting: str, strategy: str) -> dict[str, Any]:
    for row in package["primary_strategy_table"]:
        if row["suite"] == suite and row["setting"] == setting and row["strategy"] == strategy:
            return row
    raise KeyError(f"Missing transfer row: {suite}/{setting}/{strategy}")


def normalize_row(
    model_role: str,
    model_label: str,
    suite: str,
    setting: str,
    row: dict[str, Any],
) -> dict[str, Any]:
    tasks = int(row["tasks"])
    successes = int(row["successes"])
    return {
        "model_role": model_role,
        "model_label": model_label,
        "suite": suite,
        "setting": setting,
        "strategy": row["strategy"],
        "display_strategy": row.get("display_strategy", DISPLAY.get(row["strategy"], row["strategy"])),
        "success": row["success"],
        "successes": successes,
        "tasks": tasks,
        "success_rate": round(successes / tasks, 4) if tasks else 0.0,
        "negative_transfer": int(row["negative_transfer"]),
        "public_passed_hidden_failed": int(row["public_passed_hidden_failed"]),
        "artifact_adherence": int(row.get("artifact_adherence", 0)),
        "parse_errors": int(row.get("parse_errors", 0)),
        "total_tokens": int(row["total_tokens"]),
        "included_repo_tree_rows": int(row["included_repo_tree_rows"]),
        "visible_file_rows": int(row["visible_file_rows"]),
    }


def normalized_strategy_rows(
    hard_v3: dict[str, Any],
    hard_v4: dict[str, Any],
    transfer: dict[str, Any],
) -> list[dict[str, Any]]:
    baseline_packages = {"hard_v3": hard_v3, "hard_v4": hard_v4}
    rows = []
    for spec in SETTING_SPECS:
        suite = spec["suite"]
        setting = spec["setting"]
        for strategy in spec["strategies"]:
            baseline = find_baseline_row(baseline_packages[suite], spec["baseline_run"], strategy)
            rows.append(normalize_row("baseline", BASELINE_MODEL_LABEL, suite, setting, baseline))
            transfer_row = find_transfer_row(transfer, suite, setting, strategy)
            rows.append(normalize_row("transfer", TRANSFER_MODEL_LABEL, suite, setting, transfer_row))
    return rows


def row_index(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    return {
        (row["model_role"], row["suite"], row["setting"], row["strategy"]): row
        for row in rows
    }


def delta(left: dict[str, Any], right: dict[str, Any]) -> dict[str, int]:
    return {
        "success_delta": int(left["successes"]) - int(right["successes"]),
        "token_delta": int(left["total_tokens"]) - int(right["total_tokens"]),
    }


def paired_strategy_table(strategy_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = row_index(strategy_rows)
    out = []
    for spec in SETTING_SPECS:
        suite = spec["suite"]
        setting = spec["setting"]
        for strategy in spec["strategies"]:
            baseline = rows[("baseline", suite, setting, strategy)]
            transfer = rows[("transfer", suite, setting, strategy)]
            out.append(
                {
                    "suite": suite,
                    "setting": setting,
                    "strategy": strategy,
                    "display_strategy": baseline["display_strategy"],
                    "baseline_model": baseline["model_label"],
                    "baseline_success": baseline["success"],
                    "baseline_tokens": baseline["total_tokens"],
                    "baseline_artifact_adherence": f"{baseline['artifact_adherence']}/{baseline['tasks']}",
                    "transfer_model": transfer["model_label"],
                    "transfer_success": transfer["success"],
                    "transfer_tokens": transfer["total_tokens"],
                    "transfer_artifact_adherence": f"{transfer['artifact_adherence']}/{transfer['tasks']}",
                    "success_delta_transfer_minus_baseline": transfer["successes"] - baseline["successes"],
                    "token_delta_transfer_minus_baseline": transfer["total_tokens"] - baseline["total_tokens"],
                }
            )
    return out


def selected_comparison_table(strategy_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = row_index(strategy_rows)
    out = []
    for model_role, model_label in [("baseline", BASELINE_MODEL_LABEL), ("transfer", TRANSFER_MODEL_LABEL)]:
        for spec in SETTING_SPECS:
            suite = spec["suite"]
            setting = spec["setting"]
            selected = rows[(model_role, suite, setting, "skilladmit_selected")]
            no_exp = rows[(model_role, suite, setting, "no_experience")]
            out.append(
                {
                    "model_role": model_role,
                    "model_label": model_label,
                    "suite": suite,
                    "setting": setting,
                    "selected_success": selected["success"],
                    "baseline_success": no_exp["success"],
                    "selected_tokens": selected["total_tokens"],
                    "baseline_tokens": no_exp["total_tokens"],
                    **delta(selected, no_exp),
                }
            )
    return out


def context_comparison_table(strategy_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = row_index(strategy_rows)
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
    for model_role, model_label in [("baseline", BASELINE_MODEL_LABEL), ("transfer", TRANSFER_MODEL_LABEL)]:
        for suite, setting, comparison, left_strategy, right_strategy in specs:
            left = rows[(model_role, suite, setting, left_strategy)]
            right = rows[(model_role, suite, setting, right_strategy)]
            out.append(
                {
                    "model_role": model_role,
                    "model_label": model_label,
                    "suite": suite,
                    "setting": setting,
                    "comparison": comparison,
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


def forced_bad_summary(strategy_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_model = []
    for model_role, model_label in [("baseline", BASELINE_MODEL_LABEL), ("transfer", TRANSFER_MODEL_LABEL)]:
        forced_rows = [
            row
            for row in strategy_rows
            if row["model_role"] == model_role and row["strategy"] == "forced_bad_artifact"
        ]
        tasks = sum(row["tasks"] for row in forced_rows)
        successes = sum(row["successes"] for row in forced_rows)
        public_hidden = sum(row["public_passed_hidden_failed"] for row in forced_rows)
        negative_transfer = sum(row["negative_transfer"] for row in forced_rows)
        by_model.append(
            {
                "model_role": model_role,
                "model_label": model_label,
                "success": f"{successes}/{tasks}",
                "successes": successes,
                "tasks": tasks,
                "public_passed_hidden_failed": public_hidden,
                "negative_transfer": negative_transfer,
            }
        )
    return {
        "by_model": by_model,
        "combined_success": f"{sum(row['successes'] for row in by_model)}/{sum(row['tasks'] for row in by_model)}",
        "combined_tasks": sum(row["tasks"] for row in by_model),
        "combined_public_passed_hidden_failed": sum(row["public_passed_hidden_failed"] for row in by_model),
        "combined_negative_transfer": sum(row["negative_transfer"] for row in by_model),
        "replicated_across_models": all(
            row["successes"] == 0
            and row["tasks"] == 108
            and row["public_passed_hidden_failed"] == 108
            and row["negative_transfer"] == 108
            for row in by_model
        ),
    }


def sign(value: int) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "zero"


def selected_sensitivity_table(selected_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = {
        (row["model_role"], row["suite"], row["setting"]): row
        for row in selected_rows
    }
    out = []
    for spec in SETTING_SPECS:
        suite = spec["suite"]
        setting = spec["setting"]
        baseline = rows[("baseline", suite, setting)]
        transfer = rows[("transfer", suite, setting)]
        baseline_sign = sign(baseline["success_delta"])
        transfer_sign = sign(transfer["success_delta"])
        if baseline_sign == transfer_sign:
            pattern = "same_sign"
        elif baseline_sign == "zero" or transfer_sign == "zero":
            pattern = "weakened_or_strengthened_from_tie"
        else:
            pattern = "reversed_sign"
        out.append(
            {
                "suite": suite,
                "setting": setting,
                "baseline_selected_success": baseline["selected_success"],
                "baseline_no_experience_success": baseline["baseline_success"],
                "baseline_success_delta": baseline["success_delta"],
                "baseline_token_delta": baseline["token_delta"],
                "transfer_selected_success": transfer["selected_success"],
                "transfer_no_experience_success": transfer["baseline_success"],
                "transfer_success_delta": transfer["success_delta"],
                "transfer_token_delta": transfer["token_delta"],
                "pattern": pattern,
            }
        )
    return out


def derived_claims(
    selected_rows: list[dict[str, Any]],
    context_rows: list[dict[str, Any]],
    forced: dict[str, Any],
    sensitivity: list[dict[str, Any]],
) -> dict[str, Any]:
    selected_deltas = {
        f"{row['model_role']}_{row['suite']}_{row['setting'].replace(' ', '_')}": row["success_delta"]
        for row in selected_rows
    }
    selected_token_deltas = {
        f"{row['model_role']}_{row['suite']}_{row['setting'].replace(' ', '_')}": row["token_delta"]
        for row in selected_rows
    }
    strict_pre_vs_selected = [
        row
        for row in context_rows
        if row["comparison"] == "strict precondition-only vs selected"
    ]
    precondition_deltas = {
        f"{row['model_role']}_{row['suite']}": row["success_delta"]
        for row in strict_pre_vs_selected
    }
    h4_strict = [
        row
        for row in sensitivity
        if row["suite"] == "hard_v4" and row["setting"] == "strict visible"
    ][0]
    return {
        "selected_success_delta_values": selected_deltas,
        "selected_token_delta_values": selected_token_deltas,
        "selected_superiority_model_general": all(value > 0 for value in selected_deltas.values()),
        "selected_token_savings_model_general": all(value < 0 for value in selected_token_deltas.values()),
        "precondition_only_success_delta_vs_selected_values": precondition_deltas,
        "precondition_only_better_than_selected_model_general": all(value > 0 for value in precondition_deltas.values()),
        "forced_bad_replication_across_models": forced["replicated_across_models"],
        "forced_bad_combined_success": forced["combined_success"],
        "forced_bad_combined_public_passed_hidden_failed": forced["combined_public_passed_hidden_failed"],
        "hard_v3_tree_selected_tie_replicated": (
            selected_deltas["baseline_hard_v3_tree-aware"] == 0
            and selected_deltas["transfer_hard_v3_tree-aware"] == 0
        ),
        "hard_v3_strict_selected_plus_one_replicated": (
            selected_deltas["baseline_hard_v3_strict_visible"] == 1
            and selected_deltas["transfer_hard_v3_strict_visible"] == 1
        ),
        "hard_v4_strict_selected_delta_baseline": h4_strict["baseline_success_delta"],
        "hard_v4_strict_selected_delta_transfer": h4_strict["transfer_success_delta"],
        "hard_v4_strict_selected_delta_reversed": h4_strict["pattern"] == "reversed_sign",
    }


def build_package(
    hard_v3_path: Path,
    hard_v4_path: Path,
    transfer_path: Path,
) -> dict[str, Any]:
    hard_v3 = load_json(hard_v3_path)
    hard_v4 = load_json(hard_v4_path)
    transfer = load_json(transfer_path)
    strategy_rows = normalized_strategy_rows(hard_v3, hard_v4, transfer)
    paired_rows = paired_strategy_table(strategy_rows)
    selected_rows = selected_comparison_table(strategy_rows)
    context_rows = context_comparison_table(strategy_rows)
    forced = forced_bad_summary(strategy_rows)
    sensitivity = selected_sensitivity_table(selected_rows)
    derived = derived_claims(selected_rows, context_rows, forced, sensitivity)
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Cross-model synthesis over frozen hard_v3/hard_v4 downstream evidence. "
            "This report separates replicated findings from model-sensitive findings."
        ),
        "source_packages": [
            source_package("hard_v3_evidence_package", hard_v3_path, hard_v3),
            source_package("hard_v4_evidence_package", hard_v4_path, hard_v4),
            source_package("model_transfer_evidence_package", transfer_path, transfer),
        ],
        "models": {
            "baseline": BASELINE_MODEL_LABEL,
            "transfer": TRANSFER_MODEL_LABEL,
        },
        "normalized_strategy_rows": strategy_rows,
        "paired_strategy_table": paired_rows,
        "selected_comparison_table": selected_rows,
        "context_comparison_table": context_rows,
        "selected_sensitivity_table": sensitivity,
        "forced_bad_summary": forced,
        "derived_claims": derived,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def assert_current_cross_model(package: dict[str, Any]) -> None:
    if package["models"] != {"baseline": BASELINE_MODEL_LABEL, "transfer": TRANSFER_MODEL_LABEL}:
        raise AssertionError("model labels changed")
    if len(package["normalized_strategy_rows"]) != 64:
        raise AssertionError("normalized strategy row count changed")
    if len(package["paired_strategy_table"]) != 32:
        raise AssertionError("paired strategy row count changed")
    if len(package["selected_comparison_table"]) != 8:
        raise AssertionError("selected comparison row count changed")
    if len(package["context_comparison_table"]) != 12:
        raise AssertionError("context comparison row count changed")

    selected = {
        (row["model_role"], row["suite"], row["setting"]): row
        for row in package["selected_comparison_table"]
    }
    expected_selected = {
        ("baseline", "hard_v3", "tree-aware"): ("29/30", "29/30", 0, -917),
        ("baseline", "hard_v3", "strict visible"): ("29/30", "28/30", 1, -2763),
        ("baseline", "hard_v4", "tree-aware"): ("24/24", "24/24", 0, 1997),
        ("baseline", "hard_v4", "strict visible"): ("22/24", "24/24", -2, 5395),
        ("transfer", "hard_v3", "tree-aware"): ("29/30", "29/30", 0, -5242),
        ("transfer", "hard_v3", "strict visible"): ("29/30", "28/30", 1, 1698),
        ("transfer", "hard_v4", "tree-aware"): ("24/24", "23/24", 1, 3861),
        ("transfer", "hard_v4", "strict visible"): ("21/24", "18/24", 3, 422),
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
        (row["model_role"], row["suite"], row["setting"], row["comparison"]): row
        for row in package["context_comparison_table"]
    }
    expected_context = {
        ("baseline", "hard_v3", "tree-aware", "tree precondition context vs selected"): (0, 5268),
        ("baseline", "hard_v4", "tree-aware", "tree precondition context vs selected"): (0, 14904),
        ("baseline", "hard_v3", "strict visible", "strict precondition-only vs selected"): (1, 11225),
        ("baseline", "hard_v4", "strict visible", "strict precondition-only vs selected"): (1, 11511),
        ("baseline", "hard_v3", "strict visible", "strict precondition-only vs no_experience"): (2, 8462),
        ("baseline", "hard_v4", "strict visible", "strict precondition-only vs no_experience"): (-1, 16906),
        ("transfer", "hard_v3", "tree-aware", "tree precondition context vs selected"): (0, 6864),
        ("transfer", "hard_v4", "tree-aware", "tree precondition context vs selected"): (0, 2840),
        ("transfer", "hard_v3", "strict visible", "strict precondition-only vs selected"): (0, 15972),
        ("transfer", "hard_v4", "strict visible", "strict precondition-only vs selected"): (-1, 10925),
        ("transfer", "hard_v3", "strict visible", "strict precondition-only vs no_experience"): (1, 17670),
        ("transfer", "hard_v4", "strict visible", "strict precondition-only vs no_experience"): (2, 11347),
    }
    for key, expected in expected_context.items():
        row = context[key]
        actual = (row["success_delta"], row["token_delta"])
        if actual != expected:
            raise AssertionError(f"{key}: expected {expected}, got {actual}")

    forced = package["forced_bad_summary"]
    if forced["combined_success"] != "0/216":
        raise AssertionError("combined forced bad success changed")
    if forced["combined_public_passed_hidden_failed"] != 216:
        raise AssertionError("combined forced bad public-hidden count changed")
    if forced["combined_negative_transfer"] != 216:
        raise AssertionError("combined forced bad negative-transfer count changed")
    if forced["replicated_across_models"] is not True:
        raise AssertionError("forced bad replication flag changed")

    derived = package["derived_claims"]
    expected_derived = {
        "selected_superiority_model_general": False,
        "selected_token_savings_model_general": False,
        "precondition_only_better_than_selected_model_general": False,
        "forced_bad_replication_across_models": True,
        "forced_bad_combined_success": "0/216",
        "forced_bad_combined_public_passed_hidden_failed": 216,
        "hard_v3_tree_selected_tie_replicated": True,
        "hard_v3_strict_selected_plus_one_replicated": True,
        "hard_v4_strict_selected_delta_baseline": -2,
        "hard_v4_strict_selected_delta_transfer": 3,
        "hard_v4_strict_selected_delta_reversed": True,
    }
    for key, expected in expected_derived.items():
        actual = derived[key]
        if actual != expected:
            raise AssertionError(f"{key}: expected {expected}, got {actual}")

    rendered = render_markdown(package)
    required = [
        "0/216",
        "mimo-v2.5-pro",
        "mimo-v2.5",
        "hard_v4",
        "Do not claim model-general SkillAdmit-selected superiority.",
    ]
    for phrase in required:
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
    paired_rows = [
        [
            row["suite"],
            row["setting"],
            row["display_strategy"],
            row["baseline_success"],
            row["transfer_success"],
            row["success_delta_transfer_minus_baseline"],
            row["baseline_tokens"],
            row["transfer_tokens"],
        ]
        for row in package["paired_strategy_table"]
    ]
    selected_rows = [
        [
            row["model_role"],
            row["model_label"],
            row["suite"],
            row["setting"],
            row["selected_success"],
            row["baseline_success"],
            row["success_delta"],
            row["token_delta"],
        ]
        for row in package["selected_comparison_table"]
    ]
    sensitivity_rows = [
        [
            row["suite"],
            row["setting"],
            row["baseline_success_delta"],
            row["transfer_success_delta"],
            row["pattern"],
        ]
        for row in package["selected_sensitivity_table"]
    ]
    context_rows = [
        [
            row["model_role"],
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
            row["model_role"],
            row["model_label"],
            row["success"],
            row["negative_transfer"],
            row["public_passed_hidden_failed"],
        ]
        for row in package["forced_bad_summary"]["by_model"]
    ]
    derived_rows = [
        [key, json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value]
        for key, value in sorted(package["derived_claims"].items())
    ]
    source_rows = [
        [
            row["name"],
            f"`{row['path']}`",
            f"`{row['sha256'][:16]}`",
            f"`{row['generated_at_utc']}`" if row.get("generated_at_utc") else "",
        ]
        for row in package["source_packages"]
    ]
    supported = "\n".join(f"- {claim}" for claim in package["claim_boundary"]["supported"])
    not_supported = "\n".join(f"- {claim}" for claim in package["claim_boundary"]["not_supported"])
    return "\n\n".join(
        [
            "# Model-Transfer Cross-Model Synthesis",
            f"Generated at UTC: `{package['generated_at_utc']}`",
            package["purpose"],
            (
                f"Models: baseline `{package['models']['baseline']}`, transfer "
                f"`{package['models']['transfer']}`."
            ),
            "## Paired Strategy Table",
            md_table(
                [
                    "suite",
                    "setting",
                    "strategy",
                    "baseline_success",
                    "transfer_success",
                    "transfer_minus_baseline",
                    "baseline_tokens",
                    "transfer_tokens",
                ],
                paired_rows,
            ),
            "## Selected Versus No Experience",
            md_table(
                [
                    "role",
                    "model",
                    "suite",
                    "setting",
                    "selected",
                    "no_experience",
                    "success_delta",
                    "token_delta",
                ],
                selected_rows,
            ),
            "## Selected Sensitivity",
            md_table(
                ["suite", "setting", "baseline_delta", "transfer_delta", "pattern"],
                sensitivity_rows,
            ),
            "## Context Comparisons",
            md_table(
                [
                    "role",
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
            "## Forced Bad Artifact Replication",
            md_table(["role", "model", "success", "negative_transfer", "public_hidden"], forced_rows),
            (
                f"Combined: `{package['forced_bad_summary']['combined_success']}` success, "
                f"`{package['forced_bad_summary']['combined_public_passed_hidden_failed']}` "
                "public-pass/hidden-fail cases."
            ),
            "## Derived Claim Flags",
            md_table(["flag", "value"], derived_rows),
            "## Supported Claims",
            supported,
            "## Unsupported Claims",
            not_supported,
            "## Source Package Hashes",
            md_table(["name", "path", "sha256", "generated_at_utc"], source_rows),
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
        "% Auto-generated by scripts/export_model_transfer_cross_model_synthesis.py",
        "\\begin{tabular}{lllrrrr}",
        "\\hline",
        "Suite & Setting & Strategy & Baseline & Transfer & Delta & Tokens \\\\",
        "\\hline",
    ]
    for row in package["paired_strategy_table"]:
        lines.append(
            " & ".join(
                [
                    tex_escape(row["suite"]),
                    tex_escape(row["setting"]),
                    tex_escape(row["display_strategy"]),
                    tex_escape(row["baseline_success"]),
                    tex_escape(row["transfer_success"]),
                    str(row["success_delta_transfer_minus_baseline"]),
                    str(row["transfer_tokens"]),
                ]
            )
            + " \\\\"
        )
    lines.extend(["\\hline", "\\end{tabular}", "", "% Cross-model derived claim flags:"])
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
    parser.add_argument("--hard-v3-package", type=Path, default=DEFAULT_HARD_V3_PACKAGE)
    parser.add_argument("--hard-v4-package", type=Path, default=DEFAULT_HARD_V4_PACKAGE)
    parser.add_argument("--transfer-package", type=Path, default=DEFAULT_TRANSFER_PACKAGE)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX)
    parser.add_argument(
        "--assert-current-cross-model",
        action="store_true",
        help="Assert current baseline-vs-transfer synthesis values and claim invariants.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    package = build_package(args.hard_v3_package, args.hard_v4_package, args.transfer_package)
    if args.assert_current_cross_model:
        assert_current_cross_model(package)
    write_outputs(package, args.json_out, args.md_out, args.tex_out)
    print(f"paired_rows: {len(package['paired_strategy_table'])}")
    print(f"selected_rows: {len(package['selected_comparison_table'])}")
    print(f"context_rows: {len(package['context_comparison_table'])}")
    print(f"forced_bad_combined_success: {package['forced_bad_summary']['combined_success']}")
    print(f"hard_v4_strict_transfer_delta: {package['derived_claims']['hard_v4_strict_selected_delta_transfer']}")
    print(f"wrote_json: {display_path(args.json_out)}")
    print(f"wrote_md: {display_path(args.md_out)}")
    print(f"wrote_tex: {display_path(args.tex_out)}")


if __name__ == "__main__":
    main()
