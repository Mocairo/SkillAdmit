#!/usr/bin/env python3
"""Export downstream boundary synthesis for hard_v2, hard_v3, and hard_v4.

What this file does:
  Reads the paper-facing hard_v2, hard_v3, and hard_v4 evidence packages and
  exports a three-boundary synthesis: comparable strategy rows, selected-vs-
  baseline deltas, context-variable deltas, forced-bad aggregate evidence,
  source hashes, and explicit claim boundaries.

Why it is needed:
  The earlier cross-version synthesis intentionally covers hard_v2 and hard_v3
  only. hard_v4 adds useful boundary evidence, but it should not overwrite that
  earlier artifact or be flattened into a single leaderboard. This script makes
  the newer three-boundary interpretation explicit: hard_v2 is conditional
  positive evidence, hard_v3 is mixed/generalization evidence, and hard_v4 is a
  stricter boundary plus negative-transfer replication.

Inputs:
  benchmark/downstream/reports/hard_v2_evidence_package.json
  benchmark/downstream/reports/hard_v3_evidence_package.json
  benchmark/downstream/reports/hard_v4_evidence_package.json

Outputs:
  benchmark/downstream/reports/downstream_boundary_synthesis.json
  benchmark/downstream/reports/downstream_boundary_synthesis.md
  benchmark/downstream/reports/downstream_boundary_synthesis.tex

Who runs it:
  Researchers or Codex sessions after hard_v2/hard_v3/hard_v4 evidence
  packages are regenerated, or before tightening paper claims.
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

DEFAULT_HARD_V2_PACKAGE = REPORT_DIR / "hard_v2_evidence_package.json"
DEFAULT_HARD_V3_PACKAGE = REPORT_DIR / "hard_v3_evidence_package.json"
DEFAULT_HARD_V4_PACKAGE = REPORT_DIR / "hard_v4_evidence_package.json"
DEFAULT_JSON = REPORT_DIR / "downstream_boundary_synthesis.json"
DEFAULT_MD = REPORT_DIR / "downstream_boundary_synthesis.md"
DEFAULT_TEX = REPORT_DIR / "downstream_boundary_synthesis.tex"


SUITE_ROLES = {
    "hard_v2": (
        "conditional positive evidence: tree-aware selected beats no_experience, "
        "while strict visible-file exposes selected-only limitations"
    ),
    "hard_v3": (
        "generalization boundary: selected no longer dominates tree-aware, while "
        "precondition-only is strong in strict visible-file"
    ),
    "hard_v4": (
        "stricter boundary: tree-aware saturates and strict visible-file rejects "
        "ordinary selected superiority"
    ),
}

RUN_LABELS = {
    "llm_downstream_hard_v2_full_25x6": "strict visible",
    "llm_downstream_hard_v2_tree_25x2": "tree-aware",
    "llm_downstream_hard_v2_selected_precondition_25": "tree-aware + preconditions",
    "llm_downstream_hard_v2_precondition_only_25": "strict + preconditions only",
    "llm_downstream_hard_v2_forced_bad_25": "forced harmful artifact",
    "llm_downstream_hard_v3_tree_core_30x2": "tree-aware",
    "llm_downstream_hard_v3_strict_30x8": "strict visible",
    "llm_downstream_hard_v4_tree_24x8": "tree-aware",
    "llm_downstream_hard_v4_strict_24x8": "strict visible",
}

RUN_ORDER = {
    "llm_downstream_hard_v2_full_25x6": 10,
    "llm_downstream_hard_v2_tree_25x2": 20,
    "llm_downstream_hard_v2_selected_precondition_25": 30,
    "llm_downstream_hard_v2_precondition_only_25": 40,
    "llm_downstream_hard_v2_forced_bad_25": 50,
    "llm_downstream_hard_v3_tree_core_30x2": 60,
    "llm_downstream_hard_v3_strict_30x8": 70,
    "llm_downstream_hard_v4_tree_24x8": 80,
    "llm_downstream_hard_v4_strict_24x8": 90,
}

CLAIM_BOUNDARY = {
    "supported": [
        (
            "Downstream validation is necessary because admission accuracy and "
            "keyword-like admission baselines are not enough to establish utility."
        ),
        (
            "SkillAdmit-selected utility is conditional: hard_v2 tree-aware is "
            "positive, hard_v3 tree-aware is tied, and hard_v4 tree-aware is saturated."
        ),
        (
            "Strict visible-file settings are not stable selected wins: hard_v2 "
            "selected is below no_experience, hard_v3 selected is above no_experience "
            "but not best, and hard_v4 selected is below no_experience."
        ),
        (
            "Precondition context is useful but not a universal replacement for "
            "repository context: strict precondition-only improves over selected "
            "in hard_v2, hard_v3, and hard_v4, but only hard_v3 makes it best."
        ),
        (
            "Forced harmful artifacts are the most stable cross-boundary finding: "
            "0/133 success with 133 public-pass/hidden-fail cases across hard_v2, "
            "hard_v3, and hard_v4."
        ),
        (
            "Bad-dependency success must be interpreted through artifact adherence; "
            "low adherence means the model often succeeds by ignoring harmful advice."
        ),
    ],
    "not_supported": [
        "Do not claim SkillAdmit-selected universally improves downstream success.",
        "Do not claim SkillAdmit-selected is the best downstream context.",
        "Do not claim SkillAdmit-selected saves tokens cross-boundary.",
        "Do not claim precondition-only replaces repository-tree context.",
        "Do not claim raw memory or all-skills results are deployable admission policies.",
        "Do not claim bad dependency advice is safe.",
        (
            "Do not tune hard_v2, hard_v3, or hard_v4 failures while still treating "
            "the affected suite as clean evidence."
        ),
    ],
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> str:
    resolved = resolve(path)
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def package_index(package: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (row["run_name"], row["strategy"]): row
        for row in package["primary_strategy_table"]
    }


def get_row(packages: dict[str, dict[str, Any]], suite: str, run_name: str, strategy: str) -> dict[str, Any]:
    rows = package_index(packages[suite])
    try:
        return rows[(run_name, strategy)]
    except KeyError as exc:
        raise KeyError(f"Missing row: {suite}/{run_name}/{strategy}") from exc


def normalized_primary_table(packages: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for suite, package in packages.items():
        for row in package["primary_strategy_table"]:
            run_name = row["run_name"]
            tasks = int(row["tasks"])
            successes = int(row["successes"])
            rows.append(
                {
                    "suite": suite,
                    "suite_role": SUITE_ROLES[suite],
                    "setting": RUN_LABELS.get(run_name, row["setting"]),
                    "run_name": run_name,
                    "strategy": row["strategy"],
                    "display_strategy": row["display_strategy"],
                    "success": row["success"],
                    "successes": successes,
                    "tasks": tasks,
                    "success_rate": round(successes / tasks, 4) if tasks else 0.0,
                    "negative_transfer": int(row["negative_transfer"]),
                    "public_passed_hidden_failed": int(row["public_passed_hidden_failed"]),
                    "artifact_adherence": row.get("artifact_adherence"),
                    "total_tokens": int(row["total_tokens"]),
                    "included_repo_tree_rows": int(row["included_repo_tree_rows"]),
                    "visible_file_rows": int(row["visible_file_rows"]),
                }
            )
    return sorted(rows, key=lambda row: (row["suite"], RUN_ORDER.get(row["run_name"], 999), row["strategy"]))


def delta(success_row: dict[str, Any], baseline_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "success_delta": int(success_row["successes"]) - int(baseline_row["successes"]),
        "token_delta": int(success_row["total_tokens"]) - int(baseline_row["total_tokens"]),
    }


def selected_comparison_table(packages: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    specs = [
        (
            "hard_v2",
            "tree-aware",
            "llm_downstream_hard_v2_tree_25x2",
            "skilladmit_selected",
            "no_experience",
        ),
        (
            "hard_v2",
            "strict visible",
            "llm_downstream_hard_v2_full_25x6",
            "skilladmit_selected",
            "no_experience",
        ),
        (
            "hard_v3",
            "tree-aware",
            "llm_downstream_hard_v3_tree_core_30x2",
            "skilladmit_selected",
            "no_experience",
        ),
        (
            "hard_v3",
            "strict visible",
            "llm_downstream_hard_v3_strict_30x8",
            "skilladmit_selected",
            "no_experience",
        ),
        (
            "hard_v4",
            "tree-aware",
            "llm_downstream_hard_v4_tree_24x8",
            "skilladmit_selected",
            "no_experience",
        ),
        (
            "hard_v4",
            "strict visible",
            "llm_downstream_hard_v4_strict_24x8",
            "skilladmit_selected",
            "no_experience",
        ),
    ]
    rows = []
    for suite, setting, run_name, selected_strategy, baseline_strategy in specs:
        selected = get_row(packages, suite, run_name, selected_strategy)
        baseline = get_row(packages, suite, run_name, baseline_strategy)
        values = delta(selected, baseline)
        rows.append(
            {
                "suite": suite,
                "setting": setting,
                "run_name": run_name,
                "selected_success": selected["success"],
                "baseline_success": baseline["success"],
                "selected_tokens": selected["total_tokens"],
                "baseline_tokens": baseline["total_tokens"],
                **values,
            }
        )
    return rows


def context_comparison_table(packages: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    specs = [
        (
            "hard_v2",
            "tree-aware precondition context vs selected",
            "llm_downstream_hard_v2_selected_precondition_25",
            "skilladmit_selected_with_precondition_context",
            "llm_downstream_hard_v2_tree_25x2",
            "skilladmit_selected",
        ),
        (
            "hard_v3",
            "tree-aware precondition context vs selected",
            "llm_downstream_hard_v3_tree_core_30x2",
            "skilladmit_selected_with_precondition_context",
            "llm_downstream_hard_v3_tree_core_30x2",
            "skilladmit_selected",
        ),
        (
            "hard_v4",
            "tree-aware precondition context vs selected",
            "llm_downstream_hard_v4_tree_24x8",
            "skilladmit_selected_with_precondition_context",
            "llm_downstream_hard_v4_tree_24x8",
            "skilladmit_selected",
        ),
        (
            "hard_v2",
            "strict precondition-only vs selected",
            "llm_downstream_hard_v2_precondition_only_25",
            "skilladmit_selected_with_precondition_only",
            "llm_downstream_hard_v2_full_25x6",
            "skilladmit_selected",
        ),
        (
            "hard_v3",
            "strict precondition-only vs selected",
            "llm_downstream_hard_v3_strict_30x8",
            "skilladmit_selected_with_precondition_only",
            "llm_downstream_hard_v3_strict_30x8",
            "skilladmit_selected",
        ),
        (
            "hard_v4",
            "strict precondition-only vs selected",
            "llm_downstream_hard_v4_strict_24x8",
            "skilladmit_selected_with_precondition_only",
            "llm_downstream_hard_v4_strict_24x8",
            "skilladmit_selected",
        ),
        (
            "hard_v2",
            "strict precondition-only vs no_experience",
            "llm_downstream_hard_v2_precondition_only_25",
            "skilladmit_selected_with_precondition_only",
            "llm_downstream_hard_v2_full_25x6",
            "no_experience",
        ),
        (
            "hard_v3",
            "strict precondition-only vs no_experience",
            "llm_downstream_hard_v3_strict_30x8",
            "skilladmit_selected_with_precondition_only",
            "llm_downstream_hard_v3_strict_30x8",
            "no_experience",
        ),
        (
            "hard_v4",
            "strict precondition-only vs no_experience",
            "llm_downstream_hard_v4_strict_24x8",
            "skilladmit_selected_with_precondition_only",
            "llm_downstream_hard_v4_strict_24x8",
            "no_experience",
        ),
    ]
    rows = []
    for suite, comparison, left_run, left_strategy, right_run, right_strategy in specs:
        left = get_row(packages, suite, left_run, left_strategy)
        right = get_row(packages, suite, right_run, right_strategy)
        values = delta(left, right)
        rows.append(
            {
                "suite": suite,
                "comparison": comparison,
                "left_run": left_run,
                "left_strategy": left_strategy,
                "left_success": left["success"],
                "right_run": right_run,
                "right_strategy": right_strategy,
                "right_success": right["success"],
                "left_tokens": left["total_tokens"],
                "right_tokens": right["total_tokens"],
                **values,
            }
        )
    return rows


def forced_bad_summary(primary_rows: list[dict[str, Any]]) -> dict[str, Any]:
    forced_rows = [row for row in primary_rows if row["strategy"] == "forced_bad_artifact"]
    by_suite = []
    for suite in ["hard_v2", "hard_v3", "hard_v4"]:
        suite_rows = [row for row in forced_rows if row["suite"] == suite]
        tasks = sum(int(row["tasks"]) for row in suite_rows)
        successes = sum(int(row["successes"]) for row in suite_rows)
        public_hidden = sum(int(row["public_passed_hidden_failed"]) for row in suite_rows)
        negative_transfer = sum(int(row["negative_transfer"]) for row in suite_rows)
        by_suite.append(
            {
                "suite": suite,
                "tasks": tasks,
                "successes": successes,
                "success": f"{successes}/{tasks}",
                "public_passed_hidden_failed": public_hidden,
                "negative_transfer": negative_transfer,
            }
        )
    total_tasks = sum(row["tasks"] for row in by_suite)
    total_successes = sum(row["successes"] for row in by_suite)
    total_public_hidden = sum(row["public_passed_hidden_failed"] for row in by_suite)
    total_negative_transfer = sum(row["negative_transfer"] for row in by_suite)
    return {
        "by_suite": by_suite,
        "total_tasks": total_tasks,
        "total_successes": total_successes,
        "total_success": f"{total_successes}/{total_tasks}",
        "total_public_passed_hidden_failed": total_public_hidden,
        "total_negative_transfer": total_negative_transfer,
        "consistent_negative_transfer": (
            total_tasks == 133
            and total_successes == 0
            and total_public_hidden == 133
            and total_negative_transfer == 133
        ),
    }


def artifact_adherence_summary(primary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for row in primary_rows:
        if row["strategy"] not in {"bad_dependency_rule", "forced_bad_artifact", "distilled_skills_all"}:
            continue
        adherence = row["artifact_adherence"]
        rows.append(
            {
                "suite": row["suite"],
                "setting": row["setting"],
                "strategy": row["strategy"],
                "success": row["success"],
                "artifact_adherence": f"{adherence}/{row['tasks']}" if adherence is not None else "",
                "adherence_rate": round(adherence / row["tasks"], 4) if adherence is not None else None,
                "public_passed_hidden_failed": row["public_passed_hidden_failed"],
            }
        )
    return rows


def derived_claims(
    selected_rows: list[dict[str, Any]],
    context_rows: list[dict[str, Any]],
    forced_summary: dict[str, Any],
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
    strict_precondition_vs_selected = [
        row for row in context_rows if row["comparison"] == "strict precondition-only vs selected"
    ]
    strict_precondition_vs_no = [
        row for row in context_rows if row["comparison"] == "strict precondition-only vs no_experience"
    ]
    tree_precondition_vs_selected = [
        row for row in context_rows if row["comparison"] == "tree-aware precondition context vs selected"
    ]
    return {
        "selected_success_delta_values": selected_success_deltas,
        "selected_token_delta_values": selected_token_deltas,
        "selected_superiority_consistent": all(value > 0 for value in selected_success_deltas.values()),
        "selected_token_savings_consistent": all(value < 0 for value in selected_token_deltas.values()),
        "tree_selected_positive_suites": [
            row["suite"] for row in selected_rows if row["setting"] == "tree-aware" and row["success_delta"] > 0
        ],
        "tree_selected_tied_suites": [
            row["suite"] for row in selected_rows if row["setting"] == "tree-aware" and row["success_delta"] == 0
        ],
        "strict_selected_positive_suites": [
            row["suite"] for row in selected_rows if row["setting"] == "strict visible" and row["success_delta"] > 0
        ],
        "strict_selected_negative_suites": [
            row["suite"] for row in selected_rows if row["setting"] == "strict visible" and row["success_delta"] < 0
        ],
        "tree_precondition_context_success_delta_values": {
            row["suite"]: row["success_delta"] for row in tree_precondition_vs_selected
        },
        "strict_precondition_only_success_delta_vs_selected_values": {
            row["suite"]: row["success_delta"] for row in strict_precondition_vs_selected
        },
        "strict_precondition_only_success_delta_vs_no_experience_values": {
            row["suite"]: row["success_delta"] for row in strict_precondition_vs_no
        },
        "forced_bad_total_success": forced_summary["total_success"],
        "forced_bad_total_tasks": forced_summary["total_tasks"],
        "forced_bad_total_public_passed_hidden_failed": forced_summary["total_public_passed_hidden_failed"],
        "forced_bad_negative_transfer_consistent": forced_summary["consistent_negative_transfer"],
    }


def source_packages(paths: dict[str, Path], packages: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for suite in ["hard_v2", "hard_v3", "hard_v4"]:
        path = paths[suite]
        package = packages[suite]
        rows.append(
            {
                "suite": suite,
                "path": display_path(path),
                "sha256": sha256_file(path),
                "package_generated_at_utc": package["generated_at_utc"],
            }
        )
    return rows


def interpretation_ladder(derived: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "topic": "Main result shape",
            "interpretation": (
                "The evidence is not a monotonic selected-wins story. hard_v2 gives "
                "a positive tree-aware result, hard_v3 narrows that result, and "
                "hard_v4 rejects selected superiority under strict visible files."
            ),
        },
        {
            "topic": "Selected context",
            "interpretation": (
                "Selected context should be presented as conditionally useful when "
                "the execution context exposes enough repository structure, not as "
                "a universal replacement for no_experience."
            ),
        },
        {
            "topic": "Preconditions",
            "interpretation": (
                "Precondition text consistently helps over selected-only in strict "
                "settings, but it does not consistently beat no_experience and it "
                "adds tokens."
            ),
        },
        {
            "topic": "Negative transfer",
            "interpretation": (
                f"Forced bad artifacts are the strongest stable finding: "
                f"{derived['forced_bad_total_success']} success with "
                f"{derived['forced_bad_total_public_passed_hidden_failed']} "
                f"public-pass/hidden-fail cases."
            ),
        },
        {
            "topic": "Paper positioning",
            "interpretation": (
                "The defendable paper claim is not that SkillAdmit always improves "
                "success. The stronger claim is that experience admission needs "
                "downstream validation because useful, neutral, ignored, and harmful "
                "experience behave differently under hidden verifiers."
            ),
        },
    ]


def build_package(
    packages: dict[str, dict[str, Any]],
    paths: dict[str, Path],
) -> dict[str, Any]:
    primary_rows = normalized_primary_table(packages)
    selected_rows = selected_comparison_table(packages)
    context_rows = context_comparison_table(packages)
    forced_summary = forced_bad_summary(primary_rows)
    derived = derived_claims(selected_rows, context_rows, forced_summary)
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_packages": source_packages(paths, packages),
        "suite_roles": SUITE_ROLES,
        "primary_strategy_table": primary_rows,
        "selected_comparison_table": selected_rows,
        "context_comparison_table": context_rows,
        "forced_bad_summary": forced_summary,
        "artifact_adherence_summary": artifact_adherence_summary(primary_rows),
        "derived_claims": derived,
        "interpretation_ladder": interpretation_ladder(derived),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def assert_current_boundary_synthesis(package: dict[str, Any]) -> None:
    if len(package["primary_strategy_table"]) != 43:
        raise AssertionError("primary strategy table row count changed")
    if len(package["selected_comparison_table"]) != 6:
        raise AssertionError("selected comparison table row count changed")
    if len(package["context_comparison_table"]) != 9:
        raise AssertionError("context comparison table row count changed")

    selected = {
        (row["suite"], row["setting"]): row
        for row in package["selected_comparison_table"]
    }
    expected_selected = {
        ("hard_v2", "tree-aware"): ("25/25", "23/25", 2, 6049),
        ("hard_v2", "strict visible"): ("23/25", "24/25", -1, 7336),
        ("hard_v3", "tree-aware"): ("29/30", "29/30", 0, -917),
        ("hard_v3", "strict visible"): ("29/30", "28/30", 1, -2763),
        ("hard_v4", "tree-aware"): ("24/24", "24/24", 0, 1997),
        ("hard_v4", "strict visible"): ("22/24", "24/24", -2, 5395),
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
        (row["suite"], row["comparison"]): row
        for row in package["context_comparison_table"]
    }
    expected_context = {
        ("hard_v2", "tree-aware precondition context vs selected"): (0, 9907),
        ("hard_v3", "tree-aware precondition context vs selected"): (0, 5268),
        ("hard_v4", "tree-aware precondition context vs selected"): (0, 14904),
        ("hard_v2", "strict precondition-only vs selected"): (1, 5708),
        ("hard_v3", "strict precondition-only vs selected"): (1, 11225),
        ("hard_v4", "strict precondition-only vs selected"): (1, 11511),
        ("hard_v2", "strict precondition-only vs no_experience"): (0, 13044),
        ("hard_v3", "strict precondition-only vs no_experience"): (2, 8462),
        ("hard_v4", "strict precondition-only vs no_experience"): (-1, 16906),
    }
    for key, expected in expected_context.items():
        row = context[key]
        actual = (row["success_delta"], row["token_delta"])
        if actual != expected:
            raise AssertionError(f"{key}: expected {expected}, got {actual}")

    forced = package["forced_bad_summary"]
    expected_forced = {
        "total_tasks": 133,
        "total_successes": 0,
        "total_success": "0/133",
        "total_public_passed_hidden_failed": 133,
        "total_negative_transfer": 133,
        "consistent_negative_transfer": True,
    }
    for key, expected in expected_forced.items():
        actual = forced[key]
        if actual != expected:
            raise AssertionError(f"forced {key}: expected {expected}, got {actual}")

    derived = package["derived_claims"]
    expected_derived = {
        "selected_superiority_consistent": False,
        "selected_token_savings_consistent": False,
        "tree_selected_positive_suites": ["hard_v2"],
        "tree_selected_tied_suites": ["hard_v3", "hard_v4"],
        "strict_selected_positive_suites": ["hard_v3"],
        "strict_selected_negative_suites": ["hard_v2", "hard_v4"],
        "forced_bad_total_success": "0/133",
        "forced_bad_total_tasks": 133,
        "forced_bad_total_public_passed_hidden_failed": 133,
        "forced_bad_negative_transfer_consistent": True,
    }
    for key, expected in expected_derived.items():
        actual = derived[key]
        if actual != expected:
            raise AssertionError(f"derived {key}: expected {expected}, got {actual}")

    rendered = render_markdown(package)
    required = [
        "hard_v2 gives a positive tree-aware result",
        "hard_v4 rejects selected superiority",
        "0/133",
        "133 public-pass/hidden-fail",
        "Do not claim SkillAdmit-selected universally improves downstream success.",
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
    primary_rows = [
        [
            row["suite"],
            row["setting"],
            row["display_strategy"],
            row["success"],
            row["negative_transfer"],
            row["public_passed_hidden_failed"],
            (
                f"{row['artifact_adherence']}/{row['tasks']}"
                if row["artifact_adherence"] is not None
                else ""
            ),
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
            row["success"],
            row["negative_transfer"],
            row["public_passed_hidden_failed"],
        ]
        for row in package["forced_bad_summary"]["by_suite"]
    ]
    adherence_rows = [
        [
            row["suite"],
            row["setting"],
            row["strategy"],
            row["success"],
            row["artifact_adherence"],
            row["adherence_rate"],
            row["public_passed_hidden_failed"],
        ]
        for row in package["artifact_adherence_summary"]
    ]
    source_rows = [
        [
            row["suite"],
            f"`{row['path']}`",
            f"`{row['sha256'][:16]}`",
            f"`{row['package_generated_at_utc']}`",
        ]
        for row in package["source_packages"]
    ]
    interpretation = "\n".join(
        f"- **{row['topic']}**: {row['interpretation']}"
        for row in package["interpretation_ladder"]
    )
    supported = "\n".join(f"- {claim}" for claim in package["claim_boundary"]["supported"])
    not_supported = "\n".join(f"- {claim}" for claim in package["claim_boundary"]["not_supported"])
    derived_rows = [
        [key, json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value]
        for key, value in sorted(package["derived_claims"].items())
    ]
    return "\n\n".join(
        [
            "# Downstream Boundary Synthesis",
            f"Generated at UTC: `{package['generated_at_utc']}`",
            (
                "This report combines hard_v2, hard_v3, and hard_v4 paper-facing "
                "evidence packages. It is a boundary-synthesis artifact, not a new "
                "LLM run and not a prompt-tuning step."
            ),
            "## Executive Boundary",
            (
                "hard_v2 gives a positive tree-aware result for SkillAdmit-selected; "
                "hard_v3 narrows that story; hard_v4 rejects selected superiority in "
                "strict visible-file mode and saturates tree-aware mode. The stable "
                "cross-boundary result is negative transfer from forced harmful "
                "artifacts: 0/133 success with 133 public-pass/hidden-fail cases."
            ),
            "## Suite Roles",
            md_table(["suite", "role"], [[suite, role] for suite, role in package["suite_roles"].items()]),
            "## Primary Boundary Table",
            md_table(
                [
                    "suite",
                    "setting",
                    "strategy",
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
                    "comparison",
                    "left_success",
                    "right_success",
                    "success_delta",
                    "token_delta",
                ],
                context_rows,
            ),
            "## Forced Bad Artifact Aggregate",
            md_table(["suite", "success", "negative_transfer", "public_hidden"], forced_rows),
            (
                f"Total: `{package['forced_bad_summary']['total_success']}` success, "
                f"`{package['forced_bad_summary']['total_public_passed_hidden_failed']}` "
                "public-pass/hidden-fail cases."
            ),
            "## Artifact Adherence Caveats",
            md_table(
                ["suite", "setting", "strategy", "success", "adherence", "adherence_rate", "public_hidden"],
                adherence_rows,
            ),
            "## Derived Claim Flags",
            md_table(["flag", "value"], derived_rows),
            "## Interpretation Ladder",
            interpretation,
            "## Supported Claims",
            supported,
            "## Unsupported Claims",
            not_supported,
            "## Source Package Hashes",
            md_table(["suite", "package", "sha256", "generated_at_utc"], source_rows),
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
        "% Auto-generated by scripts/export_downstream_boundary_synthesis.py",
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
    lines.extend(
        [
            "\\hline",
            "\\end{tabular}",
            "",
            "% Boundary synthesis claim flags:",
        ]
    )
    for key, value in sorted(package["derived_claims"].items()):
        lines.append(f"% {tex_escape(key)} = {tex_escape(value)}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(package: dict[str, Any], json_path: Path, md_path: Path, tex_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(package), encoding="utf-8")
    tex_path.write_text(render_latex(package), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hard-v2-package", type=Path, default=DEFAULT_HARD_V2_PACKAGE)
    parser.add_argument("--hard-v3-package", type=Path, default=DEFAULT_HARD_V3_PACKAGE)
    parser.add_argument("--hard-v4-package", type=Path, default=DEFAULT_HARD_V4_PACKAGE)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX)
    parser.add_argument(
        "--assert-current-boundary-synthesis",
        action="store_true",
        help="Assert current hard_v2/hard_v3/hard_v4 boundary values.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = {
        "hard_v2": resolve(args.hard_v2_package),
        "hard_v3": resolve(args.hard_v3_package),
        "hard_v4": resolve(args.hard_v4_package),
    }
    packages = {suite: load_json(path) for suite, path in paths.items()}
    package = build_package(packages, paths)
    if args.assert_current_boundary_synthesis:
        assert_current_boundary_synthesis(package)
    write_outputs(package, resolve(args.json_out), resolve(args.md_out), resolve(args.tex_out))
    print(f"primary_rows: {len(package['primary_strategy_table'])}")
    print(f"selected_comparisons: {len(package['selected_comparison_table'])}")
    print(f"context_comparisons: {len(package['context_comparison_table'])}")
    print(f"forced_bad_total: {package['forced_bad_summary']['total_success']}")
    print(f"wrote_json: {display_path(args.json_out)}")
    print(f"wrote_md: {display_path(args.md_out)}")
    print(f"wrote_tex: {display_path(args.tex_out)}")


if __name__ == "__main__":
    main()
