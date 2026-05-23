#!/usr/bin/env python3
"""Export a predeclared model-transfer replication protocol for SkillAdmit.

What this file does:
  Builds a paper-facing protocol for running the frozen hard_v3/hard_v4
  downstream matrices with a second model. It records the exact suites,
  strategies, commands, stop rules, claim boundaries, and prerequisite checks.

Why it is needed:
  The current downstream evidence was produced with one main LLM backend. The
  next clean scientific step is not tuning hard_v3 or hard_v4, but asking
  whether the same conditional-utility and negative-transfer boundaries hold
  under a predeclared transfer model.

Inputs:
  benchmark/downstream/reports/downstream_boundary_synthesis.json
  benchmark/downstream/reports/paper_claim_consistency_audit.json

Outputs:
  benchmark/downstream/reports/model_transfer_replication_protocol.json
  benchmark/downstream/reports/model_transfer_replication_protocol.md
  benchmark/downstream/reports/model_transfer_replication_protocol.tex

Who runs it:
  Researchers or Codex sessions before any model-transfer LLM run. Generate this
  protocol first, then run the listed commands without changing prompts,
  strategies, task files, or hidden verifiers.
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

DEFAULT_BOUNDARY = REPORT_DIR / "downstream_boundary_synthesis.json"
DEFAULT_AUDIT = REPORT_DIR / "paper_claim_consistency_audit.json"
DEFAULT_JSON = REPORT_DIR / "model_transfer_replication_protocol.json"
DEFAULT_MD = REPORT_DIR / "model_transfer_replication_protocol.md"
DEFAULT_TEX = REPORT_DIR / "model_transfer_replication_protocol.tex"

TRANSFER_MODEL_ENV = "SKILLADMIT_TRANSFER_MODEL"
TRANSFER_MODEL_PLACEHOLDER = f"${TRANSFER_MODEL_ENV}"
DEFAULT_MODEL_SLUG = "transfer_model"

TREE_STRATEGIES = [
    "no_experience",
    "skilladmit_selected",
    "skilladmit_selected_with_precondition_context",
    "raw_memory",
    "distilled_skills_all",
    "promoted_rules",
    "bad_dependency_rule",
    "forced_bad_artifact",
]

STRICT_STRATEGIES = [
    "no_experience",
    "skilladmit_selected",
    "skilladmit_selected_with_precondition_only",
    "raw_memory",
    "distilled_skills_all",
    "promoted_rules",
    "bad_dependency_rule",
    "forced_bad_artifact",
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


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with resolve(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def strategy_flags(strategies: list[str]) -> str:
    return " ".join(f"--strategy {strategy}" for strategy in strategies)


def run_specs(model_slug: str, transfer_model_expr: str) -> list[dict[str, Any]]:
    base = "python scripts/run_llm_downstream_validation.py"
    return [
        {
            "run_id": "MT1_hard_v3_tree",
            "suite": "hard_v3",
            "setting": "tree-aware",
            "tasks_dir": "benchmark/downstream_hard_v3/tasks",
            "run_name": f"llm_downstream_hard_v3_transfer_{model_slug}_tree_30x8",
            "strategies": TREE_STRATEGIES,
            "include_repo_tree": True,
            "use_task_visible_files": True,
            "expected_rows": 30 * len(TREE_STRATEGIES),
            "command": (
                f'{base} --model "{transfer_model_expr}" '
                f"--run-name llm_downstream_hard_v3_transfer_{model_slug}_tree_30x8 "
                "--tasks-dir benchmark/downstream_hard_v3/tasks "
                f"{strategy_flags(TREE_STRATEGIES)} "
                "--use-task-visible-files --include-repo-tree --resume"
            ),
        },
        {
            "run_id": "MT2_hard_v3_strict",
            "suite": "hard_v3",
            "setting": "strict visible-file",
            "tasks_dir": "benchmark/downstream_hard_v3/tasks",
            "run_name": f"llm_downstream_hard_v3_transfer_{model_slug}_strict_30x8",
            "strategies": STRICT_STRATEGIES,
            "include_repo_tree": False,
            "use_task_visible_files": True,
            "expected_rows": 30 * len(STRICT_STRATEGIES),
            "command": (
                f'{base} --model "{transfer_model_expr}" '
                f"--run-name llm_downstream_hard_v3_transfer_{model_slug}_strict_30x8 "
                "--tasks-dir benchmark/downstream_hard_v3/tasks "
                f"{strategy_flags(STRICT_STRATEGIES)} "
                "--use-task-visible-files --resume"
            ),
        },
        {
            "run_id": "MT3_hard_v4_tree",
            "suite": "hard_v4",
            "setting": "tree-aware",
            "tasks_dir": "benchmark/downstream_hard_v4/tasks",
            "run_name": f"llm_downstream_hard_v4_transfer_{model_slug}_tree_24x8",
            "strategies": TREE_STRATEGIES,
            "include_repo_tree": True,
            "use_task_visible_files": True,
            "expected_rows": 24 * len(TREE_STRATEGIES),
            "command": (
                f'{base} --model "{transfer_model_expr}" '
                f"--run-name llm_downstream_hard_v4_transfer_{model_slug}_tree_24x8 "
                "--tasks-dir benchmark/downstream_hard_v4/tasks "
                f"{strategy_flags(TREE_STRATEGIES)} "
                "--use-task-visible-files --include-repo-tree --resume"
            ),
        },
        {
            "run_id": "MT4_hard_v4_strict",
            "suite": "hard_v4",
            "setting": "strict visible-file",
            "tasks_dir": "benchmark/downstream_hard_v4/tasks",
            "run_name": f"llm_downstream_hard_v4_transfer_{model_slug}_strict_24x8",
            "strategies": STRICT_STRATEGIES,
            "include_repo_tree": False,
            "use_task_visible_files": True,
            "expected_rows": 24 * len(STRICT_STRATEGIES),
            "command": (
                f'{base} --model "{transfer_model_expr}" '
                f"--run-name llm_downstream_hard_v4_transfer_{model_slug}_strict_24x8 "
                "--tasks-dir benchmark/downstream_hard_v4/tasks "
                f"{strategy_flags(STRICT_STRATEGIES)} "
                "--use-task-visible-files --resume"
            ),
        },
    ]


def build_protocol(
    boundary: dict[str, Any],
    audit: dict[str, Any],
    boundary_path: Path,
    audit_path: Path,
    model_slug: str,
    transfer_model_expr: str,
) -> dict[str, Any]:
    derived = boundary["derived_claims"]
    specs = run_specs(model_slug, transfer_model_expr)
    total_expected_rows = sum(spec["expected_rows"] for spec in specs)
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_id": "model_transfer_replication_v0",
        "purpose": (
            "Predeclare the next clean downstream validation boundary: replicate the frozen "
            "hard_v3/hard_v4 matrices with a second model, without tuning prompts, strategies, "
            "task files, or hidden verifiers from observed failures."
        ),
        "source_files": [
            {
                "name": "downstream_boundary_synthesis",
                "path": display_path(boundary_path),
                "sha256": sha256_file(boundary_path),
                "generated_at_utc": boundary["generated_at_utc"],
            },
            {
                "name": "paper_claim_consistency_audit",
                "path": display_path(audit_path),
                "sha256": sha256_file(audit_path),
                "generated_at_utc": audit["generated_at_utc"],
            },
        ],
        "prerequisites": [
            "Run paper claim consistency audit and require 12/12 checks passing.",
            "Choose one transfer model before starting; record its exact provider model id.",
            f"Set {TRANSFER_MODEL_ENV} or pass --model explicitly; do not overwrite baseline evidence.",
            "Run hard_v3 and hard_v4 deterministic checkers before any model calls.",
            "Do not inspect failures to change prompts, artifacts, strategies, or tasks.",
        ],
        "transfer_model": {
            "environment_variable": TRANSFER_MODEL_ENV,
            "model_expression": transfer_model_expr,
            "model_slug": model_slug,
            "must_differ_from_baseline": True,
            "baseline_model_label": "mimo-v2.5-pro",
        },
        "frozen_current_boundary": {
            "forced_bad_total_success": derived["forced_bad_total_success"],
            "forced_bad_total_tasks": derived["forced_bad_total_tasks"],
            "forced_bad_total_public_passed_hidden_failed": derived[
                "forced_bad_total_public_passed_hidden_failed"
            ],
            "selected_superiority_consistent": derived["selected_superiority_consistent"],
            "selected_token_savings_consistent": derived["selected_token_savings_consistent"],
            "hard_v4_strict_selected_delta_vs_no_experience": derived["selected_success_delta_values"][
                "hard_v4_strict_visible_selected_success_delta_vs_no_experience"
            ],
        },
        "run_matrix": specs,
        "expected_total_rows": total_expected_rows,
        "stop_rules": [
            "Use --resume only to recover interrupted rows; do not selectively rerun failed rows.",
            "If API outage or parser failure affects many rows, pause and document infrastructure status before rerunning.",
            "After the first full transfer run, freeze it as evidence. Any prompt or strategy adjustment must create a new protocol id.",
            "Do not add or remove tasks after seeing transfer-model outcomes.",
        ],
        "primary_comparisons": [
            "selected vs no_experience in hard_v3 tree-aware and strict settings",
            "selected vs no_experience in hard_v4 tree-aware and strict settings",
            "selected + precondition context vs selected in tree-aware settings",
            "precondition-only vs selected and no_experience in strict settings",
            "forced_bad_artifact aggregate across hard_v3 and hard_v4",
            "bad_dependency_rule artifact adherence vs forced_bad_artifact negative transfer",
        ],
        "allowed_claims_after_run": [
            "The hard_v3/hard_v4 boundary pattern replicated, weakened, or reversed under a second model.",
            "Forced harmful artifacts did or did not remain systematic negative-transfer controls under the transfer model.",
            "Repo tree and precondition context remained, weakened, or changed as context variables under the transfer model.",
        ],
        "forbidden_claims_after_run": [
            "Do not claim model-general SkillAdmit-selected superiority from one transfer model.",
            "Do not claim selected token savings unless a separate cost-controlled protocol is run.",
            "Do not compare transfer results to baseline after changing prompts, task visibility, or hidden verifiers.",
            "Do not treat forced_bad_artifact as a normal LLM-choice strategy; it is a deterministic negative-transfer control.",
        ],
        "post_run_required_exports": [
            "Inspect raw run summaries for completeness only, not for prompt tuning.",
            "Create a model-transfer evidence package before adding paper claims.",
            "Rerun paper claim consistency audit after adding any transfer-facing report.",
        ],
    }


def assert_protocol(protocol: dict[str, Any]) -> None:
    frozen = protocol["frozen_current_boundary"]
    expected = {
        "forced_bad_total_success": "0/133",
        "forced_bad_total_tasks": 133,
        "forced_bad_total_public_passed_hidden_failed": 133,
        "selected_superiority_consistent": False,
        "selected_token_savings_consistent": False,
        "hard_v4_strict_selected_delta_vs_no_experience": -2,
    }
    for key, value in expected.items():
        actual = frozen[key]
        if actual != value:
            raise AssertionError(f"{key}: expected {value}, got {actual}")
    if protocol["expected_total_rows"] != 864:
        raise AssertionError(f"expected 864 rows, got {protocol['expected_total_rows']}")
    if len(protocol["run_matrix"]) != 4:
        raise AssertionError("expected four transfer run specs")
    for spec in protocol["run_matrix"]:
        if "--resume" not in spec["command"]:
            raise AssertionError(f"missing --resume in {spec['run_id']}")
        if "--model" not in spec["command"]:
            raise AssertionError(f"missing --model in {spec['run_id']}")
        if spec["setting"] == "tree-aware" and "--include-repo-tree" not in spec["command"]:
            raise AssertionError(f"tree-aware command missing repo tree: {spec['run_id']}")
        if spec["setting"] == "strict visible-file" and "--include-repo-tree" in spec["command"]:
            raise AssertionError(f"strict command includes repo tree: {spec['run_id']}")
    rendered = render_markdown(protocol)
    required = [
        "model_transfer_replication_v0",
        "hard_v3",
        "hard_v4",
        "0/133",
        "864",
        "Do not claim model-general SkillAdmit-selected superiority",
        "Do not inspect failures to change prompts",
    ]
    for phrase in required:
        if phrase not in rendered:
            raise AssertionError(f"missing protocol phrase: {phrase}")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def render_markdown(protocol: dict[str, Any]) -> str:
    run_rows = [
        [
            row["run_id"],
            row["suite"],
            row["setting"],
            row["expected_rows"],
            f"`{row['run_name']}`",
            f"`{row['command']}`",
        ]
        for row in protocol["run_matrix"]
    ]
    fact_rows = [[key, value] for key, value in protocol["frozen_current_boundary"].items()]
    lines = [
        "# Model-Transfer Replication Protocol",
        "",
        f"Generated at UTC: `{protocol['generated_at_utc']}`",
        "",
        f"Protocol ID: `{protocol['protocol_id']}`",
        "",
        protocol["purpose"],
        "",
        "## Frozen Current Boundary",
        "",
        md_table(["fact", "value"], fact_rows),
        "",
        "## Transfer Model",
        "",
        md_table(["field", "value"], [[key, value] for key, value in protocol["transfer_model"].items()]),
        "",
        "## Prerequisites",
        "",
    ]
    lines.extend(f"- {item}" for item in protocol["prerequisites"])
    lines.extend(
        [
            "",
            "## Run Matrix",
            "",
            f"Expected total rows: `{protocol['expected_total_rows']}`",
            "",
            md_table(["run", "suite", "setting", "rows", "run_name", "command"], run_rows),
            "",
            "## Stop Rules",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in protocol["stop_rules"])
    lines.extend(["", "## Primary Comparisons", ""])
    lines.extend(f"- {item}" for item in protocol["primary_comparisons"])
    lines.extend(["", "## Allowed Claims After Run", ""])
    lines.extend(f"- {item}" for item in protocol["allowed_claims_after_run"])
    lines.extend(["", "## Forbidden Claims After Run", ""])
    lines.extend(f"- {item}" for item in protocol["forbidden_claims_after_run"])
    lines.extend(["", "## Post-Run Required Exports", ""])
    lines.extend(f"- {item}" for item in protocol["post_run_required_exports"])
    lines.extend(["", "## Source Files", ""])
    source_rows = [
        [
            source["name"],
            f"`{source['path']}`",
            f"`{source['sha256'][:16]}`",
            f"`{source['generated_at_utc']}`",
        ]
        for source in protocol["source_files"]
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


def render_latex(protocol: dict[str, Any]) -> str:
    lines = [
        "% Auto-generated by scripts/export_model_transfer_replication_protocol.py",
        "\\begin{tabular}{llll}",
        "\\hline",
        "Run & Suite & Setting & Rows \\\\",
        "\\hline",
    ]
    for row in protocol["run_matrix"]:
        lines.append(
            " & ".join(
                [
                    tex_escape(row["run_id"]),
                    tex_escape(row["suite"]),
                    tex_escape(row["setting"]),
                    tex_escape(row["expected_rows"]),
                ]
            )
            + " \\\\"
        )
    lines.extend(["\\hline", "\\end{tabular}", "", "% Forbidden claims:"])
    for item in protocol["forbidden_claims_after_run"]:
        lines.append(f"% - {tex_escape(item)}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(protocol: dict[str, Any], json_path: Path, md_path: Path, tex_path: Path) -> None:
    resolve(json_path).parent.mkdir(parents=True, exist_ok=True)
    resolve(json_path).write_text(json.dumps(protocol, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    resolve(md_path).write_text(render_markdown(protocol), encoding="utf-8")
    resolve(tex_path).write_text(render_latex(protocol), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boundary", type=Path, default=DEFAULT_BOUNDARY)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--model-slug", default=DEFAULT_MODEL_SLUG)
    parser.add_argument("--transfer-model-expr", default=TRANSFER_MODEL_PLACEHOLDER)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX)
    parser.add_argument(
        "--assert-current-protocol",
        action="store_true",
        help="Assert current predeclared model-transfer protocol values.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    boundary_path = resolve(args.boundary)
    audit_path = resolve(args.audit)
    protocol = build_protocol(
        load_json(boundary_path),
        load_json(audit_path),
        boundary_path,
        audit_path,
        args.model_slug,
        args.transfer_model_expr,
    )
    if args.assert_current_protocol:
        assert_protocol(protocol)
    write_outputs(protocol, args.json_out, args.md_out, args.tex_out)
    print(f"protocol_id: {protocol['protocol_id']}")
    print(f"run_specs: {len(protocol['run_matrix'])}")
    print(f"expected_total_rows: {protocol['expected_total_rows']}")
    print(f"wrote_json: {display_path(args.json_out)}")
    print(f"wrote_md: {display_path(args.md_out)}")
    print(f"wrote_tex: {display_path(args.tex_out)}")


if __name__ == "__main__":
    main()
