#!/usr/bin/env python3
"""Audit paper-facing downstream claim consistency for SkillAdmit.

What this file does:
  Reads the current three-boundary downstream synthesis, generated paper
  section, claim-defense matrix, artifact index, and selected Markdown reports.
  It exports a consistency audit that checks whether the paper-facing layer is
  still telling the same hard_v2/hard_v3/hard_v4 story.

Why it is needed:
  The strongest current SkillAdmit evidence is conditional, and stale wording is
  easy to reintroduce while editing paper text. This audit prevents the
  reporting layer from drifting back to an old hard_v2/hard_v3-only aggregate,
  an unsupported selected-wins claim, or an unsupported token-savings claim.

Inputs:
  benchmark/downstream/reports/downstream_boundary_synthesis.json
  benchmark/downstream/reports/downstream_paper_eval_section.json
  benchmark/downstream/reports/downstream_claim_defense_matrix.json
  benchmark/downstream/reports/paper_artifacts_index.json
  benchmark/downstream/reports/downstream_boundary_synthesis.md
  benchmark/downstream/reports/downstream_paper_eval_section.md
  benchmark/downstream/reports/downstream_claim_defense_matrix.md
  benchmark/downstream/reports/paper_artifacts_index.md
  docs/experiment_handoff.md
  docs/paper_eval_status.md
  docs/progress_log.md
  README.md

Outputs:
  benchmark/downstream/reports/paper_claim_consistency_audit.json
  benchmark/downstream/reports/paper_claim_consistency_audit.md
  benchmark/downstream/reports/paper_claim_consistency_audit.tex

Who runs it:
  Researchers or Codex sessions before paper drafting, reviewer-response work,
  or any new downstream validation boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "benchmark" / "downstream" / "reports"

DEFAULT_JSON = REPORT_DIR / "paper_claim_consistency_audit.json"
DEFAULT_MD = REPORT_DIR / "paper_claim_consistency_audit.md"
DEFAULT_TEX = REPORT_DIR / "paper_claim_consistency_audit.tex"

JSON_INPUTS = {
    "boundary_synthesis": REPORT_DIR / "downstream_boundary_synthesis.json",
    "paper_section": REPORT_DIR / "downstream_paper_eval_section.json",
    "claim_defense": REPORT_DIR / "downstream_claim_defense_matrix.json",
    "artifacts_index": REPORT_DIR / "paper_artifacts_index.json",
}

TEXT_INPUTS = {
    "boundary_synthesis_md": REPORT_DIR / "downstream_boundary_synthesis.md",
    "paper_section_md": REPORT_DIR / "downstream_paper_eval_section.md",
    "claim_defense_md": REPORT_DIR / "downstream_claim_defense_matrix.md",
    "artifacts_index_md": REPORT_DIR / "paper_artifacts_index.md",
    "experiment_handoff": ROOT / "docs" / "experiment_handoff.md",
    "paper_eval_status": ROOT / "docs" / "paper_eval_status.md",
    "progress_log": ROOT / "docs" / "progress_log.md",
    "readme": ROOT / "README.md",
}

EXPECTED_CLAIM_IDS = {
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

REQUIRED_THREE_BOUNDARY_PHRASES = [
    "hard_v2",
    "hard_v3",
    "hard_v4",
    "0/133",
    "133 public-pass/hidden-fail",
    "22/24",
    "24/24",
    "Token savings are not a supported paper claim",
]


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> str:
    resolved = resolve(path)
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(resolve(path).read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return resolve(path).read_text(encoding="utf-8")


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with resolve(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def source_file(name: str, path: Path) -> dict[str, Any]:
    resolved = resolve(path)
    return {
        "name": name,
        "path": display_path(resolved),
        "exists": resolved.exists(),
        "sha256": sha256_file(resolved) if resolved.exists() else None,
        "size_bytes": resolved.stat().st_size if resolved.exists() else None,
    }


def add_check(
    checks: list[dict[str, Any]],
    check_id: str,
    passed: bool,
    summary: str,
    details: dict[str, Any] | None = None,
) -> None:
    checks.append(
        {
            "check_id": check_id,
            "status": "pass" if passed else "fail",
            "summary": summary,
            "details": details or {},
        }
    )


def claim_by_id(claim_defense: dict[str, Any], claim_id: str) -> dict[str, Any]:
    claims = {row["claim_id"]: row for row in claim_defense["claims"]}
    if claim_id not in claims:
        raise KeyError(f"missing claim: {claim_id}")
    return claims[claim_id]


def evidence_sources(claim: dict[str, Any]) -> set[str]:
    return {str(row.get("source")) for row in claim["evidence"] if row.get("source")}


def text_contains_all(text: str, phrases: list[str]) -> tuple[bool, list[str]]:
    missing = [phrase for phrase in phrases if phrase not in text]
    return not missing, missing


def count_pattern(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, flags=re.IGNORECASE))


def build_audit(data: dict[str, dict[str, Any]], texts: dict[str, str]) -> dict[str, Any]:
    boundary = data["boundary_synthesis"]
    paper = data["paper_section"]
    claim_defense = data["claim_defense"]
    index = data["artifacts_index"]

    derived = boundary["derived_claims"]
    paper_derived = paper["derived_synthesis"]
    facts = index["key_current_facts"]
    checks: list[dict[str, Any]] = []

    add_check(
        checks,
        "A1_boundary_forced_bad_aggregate",
        derived["forced_bad_total_success"] == "0/133"
        and derived["forced_bad_total_tasks"] == 133
        and derived["forced_bad_total_public_passed_hidden_failed"] == 133
        and derived["forced_bad_negative_transfer_consistent"] is True,
        "Boundary synthesis keeps the three-suite forced_bad aggregate at 0/133.",
        {
            "forced_bad_total_success": derived["forced_bad_total_success"],
            "forced_bad_total_tasks": derived["forced_bad_total_tasks"],
            "forced_bad_total_public_passed_hidden_failed": derived[
                "forced_bad_total_public_passed_hidden_failed"
            ],
            "forced_bad_negative_transfer_consistent": derived[
                "forced_bad_negative_transfer_consistent"
            ],
        },
    )

    boundary_sha = sha256_file(JSON_INPUTS["boundary_synthesis"])
    add_check(
        checks,
        "A2_paper_section_source_boundary",
        paper["source_synthesis"]["path"] == display_path(JSON_INPUTS["boundary_synthesis"])
        and paper["source_synthesis"]["sha256"] == boundary_sha,
        "Paper section is generated from downstream_boundary_synthesis.json, not the older cross-version synthesis.",
        {
            "paper_source_path": paper["source_synthesis"]["path"],
            "expected_source_path": display_path(JSON_INPUTS["boundary_synthesis"]),
            "paper_source_sha256": paper["source_synthesis"]["sha256"],
            "actual_boundary_sha256": boundary_sha,
        },
    )

    shared_keys = [
        "forced_bad_total_tasks",
        "forced_bad_total_success",
        "forced_bad_total_public_passed_hidden_failed",
        "selected_superiority_consistent",
        "selected_token_savings_consistent",
        "forced_bad_negative_transfer_consistent",
    ]
    paper_mismatches = {
        key: {"paper": paper_derived.get(key), "boundary": derived.get(key)}
        for key in shared_keys
        if paper_derived.get(key) != derived.get(key)
    }
    add_check(
        checks,
        "A3_paper_derived_values_match_boundary",
        not paper_mismatches and len(paper["results"]) == 6 and len(paper["claim_limits"]) == 7,
        "Paper section derived values, result count, and claim-limit count match the three-boundary source.",
        {
            "mismatches": paper_mismatches,
            "result_paragraphs": len(paper["results"]),
            "claim_limits": len(paper["claim_limits"]),
        },
    )

    claim_ids = {row["claim_id"] for row in claim_defense["claims"]}
    missing_claims = sorted(EXPECTED_CLAIM_IDS - claim_ids)
    add_check(
        checks,
        "A4_claim_defense_claim_set",
        claim_defense["claim_count"] == 10 and not missing_claims,
        "Claim-defense matrix keeps the expected ten paper-facing claim cards.",
        {
            "claim_count": claim_defense["claim_count"],
            "missing_claim_ids": missing_claims,
        },
    )

    source_names = [row["name"] for row in claim_defense["source_packages"]]
    expected_sources = [
        "hard_v2_evidence_package",
        "hard_v3_evidence_package",
        "hard_v4_evidence_package",
        "downstream_boundary_synthesis",
        "downstream_paper_eval_section",
    ]
    add_check(
        checks,
        "A5_claim_defense_source_packages",
        source_names == expected_sources,
        "Claim-defense matrix cites hard_v2, hard_v3, hard_v4, boundary synthesis, and paper section.",
        {"source_packages": source_names},
    )

    c6_sources = evidence_sources(claim_by_id(claim_defense, "C6_forced_bad_artifacts_negative_transfer"))
    c9 = claim_by_id(claim_defense, "C9_selected_token_savings_not_supported")
    c9_sources = evidence_sources(c9)
    add_check(
        checks,
        "A6_c6_c9_evidence_sources",
        {"hard_v4_evidence_package", "downstream_boundary_synthesis"}.issubset(c6_sources)
        and c9["status"] == "not_supported_claim"
        and c9_sources == {"downstream_boundary_synthesis"},
        "C6 uses hard_v4 plus boundary synthesis, and C9 treats selected token savings as unsupported.",
        {
            "c6_sources": sorted(c6_sources),
            "c9_status": c9["status"],
            "c9_sources": sorted(c9_sources),
        },
    )

    expected_facts = {
        "boundary_forced_bad_total_success": "0/133",
        "boundary_forced_bad_total_tasks": 133,
        "boundary_forced_bad_total_public_passed_hidden_failed": 133,
        "boundary_selected_superiority_consistent": False,
        "boundary_selected_token_savings_consistent": False,
        "claim_count": 10,
        "paper_section_result_paragraphs": 6,
    }
    fact_mismatches = {
        key: {"index": facts.get(key), "expected": expected}
        for key, expected in expected_facts.items()
        if facts.get(key) != expected
    }
    add_check(
        checks,
        "A7_artifact_index_key_facts",
        not fact_mismatches,
        "Artifact index key facts match the current three-boundary reporting layer.",
        {"mismatches": fact_mismatches},
    )

    paper_text = texts["paper_section_md"]
    claim_text = texts["claim_defense_md"]
    index_text = texts["artifacts_index_md"]
    combined_current_reports = "\n".join(
        [
            texts["boundary_synthesis_md"],
            paper_text,
            claim_text,
        ]
    )
    required_ok, required_missing = text_contains_all(
        "\n".join([paper_text, claim_text, index_text]),
        REQUIRED_THREE_BOUNDARY_PHRASES,
    )
    add_check(
        checks,
        "A8_required_three_boundary_phrases",
        required_ok,
        "Current report text contains the core three-boundary facts and guardrail wording.",
        {"missing_phrases": required_missing},
    )

    old_aggregate_count = count_pattern(combined_current_reports, r"\b0/85\b")
    add_check(
        checks,
        "A9_no_old_0_85_in_current_three_boundary_reports",
        old_aggregate_count == 0,
        "Current boundary, paper-section, and claim-defense reports do not reuse the old 0/85 aggregate.",
        {"old_0_85_occurrences": old_aggregate_count},
    )

    guardrail_text = "\n".join(
        paper["claim_limits"] + claim_defense["global_red_lines"] + [claim_defense["global_positive_claim"]]
    )
    guardrail_ok = (
        "Do not claim universal SkillAdmit-selected superiority." in guardrail_text
        and "Do not claim cross-version SkillAdmit-selected token savings." in guardrail_text
        and "Do not tune hard_v2, hard_v3, or hard_v4" in guardrail_text
        and "hard_v4 adds a stricter boundary" in guardrail_text
    )
    add_check(
        checks,
        "A10_guardrail_wording_present",
        guardrail_ok,
        "Generated paper artifacts preserve the no-universal-selected, no-token-savings, and no-retuning guardrails.",
        {"guardrail_text": guardrail_text},
    )

    hard_v4_boundary_ok = (
        "hard_v4 strict selected trails no_experience at 22/24 versus 24/24" in paper[
            "one_paragraph_summary"
        ]
        and "hard_v4 strict visible-file, selected is 22/24 while no_experience is 24/24"
        in claim_by_id(claim_defense, "C4_hard_v3_generalization_boundary")["evidence_summary"]
    )
    add_check(
        checks,
        "A11_hard_v4_boundary_is_explicit",
        hard_v4_boundary_ok,
        "hard_v4 is stated as a stricter boundary, not a selected-utility win.",
        {
            "paper_summary": paper["one_paragraph_summary"],
            "c4_evidence_summary": claim_by_id(
                claim_defense, "C4_hard_v3_generalization_boundary"
            )["evidence_summary"],
        },
    )

    text_files_ok = all(resolve(path).exists() for path in TEXT_INPUTS.values())
    add_check(
        checks,
        "A12_text_artifact_presence",
        text_files_ok,
        "All Markdown/docs inputs used for paper-facing consistency checks exist.",
        {name: display_path(path) for name, path in TEXT_INPUTS.items()},
    )

    failures = [row for row in checks if row["status"] != "pass"]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Consistency audit for the paper-facing hard_v2/hard_v3/hard_v4 downstream "
            "claim layer. This is a reporting-hygiene artifact, not new empirical evidence."
        ),
        "source_files": [
            source_file(name, path)
            for name, path in {**JSON_INPUTS, **TEXT_INPUTS}.items()
        ],
        "summary": {
            "total_checks": len(checks),
            "passed_checks": len(checks) - len(failures),
            "failed_checks": len(failures),
            "status": "pass" if not failures else "fail",
        },
        "key_facts": {
            "forced_bad_total_success": derived["forced_bad_total_success"],
            "forced_bad_total_tasks": derived["forced_bad_total_tasks"],
            "forced_bad_total_public_passed_hidden_failed": derived[
                "forced_bad_total_public_passed_hidden_failed"
            ],
            "forced_bad_phrase": (
                f"{derived['forced_bad_total_success']} success with "
                f"{derived['forced_bad_total_public_passed_hidden_failed']} "
                "public-pass/hidden-fail cases"
            ),
            "hard_v4_strict_selected": "22/24",
            "hard_v4_strict_no_experience": "24/24",
            "selected_superiority_consistent": derived["selected_superiority_consistent"],
            "selected_token_savings_consistent": derived["selected_token_savings_consistent"],
        },
        "checks": checks,
        "claim_boundary": {
            "supported": [
                "conditional downstream utility under specific settings",
                "hidden-verifier downstream validation is necessary",
                "forced harmful artifacts produce systematic negative transfer",
            ],
            "not_supported": [
                "universal SkillAdmit-selected superiority",
                "cross-boundary selected token savings",
                "precondition-only generally replacing repository-tree context",
                "hard_v4 selected utility",
            ],
        },
        "next_recommended_step": (
            "If continuing experiments, use a predeclared model-transfer replication or a new hard_v5 "
            "boundary. Do not tune hard_v2, hard_v3, or hard_v4 from observed failures."
        ),
    }


def assert_audit(audit: dict[str, Any]) -> None:
    if audit["summary"]["total_checks"] != 12:
        raise AssertionError(f"expected 12 checks, got {audit['summary']['total_checks']}")
    if audit["summary"]["failed_checks"] != 0:
        failures = [row for row in audit["checks"] if row["status"] != "pass"]
        raise AssertionError(f"failed consistency checks: {failures}")
    rendered = render_markdown(audit)
    required = [
        "0/133",
        "133 public-pass/hidden-fail",
        "hard_v4",
        "universal SkillAdmit-selected superiority",
        "cross-boundary selected token savings",
        "not new empirical evidence",
    ]
    for phrase in required:
        if phrase not in rendered:
            raise AssertionError(f"missing audit phrase: {phrase}")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def compact(value: Any, limit: int = 140) -> str:
    text = " ".join(str(value).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def render_markdown(audit: dict[str, Any]) -> str:
    check_rows = [
        [
            row["check_id"],
            row["status"],
            row["summary"],
            compact(row["details"], 180),
        ]
        for row in audit["checks"]
    ]
    source_rows = [
        [
            row["name"],
            f"`{row['path']}`",
            row["exists"],
            f"`{row['sha256'][:16]}`" if row["sha256"] else "",
            row["size_bytes"] or "",
        ]
        for row in audit["source_files"]
    ]
    lines = [
        "# Paper Claim Consistency Audit",
        "",
        f"Generated at UTC: `{audit['generated_at_utc']}`",
        "",
        audit["purpose"],
        "",
        "## Summary",
        "",
        md_table(
            ["metric", "value"],
            [[key, value] for key, value in audit["summary"].items()],
        ),
        "",
        "## Key Facts",
        "",
        md_table(
            ["fact", "value"],
            [[key, value] for key, value in audit["key_facts"].items()],
        ),
        "",
        "## Checks",
        "",
        md_table(["check", "status", "summary", "details"], check_rows),
        "",
        "## Claim Boundary",
        "",
        "Supported:",
    ]
    lines.extend(f"- {item}" for item in audit["claim_boundary"]["supported"])
    lines.extend(["", "Not supported:"])
    lines.extend(f"- {item}" for item in audit["claim_boundary"]["not_supported"])
    lines.extend(
        [
            "",
            "## Next Recommended Step",
            "",
            audit["next_recommended_step"],
            "",
            "## Source Files",
            "",
            md_table(["name", "path", "exists", "sha256", "bytes"], source_rows),
            "",
        ]
    )
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


def render_latex(audit: dict[str, Any]) -> str:
    lines = [
        "% Auto-generated by scripts/audit_paper_claim_consistency.py",
        "\\begin{tabular}{lll}",
        "\\hline",
        "Check & Status & Summary \\\\",
        "\\hline",
    ]
    for row in audit["checks"]:
        lines.append(
            " & ".join(
                [
                    tex_escape(row["check_id"]),
                    tex_escape(row["status"]),
                    tex_escape(compact(row["summary"], 90)),
                ]
            )
            + " \\\\"
        )
    lines.extend(["\\hline", "\\end{tabular}", "", "% Claim boundary:"])
    for item in audit["claim_boundary"]["not_supported"]:
        lines.append(f"% Not supported: {tex_escape(item)}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(audit: dict[str, Any], json_path: Path, md_path: Path, tex_path: Path) -> None:
    resolve(json_path).parent.mkdir(parents=True, exist_ok=True)
    resolve(json_path).write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    resolve(md_path).write_text(render_markdown(audit), encoding="utf-8")
    resolve(tex_path).write_text(render_latex(audit), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX)
    parser.add_argument(
        "--assert-current-audit",
        action="store_true",
        help="Assert current paper-facing consistency checks and claim boundaries.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = {name: load_json(path) for name, path in JSON_INPUTS.items()}
    texts = {name: read_text(path) for name, path in TEXT_INPUTS.items()}
    audit = build_audit(data, texts)
    if args.assert_current_audit:
        assert_audit(audit)
    write_outputs(audit, args.json_out, args.md_out, args.tex_out)
    print(f"total_checks: {audit['summary']['total_checks']}")
    print(f"passed_checks: {audit['summary']['passed_checks']}")
    print(f"failed_checks: {audit['summary']['failed_checks']}")
    print(f"wrote_json: {display_path(args.json_out)}")
    print(f"wrote_md: {display_path(args.md_out)}")
    print(f"wrote_tex: {display_path(args.tex_out)}")


if __name__ == "__main__":
    main()
