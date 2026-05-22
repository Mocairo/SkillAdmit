#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark" / "admission_samples" / "v4_blind_admission_samples.jsonl"


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
    experience_cluster: list[dict[str, str]],
    candidate_memory: str,
    candidate_skill: dict[str, Any],
    candidate_rule: str,
    label_rationale: str,
) -> dict[str, Any]:
    task_ids = [item["task_id"] for item in experience_cluster]
    return {
        "sample_id": sample_id,
        "source": "v4_blind_curated_after_v3_freeze",
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
        "tags": [],
    }


def build_skill_samples() -> list[dict[str, Any]]:
    return [
        sample(
            "sample_v4_skill_cli_argument_normalization",
            "distill_into_skill",
            "CLI argument normalization repair",
            "cli_debugging",
            [
                exp("v4_cli_001", "Command passed --input-file but parser expected --input.", "The CLI accepted the wrong flag shape.", "Add an alias and normalize into one destination.", "Do not rename the user-facing command without checking compatibility."),
                exp("v4_cli_002", "Command used --max-tokens while code read max_tokens only from config.", "Runtime arguments were not mapped into config.", "Map parsed args into config before execution.", "Do not hardcode values."),
                exp("v4_cli_003", "Boolean --dry-run was parsed as a string.", "Parser type handling was wrong.", "Use argparse store_true and validate parsed config.", "Only applies to CLI parsing bugs."),
            ],
            "Several CLI failures came from argument names or types not matching the runtime config.",
            skill(
                "Repair CLI Argument Normalization",
                ["CLI command fails because provided flags are not recognized or not propagated"],
                ["Inspect the failing command.", "Inspect parser definitions.", "Add compatible aliases or correct type actions.", "Normalize parsed arguments into the runtime config.", "Rerun the command or verifier."],
                ["Do not change the required command semantics unless explicitly allowed."],
                "Low risk when the failing command is preserved.",
            ),
            "Before changing a CLI command, inspect parser definitions and preserve required command semantics.",
            "The cluster shows a reusable command-interface repair procedure.",
        ),
        sample(
            "sample_v4_skill_json_schema_field_mapping",
            "distill_into_skill",
            "JSON schema field mapping repair",
            "data_validation",
            [
                exp("v4_json_001", "Validator expected task_id but input used id.", "The schema and producer used different field names.", "Map id to task_id before validation.", "Do not disable validation."),
                exp("v4_json_002", "Schema required model_name but payload used model.", "The payload shape changed across versions.", "Add a compatibility mapping layer.", "Blindly accepting extra fields can hide bugs."),
                exp("v4_json_003", "Nested metrics.accuracy arrived as score.", "Field naming drift caused validation failure.", "Translate known aliases and validate the result.", "Only known aliases should be mapped."),
            ],
            "Several validation failures were caused by known producer/schema field-name drift.",
            skill(
                "Repair Known JSON Schema Field Drift",
                ["JSON validation fails because a known alias field is present", "Producer and consumer schema names differ"],
                ["Inspect the schema error.", "Find whether the missing field has a known alias.", "Map known aliases before validation.", "Reject unknown fields or validate after conversion.", "Rerun schema validation."],
                ["Do not remove required fields.", "Do not turn off validation."],
                "Medium risk if aliases are guessed rather than confirmed.",
            ),
            "Schema repairs should preserve validation and map only confirmed compatibility aliases.",
            "The evidence supports a transferable schema repair procedure.",
        ),
        sample(
            "sample_v4_skill_utf8_sig_encoding_repair",
            "distill_into_skill",
            "UTF-8 BOM text loading repair",
            "data_loading",
            [
                exp("v4_encoding_001", "CSV header contained an invisible leading character.", "The file was UTF-8 with BOM.", "Read with utf-8-sig.", "Do not strip arbitrary characters from all fields."),
                exp("v4_encoding_002", "JSON key lookup failed for the first key only.", "The key had a BOM prefix.", "Use utf-8-sig when opening the file.", "Only applies when BOM is actually present."),
                exp("v4_encoding_003", "Text parser saw '\\ufeffname' instead of name.", "Encoding handling caused header mismatch.", "Use an encoding that removes the BOM.", "Do not mask unrelated parsing failures."),
            ],
            "Several loaders failed because UTF-8 BOM bytes were interpreted as text.",
            skill(
                "Repair UTF-8 BOM Loading Failures",
                ["First CSV or JSON key contains a BOM marker", "Header has an invisible leading character"],
                ["Inspect the failing key or header.", "Confirm BOM-like prefix.", "Open the file with utf-8-sig.", "Rerun parser and verifier."],
                ["Do not use broad string stripping as the primary repair."],
                "Low risk when the BOM symptom is confirmed.",
            ),
            "When only the first text key has a BOM-like prefix, confirm encoding before changing parser logic.",
            "The repeated symptom supports distilling a specific loader repair skill.",
        ),
        sample(
            "sample_v4_skill_importlib_resources_package_data",
            "distill_into_skill",
            "Package data loading repair",
            "python_packaging",
            [
                exp("v4_pkgdata_001", "A package read templates/email.txt with a cwd-relative path.", "Package data should be resolved relative to the package.", "Use importlib.resources.files.", "Do not assume cwd equals package root."),
                exp("v4_pkgdata_002", "Installed package could not find data/default.yml.", "The path worked only from the source tree.", "Read package data through importlib.resources.", "Manifest inclusion still needs checking."),
                exp("v4_pkgdata_003", "Tests passed from repo root but failed after package install.", "Data access depended on repository layout.", "Load resource from the package namespace.", "Only applies to packaged data files."),
            ],
            "Several data-file failures came from treating package resources as cwd-relative files.",
            skill(
                "Repair Package Resource Loading",
                ["Packaged module cannot find its bundled data file", "cwd-relative path works in source tree but fails when installed"],
                ["Locate the data file inside the package.", "Confirm it is package data.", "Use importlib.resources to access it.", "Rerun tests from the intended launch mode."],
                ["Do not apply to user-provided external paths.", "Still verify package data is included in distribution metadata."],
                "Low risk when the file is package-owned data.",
            ),
            "Package-owned data should be loaded through package-resource APIs rather than cwd-relative paths.",
            "The cluster shows a stable package-data repair pattern.",
        ),
        sample(
            "sample_v4_skill_pytest_fixture_scope_repair",
            "distill_into_skill",
            "Pytest fixture scope repair",
            "test_debugging",
            [
                exp("v4_fixture_001", "A function-scoped fixture created an expensive client for every test.", "Fixture scope was too narrow.", "Promote fixture scope and isolate mutable state.", "Do not share mutable state accidentally."),
                exp("v4_fixture_002", "Session-scoped temp directory leaked files across tests.", "Fixture scope was too broad for mutable data.", "Use function scope for mutable temp data.", "Do not hide test isolation failures."),
                exp("v4_fixture_003", "Fixture depended on tmp_path but was declared session-scoped.", "Scope mismatch caused pytest error.", "Align fixture scope with dependencies.", "Only applies to pytest fixture dependency errors."),
            ],
            "Several pytest failures came from fixture scope not matching dependency lifetime.",
            skill(
                "Repair Pytest Fixture Scope Mismatches",
                ["pytest fixture scope error", "fixture state leaks across tests", "fixture recreated too often"],
                ["Read the fixture dependency graph.", "Identify which data is mutable.", "Align fixture scope with dependency lifetime.", "Rerun the affected tests."],
                ["Do not change test assertions to hide state leaks."],
                "Medium risk because broader scope can leak state.",
            ),
            "Fixture scope should match dependency lifetime and mutable state isolation.",
            "The repair procedure is reusable across pytest projects.",
        ),
        sample(
            "sample_v4_skill_bounded_rate_limit_backoff",
            "distill_into_skill",
            "Bounded rate-limit backoff repair",
            "api_debugging",
            [
                exp("v4_rate_001", "Batch API calls failed with HTTP 429.", "Request concurrency exceeded provider limits.", "Add bounded exponential backoff with jitter.", "Do not retry forever."),
                exp("v4_rate_002", "Immediate retry loop kept receiving 429.", "No backoff gave the provider no recovery time.", "Wait with increasing delay and max attempts.", "Budget must be capped."),
                exp("v4_rate_003", "Parallel workers caused intermittent rate failures.", "Concurrency should be limited.", "Throttle concurrency and retry boundedly.", "Do not serialize all work unnecessarily."),
            ],
            "Several API failures were rate-limit responses that needed bounded retry behavior.",
            skill(
                "Repair Rate-Limited API Calls with Bounded Backoff",
                ["HTTP 429", "provider rate limit", "intermittent rate-limit failures"],
                ["Detect rate-limit status.", "Use bounded exponential backoff with jitter.", "Limit concurrency.", "Stop after max attempts.", "Record retry statistics."],
                ["Do not retry forever.", "Do not hide persistent quota exhaustion."],
                "Medium risk because retries consume budget.",
            ),
            "Rate-limit handling should use bounded backoff and explicit retry budgets.",
            "The repeated 429 pattern supports a reusable operational skill.",
        ),
        sample(
            "sample_v4_skill_paginated_response_collection",
            "distill_into_skill",
            "Paginated API response collection",
            "api_debugging",
            [
                exp("v4_page_001", "Only the first 100 records were processed.", "Client ignored next_page_token.", "Loop until no next token remains.", "Do not loop without a termination condition."),
                exp("v4_page_002", "Response contained has_more=true but loader stopped.", "Pagination metadata was ignored.", "Continue requests using cursor.", "Respect provider rate limits."),
                exp("v4_page_003", "Duplicate records appeared after cursor retry.", "Cursor state was not advanced carefully.", "Persist last consumed cursor after successful page.", "Avoid data duplication."),
            ],
            "Several API ingestion bugs came from incomplete pagination handling.",
            skill(
                "Collect Paginated API Responses",
                ["API response includes next_page_token or has_more", "only first page of records is processed"],
                ["Inspect pagination fields.", "Loop with explicit termination.", "Advance cursor only after successful page handling.", "Deduplicate if retries occur.", "Validate total record count."],
                ["Do not use an unbounded loop.", "Respect rate limits."],
                "Low to medium risk depending on provider semantics.",
            ),
            "Paginated APIs should be consumed until the documented termination condition is reached.",
            "The cluster supports a general API ingestion skill.",
        ),
        sample(
            "sample_v4_skill_csv_header_normalization",
            "distill_into_skill",
            "CSV header normalization repair",
            "data_loading",
            [
                exp("v4_csv_001", "CSV used 'User ID' while loader expected user_id.", "Header normalization was missing.", "Normalize header case, spaces, and separators.", "Do not silently merge distinct columns."),
                exp("v4_csv_002", "Input had trailing spaces in header names.", "Exact header matching was too brittle.", "Strip header whitespace and validate required columns.", "Do not strip data values blindly."),
                exp("v4_csv_003", "Different exports used kebab-case and snake_case.", "Known header variants should map to canonical names.", "Use a canonical header mapping.", "Unknown columns still need review."),
            ],
            "Several CSV loaders failed because known header variants were not normalized.",
            skill(
                "Repair CSV Header Normalization",
                ["CSV required column is missing but a visually equivalent header exists", "headers differ by spaces, case, or separators"],
                ["Read the header row.", "Normalize case and separators.", "Map known aliases to canonical names.", "Validate required columns after normalization.", "Report unknown ambiguous columns."],
                ["Do not normalize two distinct columns into one without a warning."],
                "Low risk when aliases are explicit.",
            ),
            "CSV loaders should normalize known header variants before required-column validation.",
            "The examples support a reusable data-loading skill.",
        ),
        sample(
            "sample_v4_skill_timezone_datetime_repair",
            "distill_into_skill",
            "Timezone-aware datetime repair",
            "data_processing",
            [
                exp("v4_time_001", "Naive datetime was compared with timezone-aware timestamp.", "Datetime awareness differed.", "Attach or convert timezone explicitly.", "Do not assume local timezone silently."),
                exp("v4_time_002", "API returned UTC ISO strings with Z suffix.", "Parser produced naive objects.", "Parse Z as UTC-aware datetime.", "Only applies to timestamp fields."),
                exp("v4_time_003", "Daily grouping shifted records by one day.", "Timezone conversion was missing before date extraction.", "Convert to target timezone before grouping.", "Business timezone must be known."),
            ],
            "Several date bugs came from mixing naive and timezone-aware timestamps.",
            skill(
                "Repair Timezone-Aware Datetime Handling",
                ["naive and aware datetime comparison error", "UTC timestamp parsed without timezone", "date grouping shifts around midnight"],
                ["Identify source timezone.", "Parse timestamps as timezone-aware.", "Convert to the required business timezone.", "Only then compare or group.", "Add regression tests around boundary times."],
                ["Do not guess the business timezone if it is not specified."],
                "Medium risk when timezone requirements are unclear.",
            ),
            "Datetime repairs should preserve timezone semantics before comparison or grouping.",
            "The repeated timestamp failures justify skill admission.",
        ),
        sample(
            "sample_v4_skill_subprocess_cwd_env_repair",
            "distill_into_skill",
            "Subprocess cwd and environment repair",
            "runtime_debugging",
            [
                exp("v4_subproc_001", "A child command worked in shell but failed from Python.", "The subprocess cwd differed.", "Pass cwd explicitly.", "Do not rely on caller cwd."),
                exp("v4_subproc_002", "Child process could not find a required executable.", "PATH differed from the interactive shell.", "Pass a controlled env with PATH.", "Do not inherit secrets unnecessarily."),
                exp("v4_subproc_003", "Relative output path was created in the wrong directory.", "Subprocess launch context was implicit.", "Set cwd and resolve output paths.", "Preserve user command semantics."),
            ],
            "Several subprocess failures came from implicit cwd or environment inheritance.",
            skill(
                "Repair Subprocess Launch Context",
                ["subprocess behaves differently from shell command", "child command cannot find files or executables"],
                ["Inspect the intended command.", "Set cwd explicitly.", "Pass a controlled environment.", "Resolve relative paths deliberately.", "Rerun the same command path."],
                ["Do not leak secrets into child env.", "Do not change the command's intended semantics."],
                "Low risk when launch context is explicit.",
            ),
            "Subprocess calls should specify cwd and necessary environment rather than relying on ambient shell state.",
            "The cluster shows a reusable runtime repair skill.",
        ),
    ]


