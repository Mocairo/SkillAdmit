#!/usr/bin/env python3
"""Audit public reporting hygiene for SkillAdmit downstream artifacts.

What this file does:
  Checks the generated paper-facing reports for stale or over-strong wording.
  It verifies that the current main boundary remains the hard_v2/hard_v3/hard_v4
  0/133 story, that model-transfer 0/216 evidence stays in the optional
  replication/addendum layer, and that the older hard_v2/hard_v3 0/85 synthesis
  is labeled as historical rather than current top-level evidence.

Why it is needed:
  SkillAdmit now has several overlapping reporting layers. Without a hygiene
  audit, a public repository can accidentally mix old cross-version evidence,
  the current three-boundary evidence, and the model-transfer addendum into a
  stronger claim than the experiments support.

Inputs:
  benchmark/downstream/reports/downstream_boundary_synthesis.*
  benchmark/downstream/reports/downstream_paper_eval_section.*
  benchmark/downstream/reports/downstream_claim_defense_matrix.*
  benchmark/downstream/reports/model_transfer_paper_addendum.*
  benchmark/downstream/reports/paper_artifacts_index.*
  docs/experiment_handoff.md
  docs/paper_eval_status.md
  docs/progress_log.md
  README.md

Outputs:
  benchmark/downstream/reports/reporting_hygiene_audit.json
  benchmark/downstream/reports/reporting_hygiene_audit.md
  benchmark/downstream/reports/reporting_hygiene_audit.tex

Who runs it:
  Researchers or Codex sessions before public commits, paper drafting, or
  handoff, especially after regenerating paper-facing artifacts.
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

DEFAULT_JSON = REPORT_DIR / "reporting_hygiene_audit.json"
DEFAULT_MD = REPORT_DIR / "reporting_hygiene_audit.md"
DEFAULT_TEX = REPORT_DIR / "reporting_hygiene_audit.tex"

JSON_INPUTS = {
    "boundary_synthesis": REPORT_DIR / "downstream_boundary_synthesis.json",
    "paper_section": REPORT_DIR / "downstream_paper_eval_section.json",
    "claim_defense": REPORT_DIR / "downstream_claim_defense_matrix.json",
    "model_transfer_addendum": REPORT_DIR / "model_transfer_paper_addendum.json",
    "artifact_index": REPORT_DIR / "paper_artifacts_index.json",
}

TEXT_INPUTS = {
    "boundary_synthesis_md": REPORT_DIR / "downstream_boundary_synthesis.md",
    "paper_section_md": REPORT_DIR / "downstream_paper_eval_section.md",
    "claim_defense_md": REPORT_DIR / "downstream_claim_defense_matrix.md",
    "model_transfer_addendum_md": REPORT_DIR / "model_transfer_paper_addendum.md",
    "artifact_index_md": REPORT_DIR / "paper_artifacts_index.md",
    "readme": ROOT / "README.md",
    "experiment_handoff": ROOT / "docs" / "experiment_handoff.md",
    "paper_eval_status": ROOT / "docs" / "paper_eval_status.md",
    "progress_log": ROOT / "docs" / "progress_log.md",
}

CURRENT_MAIN_TEXTS = [
    "boundary_synthesis_md",
    "paper_section_md",
    "claim_defense_md",
]

MODEL_TRANSFER_TEXTS = [
    "model_transfer_addendum_md",
]


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


def count_phrase(text: str, phrase: str) -> int:
    return text.count(phrase)


def lines_containing(text: str, phrase: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if phrase in line]


def window_contains(text: str, phrase: str, allowed_words: set[str]) -> bool:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if phrase not in line:
            continue
        start = max(0, index - 1)
        end = min(len(lines), index + 2)
        window = " ".join(lines[start:end]).lower()
        if not any(word in window for word in allowed_words):
            return False
    return True


def forbidden_phrase_hits(texts: dict[str, str], names: list[str], phrases: list[str]) -> list[dict[str, str]]:
    hits = []
    for name in names:
        text = texts[name]
        for phrase in phrases:
            for line in lines_containing(text, phrase):
                hits.append({"source": name, "phrase": phrase, "line": line})
    return hits


def is_negated_guardrail_line(line: str) -> bool:
    lowered = line.lower()
    if lowered.startswith("- ") and "model-generally superior" in lowered:
        return True
    return any(
        marker in lowered
        for marker in [
            "do not",
            "not be used to claim",
            "not model-general",
            "not a universal",
            "outside the supported claim",
            "unsupported",
            "forbidden wording",
        ]
    )


def build_audit(data: dict[str, dict[str, Any]], texts: dict[str, str]) -> dict[str, Any]:
    boundary = data["boundary_synthesis"]
    paper = data["paper_section"]
    claim_defense = data["claim_defense"]
    addendum = data["model_transfer_addendum"]
    index = data["artifact_index"]
    checks: list[dict[str, Any]] = []

    boundary_derived = boundary["derived_claims"]
    paper_derived = paper["derived_synthesis"]
    claim_positive = claim_defense["global_positive_claim"]
    addendum_derived = addendum["derived_cross_model"]
    index_facts = index["key_current_facts"]

    add_check(
        checks,
        "H1_main_boundary_uses_0_133",
        boundary_derived["forced_bad_total_success"] == "0/133"
        and paper_derived["forced_bad_total_success"] == "0/133"
        and "0/133" in claim_positive
        and index_facts["boundary_forced_bad_total_success"] == "0/133",
        "Current main reporting layer is anchored to the hard_v2/hard_v3/hard_v4 0/133 boundary.",
        {
            "boundary": boundary_derived["forced_bad_total_success"],
            "paper": paper_derived["forced_bad_total_success"],
            "claim_positive_contains_0_133": "0/133" in claim_positive,
            "index": index_facts["boundary_forced_bad_total_success"],
        },
    )

    current_main_text = "\n".join(texts[name] for name in CURRENT_MAIN_TEXTS)
    add_check(
        checks,
        "H2_no_0_85_in_current_main_reports",
        "0/85" not in current_main_text,
        "Current main reports do not reuse the legacy hard_v2/hard_v3 0/85 aggregate.",
        {"0/85_occurrences": count_phrase(current_main_text, "0/85")},
    )

    add_check(
        checks,
        "H3_model_transfer_stays_addendum",
        addendum_derived["forced_bad_combined_success"] == "0/216"
        and addendum_derived["selected_superiority_model_general"] is False
        and "0/216" not in current_main_text
        and "This addendum is intentionally separate from the main three-boundary downstream section"
        in texts["model_transfer_addendum_md"],
        "Model-transfer 0/216 evidence is present in the addendum and absent from the main three-boundary reports.",
        {
            "addendum_forced_bad": addendum_derived["forced_bad_combined_success"],
            "main_0_216_occurrences": count_phrase(current_main_text, "0/216"),
            "selected_superiority_model_general": addendum_derived[
                "selected_superiority_model_general"
            ],
        },
    )

    artifact_index_text = texts["artifact_index_md"]
    cross_version_lines = lines_containing(artifact_index_text, "G4_cross_version_synthesis")
    add_check(
        checks,
        "H4_cross_version_marked_historical",
        bool(cross_version_lines)
        and "Historical two-boundary synthesis" in artifact_index_text
        and "Use only when discussing the earlier hard_v2/hard_v3 historical 0/85 synthesis"
        in artifact_index_text
        and "Do not use this as the current top-level downstream story" in artifact_index_text,
        "Artifact index labels the 0/85 hard_v2/hard_v3 synthesis as historical, not current top-level evidence.",
        {"cross_version_lines": cross_version_lines[:3]},
    )

    add_check(
        checks,
        "H5_index_0_85_mentions_are_legacy",
        window_contains(artifact_index_text, "0/85", {"legacy", "historical", "earlier"}),
        "Any 0/85 mention in the artifact index is explicitly legacy or historical.",
        {"0/85_lines": lines_containing(artifact_index_text, "0/85")},
    )

    overclaim_hits = forbidden_phrase_hits(
        texts,
        CURRENT_MAIN_TEXTS + MODEL_TRANSFER_TEXTS,
        [
            "proves downstream token savings",
            "has demonstrated token savings",
            "model-generally superior",
            "model-general SkillAdmit-selected superiority.",
        ],
    )
    disallowed_hits = [
        hit
        for hit in overclaim_hits
        if not is_negated_guardrail_line(hit["line"])
    ]
    add_check(
        checks,
        "H6_no_positive_token_or_model_general_overclaim",
        not disallowed_hits,
        "Current main/addendum reports do not positively claim token savings or model-general selected superiority.",
        {"disallowed_hits": disallowed_hits},
    )

    add_check(
        checks,
        "H7_no_retuning_guardrail_present",
        "Do not tune hard_v2, hard_v3, or hard_v4 failures" in current_main_text
        and "The transfer run justifies retuning hard_v3 or hard_v4" in texts[
            "model_transfer_addendum_md"
        ],
        "No-retuning guardrails are present for the main boundary and the transfer addendum.",
        {
            "main_guardrail": "Do not tune hard_v2, hard_v3, or hard_v4 failures" in current_main_text,
            "addendum_forbidden_retuning": "The transfer run justifies retuning hard_v3 or hard_v4"
            in texts["model_transfer_addendum_md"],
        },
    )

    handoff_text = "\n".join(
        [
            texts["experiment_handoff"],
            texts["paper_eval_status"],
            texts["progress_log"],
            texts["readme"],
        ]
    )
    add_check(
        checks,
        "H8_handoff_records_three_layers",
        "0/133 boundary aggregate" in handoff_text
        and "0/216" in handoff_text
        and "model-transfer paper addendum" in handoff_text.lower(),
        "Handoff docs record the main boundary, model-transfer addendum, and their separation.",
        {
            "mentions_0_133_boundary": "0/133 boundary aggregate" in handoff_text,
            "mentions_0_216": "0/216" in handoff_text,
            "mentions_addendum": "model-transfer paper addendum" in handoff_text.lower(),
        },
    )

    failures = [row for row in checks if row["status"] != "pass"]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Public reporting hygiene audit for SkillAdmit downstream artifacts. "
            "It checks aggregate separation, legacy wording, overclaim guardrails, "
            "and handoff consistency."
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
        "aggregate_roles": {
            "historical_two_boundary": {
                "aggregate": "0/85",
                "role": "legacy hard_v2/hard_v3 synthesis only",
            },
            "current_main_boundary": {
                "aggregate": "0/133",
                "role": "current hard_v2/hard_v3/hard_v4 downstream boundary",
            },
            "model_transfer_addendum": {
                "aggregate": "0/216",
                "role": "two-model hard_v3/hard_v4 replication/addendum layer",
            },
        },
        "checks": checks,
        "next_recommended_step": (
            "Use the hygiene audit before public commits or paper edits. If a new "
            "experiment is needed, predeclare a hard_v5 boundary instead of tuning "
            "hard_v3/hard_v4 failures."
        ),
    }


def assert_hygiene(audit: dict[str, Any]) -> None:
    if audit["summary"]["total_checks"] != 8:
        raise AssertionError(f"expected 8 checks, got {audit['summary']['total_checks']}")
    if audit["summary"]["failed_checks"] != 0:
        failures = [row for row in audit["checks"] if row["status"] != "pass"]
        raise AssertionError(f"failed reporting hygiene checks: {failures}")
    rendered = render_markdown(audit)
    required = [
        "0/85",
        "0/133",
        "0/216",
        "legacy hard_v2/hard_v3 synthesis only",
        "current hard_v2/hard_v3/hard_v4 downstream boundary",
        "two-model hard_v3/hard_v4 replication/addendum layer",
    ]
    for phrase in required:
        if phrase not in rendered:
            raise AssertionError(f"missing hygiene phrase: {phrase}")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def compact(value: Any, limit: int = 160) -> str:
    text = " ".join(str(value).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def render_markdown(audit: dict[str, Any]) -> str:
    role_rows = [
        [name, item["aggregate"], item["role"]]
        for name, item in audit["aggregate_roles"].items()
    ]
    check_rows = [
        [row["check_id"], row["status"], row["summary"], compact(row["details"])]
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
    return "\n\n".join(
        [
            "# Reporting Hygiene Audit",
            f"Generated at UTC: `{audit['generated_at_utc']}`",
            audit["purpose"],
            "## Summary",
            md_table(["metric", "value"], [[key, value] for key, value in audit["summary"].items()]),
            "## Aggregate Roles",
            md_table(["layer", "aggregate", "role"], role_rows),
            "## Checks",
            md_table(["check", "status", "summary", "details"], check_rows),
            "## Next Recommended Step",
            audit["next_recommended_step"],
            "## Source Files",
            md_table(["name", "path", "exists", "sha256", "bytes"], source_rows),
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


def render_latex(audit: dict[str, Any]) -> str:
    lines = [
        "% Auto-generated by scripts/audit_reporting_hygiene.py",
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
                    tex_escape(compact(row["summary"], 80)),
                ]
            )
            + " \\\\"
        )
    lines.extend(["\\hline", "\\end{tabular}", "", "% Aggregate roles:"])
    for name, item in audit["aggregate_roles"].items():
        lines.append(f"% {tex_escape(name)} = {tex_escape(item['aggregate'])}: {tex_escape(item['role'])}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(audit: dict[str, Any], json_path: Path, md_path: Path, tex_path: Path) -> None:
    json_path = resolve(json_path)
    md_path = resolve(md_path)
    tex_path = resolve(tex_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(audit), encoding="utf-8")
    tex_path.write_text(render_latex(audit), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX)
    parser.add_argument(
        "--assert-current-hygiene",
        action="store_true",
        help="Assert current public reporting hygiene invariants.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = {name: load_json(path) for name, path in JSON_INPUTS.items()}
    texts = {name: read_text(path) for name, path in TEXT_INPUTS.items()}
    audit = build_audit(data, texts)
    if args.assert_current_hygiene:
        assert_hygiene(audit)
    write_outputs(audit, args.json_out, args.md_out, args.tex_out)
    print(f"total_checks: {audit['summary']['total_checks']}")
    print(f"passed_checks: {audit['summary']['passed_checks']}")
    print(f"failed_checks: {audit['summary']['failed_checks']}")
    print(f"wrote_json: {display_path(args.json_out)}")
    print(f"wrote_md: {display_path(args.md_out)}")
    print(f"wrote_tex: {display_path(args.tex_out)}")


if __name__ == "__main__":
    main()
