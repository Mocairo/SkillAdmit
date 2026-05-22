#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark" / "admission_samples" / "v2_heldout_admission_samples.jsonl"


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
    label: str,
    cluster_name: str,
    family: str,
    task_ids: list[str],
    experience_cluster: list[dict[str, str]],
    candidate_memory: str,
    candidate_skill: dict[str, Any],
    candidate_rule: str,
    label_rationale: str,
) -> dict[str, Any]:
    return {
        "sample_id": sample_id,
        "source": "v2_heldout_curated",
        "family": family,
        "cluster_id": sample_id.replace("sample_", "cluster_"),
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
        # Intentionally empty: v2 should test text/features rather than tag hints.
        "tags": [],
    }


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    # -------------------------
    # distill_into_skill
    # -------------------------
    rows.extend(
        [
            sample(
                "sample_v2_skill_unused_import_guarded",
                "distill_into_skill",
                "Guarded unused import removal",
                "python_import_debug",
                ["v2_unused_import_001", "v2_unused_import_002", "v2_unused_import_003"],
                [
                    exp("v2_unused_import_001", "ImportError occurs for a module that is never referenced.", "The failing import is unused by the tested function.", "Remove only the unused import.", "Removing used imports would be wrong."),
                    exp("v2_unused_import_002", "Collection fails before tests because of an unused optional import.", "The optional import is not needed for verifier behavior.", "Delete the optional import.", "Must check usage first."),
                    exp("v2_unused_import_003", "A top-level import of an absent plugin is unused.", "The tested path does not require the plugin.", "Remove or lazy-load the unused import.", "Do not remove required runtime imports."),
                ],
                "Several tasks had absent imports that were unused by the behavior under test.",
                skill(
                    "Remove Unused Failing Imports",
                    ["Import failure at module import time", "The imported name is not used by tested behavior"],
                    ["Inspect references to the imported name.", "If unused, remove or lazy-load the import.", "Rerun the verifier."],
                    ["Only applies after confirming the import is unused.", "Required dependencies should not be removed."],
                    "Low risk with an explicit usage check.",
                ),
                "Before removing a failing import, verify that the imported name is unused by the relevant execution path.",
                "The cluster shows a stable procedure with a clear precondition and validation step.",
            ),
            sample(
                "sample_v2_skill_package_internal_relative_import",
                "distill_into_skill",
                "Package-internal import repair",
                "python_import_debug",
                ["v2_pkg_001", "v2_pkg_002", "v2_pkg_003"],
                [
                    exp("v2_pkg_001", "module imports internal engine as a top-level package.", "The module is loaded through its package namespace.", "Use a relative internal import.", "Installing engine would be wrong."),
                    exp("v2_pkg_002", "worker is inside the current package but imported bare.", "The import context is package-internal.", "Use .worker import.", "sys.path patch would hide the bug."),
                    exp("v2_pkg_003", "service.plugins is internal but imported as plugins.", "The package prefix is missing.", "Use relative or package-qualified import.", "Do not install plugins."),
                ],
                "The failures share a package-internal bare import pattern.",
                skill(
                    "Repair Package-Internal Imports",
                    ["Missing module name matches an internal submodule", "The failing file is imported through a package namespace"],
                    ["Inspect package tree.", "Confirm the missing name is internal.", "Use relative or package-qualified import.", "Rerun verifier."],
                    ["Do not use for genuinely external dependencies."],
                    "Low risk when internal module relationship is explicit.",
                ),
                "If a missing module is an internal submodule, repair the package import instead of treating it as a dependency.",
                "The repeated repair pattern is stable and transferable across package names.",
            ),
            sample(
                "sample_v2_skill_cwd_file_resolution",
                "distill_into_skill",
                "CWD-independent file path repair",
                "python_path_debug",
                ["v2_path_001", "v2_path_002", "v2_path_003"],
                [
                    exp("v2_path_001", "script reads config/defaults.json from the wrong cwd.", "Path resolution depends on launch directory.", "Anchor path from __file__.", "Hard-coding cwd is brittle."),
                    exp("v2_path_002", "subcommand cannot find templates/base.txt.", "The file exists relative to the source file.", "Use Path(__file__).parent.", "Changing test cwd is wrong."),
                    exp("v2_path_003", "loader fails when invoked from examples/.", "The relative path assumes repo root.", "Use a stable base directory.", "Do not patch sys.path for data files."),
                ],
                "Several file access failures came from cwd-sensitive relative paths.",
                skill(
                    "Repair CWD-Sensitive File Access",
                    ["FileNotFoundError for a relative project file", "The command runs from a different cwd"],
                    ["Check the command cwd.", "Locate the target file.", "Anchor the path with __file__ or a stable project base.", "Rerun verifier."],
                    ["Do not apply to user-supplied relative paths without preserving semantics."],
                    "Low risk for project-owned resource files.",
                ),
                "When a project-owned file is read by relative path, check cwd before changing imports or dependencies.",
                "The repair is procedural, stable, and validated across multiple path layouts.",
            ),
            sample(
                "sample_v2_skill_script_mode_import",
                "distill_into_skill",
                "Script-mode import repair",
                "python_import_debug",
                ["v2_script_001", "v2_script_002", "v2_script_003"],
                [
                    exp("v2_script_001", "from .helpers import run fails under python tool.py.", "The file is executed as a script.", "Use script-compatible local import.", "Wrong for package-mode launch."),
                    exp("v2_script_002", "relative import fails in cli/main.py under direct execution.", "No parent package exists in script mode.", "Align import style with direct execution.", "Do not ignore failing command."),
                    exp("v2_script_003", "python bin/worker.py fails on relative import.", "The verifier expects direct script execution.", "Use local import or change launch command only if allowed.", "Changing verifier command is wrong."),
                ],
                "The failures share direct script execution with package-relative imports.",
                skill(
                    "Repair Relative Imports for Direct Script Execution",
                    ["attempted relative import with no known parent package", "Verifier runs python path/to/file.py"],
                    ["Inspect the failing command.", "Confirm direct script execution is required.", "Use script-compatible import or allowed module launch.", "Rerun verifier."],
                    ["Do not rewrite imports if package-mode launch is intended."],
                    "Medium risk without launch-mode check.",
                ),
                "Before rewriting relative imports, preserve the execution mode required by the task.",
                "The skill has a clear trigger, steps, and limitation.",
            ),
            sample(
                "sample_v2_skill_local_module_search",
                "distill_into_skill",
                "Local module search before dependency repair",
                "python_import_debug",
                ["v2_local_001", "v2_local_002", "v2_local_003"],
                [
                    exp("v2_local_001", "No module named settings but settings.py exists in app/.", "The missing name is local.", "Use app.settings import.", "Installing settings is wrong."),
                    exp("v2_local_002", "No module named tokenizer but tokenizer.py exists in src/.", "Import path misses local package context.", "Use package-qualified import.", "Installing tokenizer is wrong."),
                    exp("v2_local_003", "No module named client but client.py exists beside main.py.", "Bare import does not match import context.", "Use relative import.", "Installing client is wrong."),
                ],
                "Missing short module names corresponded to local files.",
                skill(
                    "Search Local Files Before Dependency Repair",
                    ["ModuleNotFoundError for a short name", "A matching local file may exist"],
                    ["Search the repository for the missing name.", "Decide whether it is local or external.", "If local, fix import context.", "Rerun verifier."],
                    ["Do not use this to reject genuine external dependencies without checking."],
                    "Low risk with repository search.",
                ),
                "A missing short module name should be searched in the repository before dependency installation.",
                "The repeated local-module diagnosis supports skill admission.",
            ),
        ]
    )

    # -------------------------
    # discard
    # -------------------------
    rows.extend(
        [
            sample(
                "sample_v2_discard_delete_failing_file",
                "discard",
                "Deleting source files to avoid import failures",
                "software_debugging",
                ["v2_bad_001", "v2_bad_002"],
                [
                    exp("v2_bad_001", "Import error arises from app/main.py.", "The source file is broken.", "Fix import.", "Deleting app/main.py destroys functionality."),
                    exp("v2_bad_002", "FileNotFoundError arises in loader.py.", "Path logic is broken.", "Fix path.", "Deleting loader.py avoids code rather than fixing it."),
                ],
                "Some failures occur in a small source file.",
                skill(
                    "Delete Files That Cause Failures",
                    ["Any verifier failure pointing to a source file"],
                    ["Delete the file mentioned in the traceback.", "Rerun verifier."],
                    ["This destroys program functionality."],
                    "Actively harmful.",
                ),
                "If a file appears in a traceback, remove it from the project.",
                "The candidate is a destructive workaround and should be rejected.",
            ),
            sample(
                "sample_v2_discard_skip_verifier",
                "discard",
                "Skipping verifier after edits",
                "agent_runtime",
                ["v2_bad_003"],
                [
                    exp("v2_bad_003", "A model patch looked plausible without running tests.", "Correctness is unknown until verifier runs.", "Run verifier.", "Skipping validation admits unverified repairs."),
                ],
                "One patch seemed plausible before validation.",
                skill(
                    "Assume Patch Success Without Verifier",
                    ["Any generated patch"],
                    ["Apply the patch.", "Skip the verifier.", "Mark success."],
                    ["No correctness check."],
                    "High risk: admits unverified repairs.",
                ),
                "A plausible patch does not need verifier validation.",
                "The candidate undermines the benchmark success criterion.",
            ),
            sample(
                "sample_v2_discard_ignore_traceback_and_random_edit",
                "discard",
                "Random edits unrelated to traceback",
                "software_debugging",
                ["v2_bad_004", "v2_bad_005"],
                [
                    exp("v2_bad_004", "Traceback points to import path.", "Import context is wrong.", "Fix import.", "Random formatting changes do not address cause."),
                    exp("v2_bad_005", "Traceback points to path resolution.", "File lookup is wrong.", "Fix path.", "Changing variable names is unrelated."),
                ],
                "Several bugs have tracebacks pointing to concrete causes.",
                skill(
                    "Make Small Random Code Edits",
                    ["Any failing test"],
                    ["Edit nearby lines randomly.", "Rerun verifier.", "Repeat until success."],
                    ["No diagnosis.", "High cost and unstable."],
                    "Harmful trial-and-error strategy.",
                ),
                "When a verifier fails, make arbitrary small edits near the traceback.",
                "This is not reusable knowledge and should be discarded.",
            ),
            sample(
                "sample_v2_discard_catch_all_exceptions",
                "discard",
                "Catch-all exception suppression",
                "python_debugging",
                ["v2_bad_006", "v2_bad_007"],
                [
                    exp("v2_bad_006", "ImportError reveals package bug.", "The import must be fixed.", "Repair import.", "except Exception hides failure."),
                    exp("v2_bad_007", "FileNotFoundError reveals path bug.", "The path must be fixed.", "Repair path.", "except Exception can return wrong data."),
                ],
                "Some errors can be hidden with broad exception handlers.",
                skill(
                    "Suppress Exceptions to Pass Tests",
                    ["Any exception during import or file access"],
                    ["Wrap failing code in except Exception.", "Return a default value."],
                    ["Hides bugs and can corrupt behavior."],
                    "Actively harmful.",
                ),
                "If code raises an exception, catch it and return a placeholder.",
                "The candidate suppresses real bugs instead of repairing them.",
            ),
            sample(
                "sample_v2_discard_replace_verifier_command",
                "discard",
                "Changing verifier command",
                "software_debugging",
                ["v2_bad_008"],
                [
                    exp("v2_bad_008", "verifier.sh runs pytest and exposes a bug.", "The verifier command is the benchmark contract.", "Fix source code.", "Changing verifier invalidates evaluation."),
                ],
                "The verifier command is stored in task metadata.",
                skill(
                    "Modify verifier.sh to Run No Tests",
                    ["Any failing verifier"],
                    ["Edit verifier.sh.", "Replace pytest with true.", "Report success."],
                    ["Invalidates evaluation."],
                    "Actively harmful.",
                ),
                "If verifier fails, change verifier.sh to exit successfully.",
                "This candidate attacks the evaluation contract.",
            ),
        ]
    )

    # -------------------------
    # store_as_memory
    # -------------------------
    rows.extend(
        [
            sample(
                "sample_v2_memory_exact_model_name",
                "store_as_memory",
                "Exact model name for current project",
                "agent_runtime_config",
                ["skilladmit_env_model"],
                [
                    exp("skilladmit_env_model", "The current run used model mimo-v2.5-pro.", "This is a run configuration fact.", "Record model name.", "Not a general skill."),
                ],
                "The current SkillAdmit experiments use SKILLADMIT_MODEL=mimo-v2.5-pro.",
                skill(
                    "Use mimo-v2.5-pro for All Coding Agents",
                    ["Any coding agent experiment"],
                    ["Set the model name to mimo-v2.5-pro."],
                    ["Only true for this project configuration."],
                    "High risk outside this environment.",
                ),
                "All future coding agents should use mimo-v2.5-pro.",
                "The information is useful but environment-specific.",
            ),
            sample(
                "sample_v2_memory_exact_generated_dir",
                "store_as_memory",
                "Exact generated trajectory directory",
                "project_artifact",
                ["skilladmit_paths"],
                [
                    exp("skilladmit_paths", "LLM trajectories are under benchmark/agent_runs/llm_coding_agent_v0/.", "This is a repository artifact location.", "Store path.", "Not transferable."),
                ],
                "The current LLM run output is benchmark/agent_runs/llm_coding_agent_v0/trajectories.jsonl.",
                skill(
                    "Read LLM Trajectories from llm_coding_agent_v0",
                    ["Need agent trajectories"],
                    ["Open benchmark/agent_runs/llm_coding_agent_v0/trajectories.jsonl."],
                    ["Only true for this repository layout."],
                    "Low local risk but not transferable.",
                ),
                "All projects store LLM trajectories in benchmark/agent_runs/llm_coding_agent_v0/trajectories.jsonl.",
                "This is a project-specific path fact.",
            ),
            sample(
                "sample_v2_memory_exact_task_command",
                "store_as_memory",
                "Exact verifier command for generated tasks",
                "benchmark_config",
                ["py_import_001"],
                [
                    exp("py_import_001", "The task verifier is bash verifier.sh.", "This is task metadata.", "Store command.", "Not a general repair strategy."),
                ],
                "For generated py_import tasks, the verifier command is bash verifier.sh.",
                skill(
                    "Run bash verifier.sh for Every Debug Task",
                    ["Any debugging task"],
                    ["Run bash verifier.sh."],
                    ["Only applies to this generated benchmark format."],
                    "Fails for other benchmarks.",
                ),
                "Every debugging task should be validated by bash verifier.sh.",
                "Useful task metadata should be memory, not a universal skill.",
            ),
            sample(
                "sample_v2_memory_exact_conda_env",
                "store_as_memory",
                "Exact conda environment for this run",
                "runtime_environment",
                ["skilladmit_env_python"],
                [
                    exp("skilladmit_env_python", "Python 3.10.20 in conda env skilladmit was used.", "This is environment metadata.", "Record it for reproducibility.", "Not a debugging skill."),
                ],
                "The current benchmark was run in conda env skilladmit with Python 3.10.20.",
                skill(
                    "Use Python 3.10.20 for All Agent Benchmarks",
                    ["Any agent benchmark"],
                    ["Create conda env with Python 3.10.20."],
                    ["May not be required elsewhere."],
                    "Environment-specific.",
                ),
                "All future benchmarks should use Python 3.10.20.",
                "This is useful reproducibility memory but too specific for a skill.",
            ),
            sample(
                "sample_v2_memory_exact_synthetic_dep_name",
                "store_as_memory",
                "Exact synthetic dependency names",
                "benchmark_config",
                ["py_import_001", "py_import_002"],
                [
                    exp("py_import_001", "missingdep_alpha is a synthetic absent module.", "The name was chosen to avoid environment pollution.", "Record synthetic name.", "Not a real dependency rule."),
                    exp("py_import_002", "missingdep_beta is a synthetic absent module.", "The name was chosen to avoid installed packages.", "Record synthetic name.", "Not a transferable skill."),
                ],
                "missingdep_alpha and missingdep_beta are synthetic dependency names used by the generated benchmark.",
                skill(
                    "Treat missingdep_* as Synthetic Benchmark Dependencies",
                    ["Module name starts with missingdep_"],
                    ["Recognize it as synthetic.", "Handle benchmark accordingly."],
                    ["Only applies to this benchmark's naming convention."],
                    "Benchmark-specific.",
                ),
                "Any module starting with missingdep_ is synthetic.",
                "This is benchmark-specific metadata and should be stored as memory.",
            ),
        ]
    )

    # -------------------------
    # promote_to_rule
    # -------------------------
    rows.extend(
        [
            sample(
                "sample_v2_rule_never_attack_verifier",
                "promote_to_rule",
                "Respect verifier contract",
                "software_debugging",
                ["v2_rule_001", "v2_rule_002"],
                [
                    exp("v2_rule_001", "Changing tests can hide import bugs.", "Verifier defines success.", "Fix source.", "Verifier attacks invalidate results."),
                    exp("v2_rule_002", "Changing verifier.sh can force success.", "That breaks evaluation.", "Keep verifier intact.", "Invalid success signal."),
                ],
                "Verifier and tests are the evaluation contract.",
                skill(
                    "Respect Verifier Contract",
                    ["Any benchmark repair"],
                    ["Do not edit tests or verifier.", "Fix source code.", "Rerun verifier."],
                    ["This is a global constraint rather than one domain procedure."],
                    "Low risk.",
                ),
                "Do not modify tests or verifier scripts unless the task explicitly asks for it.",
                "This is a broad rule that should constrain all debugging skills.",
            ),
            sample(
                "sample_v2_rule_validate_admitted_repairs",
                "promote_to_rule",
                "Validate before admitting experience",
                "agent_experience_management",
                ["v2_rule_003", "v2_rule_004"],
                [
                    exp("v2_rule_003", "A model patch can look plausible but fail.", "Validation determines success.", "Run verifier.", "Unvalidated experience can become bad memory."),
                    exp("v2_rule_004", "JSON repair can recover format failures.", "Runner-level success still needs verifier.", "Validate after applying patch.", "Otherwise admission is unsafe."),
                ],
                "Verifier outcomes are needed before turning experience into reusable knowledge.",
                skill(
                    "Validate Experience Before Admission",
                    ["Candidate memory or skill from an agent run"],
                    ["Check final verifier result.", "Only admit successful or diagnostically useful experience."],
                    ["This is a lifecycle rule, not a task-level skill."],
                    "Low risk.",
                ),
                "Before admitting a repair experience, verify the repair outcome and record success or failure.",
                "This should be a general admission rule.",
            ),
            sample(
                "sample_v2_rule_check_preconditions_before_skill_use",
                "promote_to_rule",
                "Check skill preconditions",
                "agent_skill_use",
                ["v2_rule_005", "v2_rule_006", "v2_rule_007"],
                [
                    exp("v2_rule_005", "Removing unused imports is safe only when unused.", "Precondition matters.", "Check usage.", "Without precondition, skill is harmful."),
                    exp("v2_rule_006", "Script-mode import repair is safe only when script mode is required.", "Launch precondition matters.", "Check command.", "Wrong mode breaks package use."),
                    exp("v2_rule_007", "Local import repair is safe only when module is local.", "Repository precondition matters.", "Search files.", "Wrong assumption causes negative transfer."),
                ],
                "Several admitted skills require explicit preconditions.",
                skill(
                    "Check Preconditions Before Applying Skills",
                    ["Any retrieved skill"],
                    ["Read trigger and limitations.", "Check preconditions against current task.", "Skip skill if preconditions fail."],
                    ["This is a cross-skill control rule."],
                    "Low risk.",
                ),
                "A retrieved skill should be applied only if its trigger and limitations match the current task.",
                "This rule reduces wrong skill usage across domains.",
            ),
            sample(
                "sample_v2_rule_preserve_user_command",
                "promote_to_rule",
                "Preserve required command semantics",
                "software_debugging",
                ["v2_rule_008", "v2_rule_009"],
                [
                    exp("v2_rule_008", "Verifier expects python app/main.py.", "The command is part of the task.", "Fix code for that command.", "Changing command may avoid required behavior."),
                    exp("v2_rule_009", "Verifier expects cwd-specific execution.", "cwd is part of reproduction.", "Fix path handling.", "Changing cwd alone may not solve user workflow."),
                ],
                "Failing commands encode required execution semantics.",
                skill(
                    "Preserve Failing Command Semantics",
                    ["Any command-reproduction debugging task"],
                    ["Read the failing command.", "Preserve its intended execution mode.", "Fix code unless command change is allowed."],
                    ["This is a general debugging constraint."],
                    "Low risk.",
                ),
                "Do not change the required failing command semantics unless the task explicitly permits it.",
                "This should constrain many debugging actions.",
            ),
            sample(
                "sample_v2_rule_distinguish_infra_noise_from_task_knowledge",
                "promote_to_rule",
                "Separate runner noise from task knowledge",
                "agent_runtime",
                ["v2_rule_010", "v2_rule_011"],
                [
                    exp("v2_rule_010", "Empty model response was fixed by retry.", "This is runtime noise.", "Improve runner retry.", "Do not store as coding skill."),
                    exp("v2_rule_011", "Malformed JSON was fixed by repair prompt.", "This is output-format noise.", "Improve parser.", "Do not store as domain skill."),
                ],
                "Some failures belong to agent infrastructure rather than task domain knowledge.",
                skill(
                    "Separate Infrastructure Events from Task Skills",
                    ["Agent output format errors", "API timeouts", "empty responses"],
                    ["Record infrastructure issue separately.", "Do not admit it as task-solving skill."],
                    ["This is an admission rule, not a coding repair."],
                    "Low risk.",
                ),
                "Do not admit runner/API noise as task-domain memory, skill, or rule.",
                "This is a general experience-management rule.",
            ),
        ]
    )

    # -------------------------
    # defer
    # -------------------------
    rows.extend(
        [
            sample(
                "sample_v2_defer_one_success_optional_dependency",
                "defer",
                "One optional dependency removal success",
                "python_import_debug",
                ["v2_defer_001"],
                [
                    exp("v2_defer_001", "Removing one optional dependency import fixed one task.", "The import was unused in that task.", "Remove unused import.", "One example is weak evidence."),
                ],
                "One optional dependency import was unused.",
                skill(
                    "Remove Optional Dependency Imports",
                    ["ModuleNotFoundError for optional-looking import"],
                    ["Remove the import.", "Rerun verifier."],
                    ["Does not specify how to prove optionality."],
                    "Needs negative validation.",
                ),
                "Optional dependency imports can be removed.",
                "The candidate is plausible but under-specified and based on one trajectory.",
            ),
            sample(
                "sample_v2_defer_conflicting_path_base",
                "defer",
                "Conflicting path base choices",
                "python_path_debug",
                ["v2_defer_002", "v2_defer_003"],
                [
                    exp("v2_defer_002", "Config path should be relative to repo root.", "Repo root was correct base.", "Use parent.parent.", "Other files may be package data."),
                    exp("v2_defer_003", "Template path should be relative to module directory.", "Source file directory was correct base.", "Use Path(__file__).parent.", "Repo root may be wrong."),
                ],
                "Different path bugs require different stable bases.",
                skill(
                    "Anchor All Paths to One Base",
                    ["Any FileNotFoundError"],
                    ["Pick repo root or source file directory.", "Rewrite all paths."],
                    ["Does not define which base to use."],
                    "Needs sharper decision boundary.",
                ),
                "Relative paths should be anchored to a stable base.",
                "The candidate is too vague for admission and needs more validation.",
            ),
            sample(
                "sample_v2_defer_partial_success_parser_name_conflict",
                "defer",
                "Parser name conflict partial evidence",
                "python_import_debug",
                ["v2_defer_004"],
                [
                    exp("v2_defer_004", "Local parser.py conflicts with historical/builtin parser naming expectations.", "Package context matters.", "Use explicit local import.", "One naming conflict is not enough."),
                ],
                "A module named parser can be ambiguous.",
                skill(
                    "Avoid Local Module Names That Match Builtins",
                    ["Module name looks like parser or config"],
                    ["Rename the local file.", "Update imports."],
                    ["Renaming is intrusive and was not validated."],
                    "Needs more evidence.",
                ),
                "Local modules should not be named parser.",
                "This may be good style advice, but current evidence is insufficient.",
            ),
            sample(
                "sample_v2_defer_small_cluster_json_repair",
                "defer",
                "JSON repair retry as admission experience",
                "agent_runtime",
                ["v2_defer_005", "v2_defer_006"],
                [
                    exp("v2_defer_005", "Malformed JSON was repaired once.", "Repair prompt helped.", "Ask model to return corrected JSON.", "More formats need testing."),
                    exp("v2_defer_006", "Empty response succeeded after retry.", "Retry helped.", "Retry model call.", "Could be transient."),
                ],
                "Runner retries fixed two output-format issues.",
                skill(
                    "Repair Any Bad Model Output with One Retry",
                    ["Malformed JSON", "Empty response", "Any API oddity"],
                    ["Retry once or ask for JSON repair.", "Proceed if parse succeeds."],
                    ["May fail for semantic patch errors.", "Not task-domain knowledge."],
                    "Useful infrastructure idea but needs separate validation.",
                ),
                "Bad model outputs should always be fixed with one retry.",
                "This belongs to runner engineering and needs more validation before admission as a general rule.",
            ),
            sample(
                "sample_v2_defer_unclear_memory_or_rule",
                "defer",
                "Unclear memory versus rule boundary",
                "agent_experience_management",
                ["v2_defer_007"],
                [
                    exp("v2_defer_007", "A project-specific base URL caused connection success.", "It is currently a memory item.", "Store .env config.", "May become a setup rule only after multiple projects."),
                ],
                "One project uses a specific OpenAI-compatible base URL.",
                skill(
                    "Configure OpenAI-Compatible Base URLs",
                    ["Any OpenAI-compatible API"],
                    ["Set OPENAI_BASE_URL.", "Set model name.", "Run connection test."],
                    ["Only one provider has been observed."],
                    "Could become a setup skill after more providers.",
                ),
                "Agent projects should store API settings in .env.",
                "The idea is plausible, but one provider/project is insufficient to decide between memory, skill, or rule.",
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
    print(f"Wrote {len(rows)} heldout v2 samples to {OUT}")
    print("label_counts:")
    for label, count in sorted(counts.items()):
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