def build_discard_samples() -> list[dict[str, Any]]:
    return [
        sample(
            "sample_v4_discard_delete_failing_tests",
            "discard",
            "Deleting failing tests",
            "software_debugging",
            [
                exp("v4_bad_test_001", "A test exposed an incorrect parser result.", "The source parser is wrong.", "Fix parser behavior.", "Deleting the test invalidates verification."),
            ],
            "One failing test identifies a real source bug.",
            skill(
                "Delete Failing Tests to Unblock Verification",
                ["Any failing test file"],
                ["Remove the failing test file.", "Rerun the test suite.", "Report success if remaining tests pass."],
                ["Destroys the verifier and hides real bugs."],
                "Actively harmful.",
            ),
            "If a test blocks progress, delete the failing test.",
            "The candidate attacks the evaluation contract.",
        ),
        sample(
            "sample_v4_discard_constant_success_stub",
            "discard",
            "Replacing logic with constant success",
            "software_debugging",
            [
                exp("v4_bad_stub_001", "A classifier returned wrong labels for edge cases.", "Decision logic needs repair.", "Fix branching and add tests.", "Returning constant success fabricates results."),
            ],
            "One task needs a logic repair.",
            skill(
                "Return Constant Success from Failing Functions",
                ["Any function fails tests"],
                ["Replace the function body with return True.", "Rerun tests."],
                ["Fakes success and removes real behavior."],
                "Actively harmful.",
            ),
            "If behavior is hard to fix, return a constant successful value.",
            "The candidate fabricates correctness rather than solving the task.",
        ),
        sample(
            "sample_v4_discard_chmod_everything",
            "discard",
            "Recursive chmod workaround",
            "deployment_debugging",
            [
                exp("v4_bad_perm_001", "One generated output file was not writable.", "The output directory ownership was wrong.", "Fix ownership or target path.", "chmod 777 weakens permissions globally."),
            ],
            "A permission failure occurred in one output directory.",
            skill(
                "Make Repository World-Writable",
                ["Any permission denied error"],
                ["Run chmod -R 777 on the repository.", "Retry the operation."],
                ["Destroys permission boundaries and can hide ownership bugs."],
                "High risk workaround.",
            ),
            "Permission errors should be solved by making the whole repository world-writable.",
            "The candidate is unsafe and overbroad.",
        ),
        sample(
            "sample_v4_discard_empty_dict_on_json_error",
            "discard",
            "Returning empty dict on JSON errors",
            "data_loading",
            [
                exp("v4_bad_json_001", "JSONDecodeError revealed a truncated cache file.", "The cache should be regenerated or rejected.", "Delete only the corrupted cache and rebuild.", "Returning empty data hides corruption."),
            ],
            "One corrupted JSON file caused a loader failure.",
            skill(
                "Ignore JSONDecodeError with Empty Data",
                ["Any JSONDecodeError"],
                ["Catch JSONDecodeError.", "Return an empty dict.", "Continue execution."],
                ["Suppresses real data corruption."],
                "Actively harmful.",
            ),
            "If JSON parsing fails, catch the error and return empty data.",
            "The candidate hides data loss and should be rejected.",
        ),
        sample(
            "sample_v4_discard_unbounded_retry_loop",
            "discard",
            "Unbounded retry loop",
            "api_debugging",
            [
                exp("v4_bad_retry_001", "An API request failed with a transient 503.", "Retry may help if bounded.", "Retry with max attempts and backoff.", "A forever loop can burn budget."),
            ],
            "One API failure might be transient.",
            skill(
                "Retry Forever Until the API Works",
                ["Any API error"],
                ["Retry immediately in a tight loop.", "Never stop until success."],
                ["Can hang forever and waste tokens or quota."],
                "Harmful operational pattern.",
            ),
            "All API errors should be retried forever.",
            "The candidate lacks a termination budget.",
        ),
        sample(
            "sample_v4_discard_disable_schema_validation",
            "discard",
            "Disabling schema validation",
            "data_validation",
            [
                exp("v4_bad_schema_001", "Schema validation rejected missing required fields.", "The producer omitted required data.", "Fix producer or compatibility mapper.", "Disabling validation admits bad records."),
            ],
            "One schema validation failure blocked ingestion.",
            skill(
                "Turn Off Schema Validation",
                ["Any schema validation error"],
                ["Disable the validator.", "Accept the raw payload.", "Continue processing."],
                ["Admits malformed data and hides contract bugs."],
                "Actively harmful.",
            ),
            "If schema validation fails, bypass validation.",
            "The candidate weakens the correctness contract.",
        ),
        sample(
            "sample_v4_discard_global_pythonpath_hack",
            "discard",
            "Global PYTHONPATH import workaround",
            "python_import_debug",
            [
                exp("v4_bad_path_001", "A package-internal import failed.", "The import relation should be fixed.", "Use package-qualified or relative imports.", "Global path injection hides package bugs."),
            ],
            "One import failure involved package structure.",
            skill(
                "Set PYTHONPATH to Every Project Directory",
                ["Any ModuleNotFoundError"],
                ["Add the repository root and all subdirectories to PYTHONPATH.", "Rerun tests."],
                ["Masks real packaging bugs and can change import precedence."],
                "Brittle workaround.",
            ),
            "Import errors should be solved by adding all directories to PYTHONPATH.",
            "The candidate causes negative transfer across package layouts.",
        ),
        sample(
            "sample_v4_discard_delete_cache_database",
            "discard",
            "Deleting persistent state on failure",
            "state_management",
            [
                exp("v4_bad_state_001", "A migration failed because one column was missing.", "Migration logic should be repaired.", "Add an idempotent migration.", "Deleting the database loses user data."),
            ],
            "One local state migration failed.",
            skill(
                "Delete Persistent State When Migration Fails",
                ["Any database or cache migration error"],
                ["Delete the database or cache directory.", "Restart the app."],
                ["Can destroy user data and hides migration bugs."],
                "Actively harmful.",
            ),
            "Migration failures should be solved by deleting persistent state.",
            "The candidate is destructive and should be discarded.",
        ),
        sample(
            "sample_v4_discard_silence_all_exceptions",
            "discard",
            "Silencing all exceptions",
            "runtime_debugging",
            [
                exp("v4_bad_except_001", "A FileNotFoundError revealed a bad resource path.", "Path handling needs repair.", "Resolve the path correctly.", "A broad except leaves wrong behavior."),
            ],
            "One runtime exception exposed a real bug.",
            skill(
                "Silence Exceptions with pass",
                ["Any runtime exception"],
                ["Wrap the failing block in except Exception.", "Use pass.", "Continue execution."],
                ["Suppresses errors and leaves undefined state."],
                "Actively harmful.",
            ),
            "If code raises an exception, catch Exception and continue.",
            "The candidate suppresses the symptom instead of repairing the cause.",
        ),
        sample(
            "sample_v4_discard_lower_eval_threshold",
            "discard",
            "Lowering evaluation threshold",
            "evaluation",
            [
                exp("v4_bad_eval_001", "A model failed the required accuracy threshold.", "The model or prompt needs improvement.", "Improve the method or report failure.", "Lowering threshold changes the metric."),
            ],
            "One evaluation failed its target metric.",
            skill(
                "Lower Metrics Until the Run Passes",
                ["Any evaluation failure"],
                ["Reduce the required accuracy threshold.", "Rerun evaluation.", "Report the run as passing."],
                ["Invalidates the comparison and hides regressions."],
                "Actively harmful.",
            ),
            "If evaluation fails, lower the passing threshold.",
            "The candidate manipulates the metric rather than improving the system.",
        ),
    ]


