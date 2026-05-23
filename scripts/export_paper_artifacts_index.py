#!/usr/bin/env python3
"""Export the paper artifact index for SkillAdmit.

What this file does:
  Builds a compact index of the paper-facing artifacts produced by the
  SkillAdmit experiment: admission context, hard_v2 evidence, hard_v3 evidence,
  hard_v4 boundary evidence, cross-version synthesis, three-boundary synthesis,
  paper-section draft, claim-defense matrix, model-transfer evidence,
  model-transfer paper addendum, the paper-claim consistency audit command, the
  public reporting hygiene audit command, and the model-transfer replication
  protocol command. The index records each artifact's role, path, regeneration
  command, and claim boundary.

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
  benchmark/downstream/reports/hard_v4_evidence_package.json
  benchmark/downstream/reports/downstream_cross_version_synthesis.json
  benchmark/downstream/reports/downstream_boundary_synthesis.json
  benchmark/downstream/reports/downstream_paper_eval_section.json
  benchmark/downstream/reports/downstream_claim_defense_matrix.json
  benchmark/downstream/reports/hard_v4_scaffold_manifest.json
  benchmark/downstream/reports/model_transfer_evidence_package.json
  benchmark/downstream/reports/model_transfer_cross_model_synthesis.json
  benchmark/downstream/reports/model_transfer_paper_addendum.json

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
    "hard_v4_evidence_package": REPORT_DIR / "hard_v4_evidence_package.json",
    "downstream_cross_version_synthesis": REPORT_DIR / "downstream_cross_version_synthesis.json",
    "downstream_boundary_synthesis": REPORT_DIR / "downstream_boundary_synthesis.json",
    "downstream_paper_eval_section": REPORT_DIR / "downstream_paper_eval_section.json",
    "downstream_claim_defense_matrix": REPORT_DIR / "downstream_claim_defense_matrix.json",
    "hard_v4_scaffold_manifest": REPORT_DIR / "hard_v4_scaffold_manifest.json",
    "model_transfer_evidence_package": REPORT_DIR / "model_transfer_evidence_package.json",
    "model_transfer_cross_model_synthesis": REPORT_DIR / "model_transfer_cross_model_synthesis.json",
    "model_transfer_paper_addendum": REPORT_DIR / "model_transfer_paper_addendum.json",
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
    "boundary_synthesis_json": REPORT_DIR / "downstream_boundary_synthesis.json",
    "boundary_synthesis_md": REPORT_DIR / "downstream_boundary_synthesis.md",
    "boundary_synthesis_tex": REPORT_DIR / "downstream_boundary_synthesis.tex",
    "paper_section_json": REPORT_DIR / "downstream_paper_eval_section.json",
    "paper_section_md": REPORT_DIR / "downstream_paper_eval_section.md",
    "paper_section_tex": REPORT_DIR / "downstream_paper_eval_section.tex",
    "claim_defense_json": REPORT_DIR / "downstream_claim_defense_matrix.json",
    "claim_defense_md": REPORT_DIR / "downstream_claim_defense_matrix.md",
    "claim_defense_tex": REPORT_DIR / "downstream_claim_defense_matrix.tex",
    "hard_v4_scaffold_json": REPORT_DIR / "hard_v4_scaffold_manifest.json",
    "hard_v4_scaffold_md": REPORT_DIR / "hard_v4_scaffold_manifest.md",
    "hard_v4_scaffold_tex": REPORT_DIR / "hard_v4_scaffold_manifest.tex",
    "hard_v4_strategy_matrix_md": REPORT_DIR / "hard_v4_strategy_matrix.md",
    "hard_v4_strategy_matrix_json": REPORT_DIR / "hard_v4_strategy_matrix.json",
    "hard_v4_evidence_json": REPORT_DIR / "hard_v4_evidence_package.json",
    "hard_v4_paper_tables_md": REPORT_DIR / "hard_v4_paper_tables.md",
    "hard_v4_paper_tables_tex": REPORT_DIR / "hard_v4_paper_tables.tex",
    "model_transfer_protocol_json": REPORT_DIR / "model_transfer_replication_protocol.json",
    "model_transfer_protocol_md": REPORT_DIR / "model_transfer_replication_protocol.md",
    "model_transfer_protocol_tex": REPORT_DIR / "model_transfer_replication_protocol.tex",
    "model_transfer_evidence_json": REPORT_DIR / "model_transfer_evidence_package.json",
    "model_transfer_evidence_md": REPORT_DIR / "model_transfer_evidence_package.md",
    "model_transfer_evidence_tex": REPORT_DIR / "model_transfer_evidence_package.tex",
    "model_transfer_cross_model_json": REPORT_DIR / "model_transfer_cross_model_synthesis.json",
    "model_transfer_cross_model_md": REPORT_DIR / "model_transfer_cross_model_synthesis.md",
    "model_transfer_cross_model_tex": REPORT_DIR / "model_transfer_cross_model_synthesis.tex",
    "model_transfer_addendum_json": REPORT_DIR / "model_transfer_paper_addendum.json",
    "model_transfer_addendum_md": REPORT_DIR / "model_transfer_paper_addendum.md",
    "model_transfer_addendum_tex": REPORT_DIR / "model_transfer_paper_addendum.tex",
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
    "summarize_hard_v4": ROOT / "scripts" / "summarize_hard_v4_results.py",
    "export_hard_v4": ROOT / "scripts" / "export_hard_v4_evidence_package.py",
    "export_cross_synthesis": ROOT / "scripts" / "export_downstream_cross_version_synthesis.py",
    "export_boundary_synthesis": ROOT / "scripts" / "export_downstream_boundary_synthesis.py",
    "export_paper_section": ROOT / "scripts" / "export_downstream_paper_section.py",
    "export_claim_defense": ROOT / "scripts" / "export_downstream_claim_defense_matrix.py",
    "export_hard_v4_scaffold": ROOT / "scripts" / "export_hard_v4_scaffold_manifest.py",
    "export_artifacts_index": ROOT / "scripts" / "export_paper_artifacts_index.py",
    "audit_paper_claim_consistency": ROOT / "scripts" / "audit_paper_claim_consistency.py",
    "audit_reporting_hygiene": ROOT / "scripts" / "audit_reporting_hygiene.py",
    "export_model_transfer_protocol": ROOT / "scripts" / "export_model_transfer_replication_protocol.py",
    "export_model_transfer_evidence": ROOT / "scripts" / "export_model_transfer_evidence_package.py",
    "export_model_transfer_cross_model": ROOT / "scripts" / "export_model_transfer_cross_model_synthesis.py",
    "export_model_transfer_addendum": ROOT / "scripts" / "export_model_transfer_paper_addendum.py",
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
            "Historical two-boundary synthesis of hard_v2 and hard_v3 claim boundaries.",
            ["cross_synthesis_json", "cross_synthesis_md", "cross_synthesis_tex"],
            ["hard_v2_evidence_json", "hard_v3_evidence_json", "paper_eval_status"],
            ["python scripts/export_downstream_cross_version_synthesis.py --assert-current-synthesis"],
            "Use only when discussing the earlier hard_v2/hard_v3 historical 0/85 synthesis.",
            "Do not use this as the current top-level downstream story after hard_v4 and model-transfer reports.",
        ),
        build_artifact_group(
            "G5_boundary_synthesis",
            "Boundary Synthesis",
            "Three-boundary synthesis covering hard_v2, hard_v3, and hard_v4.",
            ["boundary_synthesis_json", "boundary_synthesis_md", "boundary_synthesis_tex"],
            ["hard_v2_evidence_json", "hard_v3_evidence_json", "hard_v4_evidence_json"],
            ["python scripts/export_downstream_boundary_synthesis.py --assert-current-boundary-synthesis"],
            (
                "Use for the high-level paper boundary story: conditional positive, "
                "generalization boundary, stricter boundary, and 0/133 forced-bad evidence."
            ),
            "Do not use boundary synthesis as a substitute for the underlying suite-specific evidence packages.",
        ),
        build_artifact_group(
            "G6_paper_section",
            "Draftable Paper Section",
            "Generated evaluation-section prose tied to the frozen three-boundary synthesis.",
            ["paper_section_json", "paper_section_md", "paper_section_tex"],
            ["boundary_synthesis_json", "claim_defense_md"],
            ["python scripts/export_downstream_paper_section.py --assert-current-paper-section"],
            "Use as the starting point for writing the downstream validation subsection.",
            "Do not edit this prose into stronger claims without updating evidence and assertions.",
        ),
        build_artifact_group(
            "G7_claim_defense",
            "Claim Defense Matrix",
            "Reviewer-facing claim-by-claim evidence map and forbidden wording ledger.",
            ["claim_defense_json", "claim_defense_md", "claim_defense_tex"],
            ["boundary_synthesis_json", "paper_section_json"],
            ["python scripts/export_downstream_claim_defense_matrix.py --assert-current-claim-defense"],
            "Use during paper revision and reviewer response drafting.",
            "Do not treat reviewer-response wording as new experimental evidence.",
        ),
        build_artifact_group(
            "G8_reporting_handoff",
            "Reporting and Handoff",
            "Human-readable state tracking and cross-session recovery anchors.",
            ["paper_eval_status", "experiment_handoff", "progress_log"],
            [],
            [],
            "Use to recover the current project state and avoid repeating frozen experiments.",
            "Do not cite progress logs as primary empirical evidence when paper-facing tables exist.",
        ),
        build_artifact_group(
            "G9_hard_v4_scaffold",
            "Hard v4 Scaffold",
            "Frozen task scaffold and deterministic verifier boundary for hard_v4.",
            ["hard_v4_scaffold_json", "hard_v4_scaffold_md", "hard_v4_scaffold_tex"],
            ["hard_v4_protocol", "paper_eval_status", "experiment_handoff"],
            [
                "python scripts/build_downstream_hard_v4_tasks.py",
                "python scripts/check_downstream_hard_v4_tasks.py",
                "python scripts/export_hard_v4_scaffold_manifest.py --run-checker --assert-current-hard-v4-scaffold",
            ],
            "Use to document the frozen hard_v4 task boundary and hidden-verifier design.",
            "Do not cite scaffold mechanics as model-performance evidence.",
        ),
        build_artifact_group(
            "G10_hard_v4_evidence",
            "Hard v4 Evidence",
            "Fresh downstream boundary evidence that narrows selected-utility claims.",
            ["hard_v4_evidence_json", "hard_v4_paper_tables_md", "hard_v4_paper_tables_tex"],
            ["hard_v4_strategy_matrix_md", "hard_v4_strategy_matrix_json", "hard_v4_protocol"],
            [
                "python scripts/check_downstream_hard_v4_tasks.py",
                "python scripts/summarize_hard_v4_results.py --assert-current-hard-v4",
                "python scripts/export_hard_v4_evidence_package.py --assert-current-hard-v4",
            ],
            "Use for hard_v4 boundary claims: tree-aware saturation, strict selected underperformance, and 0/48 forced-bad transfer.",
            "Do not use hard_v4 to claim SkillAdmit-selected superiority or selected token savings.",
        ),
        build_artifact_group(
            "G11_model_transfer_evidence",
            "Model-Transfer Evidence",
            "Second-model replication evidence over the frozen hard_v3/hard_v4 matrices.",
            [
                "model_transfer_evidence_json",
                "model_transfer_evidence_md",
                "model_transfer_evidence_tex",
            ],
            [
                "model_transfer_protocol_json",
                "model_transfer_protocol_md",
                "hard_v3_evidence_json",
                "hard_v4_evidence_json",
            ],
            [
                "python scripts/export_model_transfer_evidence_package.py --assert-current-model-transfer",
            ],
            (
                "Use to report the completed mimo-v2.5 transfer matrix: 864 rows, "
                "0/108 forced-bad success, and model-sensitive selected deltas."
            ),
            "Do not use one transfer model to claim model-general selected superiority or selected token savings.",
        ),
        build_artifact_group(
            "G12_model_transfer_cross_model",
            "Model-Transfer Cross-Model Synthesis",
            "Baseline-versus-transfer synthesis over hard_v3/hard_v4 downstream evidence.",
            [
                "model_transfer_cross_model_json",
                "model_transfer_cross_model_md",
                "model_transfer_cross_model_tex",
            ],
            [
                "hard_v3_evidence_json",
                "hard_v4_evidence_json",
                "model_transfer_evidence_json",
            ],
            [
                "python scripts/export_model_transfer_cross_model_synthesis.py --assert-current-cross-model",
            ],
            (
                "Use to separate replicated findings from model-sensitive findings: "
                "forced-bad replicates across models, while hard_v4 strict selected "
                "reverses sign between baseline and transfer."
            ),
            "Do not merge model-transfer synthesis into the hard_v2/hard_v3/hard_v4 boundary aggregate.",
        ),
        build_artifact_group(
            "G13_model_transfer_addendum",
            "Model-Transfer Paper Addendum",
            "Draftable paper appendix or replication subsection for the second-model run.",
            [
                "model_transfer_addendum_json",
                "model_transfer_addendum_md",
                "model_transfer_addendum_tex",
            ],
            [
                "model_transfer_cross_model_json",
                "model_transfer_evidence_json",
                "paper_eval_status",
            ],
            [
                "python scripts/export_model_transfer_paper_addendum.py --assert-current-addendum",
            ],
            (
                "Use as optional paper text for model-transfer replication: "
                "0/216 forced-bad combined evidence, hard_v3 selected pattern "
                "replication, and hard_v4 strict selected sign reversal."
            ),
            "Do not use the addendum to strengthen the main paper claim into model-general selected superiority.",
        ),
    ]


def build_regeneration_order() -> list[dict[str, str]]:
    commands = [
        ("check_hard_v2", "python scripts/check_downstream_hard_v2_tasks.py"),
        ("check_hard_v3", "python scripts/check_downstream_hard_v3_tasks.py"),
        ("build_hard_v4", "python scripts/build_downstream_hard_v4_tasks.py"),
        ("check_hard_v4", "python scripts/check_downstream_hard_v4_tasks.py"),
        ("admission_regression", "python scripts/run_admission_regression.py"),
        ("summarize_hard_v2", "python scripts/summarize_hard_v2_results.py --assert-current-hard-v2"),
        ("export_hard_v2", "python scripts/export_hard_v2_evidence_package.py --assert-current-hard-v2"),
        ("summarize_hard_v3", "python scripts/summarize_hard_v3_results.py --assert-current-hard-v3"),
        ("export_hard_v3", "python scripts/export_hard_v3_evidence_package.py --assert-current-hard-v3"),
        (
            "export_hard_v4_scaffold",
            "python scripts/export_hard_v4_scaffold_manifest.py --run-checker --assert-current-hard-v4-scaffold",
        ),
        ("summarize_hard_v4", "python scripts/summarize_hard_v4_results.py --assert-current-hard-v4"),
        ("export_hard_v4", "python scripts/export_hard_v4_evidence_package.py --assert-current-hard-v4"),
        ("export_cross_synthesis", "python scripts/export_downstream_cross_version_synthesis.py --assert-current-synthesis"),
        ("export_boundary_synthesis", "python scripts/export_downstream_boundary_synthesis.py --assert-current-boundary-synthesis"),
        ("export_paper_section", "python scripts/export_downstream_paper_section.py --assert-current-paper-section"),
        ("export_claim_defense", "python scripts/export_downstream_claim_defense_matrix.py --assert-current-claim-defense"),
        (
            "export_model_transfer_protocol",
            "python scripts/export_model_transfer_replication_protocol.py --assert-current-protocol",
        ),
        (
            "export_model_transfer_evidence",
            "python scripts/export_model_transfer_evidence_package.py --assert-current-model-transfer",
        ),
        (
            "export_model_transfer_cross_model",
            "python scripts/export_model_transfer_cross_model_synthesis.py --assert-current-cross-model",
        ),
        (
            "export_model_transfer_addendum",
            "python scripts/export_model_transfer_paper_addendum.py --assert-current-addendum",
        ),
        ("export_artifacts_index", "python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index"),
        ("audit_paper_claim_consistency", "python scripts/audit_paper_claim_consistency.py --assert-current-audit"),
        ("audit_reporting_hygiene", "python scripts/audit_reporting_hygiene.py --assert-current-hygiene"),
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
            "table_id": "T_hard_v4",
            "paper_role": "Hard v4 boundary table.",
            "primary_artifacts": [
                display_path(ARTIFACT_PATHS["hard_v4_paper_tables_md"]),
                display_path(ARTIFACT_PATHS["hard_v4_paper_tables_tex"]),
                display_path(ARTIFACT_PATHS["hard_v4_evidence_json"]),
            ],
            "allowed_claim": "hard_v4 shows tree-aware saturation, strict selected underperformance, and 0/48 forced-bad transfer.",
            "avoid": "Do not claim hard_v4 proves selected utility, selected token savings, or bad-advice safety.",
        },
        {
            "table_id": "T_cross_version",
            "paper_role": "Legacy two-boundary synthesis table.",
            "primary_artifacts": [
                display_path(ARTIFACT_PATHS["cross_synthesis_md"]),
                display_path(ARTIFACT_PATHS["cross_synthesis_tex"]),
                display_path(ARTIFACT_PATHS["cross_synthesis_json"]),
            ],
            "allowed_claim": "Historical hard_v2/hard_v3 synthesis: hard_v2 is positive tree-aware evidence; hard_v3 is a generalization boundary; forced bad is 0/85.",
            "avoid": "Do not use the legacy 0/85 synthesis as the current main downstream result after the 0/133 boundary synthesis exists.",
        },
        {
            "table_id": "T_boundary_synthesis",
            "paper_role": "Three-boundary synthesis table.",
            "primary_artifacts": [
                display_path(ARTIFACT_PATHS["boundary_synthesis_md"]),
                display_path(ARTIFACT_PATHS["boundary_synthesis_tex"]),
                display_path(ARTIFACT_PATHS["boundary_synthesis_json"]),
            ],
            "allowed_claim": "hard_v2/hard_v3/hard_v4 together show conditional positive evidence, generalization boundary, stricter boundary, and 0/133 forced-bad evidence.",
            "avoid": "Do not use the boundary synthesis as a selected-wins leaderboard or as a substitute for evidence packages.",
        },
        {
            "table_id": "T_model_transfer",
            "paper_role": "Optional model-transfer replication table.",
            "primary_artifacts": [
                display_path(ARTIFACT_PATHS["model_transfer_evidence_md"]),
                display_path(ARTIFACT_PATHS["model_transfer_cross_model_md"]),
                display_path(ARTIFACT_PATHS["model_transfer_evidence_json"]),
                display_path(ARTIFACT_PATHS["model_transfer_cross_model_json"]),
            ],
            "allowed_claim": "mimo-v2.5 transfer replicates forced-bad negative transfer and reveals model-sensitive selected deltas.",
            "avoid": "Do not claim model-general selected superiority or selected token savings from one transfer model.",
        },
        {
            "table_id": "T_model_transfer_addendum",
            "paper_role": "Optional paper addendum text for model-transfer replication.",
            "primary_artifacts": [
                display_path(ARTIFACT_PATHS["model_transfer_addendum_md"]),
                display_path(ARTIFACT_PATHS["model_transfer_addendum_tex"]),
                display_path(ARTIFACT_PATHS["model_transfer_addendum_json"]),
            ],
            "allowed_claim": "Use as draft text for replicated forced-bad negative transfer and model-sensitive selected behavior.",
            "avoid": "Do not paste the addendum as a stronger main result than the underlying cross-model synthesis supports.",
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
        "hard_v4_evidence_package": [display_path(ARTIFACT_PATHS["hard_v4_evidence_json"])],
        "downstream_cross_version_synthesis": [display_path(ARTIFACT_PATHS["cross_synthesis_json"])],
        "downstream_boundary_synthesis": [display_path(ARTIFACT_PATHS["boundary_synthesis_json"])],
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
            "reason": "hard_v4 task files define a frozen evaluation boundary; do not tune prompts or strategies from inspected hard_v4 failures.",
        },
        {
            "artifact_pattern": "docs/progress_log.md",
            "reason": "Progress log is a handoff ledger, not a primary empirical table.",
        },
        {
            "artifact_pattern": "benchmark/downstream/reports/paper_claim_consistency_audit.*",
            "reason": "Consistency audit reports are reporting-hygiene checks, not additional downstream evidence.",
        },
        {
            "artifact_pattern": "benchmark/downstream/reports/model_transfer_replication_protocol.*",
            "reason": "Model-transfer protocol reports are pre-run registration artifacts, not model-performance evidence.",
        },
    ]


def build_index(data: dict[str, dict[str, Any]]) -> dict[str, Any]:
    hard_v2 = data["hard_v2_evidence_package"]
    hard_v3 = data["hard_v3_evidence_package"]
    hard_v4 = data["hard_v4_evidence_package"]
    synthesis = data["downstream_cross_version_synthesis"]
    boundary = data["downstream_boundary_synthesis"]
    paper_section = data["downstream_paper_eval_section"]
    claim_defense = data["downstream_claim_defense_matrix"]
    transfer_evidence = data["model_transfer_evidence_package"]
    transfer_cross_model = data["model_transfer_cross_model_synthesis"]
    transfer_addendum = data["model_transfer_paper_addendum"]

    v2_tree_no = find_row(hard_v2, "llm_downstream_hard_v2_tree_25x2", "no_experience")
    v2_tree_selected = find_row(hard_v2, "llm_downstream_hard_v2_tree_25x2", "skilladmit_selected")
    v3_tree_no = find_row(hard_v3, "llm_downstream_hard_v3_tree_core_30x2", "no_experience")
    v3_tree_selected = find_row(hard_v3, "llm_downstream_hard_v3_tree_core_30x2", "skilladmit_selected")
    v3_strict_pre = find_row(
        hard_v3,
        "llm_downstream_hard_v3_strict_30x8",
        "skilladmit_selected_with_precondition_only",
    )
    v4_tree_no = find_row(hard_v4, "llm_downstream_hard_v4_tree_24x8", "no_experience")
    v4_tree_selected = find_row(hard_v4, "llm_downstream_hard_v4_tree_24x8", "skilladmit_selected")
    v4_strict_no = find_row(hard_v4, "llm_downstream_hard_v4_strict_24x8", "no_experience")
    v4_strict_selected = find_row(hard_v4, "llm_downstream_hard_v4_strict_24x8", "skilladmit_selected")
    v4_derived = hard_v4["derived_comparisons"]
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
            "hard_v4_tree_selected": v4_tree_selected["success"],
            "hard_v4_tree_no_experience": v4_tree_no["success"],
            "hard_v4_strict_selected": v4_strict_selected["success"],
            "hard_v4_strict_no_experience": v4_strict_no["success"],
            "hard_v4_forced_bad_total_successes": v4_derived["forced_bad_total_successes"],
            "hard_v4_forced_bad_total_tasks": v4_derived["forced_bad_total_tasks"],
            "hard_v4_forced_bad_total_public_passed_hidden_failed": v4_derived[
                "forced_bad_total_public_passed_hidden_failed"
            ],
            "boundary_forced_bad_total_success": boundary["derived_claims"]["forced_bad_total_success"],
            "boundary_forced_bad_total_tasks": boundary["derived_claims"]["forced_bad_total_tasks"],
            "boundary_forced_bad_total_public_passed_hidden_failed": boundary["derived_claims"][
                "forced_bad_total_public_passed_hidden_failed"
            ],
            "boundary_selected_superiority_consistent": boundary["derived_claims"][
                "selected_superiority_consistent"
            ],
            "boundary_selected_token_savings_consistent": boundary["derived_claims"][
                "selected_token_savings_consistent"
            ],
            "forced_bad_total_successes": derived["forced_bad_total_successes"],
            "forced_bad_total_tasks": derived["forced_bad_total_tasks"],
            "forced_bad_total_public_passed_hidden_failed": derived[
                "forced_bad_total_public_passed_hidden_failed"
            ],
            "selected_superiority_consistent": derived["selected_superiority_consistent"],
            "selected_token_savings_supported": derived["selected_token_savings_supported"],
            "model_transfer_model": transfer_evidence["transfer_model"],
            "model_transfer_forced_bad_total_success": transfer_evidence["forced_bad_summary"][
                "total_success"
            ],
            "model_transfer_forced_bad_total_tasks": transfer_evidence["forced_bad_summary"][
                "total_tasks"
            ],
            "model_transfer_forced_bad_total_public_passed_hidden_failed": transfer_evidence[
                "forced_bad_summary"
            ]["total_public_passed_hidden_failed"],
            "model_transfer_selected_superiority_consistent": transfer_evidence["derived_claims"][
                "selected_superiority_consistent"
            ],
            "cross_model_forced_bad_combined_success": transfer_cross_model["derived_claims"][
                "forced_bad_combined_success"
            ],
            "cross_model_forced_bad_public_passed_hidden_failed": transfer_cross_model[
                "derived_claims"
            ]["forced_bad_combined_public_passed_hidden_failed"],
            "cross_model_selected_superiority_model_general": transfer_cross_model[
                "derived_claims"
            ]["selected_superiority_model_general"],
            "cross_model_hard_v4_strict_selected_delta_reversed": transfer_cross_model[
                "derived_claims"
            ]["hard_v4_strict_selected_delta_reversed"],
            "model_transfer_addendum_result_paragraphs": len(transfer_addendum["result_paragraphs"]),
            "model_transfer_addendum_forced_bad_combined_success": transfer_addendum[
                "derived_cross_model"
            ]["forced_bad_combined_success"],
            "model_transfer_addendum_hard_v4_strict_reversed": transfer_addendum[
                "derived_cross_model"
            ]["hard_v4_strict_selected_delta_reversed"],
            "claim_count": claim_defense["claim_count"],
            "paper_section_result_paragraphs": len(paper_section["results"]),
        },
        "artifact_groups": build_artifact_groups(),
        "regeneration_order": build_regeneration_order(),
        "table_index": build_table_index(),
        "claim_to_artifact_map": build_claim_to_artifact_map(claim_defense),
        "do_not_cite_as_primary": build_do_not_cite_as_primary(),
        "next_experimental_boundary": {
            "recommended": "boundary-synthesis-driven paper revision, model-transfer write-up, or a predeclared hard_v5 boundary.",
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
        "hard_v4_tree_selected": "24/24",
        "hard_v4_tree_no_experience": "24/24",
        "hard_v4_strict_selected": "22/24",
        "hard_v4_strict_no_experience": "24/24",
        "hard_v4_forced_bad_total_successes": 0,
        "hard_v4_forced_bad_total_tasks": 48,
        "hard_v4_forced_bad_total_public_passed_hidden_failed": 48,
        "boundary_forced_bad_total_success": "0/133",
        "boundary_forced_bad_total_tasks": 133,
        "boundary_forced_bad_total_public_passed_hidden_failed": 133,
        "boundary_selected_superiority_consistent": False,
        "boundary_selected_token_savings_consistent": False,
        "forced_bad_total_successes": 0,
        "forced_bad_total_tasks": 85,
        "forced_bad_total_public_passed_hidden_failed": 85,
        "selected_superiority_consistent": False,
        "selected_token_savings_supported": False,
        "model_transfer_model": "mimo-v2.5",
        "model_transfer_forced_bad_total_success": "0/108",
        "model_transfer_forced_bad_total_tasks": 108,
        "model_transfer_forced_bad_total_public_passed_hidden_failed": 108,
        "model_transfer_selected_superiority_consistent": False,
        "cross_model_forced_bad_combined_success": "0/216",
        "cross_model_forced_bad_public_passed_hidden_failed": 216,
        "cross_model_selected_superiority_model_general": False,
        "cross_model_hard_v4_strict_selected_delta_reversed": True,
        "model_transfer_addendum_result_paragraphs": 5,
        "model_transfer_addendum_forced_bad_combined_success": "0/216",
        "model_transfer_addendum_hard_v4_strict_reversed": True,
        "claim_count": 10,
        "paper_section_result_paragraphs": 6,
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
    if len(index["artifact_groups"]) != 13:
        raise AssertionError("artifact group count changed")
    if len(index["table_index"]) != 9:
        raise AssertionError("table index count changed")
    if len(index["claim_to_artifact_map"]) != 10:
        raise AssertionError("claim map count changed")

    rendered = render_markdown(index)
    required = [
        "25/25",
        "23/25",
        "29/30",
        "22/24",
        "0/85",
        "0/48",
        "0/133",
        "0/108",
        "0/216",
        "Do not tune hard_v2/hard_v3/hard_v4 prompts",
        "hard_v4_scaffold_manifest.json",
        "hard_v4_evidence_package.json",
        "downstream_boundary_synthesis.json",
        "model_transfer_evidence_package.json",
        "model_transfer_cross_model_synthesis.json",
        "model_transfer_paper_addendum.json",
        "audit_paper_claim_consistency.py",
        "audit_reporting_hygiene.py",
        "export_model_transfer_replication_protocol.py",
        "export_model_transfer_evidence_package.py",
        "export_model_transfer_cross_model_synthesis.py",
        "export_model_transfer_paper_addendum.py",
        "boundary-synthesis-driven paper revision",
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
    print(f"hard_v4_forced_bad_total_tasks: {index['key_current_facts']['hard_v4_forced_bad_total_tasks']}")
    print(f"boundary_forced_bad_total_tasks: {index['key_current_facts']['boundary_forced_bad_total_tasks']}")
    print(f"wrote_json: {display_path(args.json_out)}")
    print(f"wrote_md: {display_path(args.md_out)}")
    print(f"wrote_tex: {display_path(args.tex_out)}")


if __name__ == "__main__":
    main()
