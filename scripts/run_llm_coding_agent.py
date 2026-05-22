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
MANIFEST = ROOT / "benchmark" / "task_manifest.jsonl"
RUN_DIR = ROOT / "benchmark" / "agent_runs" / "llm_coding_agent_v0"
WORKSPACES = RUN_DIR / "workspaces"
OUT = RUN_DIR / "trajectories.jsonl"


SYSTEM_PROMPT = """\
You are a careful coding agent.

You will receive a small Python project with a failing verifier.
Your job is to propose file edits that fix the project.

Rules:
- Return only JSON. Do not wrap it in markdown.
- Do not include chain-of-thought.
- Do not install packages.
- Prefer minimal code edits.
- Do not edit tests unless the task explicitly asks you to.
- The JSON schema must be:
{
  "diagnosis": "short explanation",
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


def run_cmd(cmd: list[str], cwd: Path, timeout: int = 30) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return {
        "cmd": " ".join(cmd),
        "cwd": str(cwd),
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-3000:],
        "stderr_tail": proc.stderr[-3000:],
    }


def copy_workspace(task: dict[str, Any]) -> Path:
    src = ROOT / task["task_dir"]
    dst = WORKSPACES / task["task_id"]
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return dst


def collect_files(repo: Path, max_chars_per_file: int = 6000) -> list[dict[str, str]]:
    rows = []
    for path in sorted(repo.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(repo).as_posix()
        if not (
            rel.endswith(".py")
            or rel.endswith(".txt")
            or rel.endswith(".json")
            or rel.endswith(".md")
        ):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_chars_per_file:
            text = text[:max_chars_per_file] + "\n...<truncated>..."
        rows.append({"path": rel, "content": text})
    return rows


def build_user_prompt(task: dict[str, Any], files: list[dict[str, str]], verifier_result: dict[str, Any]) -> str:
    file_blocks = []
    for item in files:
        file_blocks.append(
            f"### FILE: {item['path']}\n"
            "```text\n"
            f"{item['content']}\n"
            "```"
        )

    return dedent(f"""\
    Task:
    {task["instruction"]}

    Failing command:
    {task["failing_command"]}

    Verifier command:
    {task["verifier"]}

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
    """).strip()


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
    repair_prompt = dedent(f"""\
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
      "edits": [
        {{
          "path": "relative/path/from/repo/root.py",
          "content": "complete new file content"
        }}
      ],
      "notes": "short note"
    }}
    """).strip()

    return call_model(client, model, repair_prompt)


def parse_or_repair_patch(client: OpenAI, model: str, raw_response: str) -> tuple[dict[str, Any], dict[str, Any]]:
    repair_info: dict[str, Any] = {
        "attempted": False,
        "raw_repair_response": "",
        "repair_error": None,
        "repair_usage": {},
        "repair_latency_seconds": None,
    }

    try:
        return extract_json(raw_response), repair_info
    except Exception as exc:
        repair_info["attempted"] = True
        repair_info["repair_error"] = repr(exc)
        repaired, repair_usage, repair_latency = repair_json_response(client, model, raw_response, repr(exc))
        repair_info["raw_repair_response"] = repaired
        repair_info["repair_usage"] = repair_usage
        repair_info["repair_latency_seconds"] = repair_latency
        return extract_json(repaired), repair_info


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

        applied.append({
            "path": rel_path,
            "existed": old_content is not None,
            "changed": old_content != content,
            "new_size": len(content),
        })

    return applied


def run_agent_on_task(client: OpenAI, model: str, task: dict[str, Any]) -> dict[str, Any]:
    workspace = copy_workspace(task)
    repo = workspace / "repo"

    initial = run_cmd(["bash", "verifier.sh"], workspace)
    files = collect_files(repo)
    user_prompt = build_user_prompt(task, files, initial)

    raw_response = ""
    parsed_patch = None
    parse_error = None
    applied_edits = []
    model_usage = {}
    model_latency = None
    repair_info = {}
    retry_count = 0

    try:
        raw_response, model_usage, model_latency = call_model(client, model, user_prompt)
        if not raw_response.strip():
            retry_count += 1
            raw_response, model_usage, model_latency = call_model(client, model, user_prompt)
        parsed_patch, repair_info = parse_or_repair_patch(client, model, raw_response)
        applied_edits = apply_edits(repo, parsed_patch)
    except Exception as exc:
        parse_error = repr(exc)

    final = run_cmd(["bash", "verifier.sh"], workspace)
    success = final["returncode"] == 0

    return {
        "trajectory_id": f"llm_v0_{task['task_id']}",
        "agent": "llm_coding_agent_v0",
        "model": model,
        "task_id": task["task_id"],
        "family": task["family"],
        "template": task["template"],
        "workspace": str(workspace.relative_to(ROOT)),
        "success": success,
        "initial_returncode": initial["returncode"],
        "final_returncode": final["returncode"],
        "initial_verifier": initial,
        "final_verifier": final,
        "files_seen": [item["path"] for item in files],
        "raw_model_response": raw_response,
        "parsed_patch": parsed_patch,
        "parse_error": parse_error,
        "repair_info": repair_info,
        "retry_count": retry_count,
        "applied_edits": applied_edits,
        "model_usage": model_usage,
        "model_latency_seconds": model_latency,
        "trajectory_summary": {
            "observation": task["expected_failure"],
            "diagnosis": parsed_patch.get("diagnosis", "") if isinstance(parsed_patch, dict) else "",
            "fix_pattern": parsed_patch.get("notes", "") if isinstance(parsed_patch, dict) else "",
            "validation": "Verifier passed after patch." if success else "Verifier failed after patch.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--task-id", action="append", default=None)
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY in environment or .env")

    base_url = os.getenv("OPENAI_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")
    model = os.getenv("SKILLADMIT_MODEL", "mimo-v2.5-pro")

    client = OpenAI(api_key=api_key, base_url=base_url)

    if RUN_DIR.exists():
        shutil.rmtree(RUN_DIR)
    WORKSPACES.mkdir(parents=True, exist_ok=True)

    tasks = read_jsonl(MANIFEST)
    if args.task_id:
        wanted = set(args.task_id)
        tasks = [task for task in tasks if task["task_id"] in wanted]
    if args.limit is not None:
        tasks = tasks[: args.limit]

    rows = []

    for task in tasks:
        print(f"Running {task['task_id']} ...", flush=True)
        row = run_agent_on_task(client, model, task)
        rows.append(row)
        print(
            f"{task['task_id']}: success={row['success']} "
            f"initial={row['initial_returncode']} final={row['final_returncode']} "
            f"parse_error={row['parse_error']}",
            flush=True,
        )

        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(
            "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in rows),
            encoding="utf-8",
        )

    passed = sum(1 for row in rows if row["success"])
    print(f"Wrote {len(rows)} trajectories to {OUT}")
    print(f"passed: {passed}/{len(rows)}")


if __name__ == "__main__":
    main()