def build_memory_samples() -> list[dict[str, Any]]:
    return [
        sample(
            "sample_v4_memory_v4_sample_path",
            "store_as_memory",
            "Current v4 sample file path",
            "project_artifact",
            [
                exp("v4_mem_path_001", "The newly generated v4 samples are written to benchmark/admission_samples/v4_blind_admission_samples.jsonl.", "This is repository state.", "Store exact path for continuation.", "Other projects use different paths."),
            ],
            "The current v4 blind-style sample file is benchmark/admission_samples/v4_blind_admission_samples.jsonl.",
            skill(
                "Open the Current V4 Sample File",
                ["Need current SkillAdmit v4 samples"],
                ["Open benchmark/admission_samples/v4_blind_admission_samples.jsonl."],
                ["Only applies to this repository state."],
                "Project-specific.",
            ),
            "All projects store v4 samples at this exact path.",
            "The path is useful local memory, not a transferable skill.",
        ),
        sample(
            "sample_v4_memory_local_proxy_port",
            "store_as_memory",
            "Current local proxy port",
            "runtime_environment",
            [
                exp("v4_mem_proxy_001", "Some local debugging used proxy port 127.0.0.1:7890.", "This is a machine-specific network fact.", "Record as local environment memory.", "Not transferable to other machines."),
            ],
            "This machine may use local proxy endpoint 127.0.0.1:7890 for network debugging.",
            skill(
                "Use 127.0.0.1:7890 Proxy",
                ["Any network failure"],
                ["Route requests through 127.0.0.1:7890."],
                ["Only valid if this user's local proxy is running."],
                "Environment-specific.",
            ),
            "All network failures should use proxy 127.0.0.1:7890.",
            "This is local environment memory.",
        ),
        sample(
            "sample_v4_memory_current_model_provider",
            "store_as_memory",
            "Current MiMo model provider",
            "runtime_config",
            [
                exp("v4_mem_model_001", "The current SkillAdmit LLM runs use mimo-v2.5-pro.", "This is the current provider configuration.", "Record model name.", "Model choice can change."),
            ],
            "The current SkillAdmit LLM runner is configured with model mimo-v2.5-pro.",
            skill(
                "Use mimo-v2.5-pro for Every Agent",
                ["Any future agent experiment"],
                ["Set SKILLADMIT_MODEL=mimo-v2.5-pro."],
                ["Only valid for this current project configuration."],
                "Environment-specific.",
            ),
            "Every agent benchmark should use mimo-v2.5-pro.",
            "The model name is useful reproducibility memory.",
        ),
        sample(
            "sample_v4_memory_frozen_controller_path",
            "store_as_memory",
            "Frozen controller file path",
            "project_artifact",
            [
                exp("v4_mem_frozen_001", "The frozen controller snapshot is skilladmit/controllers/rule_based_controller_v3_frozen.py.", "This identifies the baseline used for v4 evaluation.", "Record frozen file path.", "Future snapshots may use different names."),
            ],
            "The v4 evaluation should use skilladmit/controllers/rule_based_controller_v3_frozen.py as the frozen controller snapshot.",
            skill(
                "Always Use rule_based_controller_v3_frozen",
                ["Any admission evaluation"],
                ["Import skilladmit.controllers.rule_based_controller_v3_frozen."],
                ["Only applies to the current frozen baseline."],
                "Project-specific.",
            ),
            "All future admission evaluations should use this frozen controller file.",
            "The file path is project metadata.",
        ),
        sample(
            "sample_v4_memory_prediction_output_path",
            "store_as_memory",
            "Frozen prediction output path",
            "project_artifact",
            [
                exp("v4_mem_pred_001", "Frozen v4 predictions are written to benchmark/admission_samples/v4_frozen_controller_predictions.jsonl.", "This is an artifact location.", "Store prediction output path.", "Not a general evaluation rule."),
            ],
            "The v4 frozen-controller prediction file is benchmark/admission_samples/v4_frozen_controller_predictions.jsonl.",
            skill(
                "Read Frozen Controller Predictions",
                ["Need v4 prediction details"],
                ["Open benchmark/admission_samples/v4_frozen_controller_predictions.jsonl."],
                ["Only applies after this evaluation script has run."],
                "Project-specific.",
            ),
            "All frozen predictions are stored at this exact path.",
            "This is useful repository memory.",
        ),
        sample(
            "sample_v4_memory_current_python_executable",
            "store_as_memory",
            "Current Python executable",
            "runtime_environment",
            [
                exp("v4_mem_python_001", "Commands run under /home/lijx/anaconda3/envs/skilladmit/bin/python.", "This matters for reproducing package versions.", "Record executable path.", "Not transferable to another machine."),
            ],
            "The current SkillAdmit environment uses /home/lijx/anaconda3/envs/skilladmit/bin/python.",
            skill(
                "Use This Exact Python Executable",
                ["Any Python command"],
                ["Run /home/lijx/anaconda3/envs/skilladmit/bin/python."],
                ["Only applies to this local machine."],
                "Environment-specific.",
            ),
            "Every project should run this exact Python executable.",
            "This is local reproducibility metadata.",
        ),
        sample(
            "sample_v4_memory_current_task_count",
            "store_as_memory",
            "Current generated task count",
            "benchmark_metadata",
            [
                exp("v4_mem_count_001", "The Python import/debug benchmark currently contains 20 generated tasks.", "This is benchmark metadata.", "Record current count.", "The count can change when tasks are regenerated."),
            ],
            "At this stage, benchmark/tasks contains 20 Python import/debug tasks.",
            skill(
                "Assume the Benchmark Has 20 Tasks",
                ["Any SkillAdmit run"],
                ["Use 20 as the task count."],
                ["Only true for the current generated benchmark state."],
                "Stale if benchmark expands.",
            ),
            "SkillAdmit benchmarks always contain 20 tasks.",
            "The count is useful current project memory.",
        ),
        sample(
            "sample_v4_memory_current_api_base_url",
            "store_as_memory",
            "Current API base URL variable",
            "runtime_config",
            [
                exp("v4_mem_base_001", "The configured base URL is stored in OPENAI_BASE_URL.", "This is current project configuration.", "Record env var name and value location.", "The value should not become a universal rule."),
            ],
            "The current OpenAI-compatible endpoint is configured through OPENAI_BASE_URL in the project .env.",
            skill(
                "Use OPENAI_BASE_URL from .env for All Projects",
                ["Any API client"],
                ["Load OPENAI_BASE_URL from .env."],
                ["Only confirmed for this project's setup."],
                "Project-specific.",
            ),
            "All API projects should use OPENAI_BASE_URL from .env.",
            "This is configuration memory rather than a general skill.",
        ),
        sample(
            "sample_v4_memory_current_eval_command",
            "store_as_memory",
            "Current v4 evaluation command",
            "project_artifact",
            [
                exp("v4_mem_cmd_001", "The v4 frozen evaluation command is python scripts/evaluate_frozen_controller.py.", "This is project workflow metadata.", "Record command for continuation.", "Other repos use different commands."),
            ],
            "To reproduce the v4 frozen result, run python scripts/evaluate_frozen_controller.py from the repository root.",
            skill(
                "Run evaluate_frozen_controller.py for Every Evaluation",
                ["Need admission results"],
                ["Run python scripts/evaluate_frozen_controller.py."],
                ["Only applies to this experiment phase."],
                "Project-specific.",
            ),
            "Every admission benchmark should be evaluated by this script.",
            "The command is useful local memory.",
        ),
        sample(
            "sample_v4_memory_current_docs_handoff",
            "store_as_memory",
            "Current handoff document",
            "project_artifact",
            [
                exp("v4_mem_doc_001", "The continuation guide is docs/experiment_handoff.md.", "This is repository documentation state.", "Record document path.", "Not a task-solving procedure."),
            ],
            "The current cross-session handoff document is docs/experiment_handoff.md.",
            skill(
                "Use experiment_handoff.md as Universal Protocol",
                ["Any future project"],
                ["Open docs/experiment_handoff.md."],
                ["Only applies to this repository."],
                "Project-specific.",
            ),
            "Every project should keep its handoff document at docs/experiment_handoff.md.",
            "The document path should be stored as memory.",
        ),
    ]


