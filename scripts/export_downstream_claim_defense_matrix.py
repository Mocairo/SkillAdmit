#!/usr/bin/env python3
"""Export a downstream claim-defense matrix for SkillAdmit.

What this file does:
  Reads the paper-facing hard_v2/hard_v3/hard_v4 evidence packages, the
  three-boundary synthesis, and the generated downstream paper section. It exports a
  claim-by-claim defense matrix: what can be claimed, what evidence supports
  it, what wording is allowed, what wording is forbidden, and how to answer a
  likely reviewer objection.

Why it is needed:
  SkillAdmit's current downstream result is conditional. hard_v2 supports
  tree-aware selected utility, hard_v3 limits universal selected-superiority
  claims, hard_v4 adds a stricter boundary, and forced bad artifacts provide
  the strongest negative-transfer signal. A defense matrix makes these
  boundaries explicit so a paper draft cannot accidentally turn conditional
  evidence into an absolute claim.

Inputs:
  benchmark/downstream/reports/hard_v2_evidence_package.json
  benchmark/downstream/reports/hard_v3_evidence_package.json
  benchmark/downstream/reports/hard_v4_evidence_package.json
  benchmark/downstream/reports/downstream_boundary_synthesis.json
  benchmark/downstream/reports/downstream_paper_eval_section.json

Outputs:
  benchmark/downstream/reports/downstream_claim_defense_matrix.json
  benchmark/downstream/reports/downstream_claim_defense_matrix.md
  benchmark/downstream/reports/downstream_claim_defense_matrix.tex

Who runs it:
  Researchers or Codex sessions before drafting, revising, or defending the
  SkillAdmit downstream-validation section.
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

DEFAULT_HARD_V2 = REPORT_DIR / "hard_v2_evidence_package.json"
DEFAULT_HARD_V3 = REPORT_DIR / "hard_v3_evidence_package.json"
DEFAULT_HARD_V4 = REPORT_DIR / "hard_v4_evidence_package.json"
DEFAULT_SYNTHESIS = REPORT_DIR / "downstream_boundary_synthesis.json"
DEFAULT_PAPER_SECTION = REPORT_DIR / "downstream_paper_eval_section.json"
DEFAULT_JSON = REPORT_DIR / "downstream_claim_defense_matrix.json"
DEFAULT_MD = REPORT_DIR / "downstream_claim_defense_matrix.md"
DEFAULT_TEX = REPORT_DIR / "downstream_claim_defense_matrix.tex"


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> Path:
    resolved = resolve(path)
    try:
        return resolved.relative_to(ROOT)
    except ValueError:
        return resolved


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def primary_index(package: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (row["run_name"], row["strategy"]): row
        for row in package["primary_strategy_table"]
    }


def cross_index(synthesis: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, Any]]:
    return {
        (row["suite"], row["run_name"], row["strategy"]): row
        for row in synthesis["primary_strategy_table"]
    }


def get_primary(package: dict[str, Any], run_name: str, strategy: str) -> dict[str, Any]:
    rows = primary_index(package)
    key = (run_name, strategy)
    if key not in rows:
        raise KeyError(f"Missing primary evidence row: {run_name}/{strategy}")
    return rows[key]


def get_cross(synthesis: dict[str, Any], suite: str, run_name: str, strategy: str) -> dict[str, Any]:
    rows = cross_index(synthesis)
    key = (suite, run_name, strategy)
    if key not in rows:
        raise KeyError(f"Missing cross-version row: {suite}/{run_name}/{strategy}")
    return rows[key]


def get_stability(hard_v2: dict[str, Any], group: str) -> dict[str, Any]:
    groups = {row["group"]: row for row in hard_v2["stability_table"]}
    if group not in groups:
        raise KeyError(f"Missing hard_v2 stability group: {group}")
    return groups[group]


def success(row: dict[str, Any]) -> str:
    return row["success"]


def evidence_row(
    source: str,
    row: dict[str, Any],
    note: str,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    fields = fields or ["success", "negative_transfer", "public_passed_hidden_failed", "total_tokens"]
    data = {
        "source": source,
        "setting": row.get("setting"),
        "run_name": row["run_name"],
        "strategy": row["strategy"],
        "display_strategy": row["display_strategy"],
        "note": note,
    }
    for field in fields:
        if field in row:
            data[field] = row[field]
    return data


def claim(
    claim_id: str,
    status: str,
    paper_claim: str,
    evidence_summary: str,
    evidence: list[dict[str, Any]],
    allowed_wording: list[str],
    forbidden_wording: list[str],
    required_qualifiers: list[str],
    reviewer_risk: str,
    reviewer_response: str,
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "status": status,
        "paper_claim": paper_claim,
        "evidence_summary": evidence_summary,
        "evidence": evidence,
        "allowed_wording": allowed_wording,
        "forbidden_wording": forbidden_wording,
        "required_qualifiers": required_qualifiers,
        "reviewer_risk": reviewer_risk,
        "reviewer_response": reviewer_response,
    }


def build_claims(
    hard_v2: dict[str, Any],
    hard_v3: dict[str, Any],
    hard_v4: dict[str, Any],
    synthesis: dict[str, Any],
) -> list[dict[str, Any]]:
    v2_tree_no = get_primary(hard_v2, "llm_downstream_hard_v2_tree_25x2", "no_experience")
    v2_tree_selected = get_primary(hard_v2, "llm_downstream_hard_v2_tree_25x2", "skilladmit_selected")
    v2_tree_pre = get_primary(
        hard_v2,
        "llm_downstream_hard_v2_selected_precondition_25",
        "skilladmit_selected_with_precondition_context",
    )
    v2_strict_no = get_primary(hard_v2, "llm_downstream_hard_v2_full_25x6", "no_experience")
    v2_strict_selected = get_primary(hard_v2, "llm_downstream_hard_v2_full_25x6", "skilladmit_selected")
    v2_strict_raw = get_primary(hard_v2, "llm_downstream_hard_v2_full_25x6", "raw_memory")
    v2_strict_all = get_primary(hard_v2, "llm_downstream_hard_v2_full_25x6", "distilled_skills_all")
    v2_bad_rule = get_primary(hard_v2, "llm_downstream_hard_v2_full_25x6", "bad_dependency_rule")
    v2_pre_only = get_primary(
        hard_v2,
        "llm_downstream_hard_v2_precondition_only_25",
        "skilladmit_selected_with_precondition_only",
    )
    v2_forced = get_primary(hard_v2, "llm_downstream_hard_v2_forced_bad_25", "forced_bad_artifact")
    v2_selected_stability = get_stability(hard_v2, "tree_aware_skilladmit_selected")
    v2_pre_stability = get_stability(hard_v2, "strict_precondition_only")

    v3_tree_no = get_primary(hard_v3, "llm_downstream_hard_v3_tree_core_30x2", "no_experience")
    v3_tree_selected = get_primary(hard_v3, "llm_downstream_hard_v3_tree_core_30x2", "skilladmit_selected")
    v3_tree_pre = get_primary(
        hard_v3,
        "llm_downstream_hard_v3_tree_core_30x2",
        "skilladmit_selected_with_precondition_context",
    )
    v3_tree_raw = get_primary(hard_v3, "llm_downstream_hard_v3_tree_core_30x2", "raw_memory")
    v3_tree_all = get_primary(hard_v3, "llm_downstream_hard_v3_tree_core_30x2", "distilled_skills_all")
    v3_tree_bad_rule = get_primary(hard_v3, "llm_downstream_hard_v3_tree_core_30x2", "bad_dependency_rule")
    v3_tree_forced = get_primary(hard_v3, "llm_downstream_hard_v3_tree_core_30x2", "forced_bad_artifact")
    v3_strict_no = get_primary(hard_v3, "llm_downstream_hard_v3_strict_30x8", "no_experience")
    v3_strict_selected = get_primary(hard_v3, "llm_downstream_hard_v3_strict_30x8", "skilladmit_selected")
    v3_strict_pre = get_primary(
        hard_v3,
        "llm_downstream_hard_v3_strict_30x8",
        "skilladmit_selected_with_precondition_only",
    )
    v3_strict_raw = get_primary(hard_v3, "llm_downstream_hard_v3_strict_30x8", "raw_memory")
    v3_strict_all = get_primary(hard_v3, "llm_downstream_hard_v3_strict_30x8", "distilled_skills_all")
    v3_strict_bad_rule = get_primary(hard_v3, "llm_downstream_hard_v3_strict_30x8", "bad_dependency_rule")
    v3_strict_forced = get_primary(hard_v3, "llm_downstream_hard_v3_strict_30x8", "forced_bad_artifact")

    v4_tree_no = get_primary(hard_v4, "llm_downstream_hard_v4_tree_24x8", "no_experience")
    v4_tree_selected = get_primary(hard_v4, "llm_downstream_hard_v4_tree_24x8", "skilladmit_selected")
    v4_tree_pre = get_primary(
        hard_v4,
        "llm_downstream_hard_v4_tree_24x8",
        "skilladmit_selected_with_precondition_context",
    )
    v4_tree_raw = get_primary(hard_v4, "llm_downstream_hard_v4_tree_24x8", "raw_memory")
    v4_tree_all = get_primary(hard_v4, "llm_downstream_hard_v4_tree_24x8", "distilled_skills_all")
    v4_tree_bad_rule = get_primary(hard_v4, "llm_downstream_hard_v4_tree_24x8", "bad_dependency_rule")
    v4_tree_forced = get_primary(hard_v4, "llm_downstream_hard_v4_tree_24x8", "forced_bad_artifact")
    v4_strict_no = get_primary(hard_v4, "llm_downstream_hard_v4_strict_24x8", "no_experience")
    v4_strict_selected = get_primary(hard_v4, "llm_downstream_hard_v4_strict_24x8", "skilladmit_selected")
    v4_strict_pre = get_primary(
        hard_v4,
        "llm_downstream_hard_v4_strict_24x8",
        "skilladmit_selected_with_precondition_only",
    )
    v4_strict_raw = get_primary(hard_v4, "llm_downstream_hard_v4_strict_24x8", "raw_memory")
    v4_strict_all = get_primary(hard_v4, "llm_downstream_hard_v4_strict_24x8", "distilled_skills_all")
    v4_strict_bad_rule = get_primary(hard_v4, "llm_downstream_hard_v4_strict_24x8", "bad_dependency_rule")
    v4_strict_forced = get_primary(hard_v4, "llm_downstream_hard_v4_strict_24x8", "forced_bad_artifact")

    derived = synthesis["derived_claims"]
    forced_bad = derived["forced_bad_total_success"]
    forced_public_hidden = derived["forced_bad_total_public_passed_hidden_failed"]
    forced_total_tasks = derived["forced_bad_total_tasks"]
    selected_token_deltas = derived["selected_token_delta_values"]

    claims = [
        claim(
            "C1_downstream_hidden_verifier_is_required",
            "supported_design_claim",
            "SkillAdmit should be evaluated with downstream hidden-verifier tasks, not admission labels alone.",
            (
                "hard_v2, hard_v3, and hard_v4 use hidden verifiers, and forced bad artifacts create "
                f"{forced_public_hidden} public-pass/hidden-fail cases across {forced_total_tasks} tasks."
            ),
            [
                evidence_row("hard_v2_evidence_package", v2_forced, "forced harmful artifact control"),
                evidence_row("hard_v3_evidence_package", v3_tree_forced, "tree-aware forced harmful artifact control"),
                evidence_row("hard_v3_evidence_package", v3_strict_forced, "strict visible-file forced harmful artifact control"),
                evidence_row("hard_v4_evidence_package", v4_tree_forced, "tree-aware hard_v4 forced harmful artifact control"),
                evidence_row("hard_v4_evidence_package", v4_strict_forced, "strict hard_v4 forced harmful artifact control"),
            ],
            [
                "We complement admission accuracy with downstream hidden-verifier validation.",
                "Public tests are insufficient for evaluating admitted experience.",
            ],
            [
                "Admission accuracy alone proves downstream utility.",
                "Passing public tests is enough to validate an admitted artifact.",
            ],
            [
                "Say downstream evidence is complementary and sharper for utility, not a replacement for all admission metrics.",
                "Mention hidden verification and public-pass/hidden-fail cases.",
            ],
            "A reviewer may ask why admission accuracy is not enough.",
            (
                "Admission labels test classification, while downstream tasks test whether admitted artifacts change future "
                "agent behavior under hidden verification. The forced bad-artifact controls show public tests can be fooled."
            ),
        ),
        claim(
            "C2_hard_v2_tree_selected_positive",
            "supported_conditional_claim",
            "In hard_v2 tree-aware downstream validation, SkillAdmit-selected context improves success over no_experience.",
            (
                f"hard_v2 tree-aware selected is {success(v2_tree_selected)} versus "
                f"{success(v2_tree_no)} for no_experience; selected was replicated with "
                f"success values {v2_selected_stability['success_values']}."
            ),
            [
                evidence_row("hard_v2_evidence_package", v2_tree_selected, "tree-aware selected"),
                evidence_row("hard_v2_evidence_package", v2_tree_no, "tree-aware no_experience"),
                {
                    "source": "hard_v2_evidence_package",
                    "group": "tree_aware_skilladmit_selected",
                    "success_values": v2_selected_stability["success_values"],
                    "token_values": v2_selected_stability["token_values"],
                    "note": "replication stability group",
                },
            ],
            [
                "On hard_v2 with repo-tree context, SkillAdmit-selected reached 25/25 versus 23/25 for no_experience.",
                "hard_v2 provides positive evidence for tree-aware selected utility.",
            ],
            [
                "SkillAdmit-selected universally beats no_experience.",
                "The hard_v2 result proves selected is best under every executor setting.",
            ],
            [
                "Keep the tree-aware executor qualifier.",
                "Report strict visible-file hard_v2 separately.",
            ],
            "A reviewer may point to strict visible-file hard_v2 where selected is worse.",
            (
                "That objection is correct and is part of the claim boundary. The positive claim is limited to "
                "the tree-aware coding-agent setting, while strict visible-file is reported as a separate boundary."
            ),
        ),
        claim(
            "C3_hard_v2_strict_visible_boundary",
            "boundary_claim",
            "Strict visible-file hard_v2 does not support a SkillAdmit-selected win.",
            (
                f"In strict visible-file hard_v2, selected is {success(v2_strict_selected)}, "
                f"no_experience is {success(v2_strict_no)}, and all distilled skills are {success(v2_strict_all)}."
            ),
            [
                evidence_row("hard_v2_evidence_package", v2_strict_selected, "strict visible-file selected"),
                evidence_row("hard_v2_evidence_package", v2_strict_no, "strict visible-file no_experience"),
                evidence_row("hard_v2_evidence_package", v2_strict_all, "strict visible-file all distilled skills"),
            ],
            [
                "Strict visible-file hard_v2 is a boundary where selected-only context is insufficient.",
                "All-skills is strongest in strict visible-file hard_v2, but it is more token-expensive.",
            ],
            [
                "SkillAdmit-selected wins hard_v2 overall.",
                "Selection is always better than providing all skills.",
            ],
            [
                "Separate strict visible-file and tree-aware settings.",
                "Do not collapse hard_v2 into one leaderboard.",
            ],
            "A reviewer may accuse the paper of cherry-picking tree-aware hard_v2.",
            (
                "The defense is to report strict visible-file explicitly as a negative boundary. The paper should say "
                "tree-aware selected helps, not that selected wins every hard_v2 setting."
            ),
        ),
        claim(
            "C4_hard_v3_generalization_boundary",
            "boundary_claim",
            "hard_v3 and hard_v4 do not support universal SkillAdmit-selected superiority.",
            (
                f"In hard_v3 tree-aware, selected and no_experience are both {success(v3_tree_selected)}. "
                f"In strict visible-file hard_v3, selected is {success(v3_strict_selected)} while "
                f"precondition-only and raw memory are {success(v3_strict_pre)}. "
                f"In hard_v4 strict visible-file, selected is {success(v4_strict_selected)} while "
                f"no_experience is {success(v4_strict_no)}."
            ),
            [
                evidence_row("hard_v3_evidence_package", v3_tree_selected, "tree-aware selected"),
                evidence_row("hard_v3_evidence_package", v3_tree_no, "tree-aware no_experience"),
                evidence_row("hard_v3_evidence_package", v3_strict_selected, "strict visible-file selected"),
                evidence_row("hard_v3_evidence_package", v3_strict_pre, "strict precondition-only"),
                evidence_row("hard_v3_evidence_package", v3_strict_raw, "strict raw memory"),
                evidence_row("hard_v4_evidence_package", v4_tree_selected, "hard_v4 tree-aware selected"),
                evidence_row("hard_v4_evidence_package", v4_tree_no, "hard_v4 tree-aware no_experience"),
                evidence_row("hard_v4_evidence_package", v4_strict_selected, "hard_v4 strict selected"),
                evidence_row("hard_v4_evidence_package", v4_strict_no, "hard_v4 strict no_experience"),
            ],
            [
                "hard_v3 and hard_v4 are generalization boundaries for the selected-superiority claim.",
                "SkillAdmit-selected can help in some settings, but the current evidence does not make it universally best.",
            ],
            [
                "hard_v3 proves SkillAdmit-selected superiority.",
                "hard_v4 proves SkillAdmit-selected superiority.",
                "SkillAdmit-selected is the best hard_v3 condition.",
            ],
            [
                "State that hard_v3 and hard_v4 weaken the universal claim.",
                "Mention tree-aware ties, strict non-best results, and hard_v4 strict underperformance.",
            ],
            "A reviewer may ask why hard_v3 or hard_v4 is included if selected does not win.",
            (
                "It is included exactly as a clean downstream boundary. A credible evaluation should report where "
                "the mechanism generalizes and where it does not."
            ),
        ),
        claim(
            "C5_repo_tree_and_preconditions_are_context_variables",
            "conditional_claim",
            "Repository tree and precondition context are important variables, but neither is universally sufficient or necessary.",
            (
                f"hard_v2 strict precondition-only is unstable with success values {v2_pre_stability['success_values']}; "
                f"hard_v3 strict precondition-only reaches {success(v3_strict_pre)}, while "
                f"hard_v4 strict precondition-only reaches {success(v4_strict_pre)} and still trails "
                f"no_experience at {success(v4_strict_no)}."
            ),
            [
                evidence_row("hard_v2_evidence_package", v2_tree_selected, "hard_v2 tree-aware selected"),
                evidence_row("hard_v2_evidence_package", v2_pre_only, "hard_v2 strict precondition-only"),
                {
                    "source": "hard_v2_evidence_package",
                    "group": "strict_precondition_only",
                    "success_values": v2_pre_stability["success_values"],
                    "token_values": v2_pre_stability["token_values"],
                    "note": "precondition-only stability group",
                },
                evidence_row("hard_v3_evidence_package", v3_strict_pre, "hard_v3 strict precondition-only"),
                evidence_row("hard_v4_evidence_package", v4_tree_pre, "hard_v4 tree-aware selected + preconditions"),
                evidence_row("hard_v4_evidence_package", v4_strict_pre, "hard_v4 strict precondition-only"),
                {
                    "source": "downstream_boundary_synthesis",
                    "context_success_delta_values": derived[
                        "strict_precondition_only_success_delta_vs_no_experience_values"
                    ],
                    "note": "precondition-only is suite-dependent versus no_experience",
                },
            ],
            [
                "Repo tree and preconditions should be treated as task-context variables.",
                "hard_v2 suggests tree-aware context can be more reliable than precondition text alone; hard_v3 shows precondition-only can be sufficient on another suite; hard_v4 shows it can still trail no_experience.",
            ],
            [
                "Precondition-only replaces repository tree.",
                "Repository tree is always necessary.",
            ],
            [
                "Report suite-specific differences.",
                "Do not turn hard_v2, hard_v3, or hard_v4 alone into a universal context rule.",
            ],
            "A reviewer may ask whether the mechanism is really SkillAdmit or just extra context.",
            (
                "The matrix separates artifact selection from execution context. Current evidence supports conditional "
                "utility, while repo tree and preconditions remain explicit variables rather than hidden assumptions."
            ),
        ),
        claim(
            "C6_forced_bad_artifacts_negative_transfer",
            "strong_supported_claim",
            "When harmful admitted artifacts are forced into execution, they cause systematic negative transfer.",
            (
                f"Forced bad artifacts are {forced_bad} success across hard_v2, hard_v3, and hard_v4, with "
                f"{forced_public_hidden} public-pass/hidden-fail cases."
            ),
            [
                evidence_row("hard_v2_evidence_package", v2_forced, "hard_v2 forced bad artifact"),
                evidence_row("hard_v3_evidence_package", v3_tree_forced, "hard_v3 tree-aware forced bad artifact"),
                evidence_row("hard_v3_evidence_package", v3_strict_forced, "hard_v3 strict forced bad artifact"),
                evidence_row("hard_v4_evidence_package", v4_tree_forced, "hard_v4 tree-aware forced bad artifact"),
                evidence_row("hard_v4_evidence_package", v4_strict_forced, "hard_v4 strict forced bad artifact"),
                {
                    "source": "downstream_boundary_synthesis",
                    "forced_bad_total_tasks": forced_total_tasks,
                    "forced_bad_total_success": forced_bad,
                    "forced_bad_total_public_passed_hidden_failed": forced_public_hidden,
                    "note": "three-boundary forced bad aggregate",
                },
            ],
            [
                "Forced harmful artifacts produce systematic negative transfer: 0/133 success with 133 public-pass/hidden-fail cases.",
                "The negative-transfer control supports the need for admission hygiene.",
            ],
            [
                "SkillAdmit proves all admitted artifacts are safe.",
                "Bad experience is harmless if public tests pass.",
            ],
            [
                "Say harmful artifacts damage behavior when executed.",
                "Use forced_bad_artifact as the clean negative-transfer control.",
            ],
            "A reviewer may ask whether negative transfer is deterministic or model-specific.",
            (
                "The forced artifact is a controlled downstream condition: it demonstrates the behavioral hazard "
                "of executing known-bad experience. It now holds across hard_v2, hard_v3, and hard_v4."
            ),
        ),
        claim(
            "C7_bad_dependency_rule_is_not_safe",
            "caveat_claim",
            "Ordinary bad_dependency_rule success does not prove bad advice is safe, because adherence is low on hard_v3 and hard_v4.",
            (
                f"hard_v3 bad_dependency_rule succeeds at {success(v3_tree_bad_rule)} and "
                f"{success(v3_strict_bad_rule)}, but artifact adherence is "
                f"{v3_tree_bad_rule['artifact_adherence']}/{v3_tree_bad_rule['tasks']} and "
                f"{v3_strict_bad_rule['artifact_adherence']}/{v3_strict_bad_rule['tasks']}. "
                f"hard_v4 adherence is {v4_tree_bad_rule['artifact_adherence']}/{v4_tree_bad_rule['tasks']} "
                f"and {v4_strict_bad_rule['artifact_adherence']}/{v4_strict_bad_rule['tasks']}."
            ),
            [
                evidence_row(
                    "hard_v3_evidence_package",
                    v3_tree_bad_rule,
                    "tree-aware bad_dependency_rule with low adherence",
                    ["success", "artifact_adherence", "tasks", "total_tokens"],
                ),
                evidence_row(
                    "hard_v3_evidence_package",
                    v3_strict_bad_rule,
                    "strict bad_dependency_rule with low adherence",
                    ["success", "artifact_adherence", "tasks", "total_tokens"],
                ),
                evidence_row("hard_v2_evidence_package", v2_bad_rule, "hard_v2 strict bad_dependency_rule"),
                evidence_row("hard_v3_evidence_package", v3_tree_forced, "forced control remains harmful"),
                evidence_row(
                    "hard_v4_evidence_package",
                    v4_tree_bad_rule,
                    "hard_v4 tree-aware bad_dependency_rule with low adherence",
                    ["success", "artifact_adherence", "tasks", "total_tokens"],
                ),
                evidence_row(
                    "hard_v4_evidence_package",
                    v4_strict_bad_rule,
                    "hard_v4 strict bad_dependency_rule with low adherence",
                    ["success", "artifact_adherence", "tasks", "total_tokens"],
                ),
                evidence_row("hard_v4_evidence_package", v4_tree_forced, "hard_v4 forced control remains harmful"),
            ],
            [
                "The model often succeeds by ignoring harmful advice.",
                "Use forced_bad_artifact, not ordinary bad_dependency_rule success, as negative-transfer evidence.",
            ],
            [
                "Bad dependency advice is safe.",
                "The model can always ignore harmful experience.",
            ],
            [
                "Mention artifact adherence when discussing bad_dependency_rule.",
                "Separate ignored bad advice from forced executed bad artifacts.",
            ],
            "A reviewer may argue that bad_dependency_rule success weakens the negative-transfer story.",
            (
                "It does not: low adherence means the condition often did not execute the bad advice. The forced "
                "condition answers the causal question and fails 0/133."
            ),
        ),
        claim(
            "C8_raw_memory_is_a_serious_baseline_not_a_policy",
            "boundary_claim",
            "Raw memory is a serious downstream baseline, but current evidence does not make it a safe admission policy.",
            (
                f"Raw memory is {success(v2_strict_raw)} in hard_v2 strict visible-file, but "
                f"{success(v3_tree_raw)} and {success(v3_strict_raw)} in hard_v3, and "
                f"{success(v4_tree_raw)} / {success(v4_strict_raw)} in hard_v4."
            ),
            [
                evidence_row("hard_v2_evidence_package", v2_strict_raw, "hard_v2 strict raw memory"),
                evidence_row("hard_v3_evidence_package", v3_tree_raw, "hard_v3 tree-aware raw memory"),
                evidence_row("hard_v3_evidence_package", v3_strict_raw, "hard_v3 strict raw memory"),
                evidence_row("hard_v4_evidence_package", v4_tree_raw, "hard_v4 tree-aware raw memory"),
                evidence_row("hard_v4_evidence_package", v4_strict_raw, "hard_v4 strict raw memory"),
            ],
            [
                "Raw memory must be reported as a serious comparison condition.",
                "hard_v3 raw-memory success is a baseline result, not an admission-policy proof.",
            ],
            [
                "Raw memory is safe because it reaches 30/30 on hard_v3.",
                "SkillAdmit is unnecessary because raw memory wins one suite.",
            ],
            [
                "Discuss memory cost, specificity, and harmful-memory risk before making policy claims.",
                "Keep raw memory as a baseline unless a separate policy evaluation is run.",
            ],
            "A reviewer may ask why SkillAdmit matters if raw memory reaches 30/30 on hard_v3.",
            (
                "The honest answer is that hard_v3 makes raw memory a strong baseline. It does not settle admission "
                "policy because it omits cost, specificity, and harmful-memory controls."
            ),
        ),
        claim(
            "C9_selected_token_savings_not_supported",
            "not_supported_claim",
            "The current three-boundary evidence does not support SkillAdmit-selected token savings.",
            (
                "Selected token deltas versus no_experience are mixed across the six hard_v2/hard_v3/hard_v4 "
                f"comparisons: hard_v2 tree {selected_token_deltas['hard_v2_tree-aware_selected_token_delta_vs_no_experience']:+d}, "
                f"hard_v2 strict {selected_token_deltas['hard_v2_strict_visible_selected_token_delta_vs_no_experience']:+d}, "
                f"hard_v3 tree {selected_token_deltas['hard_v3_tree-aware_selected_token_delta_vs_no_experience']:+d}, "
                f"hard_v3 strict {selected_token_deltas['hard_v3_strict_visible_selected_token_delta_vs_no_experience']:+d}, "
                f"hard_v4 tree {selected_token_deltas['hard_v4_tree-aware_selected_token_delta_vs_no_experience']:+d}, and "
                f"hard_v4 strict {selected_token_deltas['hard_v4_strict_visible_selected_token_delta_vs_no_experience']:+d}."
            ),
            [
                {
                    "source": "downstream_boundary_synthesis",
                    "selected_token_delta_values": selected_token_deltas,
                    "selected_token_savings_consistent": derived["selected_token_savings_consistent"],
                    "note": "three-boundary selected token delta summary",
                }
            ],
            [
                "Token savings are not a supported paper claim.",
                "The current evidence focuses on success, hidden-verifier safety, and negative transfer.",
            ],
            [
                "SkillAdmit-selected reduces token cost.",
                "Selection is more efficient across downstream tasks.",
            ],
            [
                "If token cost is mentioned, frame it as inconclusive or mixed.",
                "Do not use small hard_v3 token decreases to override hard_v2 increases.",
            ],
            "A reviewer may ask whether SkillAdmit is cost-effective.",
            (
                "The current downstream evidence was not designed as a cost-effectiveness study. A separate controlled "
                "token-cost evaluation would be needed."
            ),
        ),
        claim(
            "C10_all_skills_is_strong_but_not_the_target_policy",
            "boundary_claim",
            "All-skills context is a strong comparison condition, but it is not the same as an admitted selected artifact policy.",
            (
                f"All-skills reaches {success(v2_strict_all)} in hard_v2 strict and "
                f"{success(v3_tree_all)} in hard_v3 tree-aware. In hard_v4, all-skills reaches "
                f"{success(v4_tree_all)} tree-aware and {success(v4_strict_all)} strict, while selected reaches "
                f"{success(v4_tree_selected)} and {success(v4_strict_selected)}."
            ),
            [
                evidence_row("hard_v2_evidence_package", v2_strict_all, "hard_v2 strict all distilled skills"),
                evidence_row("hard_v2_evidence_package", v2_strict_selected, "hard_v2 strict selected"),
                evidence_row("hard_v3_evidence_package", v3_tree_all, "hard_v3 tree-aware all distilled skills"),
                evidence_row("hard_v3_evidence_package", v3_tree_selected, "hard_v3 tree-aware selected"),
                evidence_row("hard_v3_evidence_package", v3_strict_all, "hard_v3 strict all distilled skills"),
                evidence_row("hard_v3_evidence_package", v3_strict_selected, "hard_v3 strict selected"),
                evidence_row("hard_v4_evidence_package", v4_tree_all, "hard_v4 tree-aware all distilled skills"),
                evidence_row("hard_v4_evidence_package", v4_tree_selected, "hard_v4 tree-aware selected"),
                evidence_row("hard_v4_evidence_package", v4_strict_all, "hard_v4 strict all distilled skills"),
                evidence_row("hard_v4_evidence_package", v4_strict_selected, "hard_v4 strict selected"),
            ],
            [
                "All-skills is a strong upper-context comparison and should be reported.",
                "Selected experience is a policy target, not a claim that fewer artifacts always beat all available skills.",
            ],
            [
                "Selection always beats all-skills.",
                "All-skills success invalidates experience admission.",
            ],
            [
                "Distinguish policy selection from maximum-context baselines.",
                "Do not turn all-skills into the headline condition unless the paper is about context stuffing.",
            ],
            "A reviewer may ask why not always provide every distilled skill.",
            (
                "All-skills is a valid comparison but changes the policy question. SkillAdmit studies admission and selection; "
                "all-skills is useful as a high-context baseline with different cost and contamination risks."
            ),
        ),
    ]
    return claims


def build_matrix(
    hard_v2: dict[str, Any],
    hard_v3: dict[str, Any],
    hard_v4: dict[str, Any],
    synthesis: dict[str, Any],
    paper_section: dict[str, Any],
    paths: dict[str, Path],
) -> dict[str, Any]:
    claims = build_claims(hard_v2, hard_v3, hard_v4, synthesis)
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_packages": [
            {
                "name": name,
                "path": str(display_path(path)),
                "sha256": sha256_file(path),
                "generated_at_utc": package.get("generated_at_utc"),
            }
            for name, path, package in [
                ("hard_v2_evidence_package", paths["hard_v2"], hard_v2),
                ("hard_v3_evidence_package", paths["hard_v3"], hard_v3),
                ("hard_v4_evidence_package", paths["hard_v4"], hard_v4),
                ("downstream_boundary_synthesis", paths["synthesis"], synthesis),
                ("downstream_paper_eval_section", paths["paper_section"], paper_section),
            ]
        ],
        "claim_count": len(claims),
        "claims": claims,
        "global_red_lines": [
            "Do not claim universal SkillAdmit-selected superiority.",
            "Do not claim cross-version SkillAdmit-selected token savings.",
            "Do not claim precondition-only generally replaces repository-tree context.",
            "Do not claim raw memory is a safe admission policy from hard_v3 success alone.",
            "Do not claim bad dependency advice is safe when the model often ignored it.",
            "Do not tune hard_v2, hard_v3, or hard_v4 failures while treating them as clean evidence.",
        ],
        "global_positive_claim": (
            "SkillAdmit has conditional downstream utility evidence and strong negative-transfer evidence: "
            "hard_v2 supports tree-aware selected utility, hard_v3 bounds universal selected-superiority claims, "
            "hard_v4 adds a stricter boundary, and forced bad artifacts fail 0/133 with "
            "133 public-pass/hidden-fail cases."
        ),
    }


def assert_matrix(matrix: dict[str, Any], synthesis: dict[str, Any], hard_v2: dict[str, Any]) -> None:
    if matrix["claim_count"] != 10:
        raise AssertionError(f"expected 10 claims, got {matrix['claim_count']}")
    claim_ids = {row["claim_id"] for row in matrix["claims"]}
    required_ids = {
        "C1_downstream_hidden_verifier_is_required",
        "C2_hard_v2_tree_selected_positive",
        "C3_hard_v2_strict_visible_boundary",
        "C4_hard_v3_generalization_boundary",
        "C5_repo_tree_and_preconditions_are_context_variables",
        "C6_forced_bad_artifacts_negative_transfer",
        "C7_bad_dependency_rule_is_not_safe",
        "C8_raw_memory_is_a_serious_baseline_not_a_policy",
        "C9_selected_token_savings_not_supported",
        "C10_all_skills_is_strong_but_not_the_target_policy",
    }
    missing = required_ids - claim_ids
    if missing:
        raise AssertionError(f"missing claim ids: {sorted(missing)}")

    derived = synthesis["derived_claims"]
    forced_summary = synthesis["forced_bad_summary"]
    required_derived = {
        "forced_bad_total_success": "0/133",
        "forced_bad_total_tasks": 133,
        "forced_bad_total_public_passed_hidden_failed": 133,
        "forced_bad_negative_transfer_consistent": True,
        "selected_superiority_consistent": False,
        "selected_token_savings_consistent": False,
    }
    for key, expected in required_derived.items():
        actual = derived[key]
        if actual != expected:
            raise AssertionError(f"{key}: expected {expected}, got {actual}")
    if forced_summary["total_successes"] != 0:
        raise AssertionError(f"forced bad successes changed: {forced_summary['total_successes']}")
    if forced_summary["total_negative_transfer"] != 133:
        raise AssertionError(f"forced bad negative transfer changed: {forced_summary['total_negative_transfer']}")

    groups = {row["group"]: row for row in hard_v2["stability_table"]}
    if groups["tree_aware_skilladmit_selected"]["success_values"] != [25, 25]:
        raise AssertionError("hard_v2 tree-aware selected stability changed")
    if groups["strict_precondition_only"]["success_values"] != [24, 23]:
        raise AssertionError("hard_v2 precondition-only stability changed")

    rendered = render_markdown(matrix)
    required_phrases = [
        "0/133",
        "133 public-pass/hidden-fail",
        "25/25 versus 23/25",
        "29/30",
        "22/24",
        "7/24",
        "4/24",
        "Do not claim universal SkillAdmit-selected superiority",
        "Token savings are not a supported paper claim",
    ]
    for phrase in required_phrases:
        if phrase not in rendered:
            raise AssertionError(f"missing required defense phrase: {phrase}")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def compact(text: str, limit: int = 120) -> str:
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def render_markdown(matrix: dict[str, Any]) -> str:
    overview_rows = []
    for row in matrix["claims"]:
        overview_rows.append(
            [
                row["claim_id"],
                row["status"],
                compact(row["paper_claim"], 110),
                compact(row["evidence_summary"], 140),
            ]
        )

    lines = [
        "# Downstream Claim Defense Matrix",
        "",
        f"Generated at UTC: `{matrix['generated_at_utc']}`",
        "",
        matrix["global_positive_claim"],
        "",
        "## Overview",
        "",
        md_table(["claim_id", "status", "claim", "evidence"], overview_rows),
        "",
        "## Global Red Lines",
        "",
    ]
    lines.extend(f"- {line}" for line in matrix["global_red_lines"])
    lines.extend(["", "## Claim Cards", ""])

    for row in matrix["claims"]:
        lines.extend(
            [
                f"### {row['claim_id']}",
                "",
                f"Status: `{row['status']}`",
                "",
                f"Claim: {row['paper_claim']}",
                "",
                f"Evidence summary: {row['evidence_summary']}",
                "",
                "Allowed wording:",
            ]
        )
        lines.extend(f"- {item}" for item in row["allowed_wording"])
        lines.extend(["", "Forbidden wording:"])
        lines.extend(f"- {item}" for item in row["forbidden_wording"])
        lines.extend(["", "Required qualifiers:"])
        lines.extend(f"- {item}" for item in row["required_qualifiers"])
        lines.extend(
            [
                "",
                f"Reviewer risk: {row['reviewer_risk']}",
                "",
                f"Reviewer response: {row['reviewer_response']}",
                "",
                "Evidence rows:",
            ]
        )
        evidence_rows = []
        for evidence in row["evidence"]:
            adherence = ""
            if "artifact_adherence" in evidence and "tasks" in evidence:
                adherence = f"{evidence['artifact_adherence']}/{evidence['tasks']}"
            evidence_rows.append(
                [
                    evidence.get("source", ""),
                    evidence.get("setting", evidence.get("group", "")),
                    evidence.get("display_strategy", evidence.get("strategy", "")),
                    evidence.get("success", evidence.get("success_values", "")),
                    adherence,
                    evidence.get("public_passed_hidden_failed", evidence.get("forced_bad_total_public_passed_hidden_failed", "")),
                    evidence.get("total_tokens", evidence.get("token_values", "")),
                    compact(evidence.get("note", ""), 80),
                ]
            )
        lines.extend(
            [
                "",
                md_table(
                    ["source", "setting/group", "strategy", "success", "adherence", "public_hidden", "tokens", "note"],
                    evidence_rows,
                ),
                "",
            ]
        )

    lines.extend(["## Source Packages", ""])
    source_rows = [
        [
            source["name"],
            f"`{source['path']}`",
            f"`{source['sha256'][:16]}`",
            f"`{source['generated_at_utc']}`",
        ]
        for source in matrix["source_packages"]
    ]
    lines.extend(md_table(["name", "path", "sha256", "generated_at_utc"], source_rows).splitlines())
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


def render_latex(matrix: dict[str, Any]) -> str:
    lines = [
        "% Auto-generated by scripts/export_downstream_claim_defense_matrix.py",
        "\\begin{tabular}{llll}",
        "\\hline",
        "ID & Status & Claim & Evidence \\\\",
        "\\hline",
    ]
    for row in matrix["claims"]:
        lines.append(
            " & ".join(
                [
                    tex_escape(row["claim_id"]),
                    tex_escape(row["status"]),
                    tex_escape(compact(row["paper_claim"], 70)),
                    tex_escape(compact(row["evidence_summary"], 90)),
                ]
            )
            + " \\\\"
        )
    lines.extend(["\\hline", "\\end{tabular}", "", "% Global red lines:"])
    for line in matrix["global_red_lines"]:
        lines.append(f"% - {tex_escape(line)}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(matrix: dict[str, Any], json_path: Path, md_path: Path, tex_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(matrix, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(matrix), encoding="utf-8")
    tex_path.write_text(render_latex(matrix), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hard-v2-package", type=Path, default=DEFAULT_HARD_V2)
    parser.add_argument("--hard-v3-package", type=Path, default=DEFAULT_HARD_V3)
    parser.add_argument("--hard-v4-package", type=Path, default=DEFAULT_HARD_V4)
    parser.add_argument("--synthesis", type=Path, default=DEFAULT_SYNTHESIS)
    parser.add_argument("--paper-section", type=Path, default=DEFAULT_PAPER_SECTION)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX)
    parser.add_argument(
        "--assert-current-claim-defense",
        action="store_true",
        help="Assert current claim-defense values and forbidden-claim boundaries.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = {
        "hard_v2": resolve(args.hard_v2_package),
        "hard_v3": resolve(args.hard_v3_package),
        "hard_v4": resolve(args.hard_v4_package),
        "synthesis": resolve(args.synthesis),
        "paper_section": resolve(args.paper_section),
    }
    hard_v2 = load_json(paths["hard_v2"])
    hard_v3 = load_json(paths["hard_v3"])
    hard_v4 = load_json(paths["hard_v4"])
    synthesis = load_json(paths["synthesis"])
    paper_section = load_json(paths["paper_section"])
    matrix = build_matrix(hard_v2, hard_v3, hard_v4, synthesis, paper_section, paths)
    if args.assert_current_claim_defense:
        assert_matrix(matrix, synthesis, hard_v2)
    write_outputs(matrix, resolve(args.json_out), resolve(args.md_out), resolve(args.tex_out))
    print(f"claim_count: {matrix['claim_count']}")
    print(f"global_red_lines: {len(matrix['global_red_lines'])}")
    print(f"wrote_json: {display_path(args.json_out)}")
    print(f"wrote_md: {display_path(args.md_out)}")
    print(f"wrote_tex: {display_path(args.tex_out)}")


if __name__ == "__main__":
    main()
