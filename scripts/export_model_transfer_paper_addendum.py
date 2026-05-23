#!/usr/bin/env python3
"""Export a paper addendum for model-transfer downstream validation.

What this file does:
  Reads the cross-model synthesis over hard_v3/hard_v4 and renders a compact
  paper-ready addendum in JSON, Markdown, and LaTeX. The addendum explains what
  replicated across models, what is model-sensitive, and which claims remain
  unsupported.

Why it is needed:
  The main downstream paper section is anchored to the frozen hard_v2/hard_v3/
  hard_v4 boundary. The second-model run is valuable, but it should be reported
  as a replication/sensitivity addendum rather than folded into the main
  boundary aggregate.

Inputs:
  benchmark/downstream/reports/model_transfer_cross_model_synthesis.json

Outputs:
  benchmark/downstream/reports/model_transfer_paper_addendum.json
  benchmark/downstream/reports/model_transfer_paper_addendum.md
  benchmark/downstream/reports/model_transfer_paper_addendum.tex

Who runs it:
  Researchers or Codex sessions after regenerating the model-transfer
  cross-model synthesis, before drafting a paper appendix or replication
  subsection.
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

DEFAULT_SYNTHESIS = REPORT_DIR / "model_transfer_cross_model_synthesis.json"
DEFAULT_JSON = REPORT_DIR / "model_transfer_paper_addendum.json"
DEFAULT_MD = REPORT_DIR / "model_transfer_paper_addendum.md"
DEFAULT_TEX = REPORT_DIR / "model_transfer_paper_addendum.tex"


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


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with resolve(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def paragraph(text: str) -> str:
    return " ".join(line.strip() for line in text.strip().splitlines())


def selected_rows_by_key(synthesis: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, Any]]:
    return {
        (row["model_role"], row["suite"], row["setting"]): row
        for row in synthesis["selected_comparison_table"]
    }


def sensitivity_rows_by_key(synthesis: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (row["suite"], row["setting"]): row
        for row in synthesis["selected_sensitivity_table"]
    }


def context_rows_by_key(synthesis: dict[str, Any]) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    return {
        (row["model_role"], row["suite"], row["setting"], row["comparison"]): row
        for row in synthesis["context_comparison_table"]
    }


def build_key_tables(synthesis: dict[str, Any]) -> dict[str, Any]:
    selected = selected_rows_by_key(synthesis)
    sensitivity = sensitivity_rows_by_key(synthesis)
    context = context_rows_by_key(synthesis)
    forced = synthesis["forced_bad_summary"]
    derived = synthesis["derived_claims"]
    return {
        "selected_summary": [
            {
                "suite": row["suite"],
                "setting": row["setting"],
                "baseline_delta": row["baseline_success_delta"],
                "transfer_delta": row["transfer_success_delta"],
                "pattern": row["pattern"],
            }
            for row in synthesis["selected_sensitivity_table"]
        ],
        "forced_bad_by_model": forced["by_model"],
        "strict_precondition_vs_selected": [
            context[
                ("baseline", "hard_v3", "strict visible", "strict precondition-only vs selected")
            ],
            context[
                ("baseline", "hard_v4", "strict visible", "strict precondition-only vs selected")
            ],
            context[
                ("transfer", "hard_v3", "strict visible", "strict precondition-only vs selected")
            ],
            context[
                ("transfer", "hard_v4", "strict visible", "strict precondition-only vs selected")
            ],
        ],
        "hard_v3_tree_baseline_selected": selected[("baseline", "hard_v3", "tree-aware")],
        "hard_v3_tree_transfer_selected": selected[("transfer", "hard_v3", "tree-aware")],
        "hard_v3_strict_baseline_selected": selected[("baseline", "hard_v3", "strict visible")],
        "hard_v3_strict_transfer_selected": selected[("transfer", "hard_v3", "strict visible")],
        "hard_v4_strict": sensitivity[("hard_v4", "strict visible")],
        "derived": derived,
    }


def build_addendum(synthesis: dict[str, Any], synthesis_path: Path) -> dict[str, Any]:
    tables = build_key_tables(synthesis)
    derived = tables["derived"]
    models = synthesis["models"]
    h4_strict = tables["hard_v4_strict"]

    protocol_summary = [
        paragraph(
            f"""
            The model-transfer experiment reruns the frozen hard_v3 and hard_v4
            downstream matrices with a second model, {models['transfer']}, and
            compares it with the baseline label {models['baseline']}. The task
            files, strategies, prompts, visible-file settings, repository-tree
            settings, and hidden verifiers are not changed from observed
            outcomes.
            """
        ),
        paragraph(
            """
            This addendum is intentionally separate from the main three-boundary
            downstream section. hard_v2/hard_v3/hard_v4 remain the primary
            clean task-boundary story; the transfer run is a model-sensitivity
            and replication check over a subset of those frozen boundaries.
            """
        ),
    ]

    result_paragraphs = [
        paragraph(
            f"""
            The most stable result is negative transfer from forced harmful
            artifacts. The baseline hard_v3/hard_v4 slice gives
            {synthesis['forced_bad_summary']['by_model'][0]['success']}, and
            the transfer model gives
            {synthesis['forced_bad_summary']['by_model'][1]['success']}. Combined
            across the two models, forced bad artifacts solve
            {derived['forced_bad_combined_success']} tasks and produce
            {derived['forced_bad_combined_public_passed_hidden_failed']}
            public-pass/hidden-fail cases.
            """
        ),
        paragraph(
            f"""
            The hard_v3 selected-vs-no_experience pattern replicates. In
            tree-aware hard_v3, selected ties no_experience for both models:
            {tables['hard_v3_tree_baseline_selected']['selected_success']} vs
            {tables['hard_v3_tree_baseline_selected']['baseline_success']} for
            the baseline model and
            {tables['hard_v3_tree_transfer_selected']['selected_success']} vs
            {tables['hard_v3_tree_transfer_selected']['baseline_success']} for
            the transfer model. In strict hard_v3, selected is +1 task over
            no_experience for both models.
            """
        ),
        paragraph(
            f"""
            The hard_v4 strict selected comparison is model-sensitive. The
            baseline model has selected below no_experience by
            {abs(h4_strict['baseline_success_delta'])} tasks, while the transfer
            model has selected above no_experience by
            {h4_strict['transfer_success_delta']} tasks. This sign reversal is
            the key reason the transfer experiment should not be used to claim
            model-general SkillAdmit-selected superiority.
            """
        ),
        paragraph(
            f"""
            Precondition-only context is also not model-general improvement over
            selected context. In the baseline strict settings it is +1 over
            selected for both hard_v3 and hard_v4, but under the transfer model
            it ties selected in hard_v3 and trails selected by one task in
            hard_v4.
            """
        ),
        paragraph(
            """
            Token efficiency remains outside the supported claim set. Selected
            token deltas are mixed across models and settings, and the transfer
            protocol was not designed as a cost-controlled token-efficiency
            study.
            """
        ),
    ]

    allowed_wording = [
        (
            "A second-model replication over frozen hard_v3/hard_v4 preserves the "
            "forced harmful-artifact negative-transfer result."
        ),
        (
            "Selected context shows model-sensitive downstream utility rather than "
            "model-general superiority."
        ),
        (
            "The hard_v4 strict selected comparison reverses sign between the "
            "baseline and transfer models."
        ),
    ]

    forbidden_wording = [
        "SkillAdmit-selected is model-generally superior.",
        "SkillAdmit-selected saves tokens across models.",
        "The transfer model creates a new clean task boundary.",
        "Precondition-only generally replaces repository-tree context.",
        "The transfer run justifies retuning hard_v3 or hard_v4.",
    ]

    table_captions = [
        {
            "label": "tab:model-transfer-selected",
            "caption": paragraph(
                """
                Selected-vs-no_experience sensitivity across baseline and
                transfer models. hard_v3 patterns replicate, while hard_v4
                strict visible-file reverses sign.
                """
            ),
        },
        {
            "label": "tab:model-transfer-negative-transfer",
            "caption": paragraph(
                f"""
                Forced harmful-artifact replication across models. The combined
                result is {derived['forced_bad_combined_success']} with
                {derived['forced_bad_combined_public_passed_hidden_failed']}
                public-pass/hidden-fail cases.
                """
            ),
        },
    ]

    one_paragraph_summary = paragraph(
        f"""
        A second-model replication with {models['transfer']} strengthens the
        negative-transfer claim but not a universal selected-utility claim.
        Forced harmful artifacts fail on both the baseline and transfer
        hard_v3/hard_v4 slices, yielding {derived['forced_bad_combined_success']}
        combined success with
        {derived['forced_bad_combined_public_passed_hidden_failed']}
        public-pass/hidden-fail cases. hard_v3 selected-vs-no_experience
        patterns replicate, but hard_v4 strict visible-file reverses sign:
        baseline selected is {h4_strict['baseline_success_delta']} tasks against
        no_experience, while transfer selected is
        +{h4_strict['transfer_success_delta']} tasks. Therefore the correct
        paper claim is model sensitivity plus replicated harmful-artifact
        negative transfer, not model-general selected superiority.
        """
    )

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_synthesis": {
            "path": display_path(synthesis_path),
            "sha256": sha256_file(synthesis_path),
            "generated_at_utc": synthesis["generated_at_utc"],
        },
        "models": models,
        "protocol_summary": protocol_summary,
        "result_paragraphs": result_paragraphs,
        "table_captions": table_captions,
        "allowed_wording": allowed_wording,
        "forbidden_wording": forbidden_wording,
        "one_paragraph_summary": one_paragraph_summary,
        "selected_sensitivity_table": tables["selected_summary"],
        "forced_bad_by_model": tables["forced_bad_by_model"],
        "strict_precondition_vs_selected": tables["strict_precondition_vs_selected"],
        "derived_cross_model": {
            "forced_bad_combined_success": derived["forced_bad_combined_success"],
            "forced_bad_combined_public_passed_hidden_failed": derived[
                "forced_bad_combined_public_passed_hidden_failed"
            ],
            "forced_bad_replication_across_models": derived[
                "forced_bad_replication_across_models"
            ],
            "hard_v3_tree_selected_tie_replicated": derived[
                "hard_v3_tree_selected_tie_replicated"
            ],
            "hard_v3_strict_selected_plus_one_replicated": derived[
                "hard_v3_strict_selected_plus_one_replicated"
            ],
            "hard_v4_strict_selected_delta_baseline": derived[
                "hard_v4_strict_selected_delta_baseline"
            ],
            "hard_v4_strict_selected_delta_transfer": derived[
                "hard_v4_strict_selected_delta_transfer"
            ],
            "hard_v4_strict_selected_delta_reversed": derived[
                "hard_v4_strict_selected_delta_reversed"
            ],
            "selected_superiority_model_general": derived[
                "selected_superiority_model_general"
            ],
            "selected_token_savings_model_general": derived[
                "selected_token_savings_model_general"
            ],
            "precondition_only_better_than_selected_model_general": derived[
                "precondition_only_better_than_selected_model_general"
            ],
        },
    }


def assert_current_addendum(addendum: dict[str, Any]) -> None:
    derived = addendum["derived_cross_model"]
    expected = {
        "forced_bad_combined_success": "0/216",
        "forced_bad_combined_public_passed_hidden_failed": 216,
        "forced_bad_replication_across_models": True,
        "hard_v3_tree_selected_tie_replicated": True,
        "hard_v3_strict_selected_plus_one_replicated": True,
        "hard_v4_strict_selected_delta_baseline": -2,
        "hard_v4_strict_selected_delta_transfer": 3,
        "hard_v4_strict_selected_delta_reversed": True,
        "selected_superiority_model_general": False,
        "selected_token_savings_model_general": False,
        "precondition_only_better_than_selected_model_general": False,
    }
    for key, value in expected.items():
        actual = derived[key]
        if actual != value:
            raise AssertionError(f"{key}: expected {value}, got {actual}")

    if addendum["models"] != {"baseline": "mimo-v2.5-pro", "transfer": "mimo-v2.5"}:
        raise AssertionError("model labels changed")
    if len(addendum["result_paragraphs"]) != 5:
        raise AssertionError("result paragraph count changed")
    if len(addendum["selected_sensitivity_table"]) != 4:
        raise AssertionError("selected sensitivity row count changed")
    if len(addendum["strict_precondition_vs_selected"]) != 4:
        raise AssertionError("precondition comparison row count changed")

    rendered = render_markdown(addendum)
    required = [
        "0/216",
        "216 public-pass/hidden-fail",
        "hard_v4 strict selected comparison is model-sensitive",
        "Do not use this addendum to claim model-general selected superiority",
        "SkillAdmit-selected saves tokens across models",
    ]
    for phrase in required:
        if phrase not in rendered:
            raise AssertionError(f"missing rendered phrase: {phrase}")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def render_markdown(addendum: dict[str, Any]) -> str:
    sensitivity_rows = [
        [
            row["suite"],
            row["setting"],
            row["baseline_delta"],
            row["transfer_delta"],
            row["pattern"],
        ]
        for row in addendum["selected_sensitivity_table"]
    ]
    forced_rows = [
        [
            row["model_role"],
            row["model_label"],
            row["success"],
            row["negative_transfer"],
            row["public_passed_hidden_failed"],
        ]
        for row in addendum["forced_bad_by_model"]
    ]
    precondition_rows = [
        [
            row["model_role"],
            row["suite"],
            row["left_success"],
            row["right_success"],
            row["success_delta"],
            row["token_delta"],
        ]
        for row in addendum["strict_precondition_vs_selected"]
    ]
    derived_rows = [
        [key, value]
        for key, value in addendum["derived_cross_model"].items()
    ]
    caption_rows = [
        [row["label"], row["caption"]]
        for row in addendum["table_captions"]
    ]
    return "\n\n".join(
        [
            "# Model-Transfer Paper Addendum",
            f"Generated at UTC: `{addendum['generated_at_utc']}`",
            (
                "This addendum is generated from the frozen cross-model synthesis. "
                "Do not use this addendum to claim model-general selected superiority."
            ),
            "## One-Paragraph Summary",
            addendum["one_paragraph_summary"],
            "## Protocol Summary",
            "\n\n".join(addendum["protocol_summary"]),
            "## Results",
            "\n\n".join(addendum["result_paragraphs"]),
            "## Selected Sensitivity",
            md_table(
                ["suite", "setting", "baseline_delta", "transfer_delta", "pattern"],
                sensitivity_rows,
            ),
            "## Forced Bad Replication",
            md_table(
                ["role", "model", "success", "negative_transfer", "public_hidden"],
                forced_rows,
            ),
            "## Strict Precondition-Only Versus Selected",
            md_table(
                ["role", "suite", "precondition_only", "selected", "success_delta", "token_delta"],
                precondition_rows,
            ),
            "## Table Captions",
            md_table(["label", "caption"], caption_rows),
            "## Allowed Wording",
            "\n".join(f"- {item}" for item in addendum["allowed_wording"]),
            "## Forbidden Wording",
            "\n".join(f"- {item}" for item in addendum["forbidden_wording"]),
            "## Derived Cross-Model Flags",
            md_table(["flag", "value"], derived_rows),
            "## Source",
            md_table(
                ["field", "value"],
                [
                    ["path", f"`{addendum['source_synthesis']['path']}`"],
                    ["sha256", f"`{addendum['source_synthesis']['sha256'][:16]}`"],
                    ["generated_at_utc", f"`{addendum['source_synthesis']['generated_at_utc']}`"],
                ],
            ),
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


def render_latex(addendum: dict[str, Any]) -> str:
    lines = [
        "% Auto-generated by scripts/export_model_transfer_paper_addendum.py",
        "\\begin{tabular}{llrrl}",
        "\\hline",
        "Suite & Setting & Baseline delta & Transfer delta & Pattern \\\\",
        "\\hline",
    ]
    for row in addendum["selected_sensitivity_table"]:
        lines.append(
            " & ".join(
                [
                    tex_escape(row["suite"]),
                    tex_escape(row["setting"]),
                    str(row["baseline_delta"]),
                    str(row["transfer_delta"]),
                    tex_escape(row["pattern"]),
                ]
            )
            + " \\\\"
        )
    lines.extend(["\\hline", "\\end{tabular}", "", "% Model-transfer addendum flags:"])
    for key, value in addendum["derived_cross_model"].items():
        lines.append(f"% {tex_escape(key)} = {tex_escape(value)}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(addendum: dict[str, Any], json_path: Path, md_path: Path, tex_path: Path) -> None:
    json_path = resolve(json_path)
    md_path = resolve(md_path)
    tex_path = resolve(tex_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(addendum, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(addendum), encoding="utf-8")
    tex_path.write_text(render_latex(addendum), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthesis", type=Path, default=DEFAULT_SYNTHESIS)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX)
    parser.add_argument(
        "--assert-current-addendum",
        action="store_true",
        help="Assert current model-transfer paper-addendum facts and guardrails.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    synthesis = load_json(args.synthesis)
    addendum = build_addendum(synthesis, args.synthesis)
    if args.assert_current_addendum:
        assert_current_addendum(addendum)
    write_outputs(addendum, args.json_out, args.md_out, args.tex_out)
    print(f"result_paragraphs: {len(addendum['result_paragraphs'])}")
    print(f"selected_sensitivity_rows: {len(addendum['selected_sensitivity_table'])}")
    print(f"forced_bad_combined_success: {addendum['derived_cross_model']['forced_bad_combined_success']}")
    print(f"hard_v4_strict_reversed: {addendum['derived_cross_model']['hard_v4_strict_selected_delta_reversed']}")
    print(f"wrote_json: {display_path(args.json_out)}")
    print(f"wrote_md: {display_path(args.md_out)}")
    print(f"wrote_tex: {display_path(args.tex_out)}")


if __name__ == "__main__":
    main()
