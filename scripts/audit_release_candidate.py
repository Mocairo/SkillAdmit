#!/usr/bin/env python3
"""Audit the SkillAdmit public release candidate.

What this file does:
  Aggregates the existing public-facing audits and repository metadata into one
  release-candidate check. It verifies that claim consistency, reporting
  hygiene, public release readiness, and reproduction-guide checks all pass;
  that the main downstream boundary remains separate from the model-transfer
  addendum and historical synthesis; and that Git status does not expose local
  secrets, workspaces, agent runs, or frozen evaluation edits.

Why it is needed:
  The repository now has several smaller audits. Before a public push or release
  tag, there should be one final check that confirms the public surface is
  coherent without re-running LLM APIs or converting release hygiene into new
  experimental evidence.

Inputs:
  README.md
  docs/reproduction_guide.md
  benchmark/downstream/reports/paper_artifacts_index.json
  benchmark/downstream/reports/paper_claim_consistency_audit.json
  benchmark/downstream/reports/reporting_hygiene_audit.json
  benchmark/downstream/reports/public_release_readiness_audit.json
  benchmark/downstream/reports/reproduction_guide_audit.json
  Git index and working tree metadata

Outputs:
  benchmark/downstream/reports/release_candidate_audit.json
  benchmark/downstream/reports/release_candidate_audit.md
  benchmark/downstream/reports/release_candidate_audit.tex

Who runs it:
  Researchers or maintainers immediately before public pushes, release tags, or
  a final handoff to another environment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "benchmark" / "downstream" / "reports"

README = ROOT / "README.md"
REPRODUCTION_GUIDE = ROOT / "docs" / "reproduction_guide.md"
ARTIFACT_INDEX = REPORT_DIR / "paper_artifacts_index.json"
CLAIM_AUDIT = REPORT_DIR / "paper_claim_consistency_audit.json"
REPORTING_AUDIT = REPORT_DIR / "reporting_hygiene_audit.json"
RELEASE_AUDIT = REPORT_DIR / "public_release_readiness_audit.json"
REPRODUCTION_AUDIT = REPORT_DIR / "reproduction_guide_audit.json"

DEFAULT_JSON = REPORT_DIR / "release_candidate_audit.json"
DEFAULT_MD = REPORT_DIR / "release_candidate_audit.md"
DEFAULT_TEX = REPORT_DIR / "release_candidate_audit.tex"

EXPECTED_AUDIT_TOTALS = {
    "paper_claim_consistency": 13,
    "reporting_hygiene": 8,
    "public_release_readiness": 7,
    "reproduction_guide": 13,
}

LOCAL_PUBLIC_SURFACE_PATTERNS = [
    "/home/",
    "anaconda3/envs",
    "workspace/skilladmit",
    "skilladmit/bin/python",
]

DIRTY_RISK_PATTERNS = [
    ".env",
    "__pycache__",
    ".pytest_cache",
    "benchmark/agent_runs/",
    "/workspaces/",
]

FROZEN_EVAL_STATUS_PATTERNS = [
    "benchmark/downstream_hard_v2/",
    "benchmark/downstream_hard_v3/",
    "benchmark/downstream_hard_v4/",
    "benchmark/downstream/llm_runs/",
    "benchmark/agent_runs/",
]

FORBIDDEN_TRACKED_PATTERNS = [
    ".env",
    ".pyc",
    "__pycache__/",
    ".pytest_cache/",
    "benchmark/agent_runs/",
    "/workspaces/",
]

RELEASE_CANDIDATE_COMMAND = "python scripts/audit_release_candidate.py --assert-current-release-candidate"


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> str:
    resolved = resolve(path)
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


def run_git(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
    )


def git_status_short() -> list[str]:
    output = run_git(["status", "--short", "--untracked-files=all"]).stdout
    return [line for line in output.splitlines() if line.strip()]


def tracked_files() -> list[str]:
    output = run_git(["ls-files", "-z"]).stdout
    return [item for item in output.split("\0") if item]


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


def audit_summary_row(name: str, audit: dict[str, Any]) -> dict[str, Any]:
    summary = audit.get("summary", {})
    return {
        "name": name,
        "total_checks": summary.get("total_checks"),
        "passed_checks": summary.get("passed_checks"),
        "failed_checks": summary.get("failed_checks"),
        "status": summary.get("status"),
    }


def audit_passes(name: str, audit: dict[str, Any]) -> bool:
    summary = audit.get("summary", {})
    return (
        summary.get("status") == "pass"
        and summary.get("failed_checks") == 0
        and summary.get("total_checks") == EXPECTED_AUDIT_TOTALS[name]
    )


def regeneration_has_command(index: dict[str, Any], command: str) -> bool:
    return any(row.get("command") == command for row in index.get("regeneration_order", []))


def forbidden_public_hits(texts: dict[str, str]) -> list[dict[str, Any]]:
    hits = []
    for source, text in texts.items():
        lowered_lines = [(line_no, line, line.lower()) for line_no, line in enumerate(text.splitlines(), start=1)]
        for line_no, line, lowered in lowered_lines:
            for pattern in LOCAL_PUBLIC_SURFACE_PATTERNS:
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


def status_hits(status: list[str], patterns: list[str]) -> list[str]:
    return [line for line in status if any(pattern in line for pattern in patterns)]


def forbidden_tracked(files: list[str]) -> list[str]:
    hits = []
    for path in files:
        normalized = path.replace("\\", "/")
        if normalized == ".env" or normalized.endswith(".pyc"):
            hits.append(path)
            continue
        if any(pattern in normalized for pattern in FORBIDDEN_TRACKED_PATTERNS if pattern not in {".env", ".pyc"}):
            hits.append(path)
    return sorted(set(hits))


def contains_normalized(text: str, phrase: str) -> bool:
    return " ".join(phrase.split()) in " ".join(text.split())


def build_audit() -> dict[str, Any]:
    readme = read_text(README)
    guide = read_text(REPRODUCTION_GUIDE)
    index = load_json(ARTIFACT_INDEX)
    claim_audit = load_json(CLAIM_AUDIT)
    reporting_audit = load_json(REPORTING_AUDIT)
    release_audit = load_json(RELEASE_AUDIT)
    reproduction_audit = load_json(REPRODUCTION_AUDIT)
    status = git_status_short()
    files = tracked_files()

    audits = {
        "paper_claim_consistency": claim_audit,
        "reporting_hygiene": reporting_audit,
        "public_release_readiness": release_audit,
        "reproduction_guide": reproduction_audit,
    }
    audit_rows = [audit_summary_row(name, audit) for name, audit in audits.items()]
    facts = index["key_current_facts"]
    checks: list[dict[str, Any]] = []

    add_check(
        checks,
        "RC1_source_audits_pass",
        all(audit_passes(name, audit) for name, audit in audits.items()),
        "All source audits pass with the expected check counts.",
        {"audit_rows": audit_rows, "expected_totals": EXPECTED_AUDIT_TOTALS},
    )
    add_check(
        checks,
        "RC2_boundary_facts_stable",
        facts["boundary_forced_bad_total_success"] == "0/133"
        and facts["boundary_forced_bad_total_tasks"] == 133
        and facts["cross_model_forced_bad_combined_success"] == "0/216"
        and facts["cross_model_forced_bad_public_passed_hidden_failed"] == 216
        and facts["forced_bad_total_tasks"] == 85
        and facts["forced_bad_total_successes"] == 0
        and facts["boundary_selected_superiority_consistent"] is False
        and facts["boundary_selected_token_savings_consistent"] is False,
        "Main boundary, model-transfer addendum, and historical aggregate facts remain separated.",
        {
            "boundary": facts["boundary_forced_bad_total_success"],
            "cross_model": facts["cross_model_forced_bad_combined_success"],
            "historical_tasks": facts["forced_bad_total_tasks"],
            "selected_superiority_consistent": facts["boundary_selected_superiority_consistent"],
            "selected_token_savings_consistent": facts["boundary_selected_token_savings_consistent"],
        },
    )
    add_check(
        checks,
        "RC3_artifact_index_registers_release_candidate",
        len(index["artifact_groups"]) == 14
        and regeneration_has_command(index, RELEASE_CANDIDATE_COMMAND)
        and any(group["group_id"] == "G14_reproduction_guide" for group in index["artifact_groups"]),
        "Artifact index keeps the evidence groups stable and registers the release-candidate audit command.",
        {
            "artifact_group_count": len(index["artifact_groups"]),
            "has_release_candidate_command": regeneration_has_command(index, RELEASE_CANDIDATE_COMMAND),
        },
    )
    add_check(
        checks,
        "RC4_public_docs_explain_entrypoints_and_boundaries",
        "docs/reproduction_guide.md" in readme
        and "benchmark/downstream/reports/paper_artifacts_index.md" in readme
        and "0/133 forced_bad_artifact success" in readme
        and "0/216 forced_bad_artifact success" in readme
        and "historical forced_bad_artifact aggregate: 0/85" in guide
        and "Do not merge these numbers into one leaderboard" in guide,
        "README and reproduction guide expose entry points and aggregate roles.",
        {},
    )
    public_hits = forbidden_public_hits({"README.md": readme, "docs/reproduction_guide.md": guide})
    add_check(
        checks,
        "RC5_public_surface_has_no_local_paths",
        not public_hits,
        "Public entry files do not contain machine-specific local paths.",
        {"public_surface_hits": public_hits},
    )
    dirty_risk = status_hits(status, DIRTY_RISK_PATTERNS)
    add_check(
        checks,
        "RC6_git_status_has_no_sensitive_or_local_paths",
        not dirty_risk,
        "Git status does not expose dirty sensitive, local-run, cache, or workspace paths.",
        {"dirty_risk_lines": dirty_risk, "status_line_count": len(status)},
    )
    frozen_status = status_hits(status, FROZEN_EVAL_STATUS_PATTERNS)
    add_check(
        checks,
        "RC7_no_frozen_eval_boundary_files_changed",
        not frozen_status,
        "Git status does not include frozen task suites, LLM run workspaces, or local agent runs.",
        {"frozen_status_lines": frozen_status},
    )
    tracked_forbidden = forbidden_tracked(files)
    add_check(
        checks,
        "RC8_no_forbidden_tracked_paths",
        not tracked_forbidden,
        "No tracked .env, cache, workspace, or local agent-run paths.",
        {"forbidden_tracked_paths": tracked_forbidden},
    )
    release_notes = release_audit.get("release_notes", {})
    add_check(
        checks,
        "RC9_final_release_command_registered",
        RELEASE_CANDIDATE_COMMAND in readme
        and RELEASE_CANDIDATE_COMMAND in guide
        and RELEASE_CANDIDATE_COMMAND in release_notes.get("final_release_checks", []),
        "Final release-candidate command is visible in README, reproduction guide, and release notes.",
        {
            "readme": RELEASE_CANDIDATE_COMMAND in readme,
            "guide": RELEASE_CANDIDATE_COMMAND in guide,
            "release_notes": RELEASE_CANDIDATE_COMMAND in release_notes.get("final_release_checks", []),
        },
    )
    add_check(
        checks,
        "RC10_release_candidate_is_not_evidence",
        contains_normalized(__doc__ or "", "release-candidate check")
        and contains_normalized(__doc__ or "", "new experimental evidence")
        and "not new empirical evidence" in readme + guide,
        "Release-candidate audit is framed as public-release hygiene, not empirical evidence.",
        {},
    )

    failures = [row for row in checks if row["status"] != "pass"]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Final public release-candidate audit for SkillAdmit. This audit is "
            "not new empirical evidence; it aggregates existing public checks "
            "and verifies that the release surface stays inside the frozen "
            "downstream claim boundary."
        ),
        "summary": {
            "total_checks": len(checks),
            "passed_checks": len(checks) - len(failures),
            "failed_checks": len(failures),
            "status": "pass" if not failures else "fail",
        },
        "aggregate_roles": {
            "current_main_boundary": "0/133 hard_v2/hard_v3/hard_v4 forced_bad_artifact",
            "model_transfer_addendum": "0/216 hard_v3/hard_v4 two-model forced_bad_artifact",
            "historical_two_boundary": "0/85 hard_v2/hard_v3 forced_bad_artifact",
        },
        "source_audit_rows": audit_rows,
        "git_status_line_count": len(status),
        "checks": checks,
        "source_files": [
            source_file("readme", README),
            source_file("reproduction_guide", REPRODUCTION_GUIDE),
            source_file("artifact_index", ARTIFACT_INDEX),
            source_file("paper_claim_consistency_audit", CLAIM_AUDIT),
            source_file("reporting_hygiene_audit", REPORTING_AUDIT),
            source_file("public_release_readiness_audit", RELEASE_AUDIT),
            source_file("reproduction_guide_audit", REPRODUCTION_AUDIT),
        ],
        "next_recommended_step": (
            "If this audit and the deterministic downstream checkers pass, the "
            "next step is a public push or release tag, not more hard_v2/hard_v3/"
            "hard_v4 tuning."
        ),
    }


def assert_release_candidate(audit: dict[str, Any]) -> None:
    if audit["summary"]["total_checks"] != 10:
        raise AssertionError(f"expected 10 checks, got {audit['summary']['total_checks']}")
    if audit["summary"]["failed_checks"] != 0:
        failures = [row for row in audit["checks"] if row["status"] != "pass"]
        raise AssertionError(f"failed release-candidate checks: {failures}")
    rendered = render_markdown(audit)
    required = [
        "0/133",
        "0/216",
        "0/85",
        "RC1_source_audits_pass",
        "RC10_release_candidate_is_not_evidence",
        RELEASE_CANDIDATE_COMMAND,
    ]
    for phrase in required:
        if phrase not in rendered:
            raise AssertionError(f"missing release-candidate phrase: {phrase}")


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
    role_rows = [[name, value] for name, value in audit["aggregate_roles"].items()]
    audit_rows = [
        [row["name"], row["total_checks"], row["passed_checks"], row["failed_checks"], row["status"]]
        for row in audit["source_audit_rows"]
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
            "# Release Candidate Audit",
            f"Generated at UTC: `{audit['generated_at_utc']}`",
            audit["purpose"],
            "## Summary",
            md_table(["metric", "value"], [[key, value] for key, value in audit["summary"].items()]),
            "## Aggregate Roles",
            md_table(["layer", "role"], role_rows),
            "## Source Audits",
            md_table(["audit", "total", "passed", "failed", "status"], audit_rows),
            "## Checks",
            md_table(["check", "status", "summary", "details"], check_rows),
            "## Release Candidate Command",
            f"`{RELEASE_CANDIDATE_COMMAND}`",
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
        "% Auto-generated by scripts/audit_release_candidate.py",
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
    for name, value in audit["aggregate_roles"].items():
        lines.append(f"% {tex_escape(name)} = {tex_escape(value)}")
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
        "--assert-current-release-candidate",
        action="store_true",
        help="Assert current public release-candidate invariants.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = build_audit()
    if args.assert_current_release_candidate:
        assert_release_candidate(audit)
    write_outputs(audit, args.json_out, args.md_out, args.tex_out)
    print(f"total_checks: {audit['summary']['total_checks']}")
    print(f"passed_checks: {audit['summary']['passed_checks']}")
    print(f"failed_checks: {audit['summary']['failed_checks']}")
    print(f"status_line_count: {audit['git_status_line_count']}")
    print(f"wrote_json: {display_path(args.json_out)}")
    print(f"wrote_md: {display_path(args.md_out)}")
    print(f"wrote_tex: {display_path(args.tex_out)}")


if __name__ == "__main__":
    main()
