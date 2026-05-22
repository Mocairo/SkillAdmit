#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from textwrap import dedent
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "benchmark" / "downstream" / "tasks"
ADMISSION_SAMPLES = ROOT / "benchmark" / "admission_samples" / "llm_coding_agent_v0_admission_samples.jsonl"
RUN_ROOT = ROOT / "benchmark" / "downstream" / "llm_runs"

STRATEGIES = [
    "no_experience",
    "raw_memory",
    "promoted_rules",
    "distilled_skills_all",
    "skilladmit_selected",
    "skilladmit_selected_with_precondition_only",
    "skilladmit_selected_with_precondition_context",
    "bad_dependency_rule",
    "forced_bad_artifact",
]

DEFAULT_STRATEGIES = [
    "no_experience",
    "raw_memory",
    "promoted_rules",
    "distilled_skills_all",
    "skilladmit_selected",
    "bad_dependency_rule",
    "forced_bad_artifact",
]

SYSTEM_PROMPT = """\
You are a careful coding agent.

You will receive a small Python project with a failing verifier and, depending
on the experiment condition, optional prior experience artifacts.

Rules:
- Return only JSON. Do not wrap it in markdown.
- Do not include chain-of-thought.
- Do not install packages.
- Prefer minimal code edits.
- Do not edit tests or verifier scripts unless the task explicitly asks you to.
- You may ignore prior experience if it is irrelevant or unsafe.
- The JSON schema must be:
{
  "diagnosis": "short explanation",
  "used_artifact": "none, raw_memory, promoted_rules, distilled_skills_all, skilladmit_selected, skilladmit_selected_with_precondition_only, skilladmit_selected_with_precondition_context, bad_dependency_rule, or forced_bad_artifact",
  "edits": [
    {
      "path": "relative/path/from/repo/root.py",
      "content": "complete new file content"
    }
  ],
  "notes": "short note"
}
"""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def task_dirs(tasks_dir: Path) -> list[Path]:
    return sorted(path for path in tasks_dir.iterdir() if path.is_dir())


def load_task(task_dir: Path) -> dict[str, Any]:
    return json.loads((task_dir / "task.json").read_text(encoding="utf-8"))


def load_skill_samples() -> list[dict[str, Any]]:
    return read_jsonl(ADMISSION_SAMPLES)


def skill_name_to_sample(samples: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {sample["candidate_skill"]["name"]: sample for sample in samples}


def run_cmd(cmd: list[str], cwd: Path, timeout: int = 30) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return {
        "cmd": " ".join(cmd),
        "cwd": str(cwd),
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-3000:],
        "stderr_tail": proc.stderr[-3000:],
    }


def collect_files(
    repo: Path,
    max_chars_per_file: int = 6000,
    max_files: int | None = None,
    visible_files: list[str] | None = None,
) -> list[dict[str, str]]:
    rows = []
    if visible_files is not None:
        candidate_paths = [repo / rel_path for rel_path in visible_files]
    else:
        candidate_paths = sorted(repo.rglob("*"))

    for path in candidate_paths:
        if not path.is_file():
            continue
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(repo).as_posix()
        if not (rel.endswith(".py") or rel.endswith(".txt") or rel.endswith(".json") or rel.endswith(".md")):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_chars_per_file:
            text = text[:max_chars_per_file] + "\n...<truncated>..."
        rows.append({"path": rel, "content": text})
        if max_files is not None and len(rows) >= max_files:
            break
    return rows


def collect_repo_tree(repo: Path, max_entries: int = 160) -> list[str]:
    rows = []
    for path in sorted(repo.rglob("*")):
        if "__pycache__" in path.parts or ".pytest_cache" in path.parts:
            continue
        rel = path.relative_to(repo).as_posix()
        suffix = "/" if path.is_dir() else ""
        rows.append(rel + suffix)
        if len(rows) >= max_entries:
            rows.append("...<truncated>...")
            break
    return rows


def skill_block(sample: dict[str, Any]) -> str:
    skill = sample["candidate_skill"]
    return dedent(
        f"""\
        Skill: {skill['name']}
        Trigger:
        {json.dumps(skill.get('trigger', []), ensure_ascii=False)}
        Steps:
        {json.dumps(skill.get('steps', []), ensure_ascii=False)}
        Limitations:
        {json.dumps(skill.get('limitations', []), ensure_ascii=False)}
        Risk:
        {skill.get('risk', '')}
        """
    ).strip()