def build_rule_samples() -> list[dict[str, Any]]:
    return [
        sample(
            "sample_v4_rule_no_secret_exposure",
            "promote_to_rule",
            "Secret redaction rule",
            "runtime_config",
            [
                exp("v4_rule_secret_001", "Config debugging needed API key presence.", "Full secret value is unnecessary.", "Print only presence and redacted prefix.", "Secret exposure is irreversible."),
                exp("v4_rule_secret_002", "Provider auth failed.", "Base URL and model are safe to show, key is not.", "Log non-secret config only.", "Full key logging leaks credentials."),
            ],
            "Credential checks recur across API debugging tasks.",
            skill(
                "Redact Secrets in Logs",
                ["Any runtime config or API authentication debugging"],
                ["Never print full secret values.", "Print non-secret config.", "Report secret presence or redacted values only."],
                ["This is a global safety constraint, not a task-specific repair."],
                "Low risk.",
            ),
            "Never print full API keys, tokens, passwords, or .env contents in logs.",
            "This should constrain all future debugging workflows.",
        ),
        sample(
            "sample_v4_rule_preserve_tests_and_verifier",
            "promote_to_rule",
            "Preserve test and verifier contract",
            "evaluation",
            [
                exp("v4_rule_contract_001", "A source bug was exposed by pytest.", "The test is the acceptance contract.", "Fix source code.", "Changing tests fakes success."),
                exp("v4_rule_contract_002", "verifier.sh encoded the benchmark command.", "Verifier output defines success.", "Keep verifier intact.", "Changing verifier invalidates evaluation."),
            ],
            "Debugging benchmarks depend on stable tests and verifier scripts.",
            skill(
                "Preserve Evaluation Contract",
                ["Any benchmark repair"],
                ["Do not edit tests or verifier scripts.", "Fix the system under test.", "Rerun the original verifier."],
                ["Only change tests when the task explicitly requests test maintenance."],
                "Low risk.",
            ),
            "Do not modify tests, metrics, or verifier commands unless the task explicitly asks for it.",
            "This is a cross-task rule.",
        ),
        sample(
            "sample_v4_rule_require_validation_before_admission",
            "promote_to_rule",
            "Validation-before-admission rule",
            "experience_management",
            [
                exp("v4_rule_validation_001", "A plausible patch failed the verifier.", "Plausibility is not correctness.", "Record final verifier result.", "Unvalidated experience can become bad memory."),
                exp("v4_rule_validation_002", "A JSON repair succeeded but semantic patch failed.", "Format repair does not imply task success.", "Validate after applying edits.", "Bad artifacts can be admitted otherwise."),
            ],
            "Experience admission needs an observed validation outcome.",
            skill(
                "Validate Before Admitting Experience",
                ["Any candidate memory, skill, or rule from an agent run"],
                ["Check final verifier or task-specific validation result.", "Record success or failure.", "Do not admit unvalidated repair claims as skills."],
                ["Diagnostic failures may be stored separately if clearly useful."],
                "Low risk.",
            ),
            "Before admitting repair experience, verify and record the final validation result.",
            "This should be promoted as a lifecycle rule.",
        ),
        sample(
            "sample_v4_rule_check_skill_preconditions",
            "promote_to_rule",
            "Skill precondition rule",
            "experience_management",
            [
                exp("v4_rule_precond_001", "A local-import skill was harmful when the missing module was external.", "Trigger precondition failed.", "Check repository files first.", "Wrong skill transfer causes failure."),
                exp("v4_rule_precond_002", "A path repair skill was wrong when input path was user-provided.", "The data ownership precondition failed.", "Check source of path.", "Wrong base can break user workflow."),
            ],
            "Retrieved skills can be harmful when their trigger does not match.",
            skill(
                "Check Preconditions Before Skill Use",
                ["Any retrieved skill"],
                ["Read trigger and limitations.", "Check current task against required preconditions.", "Skip or defer if preconditions do not match."],
                ["This is a cross-skill control rule."],
                "Low risk.",
            ),
            "Apply a retrieved skill only when its trigger, scope, and limitations match the current task.",
            "This rule reduces negative transfer across domains.",
        ),
        sample(
            "sample_v4_rule_preserve_user_command",
            "promote_to_rule",
            "Preserve user command semantics",
            "software_debugging",
            [
                exp("v4_rule_command_001", "A bug reproduced with python -m package.tool.", "The launch mode matters.", "Fix code for that launch mode.", "Changing command hides the bug."),
                exp("v4_rule_command_002", "A script was required to run from a subdirectory.", "cwd is part of the workflow.", "Make paths robust.", "Changing cwd alone may not preserve user workflow."),
            ],
            "Debugging tasks often include a required command or launch mode.",
            skill(
                "Preserve Required Command Semantics",
                ["Any command-reproduction debugging task"],
                ["Read the required command.", "Preserve launch mode, cwd, and arguments.", "Fix code unless command change is explicitly allowed."],
                ["If the user asks to change the command, record that exception."],
                "Low risk.",
            ),
            "Do not change required command semantics unless the task explicitly permits it.",
            "This is a general debugging constraint.",
        ),
        sample(
            "sample_v4_rule_separate_runtime_noise",
            "promote_to_rule",
            "Separate runtime noise from task knowledge",
            "agent_runtime",
            [
                exp("v4_rule_noise_001", "A provider returned one empty streaming chunk.", "This is runtime noise.", "Improve parser robustness.", "Do not store as a domain repair skill."),
                exp("v4_rule_noise_002", "An API timeout resolved after retry.", "It may be infrastructure noise.", "Record separately from task knowledge.", "Pollutes future retrieval if admitted as skill."),
            ],
            "Infrastructure events recur but belong to a different layer than task skills.",
            skill(
                "Separate Runtime Events from Domain Skills",
                ["API timeouts", "empty model chunks", "formatting failures", "runner errors"],
                ["Classify whether the event is infrastructure or task-domain knowledge.", "Record infrastructure issues separately.", "Do not admit runtime noise as task-solving skill."],
                ["Infrastructure improvements can still become runner engineering tasks."],
                "Low risk.",
            ),
            "Do not admit runner, API, or parser noise as domain task-solving memory, skill, or rule.",
            "This should be promoted as an experience-management rule.",
        ),
        sample(
            "sample_v4_rule_budget_aware_admission",
            "promote_to_rule",
            "Budget-aware admission rule",
            "experience_management",
            [
                exp("v4_rule_budget_001", "A long skill summary cost more tokens than it saved.", "Admission has a token budget.", "Estimate future reuse before storing.", "Unbounded memory increases context cost."),
                exp("v4_rule_budget_002", "Validation tasks cost model calls.", "Risk and future utility should guide validation depth.", "Budget validation deliberately.", "Over-validation wastes resources."),
            ],
            "Experience admission consumes generation, storage, retrieval, and validation budget.",
            skill(
                "Check Utility and Cost Before Admission",
                ["Any candidate memory, skill, or rule"],
                ["Estimate future utility.", "Estimate token and validation cost.", "Compare expected benefit against risk.", "Prefer admission only when expected value is positive."],
                ["This is a global admission policy, not a task repair."],
                "Low risk.",
            ),
            "Admission should consider future utility, token cost, validation cost, and negative-transfer risk.",
            "This applies across memory, skill, and rule decisions.",
        ),
        sample(
            "sample_v4_rule_keep_scope_with_skill",
            "promote_to_rule",
            "Keep scope and limitations with skills",
            "experience_management",
            [
                exp("v4_rule_scope_001", "A shortened skill lost its trigger conditions.", "Missing scope caused misuse.", "Keep trigger and limitations.", "Unscoped skills overgeneralize."),
                exp("v4_rule_scope_002", "A safe repair became harmful when caveats were removed.", "Limitations were part of the skill.", "Store limitations with steps.", "Future retrieval needs constraints."),
            ],
            "Skills are safer when their scope and limitations travel with them.",
            skill(
                "Require Explicit Skill Scope",
                ["Any candidate skill"],
                ["Check trigger.", "Check applicability conditions.", "Check limitations.", "Reject or defer skills without explicit scope."],
                ["This is an admission rule rather than a domain procedure."],
                "Low risk.",
            ),
            "Do not admit a skill unless its triggers, scope, and limitations are explicit.",
            "This is a cross-skill guardrail.",
        ),
        sample(
            "sample_v4_rule_prefer_least_destructive_fix",
            "promote_to_rule",
            "Least destructive repair rule",
            "software_debugging",
            [
                exp("v4_rule_destructive_001", "Deleting a cache fixed one run but lost useful state.", "The root cause was one corrupt file.", "Repair or regenerate the minimal affected artifact.", "Broad deletion risks data loss."),
                exp("v4_rule_destructive_002", "Reinstalling all dependencies fixed an import once.", "The actual issue was one bad package version.", "Change the minimal dependency.", "Broad reinstall is hard to reproduce."),
            ],
            "Many quick fixes are broader than the actual fault.",
            skill(
                "Prefer Least Destructive Repair",
                ["Any debugging task with a possible destructive fix"],
                ["Identify the smallest artifact or setting causing the failure.", "Prefer local repairs over broad deletion or reset.", "Record why a destructive action is necessary if used."],
                ["This is a general repair constraint."],
                "Low risk.",
            ),
            "Prefer the least destructive repair that preserves user data, tests, and reproducibility.",
            "This should constrain future debugging skills.",
        ),
        sample(
            "sample_v4_rule_record_artifact_provenance",
            "promote_to_rule",
            "Artifact provenance rule",
            "experience_management",
            [
                exp("v4_rule_prov_001", "A skill looked useful but its source run was unclear.", "Untraceable artifacts are hard to audit.", "Record source trajectory IDs.", "No provenance weakens evidence."),
                exp("v4_rule_prov_002", "A memory item became stale after regeneration.", "The source and date mattered.", "Record source file and generation date.", "Stale artifacts can mislead future agents."),
            ],
            "Admitted artifacts need traceable evidence.",
            skill(
                "Record Provenance for Admitted Artifacts",
                ["Any admitted memory, skill, or rule"],
                ["Record source trajectories.", "Record generator script or file.", "Record validation result and date.", "Keep provenance with the artifact."],
                ["This is a general admission bookkeeping rule."],
                "Low risk.",
            ),
            "Every admitted artifact should record its source evidence and validation result.",
            "This is a general experience-management rule.",
        ),
    ]


