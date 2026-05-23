#!/usr/bin/env python3
"""Export paper-facing hard_v4 downstream evidence.

What this file does:
  Builds a compact evidence package from the hard_v4 downstream strategy
  matrix: primary tables, derived comparisons, artifact-adherence checks,
  failure taxonomy, provenance hashes, and explicit supported/unsupported
  claims.

Why it is needed:
  hard_v4 is useful precisely because it does not give a simple
  SkillAdmit-selected win. This exporter turns the full matrix into
  paper-facing tables while preventing overclaims about selected superiority,
  selected token savings, repo-tree necessity, or bad-advice safety.

Inputs:
  benchmark/downstream/llm_runs/*/{summary.json,trajectories.jsonl}
  via scripts/summarize_hard_v4_results.py

Outputs:
  benchmark/downstream/reports/hard_v4_evidence_package.json
  benchmark/downstream/reports/hard_v4_paper_tables.md
  benchmark/downstream/reports/hard_v4_paper_tables.tex

Who runs it:
  Researchers or Codex sessions after hard_v4 runs are added, resumed,
  recomputed, or before writing the downstream-validation section of a paper.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from summarize_hard_v4_results import (
    REPORT_DIR,
    ROOT,
    RUN_ROOT,
    assert_current_hard_v4,
    build_matrix,
)


DEFAULT_JSON = REPORT_DIR / "hard_v4_evidence_package.json"
DEFAULT_MD = REPORT_DIR / "hard_v4_paper_tables.md"
DEFAULT_TEX = REPORT_DIR / "hard_v4_paper_tables.tex"

PRIMARY_ROWS = [
    ("tree-aware", "llm_downstream_hard_v4_tree_24x8", "no_experience"),
    ("tree-aware", "llm_downstream_hard_v4_tree_24x8", "skilladmit_selected"),
    (
        "tree-aware",
        "llm_downstream_hard_v4_tree_24x8",
        "skilladmit_selected_with_precondition_context",
    ),
    ("tree-aware", "llm_downstream_hard_v4_tree_24x8", "raw_memory"),
    ("tree-aware", "llm_downstream_hard_v4_tree_24x8", "distilled_skills_all"),
    ("tree-aware", "llm_downstream_hard_v4_tree_24x8", "bad_dependency_rule"),
    ("tree-aware", "llm_downstream_hard_v4_tree_24x8", "promoted_rules"),
    ("tree-aware", "llm_downstream_hard_v4_tree_24x8", "forced_bad_artifact"),
    ("strict visible", "llm_downstream_hard_v4_strict_24x8", "no_experience"),
    ("strict visible", "llm_downstream_hard_v4_strict_24x8", "skilladmit_selected"),
    (
        "strict visible",
        "llm_downstream_hard_v4_strict_24x8",
        "skilladmit_selected_with_precondition_only",
    ),
    ("strict visible", "llm_downstream_hard_v4_strict_24x8", "raw_memory"),
    ("strict visible", "llm_downstream_hard_v4_strict_24x8", "distilled_skills_all"),
    ("strict visible", "llm_downstream_hard_v4_strict_24x8", "bad_dependency_rule"),
    ("strict visible", "llm_downstream_hard_v4_strict_24x8", "promoted_rules"),
    ("strict visible", "llm_downstream_hard_v4_strict_24x8", "forced_bad_artifact"),
]

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

SETTING_DISPLAY = {
    "tree_aware": "tree-aware",
    "strict_visible_file": "strict visible",
}

CLAIM_BOUNDARY = {
    "supported": [
        (
            "Hard v4 is a fresh 24-task downstream validation boundary with "
            "hidden-verifier checks and two completed executor settings."
        ),
        "Tree-aware hard_v4 is saturated: every non-forced strategy reaches 24/24.",
        (
            "Strict visible-file hard_v4 rejects selected superiority: "
            "SkillAdmit-selected reaches 22/24, while no_experience reaches 24/24."
        ),
        (
            "Strict precondition-only improves over ordinary selected by one task "
            "but still trails no_experience and all-skills."
        ),
        (
            "Forced bad artifacts produce systematic negative transfer across hard_v4: "
            "0/48 success with 48 public-pass/hidden-fail cases."
        ),
        (
            "The bad_dependency_rule LLM condition has low artifact adherence "
            "(7/24 tree-aware and 4/24 strict), so its success mostly shows "
            "that the model can ignore harmful advice."
        ),
    ],
    "not_supported": [
        "Hard v4 does not support a SkillAdmit-selected downstream-success claim.",
        "Hard v4 does not support a SkillAdmit-selected token-savings claim.",
        "Hard v4 does not show that precondition-only can replace repo tree.",
        "Hard v4 does not prove raw memory is a safe admission policy.",
        "Hard v4 does not prove bad dependency advice is safe; low artifact adherence is the key caveat.",
        "Hard v4 failures should not be used for prompt tuning unless the suite is reclassified as development data.",
    ],
}


def find_strategy(matrix: dict[str, Any], run_name: str, strategy: str) -> dict[str, Any]:
    for row in matrix["strategy_matrix"]:
        if row["run_name"] == run_name and row["strategy"] == strategy:
            return row
    raise KeyError(f"Missing strategy row: {run_name}/{strategy}")


def ratio(successes: int, tasks: int) -> str:
    return f"{successes}/{tasks}"


def primary_strategy_table(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for setting, run_name, strategy in PRIMARY_ROWS:
        row = find_strategy(matrix, run_name, strategy)
        rows.append(
            {
                "setting": setting,
                "run_name": run_name,
                "strategy": strategy,
                "display_strategy": DISPLAY.get(strategy, strategy),
                "success": ratio(row["successes"], row["tasks"]),
                "successes": row["successes"],
                "tasks": row["tasks"],
                "negative_transfer": row["negative_transfer"],
                "public_passed_hidden_failed": row["public_passed_hidden_failed"],
                "artifact_adherence": row["artifact_adherence"],
                "parse_errors": row["parse_errors"],
                "total_tokens": row["total_tokens"],
                "avg_tokens": round(float(row["avg_tokens"]), 2),
                "included_repo_tree_rows": row["included_repo_tree_rows"],
                "visible_file_rows": row["visible_file_rows"],
            }
        )
    return rows


def artifact_adherence_table(matrix: dict[str, Any]) -> list[dict[str, Any]]:
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
    for row in matrix["strategy_matrix"]:
        if row["strategy"] not in tracked:
            continue
        tasks = row["tasks"]
        adherence = row["artifact_adherence"]
        rows.append(
            {
                "setting": SETTING_DISPLAY.get(row["setting"], row["setting"]),
                "strategy": row["strategy"],
                "display_strategy": DISPLAY.get(row["strategy"], row["strategy"]),
                "artifact_adherence": f"{adherence}/{tasks}",
                "adherence_rate": adherence / tasks if tasks else 0.0,
                "success": row["success"],
                "public_passed_hidden_failed": row["public_passed_hidden_failed"],
            }
        )
    return rows


def failure_taxonomy(matrix: dict[str, Any]) -> dict[str, Any]:
    forced_by_setting: Counter[str] = Counter()
    public_hidden_by_strategy: Counter[str] = Counter()
    non_forced = []
    by_setting_strategy_template: Counter[tuple[str, str, str]] = Counter()

    for row in matrix["failures"]:
        key = (row["setting"], row["strategy"], row["template"])
        by_setting_strategy_template[key] += 1
        if row["public_passed_hidden_failed"]:
            setting = SETTING_DISPLAY.get(row["setting"], row["setting"])
            public_hidden_by_strategy[f"{setting}::{row['strategy']}"] += 1
        if row["strategy"] == "forced_bad_artifact":
            forced_by_setting[SETTING_DISPLAY.get(row["setting"], row["setting"])] += 1
            continue
        non_forced.append(
            {
                "setting": SETTING_DISPLAY.get(row["setting"], row["setting"]),
                "strategy": row["strategy"],
                "display_strategy": DISPLAY.get(row["strategy"], row["strategy"]),
                "task_id": row["task_id"],
                "template": row["template"],
                "public_tests_passed": row["public_tests_passed"],
                "public_passed_hidden_failed": row["public_passed_hidden_failed"],
                "negative_transfer": row["negative_transfer"],
                "used_artifact": row["used_artifact"],
                "diagnosis": row["diagnosis"],
                "notes": row["notes"],
            }
        )

    return {
        "forced_bad_artifact_failures_by_setting": dict(sorted(forced_by_setting.items())),
        "public_passed_hidden_failed_by_setting_strategy": dict(sorted(public_hidden_by_strategy.items())),
        "non_forced_failures": non_forced,
        "by_setting_strategy_template": [
            {
                "setting": SETTING_DISPLAY.get(setting, setting),
                "strategy": strategy,
                "template": template,
                "failures": count,
            }
            for (setting, strategy, template), count in sorted(by_setting_strategy_template.items())
        ],
    }


def source_hashes(matrix: dict[str, Any]) -> list[dict[str, str]]:
    hashes = []
    for run in matrix["run_summaries"]:
        summary = run["source_files"]["summary"]
        trajectories = run["source_files"]["trajectories"]
        hashes.append(
            {
                "run_name": run["run_name"],
                "summary_sha256": summary["sha256"],
                "trajectories_sha256": trajectories["sha256"],
            }
        )
    return hashes


def selected_comparisons(package: dict[str, Any]) -> dict[str, Any]:
    rows = {
        (row["run_name"], row["strategy"]): row
        for row in package["primary_strategy_table"]
    }
    tree_no = rows[("llm_downstream_hard_v4_tree_24x8", "no_experience")]
    tree_selected = rows[("llm_downstream_hard_v4_tree_24x8", "skilladmit_selected")]
    tree_pre = rows[
        (
            "llm_downstream_hard_v4_tree_24x8",
            "skilladmit_selected_with_precondition_context",
        )
    ]
    tree_all = rows[("llm_downstream_hard_v4_tree_24x8", "distilled_skills_all")]
    strict_no = rows[("llm_downstream_hard_v4_strict_24x8", "no_experience")]
    strict_selected = rows[("llm_downstream_hard_v4_strict_24x8", "skilladmit_selected")]
    strict_pre = rows[
        (
            "llm_downstream_hard_v4_strict_24x8",
            "skilladmit_selected_with_precondition_only",
        )
    ]
    strict_raw = rows[("llm_downstream_hard_v4_strict_24x8", "raw_memory")]
    strict_promoted = rows[("llm_downstream_hard_v4_strict_24x8", "promoted_rules")]
    strict_all = rows[("llm_downstream_hard_v4_strict_24x8", "distilled_skills_all")]
    forced_rows = [
        rows[("llm_downstream_hard_v4_tree_24x8", "forced_bad_artifact")],
        rows[("llm_downstream_hard_v4_strict_24x8", "forced_bad_artifact")],
    ]

    return {
        "tree_selected_success_delta_vs_no_experience": tree_selected["successes"] - tree_no["successes"],
        "tree_selected_token_delta_vs_no_experience": tree_selected["total_tokens"] - tree_no["total_tokens"],
        "tree_precondition_context_success_delta_vs_selected": tree_pre["successes"] - tree_selected["successes"],
        "tree_precondition_context_token_delta_vs_selected": tree_pre["total_tokens"] - tree_selected["total_tokens"],
        "tree_all_skills_success_delta_vs_no_experience": tree_all["successes"] - tree_no["successes"],
        "tree_all_skills_token_delta_vs_no_experience": tree_all["total_tokens"] - tree_no["total_tokens"],
        "strict_selected_success_delta_vs_no_experience": strict_selected["successes"] - strict_no["successes"],
        "strict_selected_token_delta_vs_no_experience": strict_selected["total_tokens"] - strict_no["total_tokens"],
        "strict_precondition_only_success_delta_vs_selected": strict_pre["successes"] - strict_selected["successes"],
        "strict_precondition_only_token_delta_vs_selected": strict_pre["total_tokens"] - strict_selected["total_tokens"],
        "strict_raw_memory_success_delta_vs_no_experience": strict_raw["successes"] - strict_no["successes"],
        "strict_raw_memory_token_delta_vs_no_experience": strict_raw["total_tokens"] - strict_no["total_tokens"],
        "strict_promoted_rules_success_delta_vs_no_experience": strict_promoted["successes"] - strict_no["successes"],
        "strict_all_skills_success_delta_vs_no_experience": strict_all["successes"] - strict_no["successes"],
        "forced_bad_total_successes": sum(row["successes"] for row in forced_rows),
        "forced_bad_total_tasks": sum(row["tasks"] for row in forced_rows),
        "forced_bad_total_public_passed_hidden_failed": sum(
            row["public_passed_hidden_failed"] for row in forced_rows
        ),
        "selected_superiority_supported": False,
        "selected_token_savings_supported": False,
    }


def build_evidence_package(matrix: dict[str, Any]) -> dict[str, Any]:
    package = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_matrix_generated_at_utc": matrix["generated_at_utc"],
        "primary_strategy_table": primary_strategy_table(matrix),
        "artifact_adherence_table": artifact_adherence_table(matrix),
        "failure_taxonomy": failure_taxonomy(matrix),
        "claim_boundary": CLAIM_BOUNDARY,
        "source_hashes": source_hashes(matrix),
    }
    package["derived_comparisons"] = selected_comparisons(package)
    return package


def assert_evidence_package(package: dict[str, Any]) -> None:
    if len(package["primary_strategy_table"]) != len(PRIMARY_ROWS):
        raise AssertionError("primary strategy table row count changed")

    primary = {
        (row["run_name"], row["strategy"]): row
        for row in package["primary_strategy_table"]
    }
    expected = {
        ("llm_downstream_hard_v4_tree_24x8", "no_experience"): "24/24",
        ("llm_downstream_hard_v4_tree_24x8", "skilladmit_selected"): "24/24",
        (
            "llm_downstream_hard_v4_tree_24x8",
            "skilladmit_selected_with_precondition_context",
        ): "24/24",
        ("llm_downstream_hard_v4_tree_24x8", "raw_memory"): "24/24",
        ("llm_downstream_hard_v4_tree_24x8", "distilled_skills_all"): "24/24",
        ("llm_downstream_hard_v4_tree_24x8", "bad_dependency_rule"): "24/24",
        ("llm_downstream_hard_v4_tree_24x8", "promoted_rules"): "24/24",
        ("llm_downstream_hard_v4_tree_24x8", "forced_bad_artifact"): "0/24",
        ("llm_downstream_hard_v4_strict_24x8", "no_experience"): "24/24",
        ("llm_downstream_hard_v4_strict_24x8", "skilladmit_selected"): "22/24",
        (
            "llm_downstream_hard_v4_strict_24x8",
            "skilladmit_selected_with_precondition_only",
        ): "23/24",
        ("llm_downstream_hard_v4_strict_24x8", "raw_memory"): "23/24",
        ("llm_downstream_hard_v4_strict_24x8", "distilled_skills_all"): "24/24",
        ("llm_downstream_hard_v4_strict_24x8", "bad_dependency_rule"): "24/24",
        ("llm_downstream_hard_v4_strict_24x8", "promoted_rules"): "23/24",
        ("llm_downstream_hard_v4_strict_24x8", "forced_bad_artifact"): "0/24",
    }
    for key, success in expected.items():
        actual = primary[key]["success"]
        if actual != success:
            raise AssertionError(f"{key}: expected {success}, got {actual}")

    for key in [
        ("llm_downstream_hard_v4_tree_24x8", "forced_bad_artifact"),
        ("llm_downstream_hard_v4_strict_24x8", "forced_bad_artifact"),
    ]:
        row = primary[key]
        if row["public_passed_hidden_failed"] != 24 or row["negative_transfer"] != 24:
            raise AssertionError(f"{key}: forced bad artifact control changed")

    if primary[("llm_downstream_hard_v4_tree_24x8", "bad_dependency_rule")]["artifact_adherence"] != 7:
        raise AssertionError("tree-aware bad_dependency_rule adherence changed")
    if primary[("llm_downstream_hard_v4_strict_24x8", "bad_dependency_rule")]["artifact_adherence"] != 4:
        raise AssertionError("strict bad_dependency_rule adherence changed")

    comparisons = package["derived_comparisons"]
    required = {
        "tree_selected_success_delta_vs_no_experience": 0,
        "tree_selected_token_delta_vs_no_experience": 1997,
        "tree_precondition_context_success_delta_vs_selected": 0,
        "tree_precondition_context_token_delta_vs_selected": 14904,
        "strict_selected_success_delta_vs_no_experience": -2,
        "strict_selected_token_delta_vs_no_experience": 5395,
        "strict_precondition_only_success_delta_vs_selected": 1,
        "strict_precondition_only_token_delta_vs_selected": 11511,
        "strict_raw_memory_success_delta_vs_no_experience": -1,
        "strict_promoted_rules_success_delta_vs_no_experience": -1,
        "strict_all_skills_success_delta_vs_no_experience": 0,
        "forced_bad_total_successes": 0,
        "forced_bad_total_tasks": 48,
        "forced_bad_total_public_passed_hidden_failed": 48,
        "selected_superiority_supported": False,
        "selected_token_savings_supported": False,
    }
    for key, expected_value in required.items():
        actual = comparisons[key]
        if actual != expected_value:
            raise AssertionError(f"{key}: expected {expected_value}, got {actual}")


def md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def render_markdown(package: dict[str, Any]) -> str:
    lines = [
        "# Hard v4 Paper Tables",
        "",
        f"Generated at UTC: `{package['generated_at_utc']}`",
        "",
        "Hard v4 is boundary evidence. It should not be collapsed into a selected-wins table.",
        "",
        "## Primary Strategy Table",
        "",
    ]
    primary_rows = []
    for row in package["primary_strategy_table"]:
        primary_rows.append(
            [
                row["setting"],
                row["display_strategy"],
                row["success"],
                str(row["negative_transfer"]),
                str(row["public_passed_hidden_failed"]),
                f"{row['artifact_adherence']}/{row['tasks']}",
                str(row["total_tokens"]),
                str(row["included_repo_tree_rows"]),
            ]
        )
    lines.extend(
        md_table(
            ["setting", "strategy", "success", "neg", "public_hidden", "adherence", "tokens", "tree_rows"],
            primary_rows,
        )
    )

    lines.extend(["", "## Selected Comparisons", ""])
    comparison_rows = [[key, str(value)] for key, value in sorted(package["derived_comparisons"].items())]
    lines.extend(md_table(["comparison", "value"], comparison_rows))

    lines.extend(["", "## Artifact Adherence", ""])
    adherence_rows = []
    for row in package["artifact_adherence_table"]:
        adherence_rows.append(
            [
                row["setting"],
                row["display_strategy"],
                row["success"],
                row["artifact_adherence"],
                f"{row['adherence_rate']:.3f}",
                str(row["public_passed_hidden_failed"]),
            ]
        )
    lines.extend(
        md_table(
            ["setting", "strategy", "success", "adherence", "adherence_rate", "public_hidden"],
            adherence_rows,
        )
    )

    lines.extend(["", "## Non-Forced Failures", ""])
    non_forced_rows = []
    for row in package["failure_taxonomy"]["non_forced_failures"]:
        diagnosis = row["diagnosis"].replace("\n", " ")
        if len(diagnosis) > 120:
            diagnosis = diagnosis[:117] + "..."
        non_forced_rows.append(
            [
                row["setting"],
                row["display_strategy"],
                row["task_id"],
                row["template"],
                str(int(bool(row["public_passed_hidden_failed"]))),
                str(int(bool(row["negative_transfer"]))),
                diagnosis,
            ]
        )
    lines.extend(
        md_table(
            ["setting", "strategy", "task", "template", "public_hidden", "neg", "diagnosis"],
            non_forced_rows,
        )
    )

    lines.extend(["", "## Claim Boundary", "", "Supported:"])
    for claim in package["claim_boundary"]["supported"]:
        lines.append(f"- {claim}")
    lines.extend(["", "Not supported:"])
    for claim in package["claim_boundary"]["not_supported"]:
        lines.append(f"- {claim}")

    lines.extend(["", "## Source Hashes", ""])
    hash_rows = [
        [f"`{row['run_name']}`", f"`{row['summary_sha256'][:16]}`", f"`{row['trajectories_sha256'][:16]}`"]
        for row in package["source_hashes"]
    ]
    lines.extend(md_table(["run", "summary_sha256", "trajectories_sha256"], hash_rows))
    lines.append("")
    return "\n".join(lines)


def latex_escape(value: Any) -> str:
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
        "% Auto-generated by scripts/export_hard_v4_evidence_package.py",
        "\\begin{tabular}{llrrrrr}",
        "\\hline",
        "Setting & Strategy & Success & Neg. & Pub./hid. & Adh. & Tokens \\\\",
        "\\hline",
    ]
    for row in package["primary_strategy_table"]:
        lines.append(
            " & ".join(
                [
                    latex_escape(row["setting"]),
                    latex_escape(row["display_strategy"]),
                    latex_escape(row["success"]),
                    str(row["negative_transfer"]),
                    str(row["public_passed_hidden_failed"]),
                    latex_escape(f"{row['artifact_adherence']}/{row['tasks']}"),
                    str(row["total_tokens"]),
                ]
            )
            + r" \\"
        )
    lines.extend(
        [
            "\\hline",
            "\\end{tabular}",
            "",
            "% Selected hard_v4 derived comparisons:",
        ]
    )
    for key, value in sorted(package["derived_comparisons"].items()):
        lines.append(f"% {latex_escape(key)} = {latex_escape(value)}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--out-tex", type=Path, default=DEFAULT_TEX)
    parser.add_argument(
        "--assert-current-hard-v4",
        action="store_true",
        help="Assert current hard_v4 evidence values and paper-claim invariants.",
    )
    args = parser.parse_args()

    run_root = args.run_root if args.run_root.is_absolute() else ROOT / args.run_root
    matrix = build_matrix(run_root)
    if args.assert_current_hard_v4:
        assert_current_hard_v4(matrix)

    package = build_evidence_package(matrix)
    if args.assert_current_hard_v4:
        assert_evidence_package(package)

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.out_md.write_text(render_markdown(package), encoding="utf-8")
    args.out_tex.write_text(render_latex(package), encoding="utf-8")

    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")
    print(f"Wrote {args.out_tex}")
    print(f"primary_rows: {len(package['primary_strategy_table'])}")
    print(f"artifact_adherence_rows: {len(package['artifact_adherence_table'])}")
    print(f"non_forced_failures: {len(package['failure_taxonomy']['non_forced_failures'])}")


if __name__ == "__main__":
    main()
