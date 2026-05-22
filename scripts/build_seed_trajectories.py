#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmark" / "task_manifest.jsonl"
OUT = ROOT / "benchmark" / "trajectories" / "seed_trajectories.jsonl"


TEMPLATE_SUMMARIES = {
    "T1_missing_third_party_package": {
        "observation": "The task fails with ModuleNotFoundError for a module that is intended to be an external third-party dependency.",
        "diagnosis": "The missing import should be treated as a dependency issue only after checking that it is not a local module.",
        "fix_pattern": "Add or provide the missing dependency, then rerun the verifier.",
        "risk": "This pattern can overgeneralize if applied to local modules with the same error message.",
    },
    "T2_local_module_mistaken_as_missing_package": {
        "observation": "The task fails with ModuleNotFoundError for a name that actually corresponds to a local project file.",
        "diagnosis": "The error is caused by an import path mismatch, not by a missing third-party dependency.",
        "fix_pattern": "Use a package-qualified import or adjust the local import according to the project structure.",
        "risk": "Installing a package with the same name would not address the local import problem.",
    },
    "T3_relative_import_executed_as_script": {
        "observation": "The task fails with an attempted relative import error because a package file is executed as a script.",
        "diagnosis": "Relative imports require package context. The launch mode and import style are inconsistent.",
        "fix_pattern": "Either run the module with package context or change the import style to match script execution.",
        "risk": "Blindly rewriting all relative imports can break package-mode usage.",
    },
    "T4_wrong_current_working_directory": {
        "observation": "The task fails because code relies on the current working directory for imports or file paths.",
        "diagnosis": "The path resolution is unstable across launch locations.",
        "fix_pattern": "Anchor file paths relative to __file__ or ensure commands run from the intended project root.",
        "risk": "Changing imports without checking cwd can hide the real path bug.",
    },
    "T5_broken_package_structure": {
        "observation": "The task fails because code inside a package uses a bare import for a package-internal submodule.",
        "diagnosis": "The import statement does not match the package-qualified context in which the module is loaded.",
        "fix_pattern": "Use a relative import or a package-qualified import for the internal submodule.",
        "risk": "Treating the missing submodule as a third-party dependency causes negative transfer.",
    },
}


def main() -> None:
    rows = []

    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        task = json.loads(line)
        summary = TEMPLATE_SUMMARIES[task["template"]]

        row = {
            "trajectory_id": f"seed_traj_{task['task_id']}",
            "task_id": task["task_id"],
            "family": task["family"],
            "template": task["template"],
            "source": "seed_summary_from_gold_task_design",
            "success": True,
            "failing_command": task["failing_command"],
            "expected_failure": task["expected_failure"],
            "trajectory_summary": {
                "observation": summary["observation"],
                "diagnosis": summary["diagnosis"],
                "fix_pattern": summary["fix_pattern"],
                "risk": summary["risk"],
            },
            "artifact_evidence": {
                "memory_signal": summary["observation"],
                "skill_signal": summary["fix_pattern"],
                "rule_signal": summary["risk"],
            },
        }
        rows.append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )

    print(f"Wrote {len(rows)} seed trajectories to {OUT}")


if __name__ == "__main__":
    main()