def build_defer_samples() -> list[dict[str, Any]]:
    return [
        sample(
            "sample_v4_defer_one_proxy_success",
            "defer",
            "Single proxy configuration success",
            "api_debugging",
            [
                exp("v4_defer_proxy_001", "One API timeout disappeared after disabling proxy inheritance.", "Proxy may have caused it in this environment.", "Set trust_env deliberately.", "Other networks may require the proxy."),
            ],
            "One run succeeded after changing proxy handling.",
            skill(
                "Disable Proxy Inheritance for API Calls",
                ["Any API timeout"],
                ["Set trust_env=false.", "Retry the request."],
                ["Only one environment observed.", "Some networks require proxies."],
                "Needs more validation.",
            ),
            "API timeouts should be solved by disabling proxy inheritance.",
            "The evidence is too environment-specific for admission.",
        ),
        sample(
            "sample_v4_defer_conflicting_resource_base",
            "defer",
            "Conflicting resource path bases",
            "path_debugging",
            [
                exp("v4_defer_path_001", "A config file should be resolved from repo root.", "Repo root was the intended base.", "Use a repo-root anchor.", "Module directory would be wrong."),
                exp("v4_defer_path_002", "A template file should be resolved from package directory.", "Package resource was the intended base.", "Use package-relative resource loading.", "Repo root would be wrong after install."),
            ],
            "Different path failures required different base directories.",
            skill(
                "Anchor All Relative Paths to Repo Root",
                ["Any FileNotFoundError for a relative path"],
                ["Find repo root.", "Rewrite all relative paths from repo root."],
                ["Conflicts with package-resource files.", "Needs clearer decision boundary."],
                "Under-specified.",
            ),
            "Relative paths should always be anchored to repository root.",
            "The evidence conflicts, so admission should be deferred.",
        ),
        sample(
            "sample_v4_defer_streaming_provider_difference",
            "defer",
            "Provider-dependent streaming behavior",
            "api_debugging",
            [
                exp("v4_defer_stream_001", "Provider A returned useful content only through streaming deltas.", "Streaming parser was necessary.", "Use stream=True.", "Provider-specific."),
                exp("v4_defer_stream_002", "Provider B returned complete non-streaming message content.", "Streaming was unnecessary.", "Use normal chat response.", "Different providers differ."),
            ],
            "OpenAI-compatible providers differed in streaming and non-streaming behavior.",
            skill(
                "Always Use Streaming Chat Mode",
                ["Any OpenAI-compatible chat request"],
                ["Set stream=True.", "Parse deltas only."],
                ["Some endpoints work fine without streaming.", "Needs provider comparison."],
                "Needs more validation.",
            ),
            "All OpenAI-compatible chat requests should use streaming.",
            "The candidate is plausible but provider-conflicting.",
        ),
        sample(
            "sample_v4_defer_latency_batch_size",
            "defer",
            "Unclear batch-size latency rule",
            "performance_tuning",
            [
                exp("v4_defer_batch_001", "Batch size 8 improved one run.", "Overhead was amortized.", "Use larger batch.", "Memory usage was not tested."),
                exp("v4_defer_batch_002", "Batch size 8 caused OOM in another run.", "Memory pressure changed the optimum.", "Use smaller batch.", "Hardware differs."),
            ],
            "Batch-size observations conflict across hardware and workload.",
            skill(
                "Use Batch Size 8 for All Runs",
                ["Any model evaluation"],
                ["Set batch_size=8.", "Run evaluation."],
                ["Only two conflicting runs observed.", "Hardware and sequence length matter."],
                "Needs broader validation.",
            ),
            "Model evaluations should use batch size 8.",
            "This needs more evidence before admission.",
        ),
        sample(
            "sample_v4_defer_env_memory_or_rule",
            "defer",
            "Unclear .env convention level",
            "runtime_config",
            [
                exp("v4_defer_env_001", "One project used .env and load_dotenv.", "This was convenient project setup.", "Store project config.", "Could become a setup skill."),
                exp("v4_defer_env_002", "Another deployment used injected environment variables.", "No .env file existed.", "Read process env directly.", "A .env rule would be wrong there."),
            ],
            "API configuration style differs across projects and deployment targets.",
            skill(
                "Require .env for All API Clients",
                ["Any API client project"],
                ["Create .env.", "Load it at process startup.", "Fail if .env is missing."],
                ["Deployment environments may inject variables directly.", "Not enough projects observed."],
                "Needs clearer boundary.",
            ),
            "All API clients should use a .env file.",
            "The decision boundary between memory, skill, and rule is unclear.",
        ),
        sample(
            "sample_v4_defer_single_flaky_retry",
            "defer",
            "Single flaky retry success",
            "agent_runtime",
            [
                exp("v4_defer_flaky_001", "One empty model response succeeded after retry.", "The failure may be transient provider noise.", "Retry once.", "Could be an API bug or parser bug."),
            ],
            "One empty response recovered after a retry.",
            skill(
                "Retry Once for Every Empty Model Response",
                ["Empty model response"],
                ["Retry once.", "Use retry result if non-empty."],
                ["Only one event observed.", "Needs more validation across providers and failure modes."],
                "Could be transient.",
            ),
            "Empty model responses should always be repaired by one retry.",
            "The evidence is too small for admission.",
        ),
        sample(
            "sample_v4_defer_exception_strategy_conflict",
            "defer",
            "Conflicting exception handling strategy",
            "runtime_debugging",
            [
                exp("v4_defer_except_001", "A missing optional plugin should not crash startup.", "A narrow ImportError fallback was acceptable.", "Catch a specific optional import.", "Broad catch would hide real bugs."),
                exp("v4_defer_except_002", "A missing core dependency should crash early.", "The dependency is required.", "Fail fast.", "Fallback would create invalid behavior."),
            ],
            "Import errors can be optional-plugin failures or required-dependency failures.",
            skill(
                "Catch ImportError and Continue",
                ["Any ImportError"],
                ["Wrap import in try/except ImportError.", "Continue with fallback behavior."],
                ["Ambiguous optional versus required dependency.", "Needs stronger preconditions."],
                "High risk without a decision boundary.",
            ),
            "ImportError should usually be handled with a fallback.",
            "The candidate needs a sharper precondition before admission.",
        ),
        sample(
            "sample_v4_defer_pydantic_config_standard",
            "defer",
            "Unclear config library standardization",
            "runtime_config",
            [
                exp("v4_defer_pyd_001", "One service benefited from pydantic settings validation.", "Structured config reduced errors.", "Use pydantic settings.", "Small script may not need it."),
                exp("v4_defer_pyd_002", "A tiny CLI became heavier after adding pydantic.", "The dependency was unnecessary.", "Use argparse validation only.", "Project size matters."),
            ],
            "Configuration validation needs differ by project size and deployment context.",
            skill(
                "Use Pydantic Settings for All Config",
                ["Any environment variable or config parsing"],
                ["Add pydantic settings.", "Model all config fields.", "Validate at startup."],
                ["Only a small number of projects observed.", "May be too heavy for small scripts."],
                "Needs broader validation.",
            ),
            "All Python projects should use pydantic settings for configuration.",
            "This may become a setup skill, but current evidence is insufficient.",
        ),
        sample(
            "sample_v4_defer_llm_cache_policy",
            "defer",
            "Unclear LLM response cache policy",
            "agent_runtime",
            [
                exp("v4_defer_cache_001", "Caching saved tokens on repeated prompts.", "Prompt and model were identical.", "Cache exact requests.", "Stale cache risk was not tested."),
                exp("v4_defer_cache_002", "Cached response became invalid after model change.", "Model version is part of cache key.", "Invalidate cache on model changes.", "Policy boundary is underspecified."),
            ],
            "LLM caching can save cost but risks stale or invalid responses.",
            skill(
                "Cache All LLM Responses",
                ["Any repeated LLM request"],
                ["Store response by prompt text.", "Reuse cache whenever prompt matches."],
                ["Needs model/version/base_url in key.", "Needs invalidation policy."],
                "Under-specified.",
            ),
            "All LLM responses should be cached by prompt text.",
            "The cache policy needs more validation and sharper keys.",
        ),
        sample(
            "sample_v4_defer_user_preference_scope",
            "defer",
            "Unclear user preference scope",
            "collaboration_memory",
            [
                exp("v4_defer_pref_001", "The user wanted to run commands themselves in one phase.", "This was workflow preference for that phase.", "Let user run commands.", "Preference may change."),
                exp("v4_defer_pref_002", "The user later asked the agent to run and improve independently.", "Preference changed with task stage.", "Act autonomously.", "A universal rule would be wrong."),
            ],
            "The user's desired autonomy level changed across phases.",
            skill(
                "Always Let User Run Commands",
                ["Any coding task"],
                ["Write commands only.", "Do not run tests yourself."],
                ["Conflicts with later explicit autonomy requests.", "Needs current-turn confirmation."],
                "Context-dependent.",
            ),
            "The assistant should never run commands and should only provide instructions.",
            "The evidence conflicts, so this should be deferred rather than admitted.",
        ),
    ]


def build_rows() -> list[dict[str, Any]]:
    rows = []
    rows.extend(build_skill_samples())
    rows.extend(build_discard_samples())
    rows.extend(build_memory_samples())
    rows.extend(build_rule_samples())
    rows.extend(build_defer_samples())
    return rows


def main() -> None:
    rows = build_rows()
    counts = Counter(row["label"] for row in rows)

    expected_labels = set(AVAILABLE_ACTIONS)
    if set(counts) != expected_labels:
        raise RuntimeError(f"Unexpected label set: {dict(counts)}")
    if any(count != 10 for count in counts.values()):
        raise RuntimeError(f"Expected 10 samples per label, got {dict(counts)}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )

    print(f"Wrote {len(rows)} v4 blind-style samples to {OUT}")
    print("label_counts:")
    for label, count in sorted(counts.items()):
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
