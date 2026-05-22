#!/usr/bin/env python3
"""Export the paper artifact index for SkillAdmit.

What this file does:
  Builds a compact index of the paper-facing artifacts produced by the
  SkillAdmit experiment: admission context, hard_v2 evidence, hard_v3 evidence,
  cross-version synthesis, paper-section draft, and claim-defense matrix. The
  index records each artifact's role, path, regeneration command, and claim
  boundary.

Why it is needed:
  The repository now contains many summaries, tables, evidence packages, and
  drafting aids. A paper should cite the right artifact for the right purpose:
  evidence packages and synthesis reports for claims, paper-section text for
  drafting, and individual run summaries only for debugging. This index keeps
  the final SkillAdmit story tied to the downstream validation boundary rather
  than scattered summary files.

Inputs:
  benchmark/reports/v7_admission_baselines.json
  benchmark/reports/llm_cost_summary.json
  benchmark/downstream/reports/hard_v2_evidence_package.json
  benchmark/downstream/reports/hard_v3_evidence_package.json
  benchmark/downstream/reports/downstream_cross_version_synthesis.json
  benchmark/downstream/reports/downstream_paper_eval_section.json
  benchmark/downstream/reports/downstream_claim_defense_matrix.json
  benchmark/downstream/reports/hard_v4_scaffold_manifest.json

Outputs:
  benchmark/downstream/reports/paper_artifacts_index.json
  benchmark/downstream/reports/paper_artifacts_index.md
  benchmark/downstream/reports/paper_artifacts_index.tex

Who runs it:
  Researchers or Codex sessions before paper writing, reviewer-response
  drafting, or handoff to another agent.
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
BENCHMARK_REPORT_DIR = ROOT / "benchmark" / "reports"

DEFAULT_JSON = REPORT_DIR / "paper_artifacts_index.json"
DEFAULT_MD = REPORT_DIR / "paper_artifacts_index.md"
DEFAULT_TEX = REPORT_DIR / "paper_artifacts_index.tex"

INPUTS = {
    "v7_admission_baselines": BENCHMARK_REPORT_DIR / "v7_admission_baselines.json",
    "llm_cost_summary": BENCHMARK_REPORT_DIR / "llm_cost_summary.json",
    "hard_v2_evidence_package": REPORT_DIR / "hard_v2_evidence_package.json",
    "hard_v3_evidence_package": REPORT_DIR / "hard_v3_evidence_package.json",
    "downstream_cross_version_synthesis": REPORT_DIR / "downstream_cross_version_synthesis.json",
    "downstream_paper_eval_section": REPORT_DIR / "downstream_paper_eval_section.json",
    "downstream_claim_defense_matrix": REPORT_DIR / "downstream_claim_defense_matrix.json",
    "hard_v4_scaffold_manifest": REPORT_DIR / "hard_v4_scaffold_manifest.json",
}


ARTIFACT_PATHS = {
    "admission_baselines_md": BENCHMARK_REPORT_DIR / "v7_admission_baselines.md",
    "admission_baselines_json": BENCHMARK_REPORT_DIR / "v7_admission_baselines.json",
    "cost_summary_md": BENCHMARK_REPORT_DIR / "llm_cost_summary.md",
    "cost_summary_json": BENCHMARK_REPORT_DIR / "llm_cost_summary.json",
    "hard_v2_strategy_matrix_md": REPORT_DIR / "hard_v2_strategy_matrix.md",
    "hard_v2_strategy_matrix_json": REPORT_DIR / "hard_v2_strategy_matrix.json",
    "hard_v2_evidence_json": REPORT_DIR / "hard_v2_evidence_package.json",
    "hard_v2_paper_tables_md": REPORT_DIR / "hard_v2_paper_tables.md",
    "hard_v2_paper_tables_tex": REPORT_DIR / "hard_v2_paper_tables.tex",
    "hard_v3_strategy_matrix_md": REPORT_DIR / "hard_v3_strategy_matrix.md",
    "hard_v3_strategy_matrix_json": REPORT_DIR / "hard_v3_strategy_matrix.json",
    "hard_v3_evidence_json": REPORT_DIR / "hard_v3_evidence_package.json",
    "hard_v3_paper_tables_md": REPORT_DIR / "hard_v3_paper_tables.md",
    "hard_v3_paper_tables_tex": REPORT_DIR / "hard_v3_paper_tables.tex",
    "cross_synthesis_json": REPORT_DIR / "downstream_cross_version_synthesis.json",
    "cross_synthesis_md": REPORT_DIR / "downstream_cross_version_synthesis.md",
    "cross_synthesis_tex": REPORT_DIR / "downstream_cross_version_synthesis.tex",
    "paper_section_json": REPORT_DIR / "downstream_paper_eval_section.json",
    "paper_section_md": REPORT_DIR / "downstream_paper_eval_section.md",
    "paper_section_tex": REPORT_DIR / "downstream_paper_eval_section.tex",
    "claim_defense_json": REPORT_DIR / "downstream_claim_defense_matrix.json",
    "claim_defense_md": REPORT_DIR / "downstream_claim_defense_matrix.md",
    "claim_defense_tex": REPORT_DIR / "downstream_claim_defense_matrix.tex",
    "hard_v4_scaffold_json": REPORT_DIR / "hard_v4_scaffold_manifest.json",
    "hard_v4_scaffold_md": REPORT_DIR / "hard_v4_scaffold_manifest.md",
    "hard_v4_scaffold_tex": REPORT_DIR / "hard_v4_scaffold_manifest.tex",
    "hard_v4_protocol": ROOT / "docs" / "llm_downstream_hard_v4.md",
    "paper_eval_status": ROOT / "docs" / "paper_eval_status.md",
    "experiment_handoff": ROOT / "docs" / "experiment_handoff.md",
    "progress_log": ROOT / "docs" / "progress_log.md",
}


SCRIPT_PATHS = {
    "run_admission_regression": ROOT / "scripts" / "run_admission_regression.py",
    "check_hard_v2": ROOT / "scripts" / "check_downstream_hard_v2_tasks.py",
    "check_hard_v3": ROOT / "scripts" / "check_downstream_hard_v3_tasks.py",
    "build_hard_v4": ROOT / "scripts" / "build_downstream_hard_v4_tasks.py",
    "check_hard_v4": ROOT / "scripts" / "check_downstream_hard_v4_tasks.py",
    "summarize_hard_v2": ROOT / "scripts" / "summarize_hard_v2_results.py",
    "export_hard_v2": ROOT / "scripts" / "export_hard_v2_evidence_package.py",
    "summarize_hard_v3": ROOT / "scripts" / "summarize_hard_v3_results.py",
    "export_hard_v3": ROOT / "scripts" / "export_hard_v3_evidence_package.py",
    "export_cross_synthesis": ROOT / "scripts" / "export_downstream_cross_version_synthesis.py",
    "export_paper_section": ROOT / "scripts" / "export_downstream_paper_section.py",
    "export_claim_defense": ROOT / "scripts" / "export_downstream_claim_defense_matrix.py",
    "export_hard_v4_scaffold": ROOT / "scripts" / "export_hard_v4_scaffold_manifest.py",
    "export_artifacts_index": ROOT / "scripts" / "export_paper_artifacts_index.py",
}


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> str:
    path = resolve(path)
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def existing_file(path: Path) -> dict[str, Any]:
    resolved = resolve(path)
    if not resolved.exists():
        return {
            "path": display_path(resolved),
            "exists": False,
            "sha256": None,
            "size_bytes": None,
        }
    return {
        "path": display_path(resolved),
        "exists": True,
        "sha256": sha256_file(resolved),
        "size_bytes": resolved.stat().st_size,
    }


def generated_at(value: Any) -> str | None:
    if isinstance(value, dict):
        generated = value.get("generated_at_utc") or value.get("generated_at")
        return str(generated) if generated is not None else None
    return None


def find_row(package: dict[str, Any], run_name: str, strategy: str) -> dict[str, Any]:
    for row in package["primary_strategy_table"]:
        if row["run_name"] == run_name and row["strategy"] == strategy:
            return row
    raise KeyError(f"Missing row: {run_name}/{strategy}")


def build_artifact_group(
    group_id: str,
    title: str,
    role: str,
    primary_files: list[str],
    support_files: list[str],
    regeneration_commands: list[str],
    use_in_paper: str,
    do_not_use_for: str,
) -> dict[str, Any]:
    return {
        "group_id": group_id,
        "title": title,
        "role": role,
        "primary_files": [existing_file(ARTIFACT_PATHS[name]) for name in primary_files],
        "support_files": [existing_file(ARTIFACT_PATHS[name]) for name in support_files],
        "regeneration_commands": regeneration_commands,
        "use_in_paper": use_in_paper,
        "do_not_use_for": do_not_use_for,
    }


def build_artifact_groups() -> list[dict[str, Any]]:
    return [
        build_artifact_group(
            "G1_admission_context",
            "Admission Context",
            "Supporting context for admission benchmark status and baseline caveats.",
            ["admission_baselines_md", "admission_baselines_json", "cost_summary_md", "cost_summary_json"],
            ["paper_eval_status", "experiment_handoff"],
            ["python scripts/run_admission_regression.py"],
            "Use to describe the frozen admission pipeline, v7 baseline caveat, and token accounting context.",
            "Do not use v7 admission accuracy as the main downstream-utility proof.",
        ),
        build_artifact_group(
            "G2_hard_v2_evidence",
            "Hard v2 Evidence",
            "Primary downstream evidence for tree-aware selected utility and strict visible-file boundary.",
            ["hard_v2_evidence_json", "hard_v2_paper_tables_md", "hard_v2_paper_tables_tex"],
            ["hard_v2_strategy_matrix_md", "hard_v2_strategy_matrix_json", "paper_eval_status"],
            [
                "python scripts/check_downstream_hard_v2_tasks.py",
                "python scripts/summarize_hard_v2_results.py --assert-current-hard-v2",
                "python scripts/export_hard_v2_evidence_package.py --assert-current-hard-v2",
            ],
            "Use for hard_v2 results, including 25/25 tree-aware selected and strict visible-file caveats.",
            "Do not flatten strict visible-file and tree-aware hard_v2 into one selected-wins leaderboard.",
        ),
        build_artifact_group(
            "G3_hard_v3_evidence",
            "Hard v3 Evidence",
            "Fresh downstream boundary evidence and artifact-adherence caveats.",
            ["hard_v3_evidence_json", "hard_v3_paper_tables_md", "hard_v3_paper_tables_tex"],
            ["hard_v3_strategy_matrix_md", "hard_v3_strategy_matrix_json", "paper_eval_status"],
            [
                "python scripts/check_downstream_hard_v3_tasks.py",
                "python scripts/summarize_hard_v3_results.py --assert-current-hard-v3",
                "python scripts/export_hard_v3_evidence_package.py --assert-current-hard-v3",
            ],
            "Use for hard_v3 boundary claims: selected ties no_experience in tree-aware and is not best in strict visible-file.",
            "Do not use hard_v3 to claim universal SkillAdmit-selected superiority or selected token savings.",
        ),
        build_artifact_group(
            "G4_cross_version_synthesis",
            "Cross-Version Synthesis",
            "Primary paper-facing synthesis of hard_v2 and hard_v3 claim boundaries.",
            ["cross_synthesis_json", "cross_synthesis_md", "cross_synthesis_tex"],
            ["hard_v2_evidence_json", "hard_v3_evidence_json", "paper_eval_status"],
            ["python scripts/export_downstream_cross_version_synthesis.py --assert-current-synthesis"],
            "Use for the top-level downstream story and forced_bad_artifact aggregate.",
            "Do not merge hard_v2 and hard_v3 into a single anonymous leaderboard.",
        ),
        build_artifact_group(
            "G5_paper_section",
            "Draftable Paper Section",
            "Generated evaluation-section prose tied to the frozen synthesis.",
            ["paper_section_json", "paper_section_md", "paper_section_tex"],
            ["cross_synthesis_json", "claim_defense_md"],
            ["python scripts/export_downstream_paper_section.py --assert-current-paper-section"],
            "Use as the starting point for writing the downstream validation subsection.",
            "Do not edit this prose into stronger claims without updating evidence and assertions.",
        ),
        build_artifact_group(
            "G6_claim_defense",
            "Claim Defense Matrix",
            "Reviewer-facing claim-by-claim evidence map and forbidden wording ledger.",
            ["claim_defense_json", "claim_defense_md", "claim_defense_tex"],
            ["cross_synthesis_json", "paper_section_json"],
            ["python scripts/export_downstream_claim_defense_matrix.py --assert-current-claim-defense"],
            "Use during paper revision and reviewer response drafting.",
            "Do not treat reviewer-response wording as new experimental evidence.",
        ),
        build_artifact_group(
            "G7_reporting_handoff",
            "Reporting and Handoff",
            "Human-readable state tracking and cross-session recovery anchors.",
            ["paper_eval_status", "experiment_handoff", "progress_log"],
            [],
            [],
            "Use to recover the current project state and avoid repeating frozen experiments.",
            "Do not cite progress logs as primary empirical evidence when paper-facing tables exist.",
        ),
        build_artifact_group(
            "G8_hard_v4_scaffold",
            "Hard v4 Scaffold",
            "Freeze-ready future downstream boundary scaffold, not current LLM evidence.",
            ["hard_v4_scaffold_json", "hard_v4_scaffold_md", "hard_v4_scaffold_tex"],
            ["hard_v4_protocol", "paper_eval_status", "experiment_handoff"],
            [
                "python scripts/build_downstream_hard_v4_tasks.py",
                "python scripts/check_downstream_hard_v4_tasks.py",
                "python scripts/export_hard_v4_scaffold_manifest.py --run-checker --assert-current-hard-v4-scaffold",
            ],
            "Use only to document the future hard_v4 boundary and its no-LLM-evidence status.",
            "Do not cite as evidence that SkillAdmit helps on hard_v4.",
        ),
    ]


def build_regeneration_order() -> list[dict[str, str]]:
    commands = [
        ("check_hard_v2", "python scripts/check_downstream_hard_v2_tasks.py"),
        ("check_hard_v3", "python scripts/check_downstream_hard_v3_tasks.py"),
        ("admission_regression", "python scripts/run_admission_regression.py"),
        ("summarize_hard_v2", "python scripts/summarize_hard_v2_results.py --assert-current-hard-v2"),
        ("export_hard_v2", "python scripts/export_hard_v2_evidence_package.py --assert-current-hard-v2"),
        ("summarize_hard_v3", "python scripts/summarize_hard_v3_results.py --assert-current-hard-v3"),
        ("export_hard_v3", "python scripts/export_hard_v3_evidence_package.py --assert-current-hard-v3"),
        ("export_cross_synthesis", "python scripts/export_downstream_cross_version_synthesis.py --assert-current-synthesis"),
        ("export_paper_section", "python scripts/export_downstream_paper_section.py --assert-current-paper-section"),
        ("export_claim_defense", "python scripts/export_downstream_claim_defense_matrix.py --assert-current-claim-defense"),
        ("build_hard_v4", "python scripts/build_downstream_hard_v4_tasks.py"),
        ("check_hard_v4", "python scripts/check_downstream_hard_v4_tasks.py"),
        (
            "export_hard_v4_scaffold",
            "python scripts/export_hard_v4_scaffold_manifest.py --run-checker --assert-current-hard-v4-scaffold",
        ),
        ("export_artifacts_index", "python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index"),
    ]
    return [
        {
            "step": index,
            "name": name,
            "command": command,
            "script_exists": SCRIPT_PATHS.get(name, Path()).exists() if name in SCRIPT_PATHS else True,
        }
        for index, (name, command) in enumerate(commands, start=1)
    ]


def build_table_index() -> list[dict[str, Any]]:
    return [
        {
            "table_id": "T_admission_context",
            "paper_role": "Optional setup table, not the main downstream claim.",
            "primary_artifacts": [
                display_path(ARTIFACT_PATHS["admission_baselines_md"]),
                display_path(ARTIFACT_PATHS["admission_baselines_json"]),
            ],
            "allowed_claim": "v7 admission is frozen and useful context, but keyword baseline caveat limits semantic claims.",
            "avoid": "Do not claim v7 admission accuracy alone proves downstream utility.",
        },
        {
            "table_id": "T_hard_v2",
            "paper_role": "Hard v2 primary result table.",
            "primary_artifacts": [
                display_path(ARTIFACT_PATHS["hard_v2_paper_tables_md"]),
                display_path(ARTIFACT_PATHS["hard_v2_paper_tables_tex"]),
                display_path(ARTIFACT_PATHS["hard_v2_evidence_json"]),
            ],
            "allowed_claim": "hard_v2 supports tree-aware selected utility and exposes strict visible-file boundary.",
            "avoid": "Do not collapse hard_v2 settings into selected universally wins.",
        },
        {
            "table_id": "T_hard_v3",
            "paper_role": "Hard v3 boundary and artifact-adherence table.",
            "primary_artifacts": [
                display_path(ARTIFACT_PATHS["hard_v3_paper_tables_md"]),
                display_path(ARTIFACT_PATHS["hard_v3_paper_tables_tex"]),
                display_path(ARTIFACT_PATHS["hard_v3_evidence_json"]),
            ],
            "allowed_claim": "hard_v3 bounds selected-superiority and strengthens negative-transfer evidence.",
            "avoid": "Do not claim hard_v3 proves selected superiority or token savings.",
        },
        {
            "table_id": "T_cross_version",
            "paper_role": "Main downstream synthesis table.",
            "primary_artifacts": [
                display_path(ARTIFACT_PATHS["cross_synthesis_md"]),
                display_path(ARTIFACT_PATHS["cross_synthesis_tex"]),
                display_path(ARTIFACT_PATHS["cross_synthesis_json"]),
            ],
            "allowed_claim": "hard_v2 is positive tree-aware evidence; hard_v3 is generalization boundary; forced bad is 0/85.",
            "avoid": "Do not read the synthesis as a single global leaderboard.",
        },
        {
            "table_id": "T_claim_defense_appendix",
            "paper_role": "Appendix or internal reviewer-response table.",
            "primary_artifacts": [
                display_path(ARTIFACT_PATHS["claim_defense_md"]),
                display_path(ARTIFACT_PATHS["claim_defense_tex"]),
                display_path(ARTIFACT_PATHS["claim_defense_json"]),
            ],
            "allowed_claim": "Use to police wording and prepare reviewer responses.",
            "avoid": "Do not cite defense wording as if it were an additional experiment.",
        },
    ]


def build_claim_to_artifact_map(claim_defense: dict[str, Any]) -> list[dict[str, Any]]:
    source_to_artifacts = {
        "hard_v2_evidence_package": [display_path(ARTIFACT_PATHS["hard_v2_evidence_json"])],
        "hard_v3_evidence_package": [display_path(ARTIFACT_PATHS["hard_v3_evidence_json"])],
        "downstream_cross_version_synthesis": [display_path(ARTIFACT_PATHS["cross_synthesis_json"])],
    }
    rows = []
    for claim in claim_defense["claims"]:
        sources = []
        for evidence in claim["evidence"]:
            for artifact in source_to_artifacts.get(evidence.get("source"), []):
                if artifact not in sources:
                    sources.append(artifact)
        rows.append(
            {
                "claim_id": claim["claim_id"],
                "status": claim["status"],
                "primary_artifact": display_path(ARTIFACT_PATHS["claim_defense_json"]),
                "supporting_artifacts": sources,
                "allowed_wording_first": claim["allowed_wording"][0],
                "forbidden_wording_first": claim["forbidden_wording"][0],
            }
        )
    return rows


def build_do_not_cite_as_primary() -> list[dict[str, str]]:
    return [
        {
            "artifact_pattern": "benchmark/downstream/llm_runs/*/summary.json",
            "reason": "Per-run summaries are useful for debugging but should not be the paper's primary evidence once matrix/evidence packages exist.",
        },
        {
            "artifact_pattern": "benchmark/downstream/llm_runs/*/trajectories.jsonl",
            "reason": "Trajectories are provenance/debugging records; cite aggregated evidence packages instead.",
        },
        {
            "artifact_pattern": "benchmark/downstream_hard_v2/tasks/* and benchmark/downstream_hard_v3/tasks/*",
            "reason": "Task files define the benchmark and verifiers; do not use inspected failures for prompt tuning while preserving clean evidence.",
        },
        {
            "artifact_pattern": "benchmark/downstream_hard_v4/tasks/*",
            "reason": "hard_v4 task files define a future boundary; do not tune prompts or strategies from inspected hard_v4 failures.",
        },
        {
            "artifact_pattern": "docs/progress_log.md",
            "reason": "Progress log is a handoff ledger, not a primary empirical table.",
        },
    ]


def build_index(data: dict[str, dict[str, Any]]) -> dict[str, Any]:
    hard_v2 = data["hard_v2_evidence_package"]
    hard_v3 = data["hard_v3_evidence_package"]
    synthesis = data["downstream_cross_version_synthesis"]
    paper_section = data["downstream_paper_eval_section"]
    claim_defense = data["downstream_claim_defense_matrix"]

    v2_tree_no = find_row(hard_v2, "llm_downstream_hard_v2_tree_25x2", "no_experience")
    v2_tree_selected = find_row(hard_v2, "llm_downstream_hard_v2_tree_25x2", "skilladmit_selected")
    v3_tree_no = find_row(hard_v3, "llm_downstream_hard_v3_tree_core_30x2", "no_experience")
    v3_tree_selected = find_row(hard_v3, "llm_downstream_hard_v3_tree_core_30x2", "skilladmit_selected")
    v3_strict_pre = find_row(
        hard_v3,
        "llm_downstream_hard_v3_strict_30x8",
        "skilladmit_selected_with_precondition_only",
    )
    derived = synthesis["derived_synthesis"]

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "One-stop index for paper-facing SkillAdmit artifacts. Use it to choose the correct evidence, "
            "table, script, and claim boundary for downstream validation writing."
        ),
        "source_inputs": [
            {
                "name": name,
                **existing_file(path),
                "generated_at_utc": generated_at(data[name]),
            }
            for name, path in INPUTS.items()
        ],
        "key_current_facts": {
            "hard_v2_tree_selected": v2_tree_selected["success"],
            "hard_v2_tree_no_experience": v2_tree_no["success"],
            "hard_v3_tree_selected": v3_tree_selected["success"],
            "hard_v3_tree_no_experience": v3_tree_no["success"],
            "hard_v3_strict_precondition_only": v3_strict_pre["success"],
            "forced_bad_total_successes": derived["forced_bad_total_successes"],
            "forced_bad_total_tasks": derived["forced_bad_total_tasks"],
            "forced_bad_total_public_passed_hidden_failed": derived[
                "forced_bad_total_public_passed_hidden_failed"
            ],
            "selected_superiority_consistent": derived["selected_superiority_consistent"],
            "selected_token_savings_supported": derived["selected_token_savings_supported"],
            "claim_count": claim_defense["claim_count"],
            "paper_section_result_paragraphs": len(paper_section["results"]),
        },
        "artifact_groups": build_artifact_groups(),
        "regeneration_order": build_regeneration_order(),
        "table_index": build_table_index(),
        "claim_to_artifact_map": build_claim_to_artifact_map(claim_defense),
        "do_not_cite_as_primary": build_do_not_cite_as_primary(),
        "next_experimental_boundary": {
            "recommended": "hard_v4 LLM matrix or model-transfer replication only after explicitly declaring a fresh evaluation boundary.",
            "avoid": "Do not tune hard_v2/hard_v3/hard_v4 prompts or strategies from observed failures while still treating them as clean evidence.",
        },
    }


def assert_index(index: dict[str, Any]) -> None:
    facts = index["key_current_facts"]
    expected = {
        "hard_v2_tree_selected": "25/25",
        "hard_v2_tree_no_experience": "23/25",
        "hard_v3_tree_selected": "29/30",
        "hard_v3_tree_no_experience": "29/30",
        "hard_v3_strict_precondition_only": "30/30",
        "forced_bad_total_successes": 0,
        "forced_bad_total_tasks": 85,
        "forced_bad_total_public_passed_hidden_failed": 85,
        "selected_superiority_consistent": False,
        "selected_token_savings_supported": False,
        "claim_count": 10,
        "paper_section_result_paragraphs": 5,
    }
    for key, value in expected.items():
        actual = facts[key]
        if actual != value:
            raise AssertionError(f"{key}: expected {value}, got {actual}")

    for source in index["source_inputs"]:
        if not source["exists"]:
            raise AssertionError(f"missing source input: {source['path']}")
    for group in index["artifact_groups"]:
        for file_info in group["primary_files"] + group["support_files"]:
            if not file_info["exists"]:
                raise AssertionError(f"missing artifact file: {file_info['path']}")
    if len(index["artifact_groups"]) != 8:
        raise AssertionError("artifact group count changed")
    if len(index["table_index"]) != 5:
        raise AssertionError("table index count changed")
    if len(index["claim_to_artifact_map"]) != 10:
        raise AssertionError("claim map count changed")

    rendered = render_markdown(index)
    required = [
        "25/25",
        "23/25",
        "29/30",
        "0/85",
        "Do not tune hard_v2/hard_v3/hard_v4 prompts",
        "hard_v4_scaffold_manifest.json",
        "hard_v4 LLM matrix or model-transfer replication",
        "downstream_claim_defense_matrix.json",
    ]
    for phrase in required:
        if phrase not in rendered:
            raise AssertionError(f"missing required index phrase: {phrase}")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def render_markdown(index: dict[str, Any]) -> str:
    facts = index["key_current_facts"]
    lines = [
        "# Paper Artifacts Index",
        "",
        f"Generated at UTC: `{index['generated_at_utc']}`",
        "",
        index["purpose"],
        "",
        "## Key Current Facts",
        "",
        md_table(
            ["fact", "value"],
            [[key, value] for key, value in facts.items()],
        ),
        "",
        "## Artifact Groups",
        "",
    ]
    group_rows = []
    for group in index["artifact_groups"]:
        group_rows.append(
            [
                group["group_id"],
                group["title"],
                group["role"],
                group["use_in_paper"],
                group["do_not_use_for"],
            ]
        )
    lines.extend(
        md_table(
            ["group", "title", "role", "use in paper", "do not use for"],
            group_rows,
        ).splitlines()
    )

    lines.extend(["", "## Primary Files By Group", ""])
    for group in index["artifact_groups"]:
        lines.extend([f"### {group['group_id']} - {group['title']}", ""])
        file_rows = []
        for file_info in group["primary_files"]:
            file_rows.append(
                [
                    "primary",
                    f"`{file_info['path']}`",
                    file_info["exists"],
                    f"`{file_info['sha256'][:16]}`" if file_info["sha256"] else "",
                    file_info["size_bytes"] or "",
                ]
            )
        for file_info in group["support_files"]:
            file_rows.append(
                [
                    "support",
                    f"`{file_info['path']}`",
                    file_info["exists"],
                    f"`{file_info['sha256'][:16]}`" if file_info["sha256"] else "",
                    file_info["size_bytes"] or "",
                ]
            )
        lines.extend(md_table(["role", "path", "exists", "sha256", "bytes"], file_rows).splitlines())
        if group["regeneration_commands"]:
            lines.extend(["", "Regeneration commands:"])
            lines.extend(f"- `{command}`" for command in group["regeneration_commands"])
        lines.append("")

    lines.extend(["## Regeneration Order", ""])
    lines.extend(
        md_table(
            ["step", "name", "command", "script exists"],
            [
                [row["step"], row["name"], f"`{row['command']}`", row["script_exists"]]
                for row in index["regeneration_order"]
            ],
        ).splitlines()
    )

    lines.extend(["", "## Table Index", ""])
    lines.extend(
        md_table(
            ["table", "paper role", "primary artifacts", "allowed claim", "avoid"],
            [
                [
                    row["table_id"],
                    row["paper_role"],
                    "<br>".join(f"`{path}`" for path in row["primary_artifacts"]),
                    row["allowed_claim"],
                    row["avoid"],
                ]
                for row in index["table_index"]
            ],
        ).splitlines()
    )

    lines.extend(["", "## Claim To Artifact Map", ""])
    lines.extend(
        md_table(
            ["claim", "status", "primary artifact", "supporting artifacts", "allowed wording", "forbidden wording"],
            [
                [
                    row["claim_id"],
                    row["status"],
                    f"`{row['primary_artifact']}`",
                    "<br>".join(f"`{path}`" for path in row["supporting_artifacts"]),
                    row["allowed_wording_first"],
                    row["forbidden_wording_first"],
                ]
                for row in index["claim_to_artifact_map"]
            ],
        ).splitlines()
    )

    lines.extend(["", "## Do Not Cite As Primary Evidence", ""])
    lines.extend(
        md_table(
            ["artifact pattern", "reason"],
            [[row["artifact_pattern"], row["reason"]] for row in index["do_not_cite_as_primary"]],
        ).splitlines()
    )

    lines.extend(
        [
            "",
            "## Next Experimental Boundary",
            "",
            f"Recommended: {index['next_experimental_boundary']['recommended']}",
            "",
            f"Avoid: {index['next_experimental_boundary']['avoid']}",
            "",
            "## Source Inputs",
            "",
        ]
    )
    lines.extend(
        md_table(
            ["name", "path", "exists", "sha256", "generated_at_utc"],
            [
                [
                    row["name"],
                    f"`{row['path']}`",
                    row["exists"],
                    f"`{row['sha256'][:16]}`" if row["sha256"] else "",
                    f"`{row['generated_at_utc']}`" if row["generated_at_utc"] else "",
                ]
                for row in index["source_inputs"]
            ],
        ).splitlines()
    )
    lines.append("")
    return "\n".join(lines)


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


def render_latex(index: dict[str, Any]) -> str:
    lines = [
        "% Auto-generated by scripts/export_paper_artifacts_index.py",
        "\\begin{tabular}{llll}",
        "\\hline",
        "Group & Role & Use & Do not use for \\\\",
        "\\hline",
    ]
    for group in index["artifact_groups"]:
        lines.append(
            " & ".join(
                [
                    tex_escape(group["group_id"]),
                    tex_escape(group["role"][:70]),
                    tex_escape(group["use_in_paper"][:70]),
                    tex_escape(group["do_not_use_for"][:70]),
                ]
            )
            + " \\\\"
        )
    lines.extend(["\\hline", "\\end{tabular}", "", "% Key current facts:"])
    for key, value in index["key_current_facts"].items():
        lines.append(f"% {tex_escape(key)} = {tex_escape(value)}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(index: dict[str, Any], json_path: Path, md_path: Path, tex_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(index), encoding="utf-8")
    tex_path.write_text(render_latex(index), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX)
    parser.add_argument(
        "--assert-current-artifacts-index",
        action="store_true",
        help="Assert current paper artifact index values and evidence-boundary invariants.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = {name: load_json(path) for name, path in INPUTS.items()}
    index = build_index(data)
    if args.assert_current_artifacts_index:
        assert_index(index)
    write_outputs(index, resolve(args.json_out), resolve(args.md_out), resolve(args.tex_out))
    print(f"artifact_groups: {len(index['artifact_groups'])}")
    print(f"table_index: {len(index['table_index'])}")
    print(f"claim_map: {len(index['claim_to_artifact_map'])}")
    print(f"forced_bad_total_tasks: {index['key_current_facts']['forced_bad_total_tasks']}")
    print(f"wrote_json: {display_path(args.json_out)}")
    print(f"wrote_md: {display_path(args.md_out)}")
    print(f"wrote_tex: {display_path(args.tex_out)}")


if __name__ == "__main__":
    main()
