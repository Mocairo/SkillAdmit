#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
ACTIONS = [
    "discard",
    "store_as_memory",
    "distill_into_skill",
    "promote_to_rule",
    "defer",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(path)


def sample_text(sample: dict[str, Any]) -> str:
    parts = [
        sample.get("cluster_name", ""),
        sample.get("candidate_memory", ""),
        sample.get("candidate_rule", ""),
        sample.get("label_rationale", ""),
    ]

    skill = sample.get("candidate_skill", {})
    parts.append(str(skill.get("name", "")))
    parts.append(str(skill.get("risk", "")))
    for key in ["trigger", "steps", "limitations"]:
        value = skill.get(key, [])
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
        else:
            parts.append(str(value))

    for item in sample.get("experience_cluster", []):
        parts.extend(str(item.get(key, "")) for key in ["observation", "diagnosis", "fix_pattern", "risk"])

    return "\n".join(parts).lower()


def contains_any(text: str, markers: list[str]) -> bool:
    return any(marker in text for marker in markers)


def keyword_level_baseline(sample: dict[str, Any]) -> str:
    """A deliberately simple text-only baseline.

    It does not read gold labels, sample IDs, or tags. Its purpose is to show how
    far plain marker matching can go before a full controller is needed.
    """
    text = sample_text(sample)

    harmful = [
        "actively harmful",
        "disable csrf",
        "log bearer tokens",
        "leaks credentials",
        "drop database constraints",
        "drop constraints",
        "mark migrations applied without running",
        "fabricates schema state",
        "delete lockfile",
        "upgrade everything",
        "ignore kafka commit failures",
        "commit base64 encoded secrets",
        "wildcard cors with credentials",
        "truncate data",
        "disable rate limits",
        "bypass",
        "turn off",
        "remove protection",
        "destroy",
        "hide corrupt data",
        "harmful workaround",
    ]
    if contains_any(text, harmful):
        return "discard"

    defer = [
        "uncertainty",
        "depends on",
        "contexts differ",
        "context differs",
        "needs more validation",
        "needs sharper",
        "policy boundary is underspecified",
        "conflicting requirement",
        "universal policy would be wrong",
        "trade off differently",
        "threshold depends",
        "privacy and debuggability",
        "forward compatibility and strict validation conflict",
        "not yet separated",
    ]
    if contains_any(text, defer):
        return "defer"

    memory = [
        "current frozen controller",
        "current regression scope",
        "current v7",
        "project root",
        "document path",
        "conda env",
        "python 3.10.20",
        "openai_base_url",
        "skilladmit_model",
        ".env",
        "repository-specific",
        "local environment",
        "evaluation snapshot",
        "benchmark metadata",
        "repository convention",
        "current protocol state",
        "only true for this repository",
        "may become stale",
        "continuation memory",
    ]
    if contains_any(text, memory):
        return "store_as_memory"

    rule = [
        "global safety constraint",
        "global compatibility rule",
        "global traceability rule",
        "evaluation protocol rule",
        "global integrity rule",
        "global correctness rule",
        "cross-skill control rule",
        "global reliability rule",
        "evaluation-reporting rule",
        "central admission rule",
        "should constrain future",
        "constrain future admissions",
        "do not weaken",
        "do not silently change",
        "every admitted artifact",
        "same task budget",
        "keep validators active",
        "preserve failure visibility",
        "state runtime assumptions",
        "cache with invalidation",
        "metrics need scope",
        "check preconditions",
    ]
    if contains_any(text, rule):
        return "promote_to_rule"

    return "distill_into_skill"


def load_controller_predictor(module_name: str) -> Callable[[dict[str, Any]], str]:
    module = importlib.import_module(module_name)
    controller = module.RuleBasedSkillAdmitController()
    return lambda sample: controller.predict(sample).prediction


@dataclass
class EvalResult:
    name: str
    sample_file: str
    total: int
    correct: int
    accuracy: float
    macro_f1: float
    confusion: dict[str, dict[str, int]]
    errors: list[dict[str, str]]


def macro_f1(confusion: dict[str, Counter[str]]) -> float:
    scores = []
    for label in ACTIONS:
        tp = confusion.get(label, Counter()).get(label, 0)
        fp = sum(preds.get(label, 0) for gold, preds in confusion.items() if gold != label)
        fn = sum(count for pred, count in confusion.get(label, Counter()).items() if pred != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        scores.append(f1)
    return sum(scores) / len(scores)


def evaluate_predictor(name: str, predictor: Callable[[dict[str, Any]], str], sample_file: Path) -> EvalResult:
    samples = load_jsonl(sample_file)
    confusion: dict[str, Counter[str]] = defaultdict(Counter)
    errors: list[dict[str, str]] = []
    correct = 0

    for sample in samples:
        gold = sample["label"]
        pred = predictor(sample)
        if pred not in ACTIONS:
            raise ValueError(f"{name} predicted invalid action {pred!r}")
        confusion[gold][pred] += 1
        if pred == gold:
            correct += 1
        else:
            errors.append(
                {
                    "sample_id": sample["sample_id"],
                    "cluster_name": sample["cluster_name"],
                    "gold": gold,
                    "pred": pred,
                }
            )

    total = len(samples)
    return EvalResult(
        name=name,
        sample_file=display_path(sample_file),
        total=total,
        correct=correct,
        accuracy=correct / total if total else 0.0,
        macro_f1=macro_f1(confusion),
        confusion={gold: dict(preds) for gold, preds in sorted(confusion.items())},
        errors=errors,
    )


def default_predictors() -> dict[str, Callable[[dict[str, Any]], str]]:
    predictors: dict[str, Callable[[dict[str, Any]], str]] = {
        "always_discard": lambda sample: "discard",
        "always_store_as_memory": lambda sample: "store_as_memory",
        "always_distill_into_skill": lambda sample: "distill_into_skill",
        "always_promote_to_rule": lambda sample: "promote_to_rule",
        "always_defer": lambda sample: "defer",
        "keyword_level_baseline": keyword_level_baseline,
    }
    return predictors


def render_markdown(results: list[EvalResult]) -> str:
    lines = [
        "# Admission Baseline Report",
        "",
        "This report compares simple admission baselines on the selected sample files.",
        "",
        "| sample_file | method | correct | total | accuracy | macro_f1 | errors |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in results:
        lines.append(
            f"| {result.sample_file} | {result.name} | {result.correct} | {result.total} | "
            f"{result.accuracy:.3f} | {result.macro_f1:.3f} | {len(result.errors)} |"
        )

    lines.extend(["", "## Error Summary", ""])
    for result in results:
        lines.append(f"### {result.sample_file} / {result.name}")
        if not result.errors:
            lines.append("")
            lines.append("No errors.")
            lines.append("")
            continue
        lines.append("")
        for error in result.errors[:20]:
            lines.append(
                f"- `{error['sample_id']}`: gold=`{error['gold']}`, "
                f"pred=`{error['pred']}`, cluster={error['cluster_name']}"
            )
        if len(result.errors) > 20:
            lines.append(f"- ... {len(result.errors) - 20} more errors")
        lines.append("")

    return "\n".join(lines) + "\n"


def print_summary(results: list[EvalResult]) -> None:
    for result in results:
        print("=" * 100)
        print(f"samples:  {result.sample_file}")
        print(f"method:   {result.name}")
        print(f"correct:  {result.correct}/{result.total}")
        print(f"accuracy: {result.accuracy:.3f}")
        print(f"macro_f1: {result.macro_f1:.3f}")
        print(f"errors:   {len(result.errors)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=Path, action="append", required=True)
    parser.add_argument(
        "--controller-module",
        action="append",
        default=[],
        help="Optional controller module to include as a method. Can be repeated.",
    )
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    args = parser.parse_args()

    predictors = default_predictors()
    for module_name in args.controller_module:
        predictors[module_name] = load_controller_predictor(module_name)

    results: list[EvalResult] = []
    for sample_file in args.samples:
        for name, predictor in predictors.items():
            results.append(evaluate_predictor(name, predictor, sample_file))

    print_summary(results)

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps([result.__dict__ for result in results], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote JSON report to {args.output_json}")

    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(render_markdown(results), encoding="utf-8")
        print(f"Wrote Markdown report to {args.output_md}")


if __name__ == "__main__":
    main()