def raw_memory_block(sample: dict[str, Any], max_items: int = 3) -> str:
    rows = []
    for item in sample.get("experience_cluster", [])[:max_items]:
        rows.append(
            dedent(
                f"""\
                Previous task: {item.get('task_id')}
                Observation: {str(item.get('observation', '')).strip()[:600]}
                Diagnosis: {item.get('diagnosis', '')}
                Fix pattern: {item.get('fix_pattern', '')}
                Notes: {item.get('notes', '')}
                Validation: {item.get('validation', '')}
                """
            ).strip()
        )
    return "\n\n".join(rows)


def rules_block(samples: list[dict[str, Any]]) -> str:
    lines = []
    for sample in samples:
        lines.append(f"- {sample['candidate_rule']}")
    lines.append("- Before applying any repair, check whether the current task satisfies the artifact preconditions.")
    lines.append("- Do not use a generic dependency-install fix until local files, launch mode, cwd, and package structure have been checked.")
    return "\n".join(lines)


def precondition_context_block(skill_name: str, has_repo_tree: bool) -> str:
    shared_guardrails = [
        "First classify the failure before editing: unused import, local module, script/package launch mode, cwd/path bug, package-internal import, or true external dependency.",
        "Do not make public pytest pass by masking the bug with compatibility stubs, duplicated data, test edits, verifier edits, or sys.path hacks unless the project structure proves that is the intended design.",
        "If a prior skill is relevant, apply it only after its preconditions are satisfied by the current repository layout and command context.",
    ]
    if has_repo_tree:
        shared_guardrails.insert(
            1,
            "Use the repository tree to check whether a missing name or target file already exists in the repo before creating any new top-level module, stub, package, or data file.",
        )
    else:
        shared_guardrails.insert(
            1,
            "This strict ablation does not provide a repository tree. Use only visible files and verifier output; do not invent unseen files or assume a hidden path unless the visible failure makes it necessary.",
        )
    by_skill = {
        "Remove Unused Missing Imports": [
            "Before treating ModuleNotFoundError as a dependency problem, inspect the importing file and confirm whether the missing import is used by behavior under test.",
            "If the import is unused, remove only that import and preserve existing functions and return values.",
        ],
        "Repair Local Module Imports": [
            (
                "Before creating a missing module, search the repository tree for the same-named local file inside the package directory."
                if has_repo_tree
                else "Before creating a missing module, inspect the visible package path and import statement; if tests import package_name.main, a same-package local module may be hidden from the strict visible-files prompt."
            ),
            "If tests import package_name.main, prefer a relative or package-qualified import that points to the existing package-local module.",
        ],
        "Repair Relative Imports for Script Execution": [
            "Before changing relative imports, inspect the verifier command and tests to determine whether the file is executed as python path/to/file.py or as python -m package.module.",
            "For direct script execution, use an import form that works from the script directory while preserving the script's observable output.",
        ],
        "Repair CWD-Sensitive File Paths": [
            (
                "Before choosing a path anchor, locate the real target data file in the repository tree."
                if has_repo_tree
                else "Before choosing a path anchor, determine whether the real target data file location is visible. If it is hidden, avoid pretending that the script directory is known to be correct."
            ),
            (
                "Do not anchor the path merely to the script directory. If the data file is at repo_root/data/name.txt, anchor through Path(__file__).resolve().parents[...] to that real location."
                if has_repo_tree
                else "Do not anchor merely to the script directory unless visible evidence shows the data lives there; hidden validation may reject that assumption."
            ),
            "Do not duplicate data under the current working directory; that masks the cwd bug and can fail hidden validation.",
            "After editing, make sure the code reads the file contents, not the path string.",
        ],
        "Repair Package-Internal Bare Imports": [
            (
                "Before creating a top-level package, check whether the missing name is an internal package/submodule already visible in the repository tree."
                if has_repo_tree
                else "Before creating a top-level package, inspect package_name.main and the import path; if tests import a package namespace, the missing bare name may be package-internal even if hidden files are not shown."
            ),
            "If tests import package_name.main, fix the package-internal bare import with a relative or package-qualified import instead of adding top-level modules.",
        ],
    }
    lines = shared_guardrails + by_skill.get(skill_name, [])
    return "\n".join(f"- {line}" for line in lines)


