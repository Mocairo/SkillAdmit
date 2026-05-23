#!/usr/bin/env python3
"""Audit public-release readiness for the SkillAdmit repository.

What this file does:
  Performs repository-level release checks that sit below the scientific
  downstream audits: secret hygiene, ignored local artifacts, tracked cache
  files, tracked workspace files, large-file thresholds, and regeneration
  command availability.

Why it is needed:
  SkillAdmit is becoming a public experimental repository. The evidence files
  are useful, but the repository should not accidentally publish `.env`, local
  LLM workspaces, caches, or credentials. This script turns those checks into a
  repeatable release artifact.

Inputs:
  .gitignore
  Git index and working tree metadata
  README.md
  benchmark/downstream/reports/paper_artifacts_index.json

Outputs:
  benchmark/downstream/reports/public_release_readiness_audit.json
  benchmark/downstream/reports/public_release_readiness_audit.md
  benchmark/downstream/reports/public_release_readiness_audit.tex

Who runs it:
  Researchers or Codex sessions before public pushes, release tags, or handoff
  to another environment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "benchmark" / "downstream" / "reports"
DEFAULT_ARTIFACT_INDEX = REPORT_DIR / "paper_artifacts_index.json"
DEFAULT_JSON = REPORT_DIR / "public_release_readiness_audit.json"
DEFAULT_MD = REPORT_DIR / "public_release_readiness_audit.md"
DEFAULT_TEX = REPORT_DIR / "public_release_readiness_audit.tex"

MAX_TRACKED_FILE_BYTES = 2_000_000
EXPECTED_IGNORED_PATHS = [
    ".env",
    "__pycache__/",
    ".pytest_cache/",
    "benchmark/agent_runs/heuristic_agent_v0/trajectories.jsonl",
    "benchmark/downstream/llm_runs/llm_downstream_hard_v4_transfer_mimo_v2_5_strict_24x8/workspaces/",
]
FORBIDDEN_TRACKED_PATTERNS = [
    ".env",
    ".pyc",
    "__pycache__/",
    ".pytest_cache/",
    "benchmark/agent_runs/",
    "/workspaces/",
]
SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----"),
    re.compile(r"(?i)\b(api[_-]?key|secret|token)\s*=\s*['\"]?[A-Za-z0-9_\-]{24,}"),
]
SECRET_SCAN_SKIP_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".zip",
    ".gz",
    ".pyc",
}
SECRET_SCAN_SKIP_PATH_PARTS = {
    "public_release_readiness_audit.json",
    "public_release_readiness_audit.md",
    "public_release_readiness_audit.tex",
}


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


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with resolve(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(resolve(path).read_text(encoding="utf-8"))


def tracked_files() -> list[str]:
    output = run_git(["ls-files", "-z"]).stdout
    return [item for item in output.split("\0") if item]


def git_status_short() -> list[str]:
    output = run_git(["status", "--short", "--untracked-files=all"]).stdout
    return [line for line in output.splitlines() if line.strip()]


def check_ignore(path: str) -> dict[str, Any]:
    result = run_git(["check-ignore", "-v", path], check=False)
    return {
        "path": path,
        "ignored": result.returncode == 0,
        "rule": result.stdout.strip() if result.returncode == 0 else "",
    }


def tracked_forbidden(files: list[str]) -> list[str]:
    bad = []
    for path in files:
        normalized = path.replace("\\", "/")
        if normalized == ".env":
            bad.append(path)
            continue
        if normalized.endswith(".pyc"):
            bad.append(path)
            continue
        if any(pattern in normalized for pattern in FORBIDDEN_TRACKED_PATTERNS if pattern not in {".env", ".pyc"}):
            bad.append(path)
    return sorted(set(bad))


def tracked_large_files(files: list[str]) -> list[dict[str, Any]]:
    rows = []
    for path in files:
        resolved = ROOT / path
        if not resolved.exists() or not resolved.is_file():
            continue
        size = resolved.stat().st_size
        if size > MAX_TRACKED_FILE_BYTES:
            rows.append(
                {
                    "path": path,
                    "size_bytes": size,
                    "size_mib": round(size / (1024 * 1024), 3),
                }
            )
    return sorted(rows, key=lambda row: row["size_bytes"], reverse=True)


def top_tracked_files(files: list[str], limit: int = 15) -> list[dict[str, Any]]:
    rows = []
    for path in files:
        resolved = ROOT / path
        if not resolved.exists() or not resolved.is_file():
            continue
        size = resolved.stat().st_size
        rows.append({"path": path, "size_bytes": size, "size_mib": round(size / (1024 * 1024), 3)})
    return sorted(rows, key=lambda row: row["size_bytes"], reverse=True)[:limit]


def should_secret_scan(path: str) -> bool:
    lowered = path.lower()
    if any(part in lowered for part in SECRET_SCAN_SKIP_PATH_PARTS):
        return False
    return Path(path).suffix.lower() not in SECRET_SCAN_SKIP_SUFFIXES


def scan_tracked_secrets(files: list[str]) -> list[dict[str, Any]]:
    hits = []
    for path in files:
        if not should_secret_scan(path):
            continue
        resolved = ROOT / path
        if not resolved.exists() or not resolved.is_file():
            continue
        if resolved.stat().st_size > 3_000_000:
            continue
        try:
            text = resolved.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if "OPENAI_API_KEY=<secret" in line or "API key" in line or "<secret" in line:
                continue
            for pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    hits.append(
                        {
                            "path": path,
                            "line": line_no,
                            "pattern": pattern.pattern,
                            "redacted_line": pattern.sub("<redacted>", line.strip())[:200],
                        }
                    )
    return hits


def command_script_name(command: str) -> str | None:
    match = re.search(r"python\s+(scripts/[A-Za-z0-9_\-/]+\.py)", command)
    if not match:
        return None
    return match.group(1)


def regeneration_order(index: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in index.get("regeneration_order", []):
        command = item["command"]
        script = command_script_name(command)
        rows.append(
            {
                "step": item["step"],
                "name": item["name"],
                "command": command,
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


def build_audit(artifact_index_path: Path) -> dict[str, Any]:
    files = tracked_files()
    status = git_status_short()
    ignore_rows = [check_ignore(path) for path in EXPECTED_IGNORED_PATHS]
    forbidden = tracked_forbidden(files)
    secret_hits = scan_tracked_secrets(files)
    large_files = tracked_large_files(files)
    top_files = top_tracked_files(files)
    artifact_index = load_json(artifact_index_path)
    regen = regeneration_order(artifact_index)
    missing_regen_scripts = [row for row in regen if not row["script_exists"]]

    checks: list[dict[str, Any]] = []
    dirty_risk_lines = [
        line
        for line in status
        if any(
            pattern in line
            for pattern in [
                ".env",
                "__pycache__",
                ".pytest_cache",
                "benchmark/agent_runs/",
                "/workspaces/",
            ]
        )
    ]
    add_check(
        checks,
        "R1_no_dirty_sensitive_or_local_paths",
        not dirty_risk_lines,
        "Git status does not expose dirty sensitive, cache, local agent-run, or LLM workspace paths.",
        {"dirty_risk_lines": dirty_risk_lines, "status_line_count": len(status)},
    )
    add_check(
        checks,
        "R2_expected_local_artifacts_ignored",
        all(row["ignored"] for row in ignore_rows),
        ".env, local agent runs, workspaces, and cache paths are ignored by Git.",
        {"ignore_rows": ignore_rows},
    )
    add_check(
        checks,
        "R3_no_forbidden_tracked_paths",
        not forbidden,
        "No tracked .env, pycache, pytest cache, local agent run, or LLM workspace paths.",
        {"forbidden_tracked_paths": forbidden},
    )
    add_check(
        checks,
        "R4_no_obvious_tracked_secrets",
        not secret_hits,
        "No obvious credential patterns were found in tracked text files.",
        {"secret_hits": secret_hits[:20], "hit_count": len(secret_hits)},
    )
    add_check(
        checks,
        "R5_no_tracked_file_over_threshold",
        not large_files,
        f"No tracked file exceeds {MAX_TRACKED_FILE_BYTES} bytes.",
        {"large_files": large_files},
    )
    add_check(
        checks,
        "R6_regeneration_scripts_exist",
        not missing_regen_scripts,
        "All script paths referenced in the artifact-index regeneration order exist.",
        {"missing_regen_scripts": missing_regen_scripts},
    )
    add_check(
        checks,
        "R7_release_docs_name_local_secret_boundary",
        "secrets belong in `.env`" in (ROOT / "README.md").read_text(encoding="utf-8")
        and "OPENAI_API_KEY=<secret" in (ROOT / "docs" / "experiment_handoff.md").read_text(encoding="utf-8"),
        "README and handoff docs explicitly keep runtime secrets in ignored local .env.",
        {},
    )

    failures = [row for row in checks if row["status"] != "pass"]
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Public-release readiness audit for repository hygiene. This is not "
            "new empirical evidence; it checks whether the repo is safe and "
            "recoverable to publish."
        ),
        "source_files": [
            {
                "name": "gitignore",
                "path": ".gitignore",
                "sha256": sha256_file(ROOT / ".gitignore"),
            },
            {
                "name": "readme",
                "path": "README.md",
                "sha256": sha256_file(ROOT / "README.md"),
            },
            {
                "name": "artifact_index",
                "path": display_path(artifact_index_path),
                "sha256": sha256_file(artifact_index_path),
            },
        ],
        "summary": {
            "total_checks": len(checks),
            "passed_checks": len(checks) - len(failures),
            "failed_checks": len(failures),
            "status": "pass" if not failures else "fail",
        },
        "checks": checks,
        "tracked_file_count": len(files),
        "top_tracked_files": top_files,
        "regeneration_order": regen,
        "release_notes": {
            "commit_do_not_include": [
                ".env",
                "benchmark/downstream/llm_runs/*/workspaces/",
                "benchmark/agent_runs/",
                "__pycache__/",
                ".pytest_cache/",
            ],
            "primary_reproduction_command": "python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index",
            "final_release_checks": [
                "python scripts/audit_paper_claim_consistency.py --assert-current-audit",
                "python scripts/audit_reporting_hygiene.py --assert-current-hygiene",
                "python scripts/audit_public_release_readiness.py --assert-current-release",
                "python scripts/audit_reproduction_guide.py --assert-current-reproduction-guide",
                "python scripts/audit_release_candidate.py --assert-current-release-candidate",
            ],
        },
    }


def assert_release(audit: dict[str, Any]) -> None:
    if audit["summary"]["total_checks"] != 7:
        raise AssertionError(f"expected 7 checks, got {audit['summary']['total_checks']}")
    if audit["summary"]["failed_checks"] != 0:
        failures = [row for row in audit["checks"] if row["status"] != "pass"]
        raise AssertionError(f"failed release readiness checks: {failures}")
    rendered = render_markdown(audit)
    required = [
        ".env",
        "workspaces",
        "No obvious credential patterns",
        "audit_public_release_readiness.py --assert-current-release",
    ]
    for phrase in required:
        if phrase not in rendered:
            raise AssertionError(f"missing release-readiness phrase: {phrase}")


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
    check_rows = [
        [row["check_id"], row["status"], row["summary"], compact(row["details"])]
        for row in audit["checks"]
    ]
    top_file_rows = [
        [row["path"], row["size_bytes"], row["size_mib"]]
        for row in audit["top_tracked_files"]
    ]
    command_rows = [
        [row["step"], row["name"], f"`{row['command']}`", row["script_exists"]]
        for row in audit["regeneration_order"]
    ]
    source_rows = [
        [row["name"], f"`{row['path']}`", f"`{row['sha256'][:16]}`"]
        for row in audit["source_files"]
    ]
    return "\n\n".join(
        [
            "# Public Release Readiness Audit",
            f"Generated at UTC: `{audit['generated_at_utc']}`",
            audit["purpose"],
            "## Summary",
            md_table(["metric", "value"], [[key, value] for key, value in audit["summary"].items()]),
            "## Checks",
            md_table(["check", "status", "summary", "details"], check_rows),
            "## Top Tracked Files",
            md_table(["path", "bytes", "MiB"], top_file_rows),
            "## Regeneration Order",
            md_table(["step", "name", "command", "script_exists"], command_rows),
            "## Release Notes",
            md_table(
                ["topic", "value"],
                [
                    ["commit_do_not_include", ", ".join(audit["release_notes"]["commit_do_not_include"])],
                    ["primary_reproduction_command", f"`{audit['release_notes']['primary_reproduction_command']}`"],
                    ["final_release_checks", "<br>".join(f"`{cmd}`" for cmd in audit["release_notes"]["final_release_checks"])],
                ],
            ),
            "## Source Files",
            md_table(["name", "path", "sha256"], source_rows),
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
        "% Auto-generated by scripts/audit_public_release_readiness.py",
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
    lines.extend(["\\hline", "\\end{tabular}", "", "% Release notes:"])
    for command in audit["release_notes"]["final_release_checks"]:
        lines.append(f"% {tex_escape(command)}")
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
    parser.add_argument("--artifact-index", type=Path, default=DEFAULT_ARTIFACT_INDEX)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX)
    parser.add_argument(
        "--assert-current-release",
        action="store_true",
        help="Assert current public-release readiness invariants.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = build_audit(args.artifact_index)
    if args.assert_current_release:
        assert_release(audit)
    write_outputs(audit, args.json_out, args.md_out, args.tex_out)
    print(f"total_checks: {audit['summary']['total_checks']}")
    print(f"passed_checks: {audit['summary']['passed_checks']}")
    print(f"failed_checks: {audit['summary']['failed_checks']}")
    print(f"tracked_file_count: {audit['tracked_file_count']}")
    print(f"wrote_json: {display_path(args.json_out)}")
    print(f"wrote_md: {display_path(args.md_out)}")
    print(f"wrote_tex: {display_path(args.tex_out)}")


if __name__ == "__main__":
    main()
