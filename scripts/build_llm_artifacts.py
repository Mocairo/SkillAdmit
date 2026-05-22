#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLUSTERS = ROOT / "benchmark" / "clusters" / "llm_coding_agent_v0_clusters.json"
OUT = ROOT / "benchmark" / "clusters" / "llm_coding_agent_v0_clusters_with_artifacts.json"


ARTIFACTS = {
    "llm_cluster_t1_missing_import_removed": {
        "candidate_memory": (
            "In these LLM trajectories, the missing dependency imports were not actually used "
            "by the program logic. The agent fixed the tasks by removing unused imports such as "
            "missingdep_alpha, missingdep_beta, missingdep_gamma, and missingdep_delta."
        ),
        "candidate_skill": {
            "name": "Remove Unused Missing Imports",
            "trigger": [
                "ModuleNotFoundError during test collection",
                "The missing module is imported but not used by the required function",
                "The verifier only depends on behavior that does not require the missing module"
            ],
            "steps": [
                "Inspect the file that raises ModuleNotFoundError.",
                "Check whether the missing import is actually used by the functions under test.",
                "If the import is unused and removing it preserves behavior, remove the import.",
                "Rerun the verifier."
            ],
            "limitations": [
                "Do not remove imports that are used at runtime.",
                "Do not use this as a general solution for missing third-party dependencies.",
                "If the missing module is required for functionality, dependency management is needed instead."
            ],
            "risk": "Medium risk: the repair is safe only when the missing import is unused."
        },
        "candidate_rule": "Before installing or stubbing a missing dependency, check whether the import is actually used by the tested behavior.",
        "label": "distill_into_skill",
        "label_rationale": (
            "The real LLM trajectories show a stable repair pattern: remove unused imports that cause "
            "collection-time ModuleNotFoundError. The skill is admissible only with a clear unused-import precondition."
        ),
    },
    "llm_cluster_t2_local_module": {
        "candidate_memory": (
            "In these LLM trajectories, short missing module names such as utils, config, service, "
            "and parser corresponded to local files inside the app directory."
        ),
        "candidate_skill": {
            "name": "Repair Local Module Imports",
            "trigger": [
                "ModuleNotFoundError for a short module name",
                "A same-named local .py file exists inside a package directory",
                "Tests import the module through a package namespace"
            ],
            "steps": [
                "Search the repository for a local file matching the missing module name.",
                "Inspect how tests import the target module.",
                "If the code is imported as a package, use a relative import or package-qualified import.",
                "Rerun the verifier."
            ],
            "limitations": [
                "Do not install a third-party package before checking local files.",
                "Do not blindly add sys.path hacks.",
                "Choose relative or package-qualified imports according to launch context."
            ],
            "risk": "Low risk when the missing module is confirmed to be local."
        },
        "candidate_rule": "When ModuleNotFoundError names a short module, search the repository before treating it as a missing dependency.",
        "label": "distill_into_skill",
        "label_rationale": (
            "The trajectories show a stable reusable procedure for local-module import failures, "
            "and all four tasks were solved by correcting the import relation."
        ),
    },
    "llm_cluster_t3_relative_import_script": {
        "candidate_memory": (
            "In these LLM trajectories, package files with relative imports were executed directly "
            "as scripts, so the parent package context was missing."
        ),
        "candidate_skill": {
            "name": "Repair Relative Imports for Script Execution",
            "trigger": [
                "ImportError: attempted relative import with no known parent package",
                "A file with from .module import name is executed via python path/to/file.py"
            ],
            "steps": [
                "Inspect whether the failing file uses relative imports.",
                "Check whether the file is executed directly as a script.",
                "If script execution is required by the verifier, change the import to a script-compatible local import.",
                "Rerun the verifier."
            ],
            "limitations": [
                "Do not rewrite relative imports if the intended launch mode is python -m package.module.",
                "Do not ignore the verifier's expected execution command."
            ],
            "risk": "Medium risk because package-mode projects may require the opposite repair."
        },
        "candidate_rule": "Before changing relative imports, determine whether the expected execution mode is script mode or package mode.",
        "label": "distill_into_skill",
        "label_rationale": (
            "The trajectories show a stable repair procedure tied to script-mode execution. "
            "The skill is useful with an explicit launch-mode precondition."
        ),
    },
    "llm_cluster_t4_wrong_cwd": {
        "candidate_memory": (
            "In these LLM trajectories, relative file paths failed when commands were executed "
            "from a subdirectory rather than the repository root."
        ),
        "candidate_skill": {
            "name": "Repair CWD-Sensitive File Paths",
            "trigger": [
                "FileNotFoundError for a relative path",
                "The command runs from a subdirectory",
                "The file exists elsewhere in the repository"
            ],
            "steps": [
                "Check the cwd used by the failing command or test.",
                "Locate the target file in the repository.",
                "Replace cwd-dependent paths with paths anchored by __file__ or another stable base.",
                "Rerun the verifier."
            ],
            "limitations": [
                "Do not change unrelated imports before checking cwd.",
                "Do not assume tests and user commands run from the same directory."
            ],
            "risk": "Low risk when the failure is clearly path-related."
        },
        "candidate_rule": "For path-related failures, check the command's current working directory before modifying imports or dependencies.",
        "label": "distill_into_skill",
        "label_rationale": (
            "The trajectories show a reusable cwd/path debugging procedure with consistent successful repairs."
        ),
    },
    "llm_cluster_t5_broken_package_import": {
        "candidate_memory": (
            "In these LLM trajectories, package modules used bare imports for internal submodules "
            "even though tests imported the modules through the package namespace."
        ),
        "candidate_skill": {
            "name": "Repair Package-Internal Bare Imports",
            "trigger": [
                "ModuleNotFoundError for an internal subpackage name",
                "A module is imported through package_name.main",
                "The failing file imports an internal submodule as if it were top-level"
            ],
            "steps": [
                "Inspect the package structure and tests' import path.",
                "Check whether the missing module is actually a package-internal submodule.",
                "Convert the bare import to a relative import or package-qualified import.",
                "Rerun the verifier."
            ],
            "limitations": [
                "Do not install a package named after the internal submodule.",
                "Do not patch sys.path before checking package structure."
            ],
            "risk": "Low risk when the internal submodule relationship is explicit."
        },
        "candidate_rule": "If a missing module name matches an internal subpackage, repair the package import instead of installing a dependency.",
        "label": "distill_into_skill",
        "label_rationale": (
            "The trajectories show a stable package-internal import repair pattern across four variants."
        ),
    },
}


def main() -> None:
    clusters = json.loads(CLUSTERS.read_text(encoding="utf-8"))

    for cluster in clusters:
        cluster_id = cluster["cluster_id"]
        artifact = ARTIFACTS[cluster_id]
        cluster["candidate_memory"] = artifact["candidate_memory"]
        cluster["candidate_skill"] = artifact["candidate_skill"]
        cluster["candidate_rule"] = artifact["candidate_rule"]
        cluster["label"] = artifact["label"]
        cluster["label_rationale"] = artifact["label_rationale"]

    OUT.write_text(json.dumps(clusters, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(clusters)} LLM artifact-enriched clusters to {OUT}")


if __name__ == "__main__":
    main()