def artifact_context(strategy: str, task: dict[str, Any], samples: list[dict[str, Any]]) -> str:
    by_skill = skill_name_to_sample(samples)
    selected = by_skill.get(task.get("downstream_gold_skill"))

    if strategy == "no_experience":
        return "No prior experience artifact is available."

    if strategy == "bad_dependency_rule":
        return dedent(
            """\
            Prior artifact:
            If Python raises ModuleNotFoundError, create or install a top-level module with the missing name.

            Warning for evaluator: this is intentionally a candidate artifact. Apply it only if it is actually appropriate.
            """
        ).strip()

    if strategy == "forced_bad_artifact":
        return dedent(
            f"""\
            Forced bad artifact:
            {task.get('forced_bad_artifact_name', 'Apply the task-provided bad artifact edits.')}

            This condition is a deterministic negative-transfer baseline, not an LLM choice.
            """
        ).strip()

    if strategy == "promoted_rules":
        return "Promoted rules:\n" + rules_block(samples)

    if strategy == "distilled_skills_all":
        return "Available distilled skills:\n\n" + "\n\n".join(skill_block(sample) for sample in samples)

    if strategy == "raw_memory":
        if not selected:
            return "No matching raw memory was retrieved."
        return "Retrieved raw memories:\n\n" + raw_memory_block(selected)

    if strategy == "skilladmit_selected":
        if not selected:
            return "SkillAdmit did not select a matching artifact."
        return "SkillAdmit-selected artifact:\n\n" + skill_block(selected)

    if strategy == "skilladmit_selected_with_precondition_only":
        if not selected:
            return "SkillAdmit did not select a matching artifact."
        skill_name = selected["candidate_skill"]["name"]
        return (
            "SkillAdmit-selected artifact:\n\n"
            + skill_block(selected)
            + "\n\nPrecondition and guardrail context for this selected skill, without repository tree context:\n"
            + precondition_context_block(skill_name, has_repo_tree=False)
            + "\n\nThis is a strict ablation: do not assume repository-tree paths that are not shown. "
            + 'If you rely on this selected skill and guardrail context, set "used_artifact" '
            + 'to "skilladmit_selected_with_precondition_only".'
        )

    if strategy == "skilladmit_selected_with_precondition_context":
        if not selected:
            return "SkillAdmit did not select a matching artifact."
        skill_name = selected["candidate_skill"]["name"]
        return (
            "SkillAdmit-selected artifact:\n\n"
            + skill_block(selected)
            + "\n\nPrecondition and guardrail context for this selected skill:\n"
            + precondition_context_block(skill_name, has_repo_tree=True)
            + "\n\nIf you rely on this selected skill and guardrail context, set "
            '"used_artifact" to "skilladmit_selected_with_precondition_context".'
        )

    raise ValueError(f"Unknown strategy: {strategy}")


def build_user_prompt(
    task: dict[str, Any],
    strategy: str,
    context: str,
    files: list[dict[str, str]],
    verifier_result: dict[str, Any],
    repo_tree: list[str] | None = None,
) -> str:
    file_blocks = []
    for item in files:
        file_blocks.append(
            f"### FILE: {item['path']}\n"
            "```text\n"
            f"{item['content']}\n"
            "```"
        )

    hidden_note = ""
    if task.get("file_context_note"):
        hidden_note = f"\nFile context note:\n{task['file_context_note']}\n"

    tree_block = ""
    if repo_tree is not None:
        tree_block = (
            "\nRepository tree, paths only:\n"
            "```text\n"
            + "\n".join(repo_tree)
            + "\n```\n"
        )

    return dedent(
        f"""\
        Experiment strategy:
        {strategy}

        Task:
        {task["instruction"]}

        Failing command:
        {task["failing_command"]}

        Verifier command:
        {task["verifier"]}

        Expected failure:
        {task["expected_failure"]}
        {hidden_note}

        Prior experience artifact context:
        ```text
        {context}
        ```
        {tree_block}

        Verifier result:
        returncode={verifier_result["returncode"]}

        stdout_tail:
        ```text
        {verifier_result["stdout_tail"]}
        ```

        stderr_tail:
        ```text
        {verifier_result["stderr_tail"]}
        ```

        Repository files:
        {chr(10).join(file_blocks)}

        Return the JSON patch now.
        """
    ).strip()


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def call_model(client: OpenAI, model: str, user_prompt: str) -> tuple[str, dict[str, int | None], float]:
    start = time.perf_counter()
    output_text = ""
    usage = None

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        top_p=0.95,
        max_completion_tokens=4096,
        stream=True,
        stream_options={"include_usage": True},
    )

    for chunk in stream:
        if getattr(chunk, "usage", None) is not None:
            usage = chunk.usage
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if delta:
            output_text += delta

    elapsed = time.perf_counter() - start
    usage_dict = {
        "prompt_tokens": getattr(usage, "prompt_tokens", None) if usage is not None else None,
        "completion_tokens": getattr(usage, "completion_tokens", None) if usage is not None else None,
        "total_tokens": getattr(usage, "total_tokens", None) if usage is not None else None,
    }
    return output_text, usage_dict, elapsed


