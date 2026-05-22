#!/usr/bin/env python3
"""Export a paper-ready downstream validation section.

What this file does:
  Reads the cross-version downstream synthesis package and renders a paper
  evaluation section in Markdown, LaTeX, and JSON. The generated text includes
  the downstream research questions, protocol summary, result interpretation,
  table captions, and explicit claim limits.

Why it is needed:
  The hard_v2 and hard_v3 evidence should not be rewritten by hand each time a
  paper draft is edited. This exporter keeps the paper narrative tied to the
  frozen synthesis package and asserts the most important claim-boundary rules:
  no universal selected-superiority claim, no selected token-savings claim, and
  systematic forced-bad negative transfer.

Inputs:
  benchmark/downstream/reports/downstream_cross_version_synthesis.json

Outputs:
  benchmark/downstream/reports/downstream_paper_eval_section.json
  benchmark/downstream/reports/downstream_paper_eval_section.md
  benchmark/downstream/reports/downstream_paper_eval_section.tex

Who runs it:
  Researchers or Codex sessions when preparing the evaluation section of a
  paper or thesis from the current SkillAdmit downstream evidence.
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

DEFAULT_SYNTHESIS = REPORT_DIR / "downstream_cross_version_synthesis.json"
DEFAULT_JSON = REPORT_DIR / "downstream_paper_eval_section.json"
DEFAULT_MD = REPORT_DIR / "downstream_paper_eval_section.md"
DEFAULT_TEX = REPORT_DIR / "downstream_paper_eval_section.tex"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> Path:
    resolved = resolve(path)
    try:
        return resolved.relative_to(ROOT)
    except ValueError:
        return resolved


def row_index(synthesis: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, Any]]:
    return {
        (row["suite"], row["run_name"], row["strategy"]): row
        for row in synthesis["primary_strategy_table"]
    }


def require_row(rows: dict[tuple[str, str, str], dict[str, Any]], suite: str, run: str, strategy: str) -> dict[str, Any]:
    key = (suite, run, strategy)
    if key not in rows:
        raise KeyError(f"Missing synthesis row: {suite}/{run}/{strategy}")
    return rows[key]


def pct(row: dict[str, Any]) -> str:
    return f"{row['successes']}/{row['tasks']}"


def build_key_results(synthesis: dict[str, Any]) -> dict[str, Any]:
    rows = row_index(synthesis)
    return {
        "hard_v2_strict_no": require_row(
            rows, "hard_v2", "llm_downstream_hard_v2_full_25x6", "no_experience"
        ),
        "hard_v2_strict_selected": require_row(
            rows, "hard_v2", "llm_downstream_hard_v2_full_25x6", "skilladmit_selected"
        ),
        "hard_v2_strict_all": require_row(
            rows, "hard_v2", "llm_downstream_hard_v2_full_25x6", "distilled_skills_all"
        ),
        "hard_v2_tree_no": require_row(
            rows, "hard_v2", "llm_downstream_hard_v2_tree_25x2", "no_experience"
        ),
        "hard_v2_tree_selected": require_row(
            rows, "hard_v2", "llm_downstream_hard_v2_tree_25x2", "skilladmit_selected"
        ),
        "hard_v2_tree_preconditions": require_row(
            rows,
            "hard_v2",
            "llm_downstream_hard_v2_selected_precondition_25",
            "skilladmit_selected_with_precondition_context",
        ),
        "hard_v2_precondition_only": require_row(
            rows,
            "hard_v2",
            "llm_downstream_hard_v2_precondition_only_25",
            "skilladmit_selected_with_precondition_only",
        ),
        "hard_v2_forced_bad": require_row(
            rows, "hard_v2", "llm_downstream_hard_v2_forced_bad_25", "forced_bad_artifact"
        ),
        "hard_v3_tree_no": require_row(
            rows, "hard_v3", "llm_downstream_hard_v3_tree_core_30x2", "no_experience"
        ),
        "hard_v3_tree_selected": require_row(
            rows, "hard_v3", "llm_downstream_hard_v3_tree_core_30x2", "skilladmit_selected"
        ),
        "hard_v3_tree_preconditions": require_row(
            rows,
            "hard_v3",
            "llm_downstream_hard_v3_tree_core_30x2",
            "skilladmit_selected_with_precondition_context",
        ),
        "hard_v3_tree_raw": require_row(
            rows, "hard_v3", "llm_downstream_hard_v3_tree_core_30x2", "raw_memory"
        ),
        "hard_v3_tree_all": require_row(
            rows, "hard_v3", "llm_downstream_hard_v3_tree_core_30x2", "distilled_skills_all"
        ),
        "hard_v3_tree_bad_rule": require_row(
            rows, "hard_v3", "llm_downstream_hard_v3_tree_core_30x2", "bad_dependency_rule"
        ),
        "hard_v3_tree_forced_bad": require_row(
            rows, "hard_v3", "llm_downstream_hard_v3_tree_core_30x2", "forced_bad_artifact"
        ),
        "hard_v3_strict_no": require_row(
            rows, "hard_v3", "llm_downstream_hard_v3_strict_30x8", "no_experience"
        ),
        "hard_v3_strict_selected": require_row(
            rows, "hard_v3", "llm_downstream_hard_v3_strict_30x8", "skilladmit_selected"
        ),
        "hard_v3_strict_precondition_only": require_row(
            rows,
            "hard_v3",
            "llm_downstream_hard_v3_strict_30x8",
            "skilladmit_selected_with_precondition_only",
        ),
        "hard_v3_strict_raw": require_row(
            rows, "hard_v3", "llm_downstream_hard_v3_strict_30x8", "raw_memory"
        ),
        "hard_v3_strict_bad_rule": require_row(
            rows, "hard_v3", "llm_downstream_hard_v3_strict_30x8", "bad_dependency_rule"
        ),
        "hard_v3_strict_forced_bad": require_row(
            rows, "hard_v3", "llm_downstream_hard_v3_strict_30x8", "forced_bad_artifact"
        ),
    }


def paragraph(text: str) -> str:
    return " ".join(line.strip() for line in text.strip().splitlines())


def build_section(synthesis: dict[str, Any], synthesis_path: Path) -> dict[str, Any]:
    derived = synthesis["derived_synthesis"]
    results = build_key_results(synthesis)
    forced_bad_success = f"{derived['forced_bad_total_successes']}/{derived['forced_bad_total_tasks']}"
    forced_bad_public_hidden = str(derived["forced_bad_total_public_passed_hidden_failed"])
    tree_bad_rule_adherence = (
        f"{results['hard_v3_tree_bad_rule']['artifact_adherence']}/"
        f"{results['hard_v3_tree_bad_rule']['tasks']}"
    )
    strict_bad_rule_adherence = (
        f"{results['hard_v3_strict_bad_rule']['artifact_adherence']}/"
        f"{results['hard_v3_strict_bad_rule']['tasks']}"
    )

    research_questions = [
        (
            "Does admitted experience improve downstream coding-agent success "
            "under hidden-verifier evaluation?"
        ),
        (
            "Are repository-tree context and explicit preconditions critical "
            "variables for transferring admitted experience?"
        ),
        (
            "Does executing harmful admitted experience create systematic "
            "negative transfer even when public tests pass?"
        ),
    ]

    protocol = [
        paragraph(
            f"""
            We evaluate SkillAdmit downstream rather than relying only on
            admission-label accuracy. hard_v2 contains 25 import/debug tasks and
            hard_v3 contains 30 more agent-like repository repair tasks. Both
            suites use hidden verifiers, so public-test success is insufficient
            for success.
            """
        ),
        paragraph(
            f"""
            The comparison includes no_experience, SkillAdmit-selected context,
            selected context with explicit preconditions, precondition-only
            ablations where available, raw memory, all distilled skills,
            promoted rules, bad dependency rules, and forced bad artifacts.
            hard_v2 and hard_v3 are reported as distinct evaluation boundaries
            rather than collapsed into one leaderboard.
            """
        ),
    ]

    result_paragraphs = [
        paragraph(
            f"""
            On hard_v2, the tree-aware setting gives the clearest positive
            downstream result for SkillAdmit-selected experience:
            SkillAdmit-selected solves {pct(results['hard_v2_tree_selected'])}
            tasks, compared with {pct(results['hard_v2_tree_no'])} for
            no_experience. The selected + precondition context condition also
            solves {pct(results['hard_v2_tree_preconditions'])}. In contrast,
            strict visible-file hard_v2 does not support a selected-win story:
            selected solves {pct(results['hard_v2_strict_selected'])}, while
            no_experience solves {pct(results['hard_v2_strict_no'])} and all
            distilled skills solve {pct(results['hard_v2_strict_all'])}.
            """
        ),
        paragraph(
            f"""
            hard_v3 is the fresh generalization boundary and is deliberately
            less favorable to a simple selected-superiority claim. In the
            tree-aware hard_v3 setting, SkillAdmit-selected and no_experience
            both solve {pct(results['hard_v3_tree_selected'])}; selected +
            preconditions also solves {pct(results['hard_v3_tree_preconditions'])}.
            Raw memory and all distilled skills solve
            {pct(results['hard_v3_tree_raw'])} and
            {pct(results['hard_v3_tree_all'])}, respectively.
            """
        ),
        paragraph(
            f"""
            In strict visible-file hard_v3, SkillAdmit-selected improves over
            no_experience by one task ({pct(results['hard_v3_strict_selected'])}
            versus {pct(results['hard_v3_strict_no'])}), but it is not the best
            condition: precondition-only and raw memory both solve
            {pct(results['hard_v3_strict_precondition_only'])}. This separates
            the claim that selected experience can help from the stronger and
            unsupported claim that selected experience is universally optimal.
            """
        ),
        paragraph(
            f"""
            The strongest stable safety result is the forced harmful-artifact
            control. Across hard_v2 and both hard_v3 settings, forced bad
            artifacts solve {forced_bad_success} tasks and produce
            {forced_bad_public_hidden}
            public-pass/hidden-fail cases. This is direct evidence that
            admitting the wrong experience can systematically damage downstream
            behavior in ways public tests do not catch.
            """
        ),
        paragraph(
            f"""
            The ordinary bad_dependency_rule rows should not be interpreted as
            proving that bad advice is safe. In hard_v3, artifact adherence for
            that condition is only {tree_bad_rule_adherence} in the tree-aware
            run and {strict_bad_rule_adherence} in the strict visible-file run,
            so success often reflects the executor ignoring harmful advice. The
            forced bad-artifact condition is the cleaner negative-transfer
            control.
            """
        ),
    ]

    interpretation = [
        paragraph(
            """
            These results support a conditional downstream-utility claim:
            SkillAdmit-selected experience can improve downstream repair success
            under a coding-agent setting, as shown by hard_v2 tree-aware
            validation, but the effect does not generalize into universal
            dominance on hard_v3.
            """
        ),
        paragraph(
            """
            The repository tree and explicit preconditions are best treated as
            context variables rather than as a single universally dominant
            representation. hard_v2 shows that precondition text alone is less
            reliable than tree-aware context, while hard_v3 shows that
            precondition-only context can be sufficient for a different task
            family.
            """
        ),
        paragraph(
            """
            Token savings are not a supported paper claim. The current evidence
            is about success, hidden-verifier safety, and negative transfer; any
            token-efficiency claim would require a separate controlled cost
            study.
            """
        ),
    ]

    claim_limits = [
        "Do not claim SkillAdmit-selected universally dominates no_experience.",
        "Do not claim SkillAdmit-selected is the universal best downstream context.",
        "Do not claim cross-version selected token savings.",
        "Do not claim precondition-only generally replaces repository-tree context.",
        "Do not claim raw memory is a safe admission policy from hard_v3 success alone.",
        "Do not claim bad dependency advice is safe when the model often ignored it.",
        "Do not tune hard_v2 or hard_v3 failures while still calling them clean evidence.",
    ]

    table_captions = [
        {
            "label": "tab:downstream-cross-version",
            "caption": paragraph(
                """
                Cross-version downstream validation. hard_v2 provides positive
                evidence for tree-aware SkillAdmit-selected utility, while
                hard_v3 is a fresh boundary showing that selected context does
                not universally dominate. Public-hidden counts indicate cases
                that pass public tests but fail hidden verification.
                """
            ),
        },
        {
            "label": "tab:negative-transfer",
            "caption": paragraph(
                f"""
                Forced harmful-artifact control. Across hard_v2 and hard_v3,
                forced bad artifacts solve {forced_bad_success} tasks and create
                {forced_bad_public_hidden}
                public-pass/hidden-fail failures.
                """
            ),
        },
    ]

    one_paragraph_summary = paragraph(
        f"""
        Overall, downstream validation gives a sharper claim boundary than
        admission accuracy alone. hard_v2 supports SkillAdmit-selected utility
        in a tree-aware coding-agent setting ({pct(results['hard_v2_tree_selected'])}
        versus {pct(results['hard_v2_tree_no'])}), but hard_v3 does not support
        universal selected superiority: tree-aware selected ties no_experience
        at {pct(results['hard_v3_tree_selected'])}, and strict selected is not
        the best condition. The strongest cross-version result is safety-related:
        forced harmful artifacts achieve {forced_bad_success} success with
        {forced_bad_public_hidden} public-pass/hidden-fail cases, demonstrating
        systematic negative transfer when
        harmful experience is executed.
        """
    )

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_synthesis": {
            "path": str(display_path(synthesis_path)),
            "sha256": sha256_file(synthesis_path),
            "generated_at_utc": synthesis["generated_at_utc"],
        },
        "research_questions": research_questions,
        "protocol": protocol,
        "results": result_paragraphs,
        "interpretation": interpretation,
        "claim_limits": claim_limits,
        "table_captions": table_captions,
        "one_paragraph_summary": one_paragraph_summary,
        "derived_synthesis": {
            "forced_bad_total_tasks": derived["forced_bad_total_tasks"],
            "forced_bad_total_successes": derived["forced_bad_total_successes"],
            "forced_bad_total_public_passed_hidden_failed": derived[
                "forced_bad_total_public_passed_hidden_failed"
            ],
            "selected_superiority_consistent": derived["selected_superiority_consistent"],
            "selected_token_savings_supported": derived["selected_token_savings_supported"],
            "repo_tree_necessity_universal": derived["repo_tree_necessity_universal"],
        },
    }


def assert_paper_section(section: dict[str, Any]) -> None:
    derived = section["derived_synthesis"]
    expected = {
        "forced_bad_total_tasks": 85,
        "forced_bad_total_successes": 0,
        "forced_bad_total_public_passed_hidden_failed": 85,
        "selected_superiority_consistent": False,
        "selected_token_savings_supported": False,
        "repo_tree_necessity_universal": False,
    }
    for key, value in expected.items():
        actual = derived[key]
        if actual != value:
            raise AssertionError(f"{key}: expected {value}, got {actual}")

    rendered = render_markdown(section)
    required_phrases = [
        "does not support universal selected superiority",
        "Token savings are not a supported paper claim",
        "0/85 tasks",
        "public-pass/hidden-fail",
        "Do not claim SkillAdmit-selected universally dominates no_experience",
    ]
    for phrase in required_phrases:
        if phrase not in rendered:
            raise AssertionError(f"Missing required paper-boundary phrase: {phrase}")


def md_bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render_markdown(section: dict[str, Any]) -> str:
    captions = "\n".join(
        f"- `{caption['label']}`: {caption['caption']}"
        for caption in section["table_captions"]
    )
    return "\n\n".join(
        [
            "# Downstream Validation Paper Section",
            f"Generated at UTC: `{section['generated_at_utc']}`",
            (
                "This is a draftable paper section generated from the frozen "
                "cross-version downstream synthesis. It should be edited for "
                "style, not for stronger claims."
            ),
            "## Research Questions",
            md_bullets(section["research_questions"]),
            "## Protocol",
            "\n\n".join(section["protocol"]),
            "## Results",
            "\n\n".join(section["results"]),
            "## Interpretation",
            "\n\n".join(section["interpretation"]),
            "## One-Paragraph Paper Wording",
            section["one_paragraph_summary"],
            "## Table Captions",
            captions,
            "## Claims This Section Must Not Make",
            md_bullets(section["claim_limits"]),
            "## Source",
            (
                f"- synthesis: `{section['source_synthesis']['path']}`\n"
                f"- synthesis_sha256: `{section['source_synthesis']['sha256']}`\n"
                f"- synthesis_generated_at_utc: `{section['source_synthesis']['generated_at_utc']}`"
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


def tex_items(items: list[str]) -> list[str]:
    lines = ["\\begin{itemize}"]
    lines.extend(f"  \\item {tex_escape(item)}" for item in items)
    lines.append("\\end{itemize}")
    return lines


def tex_paragraphs(items: list[str]) -> list[str]:
    lines: list[str] = []
    for item in items:
        lines.append(tex_escape(item))
        lines.append("")
    return lines


def render_latex(section: dict[str, Any]) -> str:
    lines = [
        "% Auto-generated by scripts/export_downstream_paper_section.py",
        "\\subsection{Downstream Validation}",
        "",
        tex_escape(section["one_paragraph_summary"]),
        "",
        "\\paragraph{Research questions.}",
    ]
    lines.extend(tex_items(section["research_questions"]))
    lines.extend(["", "\\paragraph{Protocol.}"])
    lines.extend(tex_paragraphs(section["protocol"]))
    lines.extend(["\\paragraph{Results.}"])
    lines.extend(tex_paragraphs(section["results"]))
    lines.extend(["\\paragraph{Interpretation.}"])
    lines.extend(tex_paragraphs(section["interpretation"]))
    lines.extend(["\\paragraph{Claim limits.}"])
    lines.extend(tex_items(section["claim_limits"]))
    lines.extend(["", "% Suggested table captions:"])
    for caption in section["table_captions"]:
        lines.append(f"% {tex_escape(caption['label'])}: {tex_escape(caption['caption'])}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(section: dict[str, Any], json_path: Path, md_path: Path, tex_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(section, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(section), encoding="utf-8")
    tex_path.write_text(render_latex(section), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthesis", type=Path, default=DEFAULT_SYNTHESIS)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX)
    parser.add_argument(
        "--assert-current-paper-section",
        action="store_true",
        help="Assert current paper-section claim boundaries and key evidence values.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    synthesis_path = resolve(args.synthesis)
    section = build_section(load_json(synthesis_path), synthesis_path)
    if args.assert_current_paper_section:
        assert_paper_section(section)
    write_outputs(section, resolve(args.json_out), resolve(args.md_out), resolve(args.tex_out))
    print(f"research_questions: {len(section['research_questions'])}")
    print(f"result_paragraphs: {len(section['results'])}")
    print(f"claim_limits: {len(section['claim_limits'])}")
    print(f"forced_bad_total_tasks: {section['derived_synthesis']['forced_bad_total_tasks']}")
    print(f"wrote_json: {display_path(args.json_out)}")
    print(f"wrote_md: {display_path(args.md_out)}")
    print(f"wrote_tex: {display_path(args.tex_out)}")


if __name__ == "__main__":
    main()
