#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark" / "admission_samples" / "curated_non_skill_v1_admission_samples.jsonl"


AVAILABLE_ACTIONS = [
    "discard",
    "store_as_memory",
    "distill_into_skill",
    "promote_to_rule",
    "defer",
]


def skill(name: str, trigger: list[str], steps: list[str], limitations: list[str], risk: str) -> dict[str, Any]:
    return {
        "name": name,
        "trigger": trigger,
        "steps": steps,
        "limitations": limitations,
        "risk": risk,
    }


def exp(task_id: str, observation: str, diagnosis: str, fix_pattern: str, risk: str) -> dict[str, str]:
    return {
        "task_id": task_id,
        "observation": observation,
        "diagnosis": diagnosis,
        "fix_pattern": fix_pattern,
        "risk": risk,
    }


def sample(
    sample_id: str,
    cluster_id: str,
    cluster_name: str,
    family: str,
    task_ids: list[str],
    experience_cluster: list[dict[str, str]],
    candidate_memory: str,
    candidate_skill: dict[str, Any],
    candidate_rule: str,
    label: str,
    label_rationale: str,
    tags: list[str],
) -> dict[str, Any]:
    return {
        "sample_id": sample_id,
        "source": "curated_non_skill_v1",
        "family": family,
        "cluster_id": cluster_id,
        "cluster_name": cluster_name,
        "task_ids": task_ids,
        "num_trajectories": len(experience_cluster),
        "experience_cluster": experience_cluster,
        "candidate_memory": candidate_memory,
        "candidate_skill": candidate_skill,
        "candidate_rule": candidate_rule,
        "label": label,
        "label_rationale": label_rationale,
        "available_actions": AVAILABLE_ACTIONS,
        "tags": tags,
    }


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    # -------------------------
    # discard: harmful or noisy
    # -------------------------
    rows.extend(
        [
            sample(
                sample_id="curated_v1_discard_install_any_missing_module",
                cluster_id="curated_v1_cluster_install_any_missing_module",
                cluster_name="Blind installation for every missing module",
                family="python_import_debug",
                task_ids=["py_import_005", "py_import_009", "py_import_017"],
                experience_cluster=[
                    exp("py_import_005", "utils is a local module.", "The import path is wrong.", "Use local package import.", "Blind install is negative transfer."),
                    exp("py_import_009", "Relative import lacks parent package.", "Launch mode is wrong.", "Align import style with execution.", "Installing packages is unrelated."),
                    exp("py_import_017", "core is an internal subpackage.", "Package-internal import is wrong.", "Use relative import.", "Installing core is harmful."),
                ],
                candidate_memory="ModuleNotFoundError can have several causes in these tasks.",
                candidate_skill=skill(
                    "Install Any Missing Module",
                    ["Any ModuleNotFoundError"],
                    ["Read the missing name.", "Install a package with the same name.", "Rerun tests."],
                    ["No local-module, launch-mode, cwd, or package-structure check."],
                    "Actively harmful and causes negative transfer.",
                ),
                candidate_rule="If Python says a module is missing, install a package with the same name.",
                label="discard",
                label_rationale="The candidate is an overgeneralized harmful skill and should be rejected.",
                tags=["negative_transfer", "bad_skill"],
            ),
            sample(
                sample_id="curated_v1_discard_global_syspath_hack",
                cluster_id="curated_v1_cluster_global_syspath_hack",
                cluster_name="Global sys.path hack for import failures",
                family="python_import_debug",
                task_ids=["py_import_005", "py_import_017", "py_import_020"],
                experience_cluster=[
                    exp("py_import_005", "Local import can be fixed with package-qualified import.", "The package relationship is explicit.", "Use app.utils import.", "sys.path hack is unnecessary."),
                    exp("py_import_017", "Internal subpackage can be imported relatively.", "The package structure is clear.", "Use .core.worker import.", "sys.path hack hides the real issue."),
                    exp("py_import_020", "workers is internal to samplepkg.", "Bare import is wrong.", "Use relative import.", "sys.path hack may break other imports."),
                ],
                candidate_memory="Several import tasks could be hacked by mutating sys.path, but better structural fixes exist.",
                candidate_skill=skill(
                    "Add Repo Paths to sys.path for Import Errors",
                    ["Any import failure"],
                    ["Append the repository root and all subdirectories to sys.path.", "Rerun tests."],
                    ["Does not diagnose package structure.", "Can mask real packaging bugs."],
                    "High risk: brittle and hides root causes.",
                ),
                candidate_rule="For import failures, add more directories to sys.path until imports work.",
                label="discard",
                label_rationale="The candidate is a brittle workaround, not reusable knowledge worth admitting.",
                tags=["negative_transfer", "bad_skill"],
            ),
            sample(
                sample_id="curated_v1_discard_edit_tests_to_match_bug",
                cluster_id="curated_v1_cluster_edit_tests_to_match_bug",
                cluster_name="Editing tests to pass import tasks",
                family="python_import_debug",
                task_ids=["py_import_001", "py_import_013"],
                experience_cluster=[
                    exp("py_import_001", "Verifier fails during test collection.", "Application import is broken.", "Fix app.py.", "Editing tests would invalidate verification."),
                    exp("py_import_013", "Verifier catches cwd-sensitive path bug.", "Application path resolution is broken.", "Fix loader.py.", "Editing tests avoids the bug."),
                ],
                candidate_memory="Some tasks could be made to pass by weakening tests.",
                candidate_skill=skill(
                    "Patch Tests When Verifier Fails",
                    ["Any failing verifier"],
                    ["Open the failing test.", "Change expected values or imports.", "Rerun verifier."],
                    ["Violates benchmark semantics."],
                    "Actively harmful: it destroys the verifier.",
                ),
                candidate_rule="If the verifier fails, edit tests until they pass.",
                label="discard",
                label_rationale="The candidate attacks the verifier rather than solving the task.",
                tags=["negative_transfer", "bad_skill"],
            ),
            sample(
                sample_id="curated_v1_discard_empty_response_runner_noise",
                cluster_id="curated_v1_cluster_empty_response_runner_noise",
                cluster_name="Empty model response as runner noise",
                family="agent_runtime",
                task_ids=["py_import_008"],
                experience_cluster=[
                    exp("py_import_008", "An early run returned an empty model response.", "The issue was model/API formatting noise.", "Retry logic fixed the runner issue.", "This is not task-solving knowledge."),
                ],
                candidate_memory="The LLM API once returned an empty response for py_import_008.",
                candidate_skill=skill(
                    "Fix Import Errors by Retrying Empty LLM Responses",
                    ["Any import error", "Any empty model response"],
                    ["Retry the model.", "Assume the import bug is fixed."],
                    ["Conflates infrastructure retry with code repair."],
                    "High risk: runner artifact, not a coding skill.",
                ),
                candidate_rule="Retrying an empty model response is a general import repair.",
                label="discard",
                label_rationale="This is infrastructure noise and should not enter the agent's task knowledge.",
                tags=["runner_artifact", "infrastructure_noise"],
            ),
            sample(
                sample_id="curated_v1_discard_suppress_import_errors",
                cluster_id="curated_v1_cluster_suppress_import_errors",
                cluster_name="Suppressing import errors with broad try-except",
                family="python_import_debug",
                task_ids=["py_import_001", "py_import_005", "py_import_017"],
                experience_cluster=[
                    exp("py_import_001", "Missing import can be unused.", "Usage must be checked.", "Remove unused import only if safe.", "Broad except can hide real dependencies."),
                    exp("py_import_005", "utils is local.", "The import relation is wrong.", "Fix the import.", "Broad except leaves functions undefined."),
                    exp("py_import_017", "core is internal.", "Package import is wrong.", "Use relative import.", "Broad except hides package bugs."),
                ],
                candidate_memory="Broad exception handling can hide import failures.",
                candidate_skill=skill(
                    "Wrap Imports in try/except ImportError",
                    ["Any import failure"],
                    ["Wrap the import with try/except ImportError.", "Set a fallback value.", "Rerun tests."],
                    ["Does not fix the underlying import relation.", "Can create undefined behavior."],
                    "High risk: suppresses the error instead of repairing it.",
                ),
                candidate_rule="If an import fails, catch ImportError and continue.",
                label="discard",
                label_rationale="The candidate is a harmful workaround and should be rejected.",
                tags=["negative_transfer", "bad_skill"],
            ),
        ]
    )

    # -------------------------
    # store_as_memory: useful but context-bound
    # -------------------------
    rows.extend(
        [
            sample(
                sample_id="curated_v1_memory_py_import_016_resource_path",
                cluster_id="curated_v1_cluster_py_import_016_resource_path",
                cluster_name="Exact resource path in py_import_016",
                family="python_import_debug",
                task_ids=["py_import_016"],
                experience_cluster=[
                    exp("py_import_016", "runner/loader.py reads resources/input.txt.", "The path is specific to this task layout.", "Resolve that exact file from repo root.", "Not transferable to other projects."),
                ],
                candidate_memory="In py_import_016, the exact resource file is resources/input.txt and the command runs from runner/.",
                candidate_skill=skill(
                    "Resolve resources/input.txt for Runner Tasks",
                    ["FileNotFoundError for resources/input.txt"],
                    ["Open runner/loader.py.", "Resolve resources/input.txt from repo root."],
                    ["Applies only to this exact task layout."],
                    "High risk if treated as a general skill.",
                ),
                candidate_rule="Always resolve resources/input.txt from repository root.",
                label="store_as_memory",
                label_rationale="The information is useful but bound to one exact path and task layout.",
                tags=["context_specific"],
            ),
            sample(
                sample_id="curated_v1_memory_api_base_url",
                cluster_id="curated_v1_cluster_api_base_url",
                cluster_name="Project-specific OpenAI-compatible base URL",
                family="agent_runtime_config",
                task_ids=["skilladmit_env_setup"],
                experience_cluster=[
                    exp("skilladmit_env_setup", "The project uses https://token-plan-cn.xiaomimimo.com/v1.", "This is a project/runtime configuration fact.", "Store it in .env as OPENAI_BASE_URL.", "Not a general agent skill."),
                ],
                candidate_memory="For this workspace, OPENAI_BASE_URL is https://token-plan-cn.xiaomimimo.com/v1 and SKILLADMIT_MODEL is mimo-v2.5-pro.",
                candidate_skill=skill(
                    "Use Xiaomi MiMo API for All Agent Projects",
                    ["Any LLM agent project"],
                    ["Set OPENAI_BASE_URL to the Xiaomi endpoint.", "Set model to mimo-v2.5-pro."],
                    ["Only true for this user's current project."],
                    "High risk outside this environment.",
                ),
                candidate_rule="All OpenAI-compatible agents should use the Xiaomi MiMo endpoint.",
                label="store_as_memory",
                label_rationale="This is an environment-specific fact, not a transferable skill or rule.",
                tags=["context_specific"],
            ),
            sample(
                sample_id="curated_v1_memory_specific_package_name_app_pkg",
                cluster_id="curated_v1_cluster_specific_package_name_app_pkg",
                cluster_name="Exact app_pkg.core package fact",
                family="python_import_debug",
                task_ids=["py_import_017"],
                experience_cluster=[
                    exp("py_import_017", "app_pkg/main.py needs app_pkg/core/worker.py.", "The package names are specific.", "Use .core.worker import work.", "Names do not transfer."),
                ],
                candidate_memory="In py_import_017, app_pkg.main should import work from the internal subpackage app_pkg.core.worker.",
                candidate_skill=skill(
                    "Always Import from app_pkg.core.worker",
                    ["ModuleNotFoundError: core"],
                    ["Edit app_pkg/main.py.", "Use from .core.worker import work."],
                    ["Only applies to py_import_017's exact package names."],
                    "High risk as a general skill.",
                ),
                candidate_rule="When core is missing, always import from app_pkg.core.worker.",
                label="store_as_memory",
                label_rationale="The exact package and module names are a memory item.",
                tags=["context_specific"],
            ),
            sample(
                sample_id="curated_v1_memory_exact_unused_import_missingdep_alpha",
                cluster_id="curated_v1_cluster_exact_unused_import_missingdep_alpha",
                cluster_name="Exact unused import in py_import_001",
                family="python_import_debug",
                task_ids=["py_import_001"],
                experience_cluster=[
                    exp("py_import_001", "app.py imports missingdep_alpha but get_name does not use it.", "This exact import is unused.", "Remove missingdep_alpha.", "Other missing imports may be required."),
                ],
                candidate_memory="In py_import_001, missingdep_alpha is unused and can be removed from app.py.",
                candidate_skill=skill(
                    "Remove missingdep_alpha",
                    ["ModuleNotFoundError: missingdep_alpha"],
                    ["Open app.py.", "Delete import missingdep_alpha."],
                    ["Only applies to this exact synthetic dependency name."],
                    "Low local risk but not transferable.",
                ),
                candidate_rule="If missingdep_alpha is missing, remove it.",
                label="store_as_memory",
                label_rationale="This is useful local knowledge but too specific for a reusable skill.",
                tags=["context_specific"],
            ),
            sample(
                sample_id="curated_v1_memory_exact_cli_assets_path",
                cluster_id="curated_v1_cluster_exact_cli_assets_path",
                cluster_name="Exact cli/assets path fact",
                family="python_import_debug",
                task_ids=["py_import_014"],
                experience_cluster=[
                    exp("py_import_014", "cli/loader.py reads assets/message.txt.", "The file name and directory are exact.", "Resolve assets/message.txt from repo root.", "Not a general path rule by itself."),
                ],
                candidate_memory="In py_import_014, assets/message.txt exists under the repo root while the command runs from cli/.",
                candidate_skill=skill(
                    "Resolve assets/message.txt from Repo Root",
                    ["FileNotFoundError: assets/message.txt"],
                    ["Edit cli/loader.py.", "Resolve assets/message.txt from repo root."],
                    ["Only applies to this exact task layout."],
                    "High risk outside this context.",
                ),
                candidate_rule="All assets/message.txt paths should be resolved from repo root.",
                label="store_as_memory",
                label_rationale="The exact file path is useful but context-bound.",
                tags=["context_specific"],
            ),
        ]
    )

    # -------------------------
    # promote_to_rule: broad guardrails
    # -------------------------
    rows.extend(
        [
            sample(
                sample_id="curated_v1_rule_check_local_before_install",
                cluster_id="curated_v1_cluster_check_local_before_install",
                cluster_name="Check local project before dependency installation",
                family="python_import_debug",
                task_ids=["py_import_005", "py_import_017", "py_import_020"],
                experience_cluster=[
                    exp("py_import_005", "utils exists locally.", "It is not a dependency issue.", "Fix local import.", "Blind install is wrong."),
                    exp("py_import_017", "core is internal.", "It is not a dependency issue.", "Fix package import.", "Blind install is wrong."),
                    exp("py_import_020", "workers is internal.", "It is not a dependency issue.", "Fix package import.", "Blind install is wrong."),
                ],
                candidate_memory="Multiple tasks show that missing module names can be local or internal.",
                candidate_skill=skill(
                    "Check Local Modules Before Installing Dependencies",
                    ["ModuleNotFoundError"],
                    ["Search local files.", "Inspect package structure.", "Only then consider dependencies."],
                    ["Broad diagnostic procedure."],
                    "Low risk.",
                ),
                candidate_rule="Before installing a missing Python module, check whether the name belongs to local files or internal packages.",
                label="promote_to_rule",
                label_rationale="This is a broad guardrail that should constrain many import-debugging actions.",
                tags=["guardrail", "cross_cluster"],
            ),
            sample(
                sample_id="curated_v1_rule_do_not_edit_tests",
                cluster_id="curated_v1_cluster_do_not_edit_tests",
                cluster_name="Do not edit tests to satisfy verifier",
                family="software_debugging",
                task_ids=["py_import_001", "py_import_013", "py_import_017"],
                experience_cluster=[
                    exp("py_import_001", "The app import fails.", "The app code is wrong.", "Fix app.py.", "Editing tests invalidates verifier."),
                    exp("py_import_013", "Path resolution fails.", "Application code is wrong.", "Fix loader.py.", "Editing tests hides the issue."),
                    exp("py_import_017", "Package import fails.", "Application import is wrong.", "Fix main.py.", "Editing tests hides the issue."),
                ],
                candidate_memory="The verifier tests should stay unchanged in these benchmark tasks.",
                candidate_skill=skill(
                    "Avoid Editing Tests During Bug Fixing",
                    ["Any benchmark debugging task"],
                    ["Inspect application code.", "Patch source files.", "Do not modify tests unless instructed."],
                    ["This is more of a global constraint than a task procedure."],
                    "Low risk.",
                ),
                candidate_rule="Do not edit verifier tests unless the task explicitly asks for test changes.",
                label="promote_to_rule",
                label_rationale="This is a cross-task constraint, not a task-specific skill.",
                tags=["guardrail", "cross_cluster"],
            ),
            sample(
                sample_id="curated_v1_rule_preserve_launch_mode",
                cluster_id="curated_v1_cluster_preserve_launch_mode",
                cluster_name="Preserve intended Python launch mode",
                family="python_import_debug",
                task_ids=["py_import_009", "py_import_010", "py_import_011", "py_import_012"],
                experience_cluster=[
                    exp("py_import_009", "Verifier runs python app/main.py.", "Script mode is expected.", "Use script-compatible import.", "Changing to package mode may violate verifier."),
                    exp("py_import_010", "Verifier runs python srcpkg/main.py.", "Script mode is expected.", "Use script-compatible import.", "Ignoring command is risky."),
                    exp("py_import_011", "Verifier runs python runnerpkg/main.py.", "Script mode is expected.", "Use script-compatible import.", "Ignoring command is risky."),
                    exp("py_import_012", "Verifier runs python nestedpkg/main.py.", "Script mode is expected.", "Use script-compatible import.", "Ignoring command is risky."),
                ],
                candidate_memory="T3 tasks are executed as scripts by the verifier.",
                candidate_skill=skill(
                    "Repair Relative Imports for Script Mode",
                    ["attempted relative import with no known parent package"],
                    ["Check failing command.", "If direct script execution is required, use script-compatible imports."],
                    ["This is procedural but depends on a broader launch-mode rule."],
                    "Medium risk if launch mode is ignored.",
                ),
                candidate_rule="Before rewriting relative imports, preserve the launch mode required by the failing command or verifier.",
                label="promote_to_rule",
                label_rationale="The principle should guard many import repairs, including but not limited to T3.",
                tags=["guardrail", "cross_cluster"],
            ),
            sample(
                sample_id="curated_v1_rule_verify_after_patch",
                cluster_id="curated_v1_cluster_verify_after_patch",
                cluster_name="Always rerun verifier after patch",
                family="software_debugging",
                task_ids=["py_import_001", "py_import_005", "py_import_013", "py_import_017"],
                experience_cluster=[
                    exp("py_import_001", "Patch removed missing import.", "Correctness was confirmed by verifier.", "Rerun verifier.", "Without validation, success is unknown."),
                    exp("py_import_005", "Patch changed local import.", "Correctness was confirmed by verifier.", "Rerun verifier.", "Without validation, import may still fail."),
                    exp("py_import_013", "Patch changed path resolution.", "Correctness was confirmed by verifier.", "Rerun verifier.", "Without validation, path may still fail."),
                    exp("py_import_017", "Patch changed relative import.", "Correctness was confirmed by verifier.", "Rerun verifier.", "Without validation, collection may still fail."),
                ],
                candidate_memory="The LLM agent verified every accepted patch by rerunning verifier.sh.",
                candidate_skill=skill(
                    "Rerun Verifier After Code Edits",
                    ["Any code repair"],
                    ["Apply patch.", "Run verifier.", "Only accept if verifier passes."],
                    ["This is a global validation rule rather than a domain-specific skill."],
                    "Low risk.",
                ),
                candidate_rule="After applying a code patch, rerun the task verifier before admitting the repair as successful.",
                label="promote_to_rule",
                label_rationale="This should be a global rule across all debugging skills.",
                tags=["guardrail", "cross_cluster"],
            ),
            sample(
                sample_id="curated_v1_rule_no_syspath_before_structure",
                cluster_id="curated_v1_cluster_no_syspath_before_structure",
                cluster_name="Inspect package structure before sys.path changes",
                family="python_import_debug",
                task_ids=["py_import_005", "py_import_017", "py_import_018"],
                experience_cluster=[
                    exp("py_import_005", "app/utils.py exists.", "Package import should be fixed structurally.", "Use package import.", "sys.path is unnecessary."),
                    exp("py_import_017", "app_pkg/core exists.", "Package-internal import should be fixed.", "Use relative import.", "sys.path is unnecessary."),
                    exp("py_import_018", "toolkit/engine exists.", "Package-internal import should be fixed.", "Use relative import.", "sys.path is unnecessary."),
                ],
                candidate_memory="Several import failures had clear package structures that did not need sys.path hacks.",
                candidate_skill=skill(
                    "Avoid sys.path Hacks in Structured Packages",
                    ["Import failure in a structured package"],
                    ["Inspect package tree.", "Prefer relative or package-qualified imports.", "Avoid sys.path unless no structural fix exists."],
                    ["Broad guardrail."],
                    "Low risk.",
                ),
                candidate_rule="Inspect package structure and import context before adding sys.path hacks.",
                label="promote_to_rule",
                label_rationale="This is a broad constraint that should apply across import-debugging skills.",
                tags=["guardrail", "cross_cluster"],
            ),
        ]
    )

    # -------------------------
    # defer: plausible but not enough evidence
    # -------------------------
    rows.extend(
        [
            sample(
                sample_id="curated_v1_defer_single_unused_import",
                cluster_id="curated_v1_cluster_single_unused_import",
                cluster_name="Single unused missing import success",
                family="python_import_debug",
                task_ids=["py_import_001"],
                experience_cluster=[
                    exp("py_import_001", "Removing missingdep_alpha fixed one task.", "The import was unused.", "Remove unused import.", "One success is not enough."),
                ],
                candidate_memory="In py_import_001, missingdep_alpha was unused.",
                candidate_skill=skill(
                    "Remove Missing Imports",
                    ["ModuleNotFoundError"],
                    ["Remove the failing import.", "Rerun verifier."],
                    ["Does not require checking usage.", "Based on one trajectory."],
                    "High risk until validated.",
                ),
                candidate_rule="If an import is missing, remove it.",
                label="defer",
                label_rationale="The pattern may be useful but needs negative examples and a usage-check precondition.",
                tags=["insufficient_evidence"],
            ),
            sample(
                sample_id="curated_v1_defer_conflicting_missing_dependency_repairs",
                cluster_id="curated_v1_cluster_conflicting_missing_dependency_repairs",
                cluster_name="Conflicting repairs for missing dependency imports",
                family="python_import_debug",
                task_ids=["py_import_001", "external_dep_hypothetical_001"],
                experience_cluster=[
                    exp("py_import_001", "Missing import was unused.", "Removal worked.", "Remove import.", "May fail if import is needed."),
                    exp("external_dep_hypothetical_001", "Missing import is required by runtime behavior.", "Removal would break functionality.", "Add dependency.", "Dependency install may be needed."),
                ],
                candidate_memory="Some missing imports are unused, while others may be required dependencies.",
                candidate_skill=skill(
                    "Remove or Install Missing Dependencies",
                    ["ModuleNotFoundError for external-looking names"],
                    ["If tests pass after removal, remove it.", "Otherwise install it."],
                    ["Decision boundary is underspecified."],
                    "Needs validation because repairs conflict.",
                ),
                candidate_rule="Missing dependencies can either be removed or installed depending on usage.",
                label="defer",
                label_rationale="The evidence is conflicting and the candidate lacks a precise decision rule.",
                tags=["insufficient_evidence"],
            ),
            sample(
                sample_id="curated_v1_defer_two_cwd_repairs_not_enough",
                cluster_id="curated_v1_cluster_two_cwd_repairs_not_enough",
                cluster_name="Small cwd path repair cluster",
                family="python_import_debug",
                task_ids=["py_import_013", "py_import_014"],
                experience_cluster=[
                    exp("py_import_013", "data/config.txt failed from app cwd.", "Path should be anchored.", "Use __file__.", "Only one layout family."),
                    exp("py_import_014", "assets/message.txt failed from cli cwd.", "Path should be anchored.", "Use __file__.", "Still only path-read examples."),
                ],
                candidate_memory="Two tasks had cwd-sensitive file reads.",
                candidate_skill=skill(
                    "Always Anchor Relative Paths with __file__",
                    ["Any FileNotFoundError"],
                    ["Replace relative paths with __file__-anchored paths."],
                    ["Not validated for config files, package data, or user-supplied paths."],
                    "Plausible but broad.",
                ),
                candidate_rule="All relative paths should be converted to __file__ paths.",
                label="defer",
                label_rationale="The skill is plausible, but the broad trigger needs more validation.",
                tags=["insufficient_evidence"],
            ),
            sample(
                sample_id="curated_v1_defer_convert_all_relative_imports",
                cluster_id="curated_v1_cluster_convert_all_relative_imports",
                cluster_name="Underspecified relative import conversion",
                family="python_import_debug",
                task_ids=["py_import_009"],
                experience_cluster=[
                    exp("py_import_009", "Direct script execution failed with relative import.", "Script mode required a compatible import.", "Convert .utils to utils.", "Package-mode tasks may need the opposite."),
                ],
                candidate_memory="One script-mode task was fixed by converting a relative import to a local import.",
                candidate_skill=skill(
                    "Convert All Relative Imports to Absolute Imports",
                    ["Any attempted relative import error"],
                    ["Remove leading dots from imports.", "Rerun tests."],
                    ["Ignores package-mode execution.", "Based on one trajectory."],
                    "Needs negative validation.",
                ),
                candidate_rule="Relative imports should always be converted to absolute imports.",
                label="defer",
                label_rationale="The candidate may be useful in script-mode cases, but is too broad without more evidence.",
                tags=["insufficient_evidence"],
            ),
            sample(
                sample_id="curated_v1_defer_package_import_style_choice",
                cluster_id="curated_v1_cluster_package_import_style_choice",
                cluster_name="Relative versus package-qualified import choice",
                family="python_import_debug",
                task_ids=["py_import_017", "py_import_005"],
                experience_cluster=[
                    exp("py_import_017", "Relative import .core.worker fixed package-internal import.", "Relative import was appropriate.", "Use relative import.", "Other projects may prefer package-qualified imports."),
                    exp("py_import_005", "Package-qualified app.utils fixed local module import.", "Package-qualified import was appropriate.", "Use package-qualified import.", "Relative import may fail in script mode."),
                ],
                candidate_memory="Two successful fixes used different import styles.",
                candidate_skill=skill(
                    "Choose Relative or Package-Qualified Import",
                    ["Local module import failure"],
                    ["Choose relative import or package-qualified import.", "Rerun tests."],
                    ["Does not specify when to choose which style."],
                    "Needs a sharper decision boundary.",
                ),
                candidate_rule="Local imports can be fixed with relative or package-qualified imports.",
                label="defer",
                label_rationale="The candidate is plausible but underspecified; more evidence is needed before admission.",
                tags=["insufficient_evidence"],
            ),
        ]
    )

    return rows


def main() -> None:
    rows = build_rows()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )

    counts = Counter(row["label"] for row in rows)
    print(f"Wrote {len(rows)} curated non-skill v1 samples to {OUT}")
    print("label_counts:")
    for label, count in sorted(counts.items()):
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