def repair_json_response(client: OpenAI, model: str, raw_response: str, error: str) -> tuple[str, dict[str, int | None], float]:
    repair_prompt = dedent(
        f"""\
        The following model output was intended to be JSON, but it failed to parse.

        Parse error:
        {error}

        Broken output:
        ```text
        {raw_response}
        ```

        Return only corrected JSON matching this exact schema:
        {{
          "diagnosis": "short explanation",
          "used_artifact": "none, raw_memory, promoted_rules, distilled_skills_all, skilladmit_selected, skilladmit_selected_with_precondition_only, skilladmit_selected_with_precondition_context, bad_dependency_rule, or forced_bad_artifact",
          "edits": [
            {{
              "path": "relative/path/from/repo/root.py",
              "content": "complete new file content"
            }}
          ],
          "notes": "short note"
        }}
        """
    ).strip()
    return call_model(client, model, repair_prompt)


def parse_or_repair_patch(client: OpenAI, model: str, raw_response: str) -> tuple[dict[str, Any], dict[str, Any]]:
    info: dict[str, Any] = {
        "attempted": False,
        "raw_repair_response": "",
        "repair_error": None,
        "repair_usage": {},
        "repair_latency_seconds": None,
    }
    try:
        return extract_json(raw_response), info
    except Exception as exc:
        info["attempted"] = True
        info["repair_error"] = repr(exc)
        repaired, usage, latency = repair_json_response(client, model, raw_response, repr(exc))
        info["raw_repair_response"] = repaired
        info["repair_usage"] = usage
        info["repair_latency_seconds"] = latency
        return extract_json(repaired), info


def apply_edits(repo: Path, patch: dict[str, Any]) -> list[dict[str, Any]]:
    applied = []
    edits = patch.get("edits", [])
    if not isinstance(edits, list):
        raise ValueError("patch['edits'] must be a list")

    for edit in edits:
        rel_path = edit["path"]
        content = edit["content"]
        if rel_path.startswith("/") or ".." in Path(rel_path).parts:
            raise ValueError(f"Unsafe edit path: {rel_path}")
        path = repo / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        old_content = path.read_text(encoding="utf-8", errors="replace") if path.exists() else None
        path.write_text(content, encoding="utf-8")
        applied.append(
            {
                "path": rel_path,
                "existed": old_content is not None,
                "changed": old_content != content,
                "new_size": len(content),
            }
        )
    return applied


def forced_bad_patch(task: dict[str, Any]) -> dict[str, Any]:
    edits = task.get("forced_bad_artifact_edits")
    if not edits:
        raise ValueError(f"Task does not define forced_bad_artifact_edits: {task.get('task_id')}")
    return {
        "diagnosis": "Deterministically applying the task-provided bad artifact to measure negative transfer.",
        "used_artifact": "forced_bad_artifact",
        "edits": edits,
        "notes": "This baseline intentionally applies a masking or overgeneralized repair.",
    }


def artifact_adherence(strategy: str, patch: dict[str, Any] | None) -> bool:
    used = (patch or {}).get("used_artifact")
    if strategy == "no_experience":
        return used in (None, "none")
    if strategy in ("skilladmit_selected_with_precondition_only", "skilladmit_selected_with_precondition_context"):
        return used in (strategy, "skilladmit_selected")
    return used == strategy


def copy_workspace(task_dir: Path, run_dir: Path, strategy: str) -> Path:
    workspace = run_dir / "workspaces" / strategy / task_dir.name
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(task_dir, workspace)
    return workspace


