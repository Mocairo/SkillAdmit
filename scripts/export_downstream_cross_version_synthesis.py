#!/usr/bin/env python3
"""Export cross-version downstream synthesis for hard_v2 and hard_v3.

What this file does:
  Reads the frozen paper-facing hard_v2 and hard_v3 evidence packages and
  builds a compact cross-version synthesis: a combined strategy table, derived
  comparisons, source package hashes, and explicit paper claim boundaries.

Why it is needed:
  hard_v2 and hard_v3 tell different but compatible stories. hard_v2 is the
  positive tree-aware selected result; hard_v3 is the fresh boundary result
  showing that selected is not a universal best context. This script prevents
  hand-written summaries from flattening those differences.

Inputs:
  benchmark/downstream/reports/hard_v2_evidence_package.json
  benchmark/downstream/reports/hard_v3_evidence_package.json

Outputs:
  benchmark/downstream/reports/downstream_cross_version_synthesis.json
  benchmark/downstream/reports/downstream_cross_version_synthesis.md
  benchmark/downstream/reports/downstream_cross_version_synthesis.tex

Who runs it:
  Researchers or Codex sessions after hard_v2/hard_v3 evidence packages are
  regenerated, or before drafting the downstream-validation section of a paper.
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
DEFAULT_JSON = REPORT_DIR / "downstream_cross_version_synthesis.json"
DEFAULT_MD = REPORT_DIR / "downstream_cross_version_synthesis.md"
DEFAULT_TEX = REPORT_DIR / "downstream_cross_version_synthesis.tex"


PRIMARY_ROWS = [
    ("hard_v2", "strict visible", "llm_downstream_hard_v2_full_25x6", "no_experience"),
    ("hard_v2", "strict visible", "llm_downstream_hard_v2_full_25x6", "skilladmit_selected"),
    ("hard_v2", "strict visible", "llm_downstream_hard_v2_full_25x6", "raw_memory"),
    ("hard_v2", "strict visible", "llm_downstream_hard_v2_full_25x6", "promoted_rules"),
    ("hard_v2", "strict visible", "llm_downstream_hard_v2_full_25x6", "bad_dependency_rule"),
    ("hard_v2", "strict visible", "llm_downstream_hard_v2_full_25x6", "distilled_skills_all"),
    ("hard_v2", "tree-aware", "llm_downstream_hard_v2_tree_25x2", "no_experience"),
    ("hard_v2", "tree-aware", "llm_downstream_hard_v2_tree_25x2", "skilladmit_selected"),
    (
        "hard_v2",
        "tree-aware + preconditions",
        "llm_downstream_hard_v2_selected_precondition_25",
        "skilladmit_selected_with_precondition_context",
    ),
    (
        "hard_v2",
        "strict + preconditions only",
        "llm_downstream_hard_v2_precondition_only_25",
        "skilladmit_selected_with_precondition_only",
    ),
    ("hard_v2", "forced harmful artifact", "llm_downstream_hard_v2_forced_bad_25", "forced_bad_artifact"),
    ("hard_v3", "tree-aware", "llm_downstream_hard_v3_tree_core_30x2", "no_experience"),
    ("hard_v3", "tree-aware", "llm_downstream_hard_v3_tree_core_30x2", "skilladmit_selected"),
    (
        "hard_v3",
        "tree-aware",
        "llm_downstream_hard_v3_tree_core_30x2",
        "skilladmit_selected_with_precondition_context",
    ),
    ("hard_v3", "tree-aware", "llm_downstream_hard_v3_tree_core_30x2", "raw_memory"),
    ("hard_v3", "tree-aware", "llm_downstream_hard_v3_tree_core_30x2", "distilled_skills_all"),
    ("hard_v3", "tree-aware", "llm_downstream_hard_v3_tree_core_30x2", "bad_dependency_rule"),
    ("hard_v3", "tree-aware", "llm_downstream_hard_v3_tree_core_30x2", "promoted_rules"),
    ("hard_v3", "tree-aware", "llm_downstream_hard_v3_tree_core_30x2", "forced_bad_artifact"),
    ("hard_v3", "strict visible", "llm_downstream_hard_v3_strict_30x8", "no_experience"),
    ("hard_v3", "strict visible", "llm_downstream_hard_v3_strict_30x8", "skilladmit_selected"),
    (
        "hard_v3",
        "strict visible",
        "llm_downstream_hard_v3_strict_30x8",
        "skilladmit_selected_with_precondition_only",
    ),
    ("hard_v3", "strict visible", "llm_downstream_hard_v3_strict_30x8", "raw_memory"),
    ("hard_v3", "strict visible", "llm_downstream_hard_v3_strict_30x8", "distilled_skills_all"),
    ("hard_v3", "strict visible", "llm_downstream_hard_v3_strict_30x8", "bad_dependency_rule"),
    ("hard_v3", "strict visible", "llm_downstream_hard_v3_strict_30x8", "promoted_rules"),
    ("hard_v3", "strict visible", "llm_downstream_hard_v3_strict_30x8", "forced_bad_artifact"),
]


CLAIM_LADDER = {
    "supported": [
        (
            "Downstream hidden-verifier evidence is stronger than admission-label "
            "accuracy alone for this project stage."
        ),
        (
            "Forced harmful artifacts produce systematic negative transfer across "
            "hard_v2 and hard_v3: 0/85 success with 85 public-pass/hidden-fail cases."
        ),
        (
            "hard_v2 supports a positive tree-aware SkillAdmit-selected result: "
            "25/25 versus 23/25 for no_experience, with 25/25 replicated."
        ),
        (
            "hard_v3 is boundary evidence: tree-aware selected ties no_experience "
            "at 29/30, and strict selected is only 29/30 while other conditions reach 30/30."
        ),
        (
            "Repo tree and precondition context are important variables, but their "
            "effects are suite-dependent rather than universal."
        ),
        (
            "Raw memory must remain a serious comparison condition because it is "
            "weak on hard_v2 strict visible-file but reaches 30/30 in both hard_v3 settings."
        ),
        (
            "Bad dependency advice is only interpretable through the forced control: "
            "ordinary bad_dependency_rule rows have low artifact adherence on hard_v3."
        ),
    ],
    "not_supported": [
        "Do not claim SkillAdmit-selected universally dominates no_experience.",
        "Do not claim SkillAdmit-selected is the universal best downstream context.",
        "Do not claim SkillAdmit-selected has established cross-version token savings.",
        "Do not claim precondition-only replaces repository context in general.",
        "Do not claim raw memory is a safe admission policy from hard_v3 success alone.",
        "Do not claim bad dependency advice is safe when the model often ignored it.",
        "Do not tune hard_v2 or hard_v3 failures while still treating those suites as clean evidence.",
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


def find_row(package: dict[str, Any], run_name: str, strategy: str) -> dict[str, Any]:
    for row in package["primary_strategy_table"]:
        if row["run_name"] == run_name and row["strategy"] == strategy:
            return row
    raise KeyError(f"Missing evidence row: {run_name}/{strategy}")


def row_index(package: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (row["run_name"], row["strategy"]): row
        for row in package["primary_strategy_table"]
    }


def build_primary_table(hard_v2: dict[str, Any], hard_v3: dict[str, Any]) -> list[dict[str, Any]]:
    packages = {"hard_v2": hard_v2, "hard_v3": hard_v3}
    rows = []
    for suite, setting, run_name, strategy in PRIMARY_ROWS:
        source = find_row(packages[suite], run_name, strategy)
        tasks = int(source["tasks"])
        successes = int(source["successes"])
        rows.append(
            {
                "suite": suite,
                "setting": setting,
                "run_name": run_name,
                "strategy": strategy,
                "display_strategy": source["display_strategy"],
                "success": source["success"],
                "successes": successes,
                "tasks": tasks,
                "success_rate": round(successes / tasks, 4) if tasks else 0.0,
                "negative_transfer": int(source["negative_transfer"]),
                "public_passed_hidden_failed": int(source["public_passed_hidden_failed"]),
                "artifact_adherence": source.get("artifact_adherence"),
                "total_tokens": int(source["total_tokens"]),
                "included_repo_tree_rows": int(source["included_repo_tree_rows"]),
                "visible_file_rows": int(source["visible_file_rows"]),
            }
        )
    return rows


def forced_bad_rows(primary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in primary_rows if row["strategy"] == "forced_bad_artifact"]


def derived_synthesis(
    hard_v2: dict[str, Any],
    hard_v3: dict[str, Any],
    primary_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    v2 = row_index(hard_v2)
    v3 = row_index(hard_v3)
    v2_tree_no = v2[("llm_downstream_hard_v2_tree_25x2", "no_experience")]
    v2_tree_selected = v2[("llm_downstream_hard_v2_tree_25x2", "skilladmit_selected")]
    v2_strict_no = v2[("llm_downstream_hard_v2_full_25x6", "no_experience")]
    v2_strict_selected = v2[("llm_downstream_hard_v2_full_25x6", "skilladmit_selected")]
    v2_strict_raw = v2[("llm_downstream_hard_v2_full_25x6", "raw_memory")]
    v2_strict_all = v2[("llm_downstream_hard_v2_full_25x6", "distilled_skills_all")]
    v2_pre_only = v2[
        (
            "llm_downstream_hard_v2_precondition_only_25",
            "skilladmit_selected_with_precondition_only",
        )
    ]
    v2_pre_context = v2[
        (
            "llm_downstream_hard_v2_selected_precondition_25",
            "skilladmit_selected_with_precondition_context",
        )
    ]
    v3_tree_no = v3[("llm_downstream_hard_v3_tree_core_30x2", "no_experience")]
    v3_tree_selected = v3[("llm_downstream_hard_v3_tree_core_30x2", "skilladmit_selected")]
    v3_tree_pre = v3[
        (
            "llm_downstream_hard_v3_tree_core_30x2",
            "skilladmit_selected_with_precondition_context",
        )
    ]
    v3_tree_raw = v3[("llm_downstream_hard_v3_tree_core_30x2", "raw_memory")]
    v3_tree_all = v3[("llm_downstream_hard_v3_tree_core_30x2", "distilled_skills_all")]
    v3_strict_no = v3[("llm_downstream_hard_v3_strict_30x8", "no_experience")]
    v3_strict_selected = v3[("llm_downstream_hard_v3_strict_30x8", "skilladmit_selected")]
    v3_strict_pre = v3[
        (
            "llm_downstream_hard_v3_strict_30x8",
            "skilladmit_selected_with_precondition_only",
        )
    ]
    v3_strict_raw = v3[("llm_downstream_hard_v3_strict_30x8", "raw_memory")]
    v3_strict_all = v3[("llm_downstream_hard_v3_strict_30x8", "distilled_skills_all")]
    forced_rows = forced_bad_rows(primary_rows)
    forced_tasks = sum(row["tasks"] for row in forced_rows)
    forced_successes = sum(row["successes"] for row in forced_rows)
    forced_public_hidden = sum(row["public_passed_hidden_failed"] for row in forced_rows)
    forced_negative_transfer = sum(row["negative_transfer"] for row in forced_rows)
    selected_success_deltas = {
        "hard_v2_tree_selected_success_delta_vs_no_experience": (
            v2_tree_selected["successes"] - v2_tree_no["successes"]
        ),
        "hard_v2_strict_selected_success_delta_vs_no_experience": (
            v2_strict_selected["successes"] - v2_strict_no["successes"]
        ),
        "hard_v3_tree_selected_success_delta_vs_no_experience": (
            v3_tree_selected["successes"] - v3_tree_no["successes"]
        ),
        "hard_v3_strict_selected_success_delta_vs_no_experience": (
            v3_strict_selected["successes"] - v3_strict_no["successes"]
        ),
    }
    selected_token_deltas = {
        "hard_v2_tree_selected_token_delta_vs_no_experience": (
            v2_tree_selected["total_tokens"] - v2_tree_no["total_tokens"]
        ),
        "hard_v2_strict_selected_token_delta_vs_no_experience": (
            v2_strict_selected["total_tokens"] - v2_strict_no["total_tokens"]
        ),
        "hard_v3_tree_selected_token_delta_vs_no_experience": (
            v3_tree_selected["total_tokens"] - v3_tree_no["total_tokens"]
        ),
        "hard_v3_strict_selected_token_delta_vs_no_experience": (
            v3_strict_selected["total_tokens"] - v3_strict_no["total_tokens"]
        ),
    }
    return {
        **selected_success_deltas,
        **selected_token_deltas,
        "hard_v2_tree_precondition_context_success_delta_vs_tree_selected": (
            v2_pre_context["successes"] - v2_tree_selected["successes"]
        ),
        "hard_v2_tree_precondition_context_token_delta_vs_tree_selected": (
            v2_pre_context["total_tokens"] - v2_tree_selected["total_tokens"]
        ),
        "hard_v2_strict_precondition_only_success_delta_vs_selected": (
            v2_pre_only["successes"] - v2_strict_selected["successes"]
        ),
        "hard_v3_tree_precondition_context_success_delta_vs_selected": (
            v3_tree_pre["successes"] - v3_tree_selected["successes"]
        ),
        "hard_v3_tree_precondition_context_token_delta_vs_selected": (
            v3_tree_pre["total_tokens"] - v3_tree_selected["total_tokens"]
        ),
        "hard_v3_strict_precondition_only_success_delta_vs_selected": (
            v3_strict_pre["successes"] - v3_strict_selected["successes"]
        ),
        "hard_v3_strict_precondition_only_token_delta_vs_selected": (
            v3_strict_pre["total_tokens"] - v3_strict_selected["total_tokens"]
        ),
        "hard_v2_strict_raw_success_delta_vs_no_experience": (
            v2_strict_raw["successes"] - v2_strict_no["successes"]
        ),
        "hard_v3_tree_raw_success_delta_vs_no_experience": (
            v3_tree_raw["successes"] - v3_tree_no["successes"]
        ),
        "hard_v3_strict_raw_success_delta_vs_no_experience": (
            v3_strict_raw["successes"] - v3_strict_no["successes"]
        ),
        "hard_v2_strict_all_skills_success_delta_vs_selected": (
            v2_strict_all["successes"] - v2_strict_selected["successes"]
        ),
        "hard_v3_tree_all_skills_success_delta_vs_selected": (
            v3_tree_all["successes"] - v3_tree_selected["successes"]
        ),
        "hard_v3_strict_all_skills_success_delta_vs_selected": (
            v3_strict_all["successes"] - v3_strict_selected["successes"]
        ),
        "forced_bad_total_tasks": forced_tasks,
        "forced_bad_total_successes": forced_successes,
        "forced_bad_total_public_passed_hidden_failed": forced_public_hidden,
        "forced_bad_total_negative_transfer": forced_negative_transfer,
        "selected_success_delta_values": selected_success_deltas,
        "selected_token_delta_values": selected_token_deltas,
        "selected_superiority_consistent": all(value > 0 for value in selected_success_deltas.values()),
        "selected_token_savings_supported": all(value < 0 for value in selected_token_deltas.values()),
        "repo_tree_necessity_universal": False,
        "forced_bad_negative_transfer_consistent": (
            forced_tasks == 85
            and forced_successes == 0
            and forced_public_hidden == 85
            and forced_negative_transfer == 85
        ),
    }


def build_interpretation(derived: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "topic": "Admission accuracy versus downstream utility",
            "interpretation": (
                "v7 admission accuracy is useful regression evidence, but the "
                "paper-facing scientific signal now comes from hidden-verifier "
                "downstream behavior and negative-transfer controls."
            ),
        },
        {
            "topic": "SkillAdmit-selected",
            "interpretation": (
                "hard_v2 supports tree-aware selected utility, but hard_v3 rejects "
                "a universal selected-superiority claim. The correct claim is "
                "conditional and suite-specific."
            ),
        },
        {
            "topic": "Repository tree and preconditions",
            "interpretation": (
                "hard_v2 shows that repo tree can be more reliable than precondition "
                "text alone; hard_v3 shows that precondition-only can sometimes be "
                "enough. Treat both as task-context variables."
            ),
        },
        {
            "topic": "Token cost",
            "interpretation": (
                "The cross-version evidence does not support a selected token-savings "
                "claim. Success and safety are the central claims, not economy."
            ),
        },
        {
            "topic": "Negative transfer",
            "interpretation": (
                f"Forced bad artifacts are the strongest stable signal: "
                f"{derived['forced_bad_total_successes']}/"
                f"{derived['forced_bad_total_tasks']} success with "
                f"{derived['forced_bad_total_public_passed_hidden_failed']} "
                f"public-pass/hidden-fail cases."
            ),
        },
    ]


def build_package(
    hard_v2: dict[str, Any],
    hard_v3: dict[str, Any],
    hard_v2_path: Path,
    hard_v3_path: Path,
) -> dict[str, Any]:
    primary_rows = build_primary_table(hard_v2, hard_v3)
    derived = derived_synthesis(hard_v2, hard_v3, primary_rows)
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_packages": [
            {
                "suite": "hard_v2",
                "path": str(hard_v2_path.relative_to(ROOT)),
                "sha256": sha256_file(hard_v2_path),
                "package_generated_at_utc": hard_v2["generated_at_utc"],
            },
            {
                "suite": "hard_v3",
                "path": str(hard_v3_path.relative_to(ROOT)),
                "sha256": sha256_file(hard_v3_path),
                "package_generated_at_utc": hard_v3["generated_at_utc"],
            },
        ],
        "primary_strategy_table": primary_rows,
        "derived_synthesis": derived,
        "interpretation_ladder": build_interpretation(derived),
        "claim_ladder": CLAIM_LADDER,
    }


def assert_synthesis(package: dict[str, Any]) -> None:
    rows = {
        (row["suite"], row["run_name"], row["strategy"]): row
        for row in package["primary_strategy_table"]
    }
    expected_successes = {
        ("hard_v2", "llm_downstream_hard_v2_tree_25x2", "no_experience"): "23/25",
        ("hard_v2", "llm_downstream_hard_v2_tree_25x2", "skilladmit_selected"): "25/25",
        ("hard_v2", "llm_downstream_hard_v2_forced_bad_25", "forced_bad_artifact"): "0/25",
        ("hard_v3", "llm_downstream_hard_v3_tree_core_30x2", "no_experience"): "29/30",
        ("hard_v3", "llm_downstream_hard_v3_tree_core_30x2", "skilladmit_selected"): "29/30",
        (
            "hard_v3",
            "llm_downstream_hard_v3_strict_30x8",
            "skilladmit_selected_with_precondition_only",
        ): "30/30",
        ("hard_v3", "llm_downstream_hard_v3_strict_30x8", "forced_bad_artifact"): "0/30",
    }
    for key, expected in expected_successes.items():
        actual = rows[key]["success"]
        if actual != expected:
            raise AssertionError(f"{key}: expected {expected}, got {actual}")

    derived = package["derived_synthesis"]
    required_values = {
        "hard_v2_tree_selected_success_delta_vs_no_experience": 2,
        "hard_v3_tree_selected_success_delta_vs_no_experience": 0,
        "hard_v3_strict_precondition_only_success_delta_vs_selected": 1,
        "forced_bad_total_tasks": 85,
        "forced_bad_total_successes": 0,
        "forced_bad_total_public_passed_hidden_failed": 85,
        "forced_bad_total_negative_transfer": 85,
        "selected_superiority_consistent": False,
        "selected_token_savings_supported": False,
        "repo_tree_necessity_universal": False,
        "forced_bad_negative_transfer_consistent": True,
    }
    for key, expected in required_values.items():
        actual = derived[key]
        if actual != expected:
            raise AssertionError(f"{key}: expected {expected}, got {actual}")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def render_markdown(package: dict[str, Any]) -> str:
    derived = package["derived_synthesis"]
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
    comparison_rows = [
        [key, value]
        for key, value in sorted(derived.items())
        if not isinstance(value, dict)
    ]
    source_rows = [
        [
            source["suite"],
            f"`{source['path']}`",
            f"`{source['sha256'][:16]}`",
            f"`{source['package_generated_at_utc']}`",
        ]
        for source in package["source_packages"]
    ]
    supported = "\n".join(f"- {claim}" for claim in package["claim_ladder"]["supported"])
    not_supported = "\n".join(f"- {claim}" for claim in package["claim_ladder"]["not_supported"])
    interpretation = "\n".join(
        f"- **{row['topic']}**: {row['interpretation']}"
        for row in package["interpretation_ladder"]
    )
    return "\n\n".join(
        [
            "# Downstream Cross-Version Synthesis",
            f"Generated at UTC: `{package['generated_at_utc']}`",
            (
                "This report combines frozen hard_v2 and hard_v3 paper-facing "
                "evidence packages. It is an analysis artifact, not a new tuning run."
            ),
            "## Executive Claim Boundary",
            (
                "hard_v2 is positive evidence for tree-aware SkillAdmit-selected "
                "downstream utility. hard_v3 is boundary evidence showing that "
                "selected does not universally dominate. Across both suites, the "
                "strongest stable claim is that harmful admitted artifacts can "
                "cause systematic public-pass/hidden-fail negative transfer."
            ),
            "## Cross-Version Primary Table",
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
            "## Derived Synthesis",
            md_table(["comparison", "value"], comparison_rows),
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
        "% Auto-generated by scripts/export_downstream_cross_version_synthesis.py",
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
            "% Cross-version derived synthesis:",
        ]
    )
    for key, value in sorted(package["derived_synthesis"].items()):
        if isinstance(value, dict):
            continue
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
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX)
    parser.add_argument(
        "--assert-current-synthesis",
        action="store_true",
        help="Assert current cross-version evidence values and claim-boundary invariants.",
    )
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> Path:
    resolved = resolve(path)
    try:
        return resolved.relative_to(ROOT)
    except ValueError:
        return resolved


def main() -> None:
    args = parse_args()
    hard_v2_path = resolve(args.hard_v2_package)
    hard_v3_path = resolve(args.hard_v3_package)
    package = build_package(
        load_json(hard_v2_path),
        load_json(hard_v3_path),
        hard_v2_path,
        hard_v3_path,
    )
    if args.assert_current_synthesis:
        assert_synthesis(package)
    write_outputs(package, resolve(args.json_out), resolve(args.md_out), resolve(args.tex_out))
    print(f"primary_rows: {len(package['primary_strategy_table'])}")
    print(f"forced_bad_total_tasks: {package['derived_synthesis']['forced_bad_total_tasks']}")
    print(f"selected_superiority_consistent: {package['derived_synthesis']['selected_superiority_consistent']}")
    print(f"selected_token_savings_supported: {package['derived_synthesis']['selected_token_savings_supported']}")
    print(f"wrote_json: {display_path(args.json_out)}")
    print(f"wrote_md: {display_path(args.md_out)}")
    print(f"wrote_tex: {display_path(args.tex_out)}")


if __name__ == "__main__":
    main()
