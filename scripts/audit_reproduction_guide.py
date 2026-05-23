#!/usr/bin/env python3
"""Audit the public SkillAdmit reproduction guide.

What this file does:
  Checks that docs/reproduction_guide.md remains aligned with the generated
  downstream evidence artifacts. It verifies command availability, aggregate
  separation, claim guardrails, no-retuning language, and README/artifact-index
  discoverability. It also checks that README.md gives a public reader enough
  context to enter the repo without confusing the main boundary, historical
  synthesis, and model-transfer addendum.

Why it is needed:
  A public repository can be technically reproducible but still misleading if
  the entry guide mixes main evidence, historical synthesis, and model-transfer
  addenda. This audit makes the public reproduction path executable and keeps
  the guide inside the supported SkillAdmit claim boundary.

Inputs:
  docs/reproduction_guide.md
  README.md
  benchmark/downstream/reports/paper_artifacts_index.json
  benchmark/downstream/reports/downstream_boundary_synthesis.json
  benchmark/downstream/reports/model_transfer_cross_model_synthesis.json

Outputs:
  benchmark/downstream/reports/reproduction_guide_audit.json
  benchmark/downstream/reports/reproduction_guide_audit.md
  benchmark/downstream/reports/reproduction_guide_audit.tex

Who runs it:
  Researchers or Codex sessions before public commits, public README edits, or
  handoff to another environment.
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

GUIDE_PATH = ROOT / "docs" / "reproduction_guide.md"
README_PATH = ROOT / "README.md"
ARTIFACT_INDEX_PATH = REPORT_DIR / "paper_artifacts_index.json"
BOUNDARY_SYNTHESIS_PATH = REPORT_DIR / "downstream_boundary_synthesis.json"
CROSS_MODEL_SYNTHESIS_PATH = REPORT_DIR / "model_transfer_cross_model_synthesis.json"

DEFAULT_JSON = REPORT_DIR / "reproduction_guide_audit.json"
DEFAULT_MD = REPORT_DIR / "reproduction_guide_audit.md"
DEFAULT_TEX = REPORT_DIR / "reproduction_guide_audit.tex"

PUBLIC_SURFACE_FORBIDDEN_PATTERNS = [
    "/home/",
    "anaconda3/envs",
    "workspace/skilladmit",
    "skilladmit/bin/python",
]

REQUIRED_COMMANDS = [
    "python scripts/check_downstream_hard_v2_tasks.py",
    "python scripts/check_downstream_hard_v3_tasks.py",
    "python scripts/build_downstream_hard_v4_tasks.py",
    "python scripts/check_downstream_hard_v4_tasks.py",
    "python scripts/run_admission_regression.py",
    "python scripts/summarize_hard_v2_results.py --assert-current-hard-v2",
    "python scripts/export_hard_v2_evidence_package.py --assert-current-hard-v2",
    "python scripts/summarize_hard_v3_results.py --assert-current-hard-v3",
    "python scripts/export_hard_v3_evidence_package.py --assert-current-hard-v3",
    "python scripts/export_hard_v4_scaffold_manifest.py --run-checker --assert-current-hard-v4-scaffold",
    "python scripts/summarize_hard_v4_results.py --assert-current-hard-v4",
    "python scripts/export_hard_v4_evidence_package.py --assert-current-hard-v4",
    "python scripts/export_downstream_cross_version_synthesis.py --assert-current-synthesis",
    "python scripts/export_downstream_boundary_synthesis.py --assert-current-boundary-synthesis",
    "python scripts/export_downstream_paper_section.py --assert-current-paper-section",
    "python scripts/export_downstream_claim_defense_matrix.py --assert-current-claim-defense",
    "python scripts/export_model_transfer_replication_protocol.py --assert-current-protocol",
    "python scripts/export_model_transfer_evidence_package.py --assert-current-model-transfer",
    "python scripts/export_model_transfer_cross_model_synthesis.py --assert-current-cross-model",
    "python scripts/export_model_transfer_paper_addendum.py --assert-current-addendum",
    "python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index",
    "python scripts/audit_paper_claim_consistency.py --assert-current-audit",
    "python scripts/audit_reporting_hygiene.py --assert-current-hygiene",
    "python scripts/audit_public_release_readiness.py --assert-current-release",
    "python scripts/audit_reproduction_guide.py --assert-current-reproduction-guide",
]


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> str:
    resolved = resolve(path)
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


def read_text(path: Path) -> str:
    return resolve(path).read_text(encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(resolve(path).read_text(encoding="utf-8"))


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


def command_script(command: str) -> str | None:
    match = re.search(r"python\s+(scripts/[A-Za-z0-9_\-/]+\.py)", command)
    if not match:
        return None
    return match.group(1)


def command_rows(commands: list[str], guide_text: str) -> list[dict[str, Any]]:
    rows = []
    for command in commands:
        script = command_script(command)
        rows.append(
            {
                "command": command,
                "present_in_guide": command in guide_text,
                "script": script,
                "script_exists": bool(script and (ROOT / script).exists()),
            }
        )
    return rows


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


def artifact_index_has_reproduction_group(index: dict[str, Any]) -> bool:
    return any(group["group_id"] == "G14_reproduction_guide" for group in index["artifact_groups"])


def artifact_index_has_audit_command(index: dict[str, Any]) -> bool:
    expected = "python scripts/audit_reproduction_guide.py --assert-current-reproduction-guide"
    return any(row["command"] == expected for row in index["regeneration_order"])


def forbidden_public_surface_hits(texts: dict[str, str]) -> list[dict[str, str]]:
    hits = []
    for source, text in texts.items():
        for line_no, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            for pattern in PUBLIC_SURFACE_FORBIDDEN_PATTERNS:
                if pattern in lowered:
                    hits.append(
                        {
                            "source": source,
                            "line": line_no,
                            "pattern": pattern,
                            "text": line.strip()[:200],
                        }
                    )
    return hits


def contains_normalized(text: str, phrase: str) -> bool:
    return " ".join(phrase.split()) in " ".join(text.split())


def build_audit(
    guide_path: Path,
    readme_path: Path,
    artifact_index_path: Path,
    boundary_path: Path,
    cross_model_path: Path,
) -> dict[str, Any]:
    guide_text = read_text(guide_path)
    readme_text = read_text(readme_path)
    artifact_index = load_json(artifact_index_path)
    boundary = load_json(boundary_path)
    cross_model = load_json(cross_model_path)

    boundary_claims = boundary["derived_claims"]
    cross_model_claims = cross_model["derived_claims"]
    rows = command_rows(REQUIRED_COMMANDS, guide_text)
    missing_commands = [row for row in rows if not row["present_in_guide"]]
    missing_scripts = [row for row in rows if not row["script_exists"]]
    forbidden_public_surface = forbidden_public_surface_hits(
        {
            "README.md": readme_text,
            "docs/reproduction_guide.md": guide_text,
        }
    )

    checks: list[dict[str, Any]] = []
    add_check(
        checks,
        "RG1_guide_is_discoverable",
        guide_path.exists()
        and "docs/reproduction_guide.md" in readme_text
        and "Reproduction Guide" in guide_text,
        "README points to the reproduction guide and the guide exists.",
        {
            "guide_exists": guide_path.exists(),
            "readme_links_guide": "docs/reproduction_guide.md" in readme_text,
        },
    )
    add_check(
        checks,
        "RG2_commands_present_and_scripts_exist",
        not missing_commands and not missing_scripts,
        "Required report-regeneration and audit commands are present and their scripts exist.",
        {"missing_commands": missing_commands, "missing_scripts": missing_scripts},
    )
    add_check(
        checks,
        "RG3_artifact_index_exposes_guide",
        artifact_index_has_reproduction_group(artifact_index) and artifact_index_has_audit_command(artifact_index),
        "Artifact index exposes the reproduction guide and the guide audit command.",
        {
            "has_group": artifact_index_has_reproduction_group(artifact_index),
            "has_audit_command": artifact_index_has_audit_command(artifact_index),
        },
    )
    add_check(
        checks,
        "RG4_main_boundary_aggregate_matches_report",
        boundary_claims["forced_bad_total_success"] == "0/133"
        and boundary_claims["forced_bad_total_public_passed_hidden_failed"] == 133
        and "0/133" in guide_text
        and "public-pass/hidden-fail cases: 133" in guide_text,
        "Guide reports the current hard_v2/hard_v3/hard_v4 main boundary aggregate.",
        {
            "report_forced_bad": boundary_claims["forced_bad_total_success"],
            "report_public_hidden": boundary_claims["forced_bad_total_public_passed_hidden_failed"],
        },
    )
    add_check(
        checks,
        "RG5_addendum_aggregate_matches_report",
        cross_model_claims["forced_bad_combined_success"] == "0/216"
        and cross_model_claims["forced_bad_combined_public_passed_hidden_failed"] == 216
        and "0/216" in guide_text
        and "public-pass/hidden-fail cases: 216" in guide_text,
        "Guide reports the model-transfer addendum aggregate without merging it into the main boundary.",
        {
            "report_forced_bad": cross_model_claims["forced_bad_combined_success"],
            "report_public_hidden": cross_model_claims[
                "forced_bad_combined_public_passed_hidden_failed"
            ],
        },
    )
    add_check(
        checks,
        "RG6_layer_roles_are_separated",
        "current main boundary" in guide_text
        and "model-transfer addendum" in guide_text
        and "historical hard_v2/hard_v3 synthesis" in guide_text
        and "0/85" in guide_text
        and "Do not merge these numbers into one leaderboard" in guide_text,
        "Guide separates current, addendum, and historical aggregate roles.",
        {},
    )
    add_check(
        checks,
        "RG7_claim_guardrails_present",
        "Do not claim universal SkillAdmit-selected superiority" in guide_text
        and "Do not claim selected token savings" in guide_text
        and "Do not claim hard_v4 proves SkillAdmit-selected utility" in guide_text
        and "model-general selected superiority" in guide_text,
        "Guide includes unsupported-claim guardrails.",
        {},
    )
    add_check(
        checks,
        "RG8_no_retuning_rule_present",
        "Do not tune hard_v2, hard_v3, or hard_v4" in guide_text
        and "predeclare a hard_v5 boundary" in guide_text,
        "Guide states the frozen-boundary no-retuning rule.",
        {},
    )
    add_check(
        checks,
        "RG9_secret_and_no_api_boundary_present",
        ".env" in guide_text
        and "do not commit `.env`" in guide_text
        and contains_normalized(guide_text, "do not require a new LLM API run"),
        "Guide states the local-secret boundary and avoids accidental API reruns.",
        {},
    )
    add_check(
        checks,
        "RG10_guide_declares_not_new_evidence",
        "This guide is not new empirical evidence" in guide_text,
        "Guide is explicitly marked as a reproduction entry, not an evidence source.",
        {},
    )
    add_check(
        checks,
        "RG11_readme_names_reader_entry_points",
        "docs/reproduction_guide.md" in readme_text
        and "benchmark/downstream/reports/paper_artifacts_index.md" in readme_text
        and "benchmark/downstream/reports/downstream_boundary_synthesis.md" in readme_text
        and "benchmark/downstream/reports/model_transfer_cross_model_synthesis.md" in readme_text,
        "README names the public reproduction guide, artifact index, main boundary, and transfer addendum.",
        {},
    )
    add_check(
        checks,
        "RG12_readme_preserves_public_claim_boundary",
        "0/133 forced_bad_artifact success" in readme_text
        and "0/216 forced_bad_artifact success" in readme_text
        and "0/85 forced_bad_artifact success" in readme_text
        and "Do not read these aggregates as one leaderboard" in readme_text
        and "Do not claim universal SkillAdmit-selected superiority" in readme_text
        and "Do not claim selected token savings" in readme_text
        and "Do not tune hard_v2, hard_v3, or hard_v4" in readme_text,
        "README exposes the aggregate roles and unsupported-claim guardrails.",
        {},
    )
    add_check(
        checks,
        "RG13_public_surface_avoids_local_paths",
        not forbidden_public_surface
        and "cd SkillAdmit" in guide_text
        and "python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index" in guide_text,
        "README and reproduction guide avoid machine-specific absolute paths.",
        {"forbidden_public_surface_hits": forbidden_public_surface},
    )

    failures = [row for row in checks if row["status"] != "pass"]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Public reproduction-guide audit for SkillAdmit. It checks that the "
            "public entry guide matches the generated downstream evidence "
            "boundary and avoids unsupported claims."
        ),
        "summary": {
            "total_checks": len(checks),
            "passed_checks": len(checks) - len(failures),
            "failed_checks": len(failures),
            "status": "pass" if not failures else "fail",
        },
        "checked_commands": rows,
        "aggregate_roles": {
            "current_main_boundary": {
                "aggregate": boundary_claims["forced_bad_total_success"],
                "public_passed_hidden_failed": boundary_claims[
                    "forced_bad_total_public_passed_hidden_failed"
                ],
                "role": "hard_v2/hard_v3/hard_v4 downstream validation",
            },
            "model_transfer_addendum": {
                "aggregate": cross_model_claims["forced_bad_combined_success"],
                "public_passed_hidden_failed": cross_model_claims[
                    "forced_bad_combined_public_passed_hidden_failed"
                ],
                "role": "two-model hard_v3/hard_v4 sensitivity layer",
            },
            "historical_two_boundary": {
                "aggregate": "0/85",
                "role": "historical hard_v2/hard_v3 synthesis only",
            },
        },
        "checks": checks,
        "source_files": [
            source_file("reproduction_guide", guide_path),
            source_file("readme", readme_path),
            source_file("artifact_index", artifact_index_path),
            source_file("boundary_synthesis", boundary_path),
            source_file("cross_model_synthesis", cross_model_path),
        ],
        "next_recommended_step": (
            "Use this audit with the claim, reporting, and release audits before "
            "public README edits or release pushes."
        ),
    }


def assert_reproduction_guide(audit: dict[str, Any]) -> None:
    if audit["summary"]["total_checks"] != 13:
        raise AssertionError(f"expected 13 checks, got {audit['summary']['total_checks']}")
    if audit["summary"]["failed_checks"] != 0:
        failures = [row for row in audit["checks"] if row["status"] != "pass"]
        raise AssertionError(f"failed reproduction-guide checks: {failures}")
    rendered = render_markdown(audit)
    required = [
        "0/85",
        "0/133",
        "0/216",
        "current hard_v2/hard_v3/hard_v4",
        "model-transfer addendum",
        "audit_reproduction_guide.py --assert-current-reproduction-guide",
    ]
    for phrase in required:
        if phrase not in rendered:
            raise AssertionError(f"missing reproduction-guide phrase: {phrase}")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def compact(value: Any, limit: int = 180) -> str:
    text = " ".join(str(value).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def render_markdown(audit: dict[str, Any]) -> str:
    role_rows = [
        [name, item["aggregate"], item.get("public_passed_hidden_failed", ""), item["role"]]
        for name, item in audit["aggregate_roles"].items()
    ]
    check_rows = [
        [row["check_id"], row["status"], row["summary"], compact(row["details"])]
        for row in audit["checks"]
    ]
    command_rows = [
        [
            f"`{row['command']}`",
            row["present_in_guide"],
            row["script_exists"],
        ]
        for row in audit["checked_commands"]
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
            "# Reproduction Guide Audit",
            f"Generated at UTC: `{audit['generated_at_utc']}`",
            audit["purpose"],
            "## Summary",
            md_table(["metric", "value"], [[key, value] for key, value in audit["summary"].items()]),
            "## Aggregate Roles",
            md_table(["layer", "aggregate", "public_hidden", "role"], role_rows),
            "## Checks",
            md_table(["check", "status", "summary", "details"], check_rows),
            "## Checked Commands",
            md_table(["command", "present_in_guide", "script_exists"], command_rows),
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
        "% Auto-generated by scripts/audit_reproduction_guide.py",
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
    parser.add_argument("--guide", type=Path, default=GUIDE_PATH)
    parser.add_argument("--readme", type=Path, default=README_PATH)
    parser.add_argument("--artifact-index", type=Path, default=ARTIFACT_INDEX_PATH)
    parser.add_argument("--boundary-synthesis", type=Path, default=BOUNDARY_SYNTHESIS_PATH)
    parser.add_argument("--cross-model-synthesis", type=Path, default=CROSS_MODEL_SYNTHESIS_PATH)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX)
    parser.add_argument(
        "--assert-current-reproduction-guide",
        action="store_true",
        help="Assert current public reproduction-guide invariants.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = build_audit(
        args.guide,
        args.readme,
        args.artifact_index,
        args.boundary_synthesis,
        args.cross_model_synthesis,
    )
    if args.assert_current_reproduction_guide:
        assert_reproduction_guide(audit)
    write_outputs(audit, args.json_out, args.md_out, args.tex_out)
    print(f"total_checks: {audit['summary']['total_checks']}")
    print(f"passed_checks: {audit['summary']['passed_checks']}")
    print(f"failed_checks: {audit['summary']['failed_checks']}")
    print(f"wrote_json: {display_path(args.json_out)}")
    print(f"wrote_md: {display_path(args.md_out)}")
    print(f"wrote_tex: {display_path(args.tex_out)}")


if __name__ == "__main__":
    main()
