#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLUSTERS = ROOT / "benchmark" / "clusters" / "seed_clusters.json"
OUT = ROOT / "benchmark" / "clusters" / "seed_clusters_with_artifacts.json"


ARTIFACTS = {
    "cluster_t1_missing_third_party": {
        "candidate_memory": "In this task group, the failing imports are true third-party dependencies such as yaml, dotenv, requests, or pydantic.",
        "candidate_skill": {
            "name": "Install Missing Python Dependencies",
            "trigger": [
                "ModuleNotFoundError for an imported module",
                "The missing module is confirmed to be an external dependency"
            ],
            "steps": [
                "Read the failing import and error message.",
                "Check whether the missing module exists as a local file or package.",
                "If it is not local, treat it as a third-party dependency.",
                "Add or provide the dependency, then rerun the verifier."
            ],
            "limitations": [
                "Do not apply before checking whether the missing module is local.",
                "Do not assume every ModuleNotFoundError means a package must be installed."
            ],
            "risk": "Medium risk because it can become a bad skill if shortened to 'pip install every missing module'."
        },
        "candidate_rule": "Before installing a missing Python module, first check whether the missing name belongs to the local project.",
    },
    "cluster_t2_local_module": {
        "candidate_memory": "In this task group, the missing names such as utils, config, service, or parser are local modules inside the app directory.",
        "candidate_skill": {
            "name": "Diagnose Local Module Import Failures",
            "trigger": [
                "ModuleNotFoundError for a short module name",
                "The project contains a file or package with the missing name"
            ],
            "steps": [
                "Search the repository for the missing module name.",
                "Determine whether it is a local module rather than a third-party package.",
                "Inspect the package structure and test import path.",
                "Replace bare imports with package-qualified imports when the module is imported as part of a package.",
                "Rerun the verifier."
            ],
            "limitations": [
                "Do not install a package before checking the repository.",
                "Do not rewrite imports without checking how the code is executed."
            ],
            "risk": "Low risk if the local-module check is kept as an explicit precondition."
        },
        "candidate_rule": "Do not treat ModuleNotFoundError as a dependency problem until local files and packages have been checked.",
    },
    "cluster_t3_relative_import_script": {
        "candidate_memory": "In this task group, files with relative imports are executed directly as scripts, causing parent-package context to be missing.",
        "candidate_skill": {
            "name": "Diagnose Relative Import Script-Mode Failures",
            "trigger": [
                "ImportError: attempted relative import with no known parent package",
                "A Python file uses from .module import name"
            ],
            "steps": [
                "Inspect the failing file for relative imports.",
                "Check whether the file is executed directly with python path/to/file.py.",
                "Decide whether the intended usage is script mode or package mode.",
                "Either run the module with python -m package.module or change imports to match script execution.",
                "Rerun the verifier from the project root."
            ],
            "limitations": [
                "Do not blindly convert all relative imports to absolute imports.",
                "Preserve the intended launch mode of the project."
            ],
            "risk": "Low to medium risk depending on whether the intended launch mode is known."
        },
        "candidate_rule": "Before changing relative imports, confirm whether the file is intended to run as a script or as a package module.",
    },
    "cluster_t4_wrong_cwd": {
        "candidate_memory": "In this task group, failures are caused by code relying on the current working directory for paths.",
        "candidate_skill": {
            "name": "Diagnose Current-Working-Directory Path Failures",
            "trigger": [
                "FileNotFoundError for a relative path",
                "A command succeeds from one directory but fails from another"
            ],
            "steps": [
                "Identify the command's current working directory.",
                "Find relative paths used by the failing code.",
                "Decide whether paths should be relative to the project root or the source file.",
                "Use pathlib and __file__ for stable file-relative paths when appropriate.",
                "Rerun the verifier from the failing cwd."
            ],
            "limitations": [
                "Do not patch sys.path before checking cwd.",
                "Do not assume the verifier runs from the same directory as the user command."
            ],
            "risk": "Low risk when the failure includes cwd-sensitive file access."
        },
        "candidate_rule": "When debugging import or path failures, check the current working directory before changing imports or file paths.",
    },
    "cluster_t5_broken_package_import": {
        "candidate_memory": "In this task group, a package module uses a bare import for an internal submodule even though it is imported through the package namespace.",
        "candidate_skill": {
            "name": "Diagnose Package-Internal Bare Import Failures",
            "trigger": [
                "ModuleNotFoundError for an internal subpackage name",
                "Tests import a module through package_name.main"
            ],
            "steps": [
                "Inspect whether the failing module is loaded as part of a package.",
                "Check whether an internal submodule is imported with a bare top-level import.",
                "Replace the bare import with a relative import or package-qualified import.",
                "Rerun the verifier."
            ],
            "limitations": [
                "Do not install a package named after the internal submodule.",
                "Do not add sys.path hacks before checking package structure."
            ],
            "risk": "Low risk if limited to package-internal imports."
        },
        "candidate_rule": "When a missing module name matches an internal subpackage, fix the package import rather than installing a dependency.",
    },
}


def main() -> None:
    clusters = json.loads(CLUSTERS.read_text(encoding="utf-8"))

    for cluster in clusters:
        cluster_id = cluster["cluster_id"]
        artifacts = ARTIFACTS[cluster_id]
        cluster["candidate_memory"] = artifacts["candidate_memory"]
        cluster["candidate_skill"] = artifacts["candidate_skill"]
        cluster["candidate_rule"] = artifacts["candidate_rule"]

    OUT.write_text(json.dumps(clusters, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(clusters)} artifact-enriched clusters to {OUT}")


if __name__ == "__main__":
    main()