def run_one(
    client: OpenAI,
    model: str,
    task_dir: Path,
    strategy: str,
    skill_samples: list[dict[str, Any]],
    run_dir: Path,
    max_files: int | None,
    use_task_visible_files: bool,
    include_repo_tree: bool,
) -> dict[str, Any]:
    task = load_task(task_dir)
    workspace = copy_workspace(task_dir, run_dir, strategy)
    repo = workspace / "repo"

    initial = run_cmd(["bash", "verifier.sh"], workspace)
    visible_files = task.get("visible_files") if use_task_visible_files else None
    files = collect_files(repo, max_files=max_files, visible_files=visible_files)
    effective_include_repo_tree = include_repo_tree or strategy == "skilladmit_selected_with_precondition_context"
    repo_tree = collect_repo_tree(repo) if effective_include_repo_tree else None
    context = artifact_context(strategy, task, skill_samples)
    prompt = build_user_prompt(task, strategy, context, files, initial, repo_tree=repo_tree)

    raw_response = ""
    parsed_patch = None
    parse_error = None
    applied_edits: list[dict[str, Any]] = []
    model_usage: dict[str, int | None] = {}
    model_latency = None
    repair_info: dict[str, Any] = {}
    retry_count = 0

    try:
        if strategy == "forced_bad_artifact":
            parsed_patch = forced_bad_patch(task)
            raw_response = json.dumps(parsed_patch, ensure_ascii=False, indent=2)
            model_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            model_latency = 0.0
            repair_info = {
                "attempted": False,
                "raw_repair_response": "",
                "repair_error": None,
                "repair_usage": {},
                "repair_latency_seconds": None,
            }
        else:
            raw_response, model_usage, model_latency = call_model(client, model, prompt)
            if not raw_response.strip():
                retry_count += 1
                raw_response, model_usage, model_latency = call_model(client, model, prompt)
            parsed_patch, repair_info = parse_or_repair_patch(client, model, raw_response)
        applied_edits = apply_edits(repo, parsed_patch)
    except Exception as exc:
        parse_error = repr(exc)

    public_tests = run_cmd(["python", "-m", "pytest", "-q"], repo)
    final = run_cmd(["bash", "verifier.sh"], workspace)
    success = final["returncode"] == 0
    changed = any(edit.get("changed") for edit in applied_edits)
    public_passed_hidden_failed = public_tests["returncode"] == 0 and not success

    return {
        "run_id": run_dir.name,
        "agent": "llm_downstream_validation_v0",
        "model": model,
        "strategy": strategy,
        "task_id": task["task_id"],
        "template": task["template"],
        "gold_skill": task.get("downstream_gold_skill"),
        "workspace": str(workspace.relative_to(ROOT)),
        "success": success,
        "negative_transfer": changed and not success,
        "initial_returncode": initial["returncode"],
        "final_returncode": final["returncode"],
        "initial_verifier": initial,
        "public_tests_after_edit": public_tests,
        "public_tests_passed": public_tests["returncode"] == 0,
        "public_passed_hidden_failed": public_passed_hidden_failed,
        "final_verifier": final,
        "files_seen": [item["path"] for item in files],
        "repo_tree_seen": repo_tree or [],
        "included_repo_tree": effective_include_repo_tree,
        "used_task_visible_files": use_task_visible_files,
        "artifact_context_chars": len(context),
        "raw_model_response": raw_response,
        "parsed_patch": parsed_patch,
        "artifact_adherence": artifact_adherence(strategy, parsed_patch),
        "parse_error": parse_error,
        "repair_info": repair_info,
        "retry_count": retry_count,
        "applied_edits": applied_edits,
        "model_usage": model_usage,
        "model_latency_seconds": model_latency,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["strategy"], []).append(row)

    strategies = {}
    for strategy, items in sorted(grouped.items()):
        total_tokens = sum(int((item.get("model_usage") or {}).get("total_tokens") or 0) for item in items)
        latencies = [float(item["model_latency_seconds"]) for item in items if item.get("model_latency_seconds") is not None]
        strategies[strategy] = {
            "tasks": len(items),
            "successes": sum(1 for item in items if item["success"]),
            "success_rate": sum(1 for item in items if item["success"]) / len(items) if items else 0.0,
            "negative_transfer": sum(1 for item in items if item["negative_transfer"]),
            "public_passed_hidden_failed": sum(1 for item in items if item.get("public_passed_hidden_failed")),
            "artifact_adherence": sum(1 for item in items if item.get("artifact_adherence")),
            "parse_errors": sum(1 for item in items if item["parse_error"]),
            "total_tokens": total_tokens,
            "avg_tokens": total_tokens / len(items) if items else 0.0,
            "total_latency_seconds": sum(latencies),
            "avg_latency_seconds": sum(latencies) / len(latencies) if latencies else 0.0,
        }
    return {
        "total_rows": len(rows),
        "strategies": strategies,
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# LLM Downstream Validation v0",
        "",
        "This report summarizes a real LLM smoke/downstream run with artifact contexts.",
        "",
        "| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens | avg_latency_sec |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for strategy, item in summary["strategies"].items():
        lines.append(
            f"| {strategy} | {item['successes']} | {item['tasks']} | {item['success_rate']:.3f} | "
            f"{item['negative_transfer']} | {item['public_passed_hidden_failed']} | "
            f"{item['artifact_adherence']} | {item['parse_errors']} | {item['total_tokens']} | "
            f"{item['avg_tokens']:.1f} | {item['avg_latency_seconds']:.2f} |"
        )
    lines.extend(
        [
            "",
            "## Caveat",
            "",
            "This is an LLM-based validation runner, but small smoke runs are not full downstream evidence.",
            "Use the same script on all 25 downstream tasks and all target strategies for a paper-grade run.",
            "",
        ]
    )
    return "\n".join(lines)


def selected_task_dirs(tasks_dir: Path, task_ids: list[str] | None, limit: int | None) -> list[Path]:
    dirs = task_dirs(tasks_dir)
    if task_ids:
        wanted = set(task_ids)
        dirs = [path for path in dirs if load_task(path)["task_id"] in wanted]
    if limit is not None:
        dirs = dirs[:limit]
    return dirs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-name", default="llm_downstream_v0_smoke")
    parser.add_argument("--tasks-dir", type=Path, default=TASKS_DIR)
    parser.add_argument("--strategy", action="append", choices=STRATEGIES)
    parser.add_argument("--task-id", action="append")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-files", type=int)
    parser.add_argument("--use-task-visible-files", action="store_true")
    parser.add_argument("--include-repo-tree", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY in environment or .env")

    base_url = os.getenv("OPENAI_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")
    model = os.getenv("SKILLADMIT_MODEL", "mimo-v2.5-pro")
    client = OpenAI(api_key=api_key, base_url=base_url)

    tasks_dir = args.tasks_dir
    if not tasks_dir.is_absolute():
        tasks_dir = ROOT / tasks_dir
    if not tasks_dir.exists():
        raise SystemExit(f"Missing downstream tasks: {tasks_dir}")

    run_dir = RUN_ROOT / args.run_name
    out_jsonl = run_dir / "trajectories.jsonl"
    rows: list[dict[str, Any]] = []
    if run_dir.exists() and not args.resume:
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    if args.resume and out_jsonl.exists():
        rows = read_jsonl(out_jsonl)
        print(f"Resuming {args.run_name}: loaded {len(rows)} existing rows", flush=True)

    strategies = args.strategy or DEFAULT_STRATEGIES
    tasks = selected_task_dirs(tasks_dir, args.task_id, args.limit)
    skill_samples = load_skill_samples()
    existing_keys = {(row["strategy"], row["task_id"]) for row in rows}

    for strategy in strategies:
        for task_dir in tasks:
            task = load_task(task_dir)
            key = (strategy, task["task_id"])
            if args.resume and key in existing_keys:
                print(f"Skipping existing strategy={strategy} task={task['task_id']}", flush=True)
                continue
            print(f"Running strategy={strategy} task={task['task_id']} ...", flush=True)
            row = run_one(
                client,
                model,
                task_dir,
                strategy,
                skill_samples,
                run_dir,
                args.max_files,
                args.use_task_visible_files,
                args.include_repo_tree,
            )
            rows.append(row)
            existing_keys.add(key)
            write_jsonl(out_jsonl, rows)
            print(
                f"{strategy} {task['task_id']}: success={row['success']} "
                f"final={row['final_returncode']} parse_error={row['parse_error']} "
                f"tokens={(row.get('model_usage') or {}).get('total_tokens')}",
                flush=True,
            )

    summary = summarize(rows)
    summary_json = run_dir / "summary.json"
    summary_md = run_dir / "report.md"
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_md.write_text(render_markdown(summary), encoding="utf-8")

    print("=" * 100)
    for strategy, item in summary["strategies"].items():
        print(
            f"{strategy}: {item['successes']}/{item['tasks']} "
            f"success_rate={item['success_rate']:.3f} "
            f"negative_transfer={item['negative_transfer']} "
            f"public_hidden_failures={item['public_passed_hidden_failed']} "
            f"total_tokens={item['total_tokens']}"
        )
    print(f"Wrote trajectories to {out_jsonl}")
    print(f"Wrote summary to {summary_json}")
    print(f"Wrote report to {summary_md}")


if __name__ == "__main__":
    main()
