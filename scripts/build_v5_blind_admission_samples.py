#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark" / "admission_samples" / "v5_blind_admission_samples.jsonl"


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
    return {
        "sample_id": sample_id,
        "source": "v5_blind_curated_after_v4_freeze",
        "family": family,
        "cluster_id": sample_id.replace("sample_", "cluster_"),
        "cluster_name": cluster_name,
        "task_ids": [item["task_id"] for item in experience_cluster],
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
            "sample_v5_skill_yaml_default_merge",
            "distill_into_skill",
            "YAML default merge repair",
            "config_debugging",
            [
                exp("v5_skill_yaml_001", "A YAML override dropped default timeout.", "The merge replaced nested config instead of merging it.", "Deep-merge known config sections.", "Do not merge unknown fields blindly."),
                exp("v5_skill_yaml_002", "Model config lost retry settings after loading profile override.", "Nested defaults were overwritten.", "Merge profile over defaults recursively.", "List merge semantics must be explicit."),
                exp("v5_skill_yaml_003", "Environment-specific YAML missed inherited logging config.", "Inheritance was shallow.", "Apply recursive merge then validate schema.", "Do not skip validation."),
            ],
            "Several configuration failures came from shallow YAML override semantics.",
            skill(
                "Repair YAML Default Override Merges",
                ["YAML config override drops nested default values", "profile-specific config replaces a whole nested section"],
                ["Load defaults and override separately.", "Deep-merge known mapping sections.", "Define list replacement semantics.", "Validate the merged config.", "Rerun the failing command."],
                ["Do not invent defaults for unknown fields.", "Do not skip schema validation."],
                "Low risk when schema and merge semantics are explicit.",
            ),
            "Config overrides should preserve validated defaults unless the override explicitly replaces them.",
            "The cluster supports a reusable configuration repair procedure.",
        ),
        sample(
            "sample_v5_skill_expanduser_path",
            "distill_into_skill",
            "User-home path expansion repair",
            "path_debugging",
            [
                exp("v5_skill_path_001", "A cache path '~/cache/app' was treated as a literal folder name.", "The code did not expand user-home syntax.", "Call expanduser before resolving.", "Only applies to user-provided filesystem paths."),
                exp("v5_skill_path_002", "Environment variable DATA_DIR contained '~'.", "Path normalization was incomplete.", "Expand user and environment variables at config load.", "Do not expand arbitrary data strings."),
                exp("v5_skill_path_003", "CLI path worked in shell but failed inside Python.", "Shell expansion did not happen for config values.", "Normalize path in Python.", "Validate existence after normalization."),
            ],
            "Several path bugs came from unexpanded user-home path syntax.",
            skill(
                "Normalize User-Provided Paths",
                ["path contains ~ or environment variables", "filesystem path from CLI or config fails unexpectedly"],
                ["Identify fields that are filesystem paths.", "Expand user-home syntax.", "Expand known environment variables.", "Resolve or validate the path.", "Preserve non-path strings."],
                ["Do not apply path expansion to arbitrary text values."],
                "Low risk when only declared path fields are normalized.",
            ),
            "User-provided filesystem paths should be normalized before file access.",
            "The repeated failures support skill admission.",
        ),
        sample(
            "sample_v5_skill_http_content_type_json",
            "distill_into_skill",
            "HTTP content-type JSON parsing repair",
            "api_debugging",
            [
                exp("v5_skill_http_001", "Client parsed response text manually although content-type was application/json.", "The response should use JSON parser.", "Use response.json with error handling.", "Do not assume every 200 response is JSON."),
                exp("v5_skill_http_002", "Provider returned JSON with charset in content-type.", "Exact content-type comparison failed.", "Parse media type ignoring charset.", "Still handle non-JSON responses."),
                exp("v5_skill_http_003", "Error response returned JSON body with non-2xx status.", "Parser skipped useful error details.", "Parse JSON error body before raising.", "Do not treat error body as success."),
            ],
            "Several API parsing bugs involved JSON content-type handling.",
            skill(
                "Repair HTTP JSON Response Parsing",
                ["HTTP response content-type indicates JSON", "manual text parser fails on JSON response"],
                ["Inspect status code and content-type.", "Parse JSON bodies through a structured parser.", "Handle charset parameters.", "Preserve non-2xx error semantics.", "Validate expected response fields."],
                ["Do not parse every response as JSON.", "Do not treat JSON error bodies as success."],
                "Low risk when status and content-type are both checked.",
            ),
            "HTTP clients should parse structured JSON responses through schema-aware code.",
            "The cluster shows a transferable API parsing repair.",
        ),
        sample(
            "sample_v5_skill_async_await_missing",
            "distill_into_skill",
            "Missing await repair",
            "async_debugging",
            [
                exp("v5_skill_async_001", "A coroutine object was returned instead of data.", "The async function was called without await.", "Await the coroutine in the async call path.", "Do not block the event loop with sync wrappers."),
                exp("v5_skill_async_002", "Test warned that coroutine was never awaited.", "The caller missed await.", "Propagate async or await at the boundary.", "Launch context matters."),
                exp("v5_skill_async_003", "Result serialization failed on coroutine object.", "Async task was not resolved.", "Await before serialization.", "Do not hide by str(coroutine)."),
            ],
            "Several runtime failures came from missing await in an async call path.",
            skill(
                "Repair Missing Await in Async Call Paths",
                ["coroutine object returned", "coroutine was never awaited warning", "async result is serialized before resolution"],
                ["Trace the async call chain.", "Await coroutine at an async boundary.", "Propagate async if needed.", "Rerun async tests.", "Avoid blocking event-loop hacks."],
                ["Do not use blocking wrappers inside a running event loop."],
                "Medium risk when launch context is unclear.",
            ),
            "Async repairs should preserve event-loop semantics while awaiting unresolved coroutines.",
            "The evidence supports a reusable async debugging skill.",
        ),
        sample(
            "sample_v5_skill_sqlite_locked_transaction",
            "distill_into_skill",
            "SQLite locked transaction repair",
            "database_debugging",
            [
                exp("v5_skill_sqlite_001", "SQLite reported database is locked during concurrent writes.", "Transactions were held too long.", "Use short transactions and busy timeout.", "Do not retry forever."),
                exp("v5_skill_sqlite_002", "A reader blocked a writer in test runs.", "Connection lifecycle was wrong.", "Close connections and set timeout.", "Concurrency model still matters."),
                exp("v5_skill_sqlite_003", "Batch insert failed intermittently with lock errors.", "Write contention was unmanaged.", "Serialize writes or use bounded retry.", "Do not drop writes."),
            ],
            "Several local database failures came from SQLite write-lock handling.",
            skill(
                "Repair SQLite Lock Contention",
                ["SQLite database is locked", "intermittent lock errors during concurrent local writes"],
                ["Inspect connection lifetime.", "Keep transactions short.", "Set a busy timeout.", "Use bounded retry or serialize writes.", "Validate that writes are not dropped."],
                ["Do not retry forever.", "Do not delete the database as a repair."],
                "Medium risk because retry policies can hide contention.",
            ),
            "SQLite lock repairs should bound retry and preserve write correctness.",
            "The repeated lock failures justify a procedural skill.",
        ),
        sample(
            "sample_v5_skill_atomic_file_write",
            "distill_into_skill",
            "Atomic file write repair",
            "io_debugging",
            [
                exp("v5_skill_atomic_001", "A config file became truncated after crash during write.", "Writes were not atomic.", "Write temp file then replace.", "Do not ignore fsync requirements for critical files."),
                exp("v5_skill_atomic_002", "Concurrent readers saw partial JSON.", "The file was overwritten in place.", "Use atomic rename after full write.", "Still validate JSON after read."),
                exp("v5_skill_atomic_003", "Cache metadata was sometimes empty.", "Writer interruption left partial file.", "Use temp path and atomic replace.", "Clean stale temp files carefully."),
            ],
            "Several file corruption bugs came from in-place writes.",
            skill(
                "Repair Non-Atomic File Writes",
                ["partial file observed after crash", "readers see truncated JSON or config"],
                ["Write content to a temporary file.", "Flush as needed.", "Atomically replace the target file.", "Validate the final file.", "Clean stale temporary files safely."],
                ["Do not delete unrelated files.", "Critical durability may require fsync."],
                "Low to medium risk depending on durability requirements.",
            ),
            "Writers should use atomic replace when readers require complete files.",
            "The cluster supports a reusable IO repair skill.",
        ),
        sample(
            "sample_v5_skill_dependency_import_rename",
            "distill_into_skill",
            "Dependency import rename repair",
            "python_import_debug",
            [
                exp("v5_skill_dep_001", "Installed package exposed new_module while code imported old_module.", "Dependency API changed names.", "Check installed package docs and update import.", "Do not install random similarly named packages."),
                exp("v5_skill_dep_002", "Import failed after library upgrade.", "The symbol moved to a submodule.", "Use compatibility import or update call sites.", "Version range should be recorded."),
                exp("v5_skill_dep_003", "A deprecation warning showed the replacement module.", "The old path was removed.", "Migrate to the documented import path.", "Do not silence import errors."),
            ],
            "Several import failures came from documented dependency module renames.",
            skill(
                "Repair Documented Dependency Import Renames",
                ["import fails after dependency upgrade", "package documentation shows a renamed module or moved symbol"],
                ["Check installed package version.", "Find documented new import path.", "Update imports or add compatibility shim.", "Record version constraint.", "Rerun tests."],
                ["Do not install unrelated packages.", "Do not add sys.path hacks."],
                "Medium risk without version checks.",
            ),
            "Dependency import repairs should be based on installed version and documented replacement paths.",
            "The examples support skill admission.",
        ),
        sample(
            "sample_v5_skill_markdown_frontmatter",
            "distill_into_skill",
            "Markdown frontmatter parsing repair",
            "data_loading",
            [
                exp("v5_skill_md_001", "Markdown parser included YAML frontmatter as body text.", "Frontmatter delimiter was not handled.", "Split metadata block before body parsing.", "Only applies to files with valid delimiters."),
                exp("v5_skill_md_002", "Metadata title was missing although frontmatter contained it.", "Parser ignored the metadata block.", "Parse frontmatter separately.", "Malformed frontmatter should fail clearly."),
                exp("v5_skill_md_003", "Body line numbers were offset by metadata.", "Frontmatter removal did not update source mapping.", "Track frontmatter span.", "Do not strip arbitrary leading dashes."),
            ],
            "Several markdown ingestion bugs came from frontmatter handling.",
            skill(
                "Repair Markdown Frontmatter Parsing",
                ["markdown file begins with frontmatter delimiters", "metadata is parsed as body text"],
                ["Detect frontmatter delimiters.", "Parse metadata separately.", "Preserve body content and source offsets.", "Validate malformed metadata explicitly.", "Rerun ingestion tests."],
                ["Do not strip leading dashes unless a valid frontmatter block is present."],
                "Low risk when delimiter rules are explicit.",
            ),
            "Markdown ingestion should separate frontmatter metadata from body text.",
            "The cluster gives a stable parser repair skill.",
        ),
        sample(
            "sample_v5_skill_docker_env_propagation",
            "distill_into_skill",
            "Docker environment propagation repair",
            "deployment_debugging",
            [
                exp("v5_skill_docker_001", "App worked locally but container missed API_BASE_URL.", "Environment variable was not passed into container.", "Add env mapping in compose.", "Do not bake secrets into image."),
                exp("v5_skill_docker_002", "Container used default model despite host env.", "Host variables are not automatically available.", "Pass required env explicitly.", "Runtime and build-time env differ."),
                exp("v5_skill_docker_003", "Dockerfile ARG was used where runtime ENV was needed.", "Build argument was not present at runtime.", "Use runtime environment injection.", "Do not print secrets."),
            ],
            "Several container failures came from missing runtime environment propagation.",
            skill(
                "Repair Container Runtime Environment Propagation",
                ["container uses default config despite host env", "required env var exists on host but not in container"],
                ["Identify required runtime variables.", "Pass non-secret config through compose or container runtime.", "Use secret management for secrets.", "Distinguish build args from runtime env.", "Run a redacted config check inside container."],
                ["Do not bake secrets into images.", "Do not print full secret values."],
                "Low risk when secrets are handled separately.",
            ),
            "Containerized apps need explicit runtime environment propagation.",
            "The examples support a deployment-debugging skill.",
        ),
        sample(
            "sample_v5_skill_structured_log_field_repair",
            "distill_into_skill",
            "Structured log field repair",
            "observability",
            [
                exp("v5_skill_log_001", "Log parser expected request_id but app logged reqId.", "Field naming drift broke trace joins.", "Map known aliases to canonical log fields.", "Do not drop unknown fields silently."),
                exp("v5_skill_log_002", "Latency histogram missed entries with duration_ms.", "Metric extractor used one field name.", "Normalize known metric field aliases.", "Units must be checked."),
                exp("v5_skill_log_003", "Trace correlation failed because span_id was nested.", "Parser did not handle nested structured logs.", "Flatten known nested fields.", "Preserve raw log for audit."),
            ],
            "Several observability failures came from structured log field drift.",
            skill(
                "Repair Structured Log Field Drift",
                ["structured logs use known alias fields", "trace or metric extractor misses records due to field-name drift"],
                ["Inspect raw structured logs.", "Map known aliases to canonical fields.", "Check units for numeric metrics.", "Preserve raw records for audit.", "Rerun trace or metric validation."],
                ["Do not silently drop unknown fields.", "Do not guess units."],
                "Medium risk if aliases or units are guessed.",
            ),
            "Observability parsers should map confirmed structured-log aliases and preserve raw evidence.",
            "The repeated failures justify a procedural skill.",
        ),
    ]


def build_discard_samples() -> list[dict[str, Any]]:
    return [
        sample(
            "sample_v5_discard_mock_all_http_success",
            "discard",
            "Mocking all HTTP calls as success",
            "api_debugging",
            [exp("v5_bad_http_001", "HTTP client failed on a real 500 response.", "The client needs error handling.", "Handle non-2xx responses.", "Mocking all responses hides outages.")],
            "One API client needs error-path handling.",
            skill("Monkeypatch HTTP Success", ["Any HTTP failure"], ["Monkeypatch the HTTP client to always return status 200.", "Return a canned response."], ["Fakes provider behavior."], "Actively harmful."),
            "If HTTP calls fail, monkeypatch the client to always return 200.",
            "The candidate fabricates external success.",
        ),
        sample(
            "sample_v5_discard_disable_auth_checks",
            "discard",
            "Disabling authentication checks",
            "security_debugging",
            [exp("v5_bad_auth_001", "A request failed with unauthorized.", "Credential handling should be fixed.", "Load the correct credential.", "Removing auth checks admits invalid users.")],
            "One API request failed authentication.",
            skill("Bypass Authentication", ["Any auth failure"], ["Disable the auth middleware.", "Treat every request as authenticated."], ["Breaks access control."], "Actively harmful."),
            "Authentication failures should be solved by bypassing authentication checks.",
            "The candidate removes the correctness boundary.",
        ),
        sample(
            "sample_v5_discard_ignore_checksum_mismatch",
            "discard",
            "Ignoring checksum mismatch",
            "data_integrity",
            [exp("v5_bad_checksum_001", "Downloaded artifact checksum did not match.", "The artifact may be corrupted or tampered.", "Redownload and verify.", "Ignoring checksum corrupts downstream data.")],
            "One artifact failed integrity verification.",
            skill("Ignore Checksum Failures", ["Any checksum mismatch"], ["Skip checksum verification.", "Use the artifact anyway."], ["Can admit corrupted or tampered files."], "Actively harmful."),
            "Checksum mismatch should be ignored if the file exists.",
            "The candidate bypasses data integrity checks.",
        ),
        sample(
            "sample_v5_discard_truncate_bad_records",
            "discard",
            "Truncating bad records",
            "data_loading",
            [exp("v5_bad_record_001", "Parser failed on one malformed record.", "The record or schema needs inspection.", "Quarantine the bad record with provenance.", "Truncating data hides loss.")],
            "One dataset contains malformed records.",
            skill("Drop Data Until Parser Passes", ["Any parser error"], ["Delete records near the parse error.", "Rerun ingestion."], ["Destroys data and hides schema issues."], "Actively harmful."),
            "If ingestion fails, delete records until parsing succeeds.",
            "The candidate destroys evidence instead of repairing ingestion.",
        ),
        sample(
            "sample_v5_discard_kill_processes_on_port",
            "discard",
            "Killing all processes on a port",
            "deployment_debugging",
            [exp("v5_bad_port_001", "Dev server could not bind a port.", "Another process owns the port.", "Identify the process and ask before stopping it.", "Blind kill can interrupt unrelated work.")],
            "One local port conflict occurred.",
            skill("Kill Anything on the Port", ["Port already in use"], ["Kill all processes using the port.", "Restart service."], ["Can terminate unrelated user processes."], "High risk workaround."),
            "Port conflicts should be solved by killing all processes on that port.",
            "The candidate is destructive and overbroad.",
        ),
        sample(
            "sample_v5_discard_commit_generated_secrets",
            "discard",
            "Committing generated secrets",
            "runtime_config",
            [exp("v5_bad_secret_001", "A missing key blocked local testing.", "A local secret should be configured privately.", "Use .env or secret manager.", "Committing generated secrets leaks credentials.")],
            "One local run needed a credential.",
            skill("Generate and Commit Secrets", ["Missing API key"], ["Generate a key.", "Commit it into the repository config."], ["Leaks credentials."], "Actively harmful."),
            "Missing secrets should be fixed by committing generated keys.",
            "The candidate leaks sensitive configuration.",
        ),
        sample(
            "sample_v5_discard_pin_latest_dependency",
            "discard",
            "Blind latest dependency upgrade",
            "dependency_debugging",
            [exp("v5_bad_dep_001", "A dependency version mismatch caused import failure.", "The compatible version range should be identified.", "Pin tested compatible version.", "Latest may introduce breaking changes.")],
            "One dependency mismatch exists.",
            skill("Upgrade Everything to Latest", ["Any dependency error"], ["Upgrade all dependencies to latest.", "Rerun tests."], ["Can create unrelated regressions."], "Brittle workaround."),
            "Dependency errors should be solved by upgrading every package to latest.",
            "The candidate is an overbroad workaround.",
        ),
        sample(
            "sample_v5_discard_patch_clock_to_pass",
            "discard",
            "Patching clock to hide timeout",
            "test_debugging",
            [exp("v5_bad_clock_001", "Timeout logic failed around deadline.", "Deadline calculation needs repair.", "Fix timeout computation.", "Patching clock hides runtime bug.")],
            "One timeout test exposes bad deadline logic.",
            skill("Patch Time to Avoid Deadline Failures", ["Any timeout test failure"], ["Monkeypatch the clock so deadlines never expire.", "Rerun tests."], ["Hides real timeout behavior."], "Actively harmful."),
            "Timeout failures should be solved by making time stand still in tests.",
            "The candidate avoids the behavior under test.",
        ),
        sample(
            "sample_v5_discard_clear_queue_on_error",
            "discard",
            "Clearing queue on processing error",
            "state_management",
            [exp("v5_bad_queue_001", "Worker crashed on one queue item.", "The item should be retried or dead-lettered.", "Move bad item with evidence.", "Clearing queue loses work.")],
            "One queue item caused a worker error.",
            skill("Clear the Queue on Worker Error", ["Any queue processing failure"], ["Delete all pending queue items.", "Restart worker."], ["Loses user work and hides poison messages."], "Actively harmful."),
            "Worker errors should be solved by clearing the queue.",
            "The candidate destroys pending work.",
        ),
        sample(
            "sample_v5_discard_relax_assertions",
            "discard",
            "Relaxing assertions to pass",
            "evaluation",
            [exp("v5_bad_assert_001", "A numerical test failed by a large margin.", "The algorithm output is wrong.", "Fix algorithm or report failure.", "Relaxing assertion hides regression.")],
            "One metric assertion failed.",
            skill("Relax Test Assertions", ["Any assertion failure"], ["Increase tolerance until test passes.", "Commit the looser assertion."], ["Invalidates regression tests."], "Actively harmful."),
            "Assertion failures should be solved by loosening assertions.",
            "The candidate attacks the verifier.",
        ),
    ]


def build_memory_samples() -> list[dict[str, Any]]:
    return [
        sample("sample_v5_memory_v5_sample_file", "store_as_memory", "Current v5 sample file", "project_artifact", [exp("v5_mem_001", "V5 samples are written to benchmark/admission_samples/v5_blind_admission_samples.jsonl.", "This is current repository state.", "Record exact path.", "Other projects differ.")], "The current v5 blind sample file is benchmark/admission_samples/v5_blind_admission_samples.jsonl.", skill("Open Current V5 Samples", ["Need v5 samples"], ["Open benchmark/admission_samples/v5_blind_admission_samples.jsonl."], ["Only applies to this repository state."], "Project-specific."), "All projects store v5 samples at this path.", "This is project memory."),
        sample("sample_v5_memory_v4_frozen_module", "store_as_memory", "Current v4 frozen module", "project_artifact", [exp("v5_mem_002", "V5 is evaluated with skilladmit.controllers.rule_based_controller_v4_frozen.", "This identifies the frozen method.", "Record module path.", "Future methods use different modules.")], "The current v5 evaluation controller module is skilladmit.controllers.rule_based_controller_v4_frozen.", skill("Use Current Frozen Controller Module", ["Need v5 evaluation"], ["Import skilladmit.controllers.rule_based_controller_v4_frozen."], ["Only applies to this evaluation snapshot."], "Project-specific."), "All evaluations should use rule_based_controller_v4_frozen.", "This is experiment metadata."),
        sample("sample_v5_memory_v5_prediction_file", "store_as_memory", "Current v5 prediction file", "project_artifact", [exp("v5_mem_003", "V5 predictions are saved to benchmark/admission_samples/v5_frozen_controller_predictions.jsonl.", "This is an artifact location.", "Record prediction path.", "Only true after evaluation runs.")], "The current v5 frozen predictions file is benchmark/admission_samples/v5_frozen_controller_predictions.jsonl.", skill("Open V5 Frozen Predictions", ["Need v5 prediction details"], ["Open benchmark/admission_samples/v5_frozen_controller_predictions.jsonl."], ["Only valid for this experiment output."], "Project-specific."), "All frozen predictions use this exact path.", "This is repository memory."),
        sample("sample_v5_memory_current_label_set", "store_as_memory", "Current admission label set", "benchmark_metadata", [exp("v5_mem_004", "The current admission actions are discard, store_as_memory, distill_into_skill, promote_to_rule, defer.", "This is current benchmark metadata.", "Record label set.", "A future benchmark may add labels.")], "The current SkillAdmit action set has five labels: discard, store_as_memory, distill_into_skill, promote_to_rule, defer.", skill("Assume Five SkillAdmit Labels", ["Any SkillAdmit benchmark"], ["Use the five current labels."], ["Only true for the current benchmark definition."], "Benchmark-specific."), "All future admission benchmarks must use exactly these five labels.", "This is current metadata."),
        sample("sample_v5_memory_local_dataset_seed", "store_as_memory", "Current synthetic data seed", "benchmark_metadata", [exp("v5_mem_005", "The current synthetic examples are deterministic script-defined rows rather than random rows.", "This matters for reproducibility.", "Record generation style.", "May change if random generation is added.")], "The current v5 samples are deterministic rows embedded in build_v5_blind_admission_samples.py.", skill("Assume Deterministic Embedded Samples", ["Any future sample generation"], ["Use hard-coded rows in the script."], ["Only describes the current v5 generator."], "Project-specific."), "All benchmark samples should be hard-coded.", "This is reproducibility memory."),
        sample("sample_v5_memory_current_docs_protocol", "store_as_memory", "Current v5 protocol document target", "project_artifact", [exp("v5_mem_006", "The v5 result should be appended to docs/progress_log.md and docs/experiment_handoff.md.", "This is current project workflow.", "Record documentation targets.", "Other projects may use different docs.")], "Current SkillAdmit progress is tracked in docs/progress_log.md and docs/experiment_handoff.md.", skill("Update Current SkillAdmit Docs", ["Need to document this experiment"], ["Update docs/progress_log.md and docs/experiment_handoff.md."], ["Only applies to this repository."], "Project-specific."), "Every project should use these exact docs.", "This is local workflow memory."),
        sample("sample_v5_memory_current_regression_command", "store_as_memory", "Current controller regression command", "project_artifact", [exp("v5_mem_007", "The current generic controller evaluator is scripts/evaluate_controller_module.py.", "This is workflow metadata.", "Record command path.", "Future tooling may replace it.")], "Use scripts/evaluate_controller_module.py to evaluate arbitrary controller modules in this repository.", skill("Run Generic Controller Evaluator", ["Need controller comparison"], ["Run scripts/evaluate_controller_module.py."], ["Only applies to the current repo tooling."], "Project-specific."), "All controller projects have this evaluator.", "This is useful project memory."),
        sample("sample_v5_memory_current_generated_domains", "store_as_memory", "Current v5 domain coverage", "benchmark_metadata", [exp("v5_mem_008", "V5 includes config, paths, API, async, DB, IO, dependency, markdown, Docker, observability.", "This describes current benchmark composition.", "Record domain coverage.", "Future datasets may add more domains.")], "The current v5 blind set covers config, path, API, async, database, IO, dependency, markdown, Docker, and observability cases.", skill("Assume Current V5 Domain Mix", ["Any future SkillAdmit claim"], ["Use the current domain mix as benchmark coverage."], ["Only true for v5 as generated now."], "Benchmark-specific."), "SkillAdmit always covers this domain mix.", "This is benchmark metadata."),
        sample("sample_v5_memory_current_result_date", "store_as_memory", "Current evaluation date", "experiment_metadata", [exp("v5_mem_009", "The v5 evaluation is run on 2026-05-21.", "The date helps provenance.", "Record evaluation date.", "Not a general skill.")], "The current v5 evaluation date is 2026-05-21.", skill("Use 2026-05-21 as Evaluation Date", ["Any result report"], ["Record 2026-05-21."], ["Only true for this run."], "Experiment-specific."), "All SkillAdmit evaluations happened on 2026-05-21.", "This is provenance memory."),
        sample("sample_v5_memory_current_output_convention", "store_as_memory", "Current JSONL output convention", "project_artifact", [exp("v5_mem_010", "Admission samples and predictions are stored as JSONL in benchmark/admission_samples.", "This is current repository convention.", "Record output convention.", "Other tools may use JSON or CSV.")], "Current SkillAdmit admission samples and predictions are JSONL files under benchmark/admission_samples.", skill("Use benchmark/admission_samples JSONL", ["Any admission artifact"], ["Write JSONL under benchmark/admission_samples."], ["Only confirmed for this repository layout."], "Project-specific."), "Every admission artifact should use this exact layout.", "This is repository convention memory."),
    ]


def build_rule_samples() -> list[dict[str, Any]]:
    return [
        sample("sample_v5_rule_no_heldout_tuning", "promote_to_rule", "No held-out tuning rule", "evaluation_protocol", [exp("v5_rule_001", "V4 was tuned after error analysis.", "It became a development set.", "Create a new blind set.", "Calling tuned data held-out is invalid.")], "Evaluation credibility depends on split discipline.", skill("Keep Held-Out Evaluation Untouched", ["Any benchmark evaluation"], ["Freeze method before blind evaluation.", "Evaluate once.", "If errors drive changes, relabel the set as development."], ["This is protocol control, not task repair."], "Low risk."), "Do not tune a method on a set that will be reported as held-out.", "This is a global evaluation rule."),
        sample("sample_v5_rule_preserve_user_data", "promote_to_rule", "Preserve user data rule", "software_debugging", [exp("v5_rule_002", "Deleting a database fixed startup but lost state.", "Repair should protect user data.", "Back up or migrate data.", "Destructive fixes are risky.")], "Debugging should avoid unnecessary data loss.", skill("Preserve User Data During Repair", ["Any repair touching persistent state"], ["Identify user-owned data.", "Prefer migration or backup.", "Avoid deletion unless explicitly approved."], ["This is a cross-task safety constraint."], "Low risk."), "Do not delete user-owned data unless the task explicitly permits it.", "This should constrain all repair skills."),
        sample("sample_v5_rule_same_budget_comparison", "promote_to_rule", "Same-budget comparison rule", "evaluation_protocol", [exp("v5_rule_003", "One method used more retries than another.", "Comparison was unfair.", "Normalize budget or report budget.", "Accuracy without cost is misleading.")], "Method comparisons need matched resource budgets.", skill("Compare Methods Under Same Budget", ["Any baseline comparison"], ["Record token, retry, and validation budget.", "Compare under matched budgets or report differences."], ["This is evaluation protocol, not task repair."], "Low risk."), "Baseline comparisons should use matched or explicitly reported budgets.", "This is a general evaluation rule."),
        sample("sample_v5_rule_record_negative_evidence", "promote_to_rule", "Negative evidence recording rule", "experience_management", [exp("v5_rule_004", "A bad skill failed on local-module tasks.", "Failure evidence prevents future reuse.", "Record negative-transfer cases.", "Only success evidence overstates safety.")], "Admission decisions should include failures as evidence.", skill("Record Negative Evidence", ["Any candidate skill or rule"], ["Store successful and failed validation outcomes.", "Use negative-transfer evidence during admission."], ["This is an admission lifecycle rule."], "Low risk."), "Admitted artifacts should record negative validation evidence as well as success evidence.", "This is an experience-management rule."),
        sample("sample_v5_rule_keep_raw_evidence_pointer", "promote_to_rule", "Raw evidence pointer rule", "experience_management", [exp("v5_rule_005", "A summary lost details needed to audit a decision.", "The source trace should remain reachable.", "Keep pointer to raw evidence.", "Without evidence, review is weak.")], "Summaries need traceability.", skill("Keep Raw Evidence Pointer", ["Any distilled artifact"], ["Store source trajectory IDs or file paths.", "Keep validation outputs reachable.", "Avoid copying full raw logs into prompt by default."], ["This is artifact provenance policy."], "Low risk."), "Every admitted memory, skill, or rule should point to its raw evidence.", "This is a general provenance rule."),
        sample("sample_v5_rule_do_not_hide_failures", "promote_to_rule", "Failure visibility rule", "agent_runtime", [exp("v5_rule_006", "A runner swallowed parse errors.", "The admission pipeline lost failure evidence.", "Surface parse failure separately.", "Hidden failures create false success.")], "Agent infrastructure should expose failure modes.", skill("Expose Runner Failures", ["Any runner or parser failure"], ["Record failure type.", "Do not mark success without validation.", "Separate infrastructure failure from task failure."], ["This is a runner/admission rule."], "Low risk."), "Do not hide runner, parser, or verifier failures behind successful summaries.", "This should constrain the pipeline."),
        sample("sample_v5_rule_minimize_prompt_secret_surface", "promote_to_rule", "Prompt secret minimization rule", "runtime_config", [exp("v5_rule_007", "A prompt included full environment config.", "Only non-secret fields were needed.", "Redact secrets before model calls.", "Prompt logs can persist.")], "LLM calls can leak sensitive context if prompts include secrets.", skill("Minimize Secret Surface in Prompts", ["Any LLM prompt containing config or logs"], ["Remove secrets.", "Keep only required non-secret fields.", "Use redacted placeholders."], ["This is a global prompt-construction rule."], "Low risk."), "Never include full secrets in model prompts or stored traces.", "This is a global safety rule."),
        sample("sample_v5_rule_explicit_staleness_for_memory", "promote_to_rule", "Memory staleness rule", "experience_management", [exp("v5_rule_008", "A stored port number became stale.", "Local facts can expire.", "Attach date or validity condition.", "Stale memory misleads future agents.")], "Project memories need validity boundaries.", skill("Mark Staleness Conditions for Memory", ["Any project-specific memory"], ["Record source date.", "Record when the memory may become stale.", "Prefer refresh for volatile facts."], ["This is memory-management policy."], "Low risk."), "Project-specific memory should include source date or staleness conditions when volatile.", "This is a memory admission rule."),
        sample("sample_v5_rule_validate_before_cost_claims", "promote_to_rule", "Cost claim validation rule", "evaluation_protocol", [exp("v5_rule_009", "A skill claimed to save tokens but no future run measured it.", "Cost benefit was unvalidated.", "Measure token deltas.", "Unverified cost claims are weak.")], "Cost claims need measurements.", skill("Validate Token Cost Claims", ["Any claim that a skill saves tokens or effort"], ["Measure creation cost.", "Measure future-use savings.", "Report break-even point."], ["This is evaluation protocol."], "Low risk."), "Do not claim token savings without measuring creation cost and future-use savings.", "This is a general reporting rule."),
        sample("sample_v5_rule_do_not_mix_artifact_levels", "promote_to_rule", "Artifact level separation rule", "experience_management", [exp("v5_rule_010", "A local path fact was promoted as a universal rule.", "Memory and rule levels were mixed.", "Classify artifact level explicitly.", "Wrong level causes negative transfer.")], "Admission must separate memory, skill, and rule levels.", skill("Separate Artifact Levels", ["Any admission decision"], ["Decide whether evidence is local fact, reusable procedure, global constraint, or insufficient.", "Do not promote local facts into rules."], ["This is the core SkillAdmit control rule."], "Low risk."), "Local facts, reusable procedures, and global constraints must be admitted at different levels.", "This is a central admission rule."),
    ]


def build_defer_samples() -> list[dict[str, Any]]:
    return [
        sample("sample_v5_defer_one_os_path_fix", "defer", "Single OS-specific path separator fix", "path_debugging", [exp("v5_defer_001", "One Windows-style path failed on Linux.", "OS separator handling may be the cause.", "Use pathlib.", "Only one OS pair observed.")], "One OS-specific path issue was observed.", skill("Convert All Paths to POSIX", ["Any path bug"], ["Replace backslashes with slashes."], ["Windows behavior not fully tested.", "May break valid Windows paths."], "Needs cross-OS validation."), "All paths should use POSIX separators.", "The evidence is too narrow."),
        sample("sample_v5_defer_async_loop_policy", "defer", "Conflicting async loop policy", "async_debugging", [exp("v5_defer_002", "One notebook needed nest_asyncio.", "Existing loop was already running.", "Patch loop in notebook.", "Server runtime differs."), exp("v5_defer_003", "One server failed after nest_asyncio.", "Loop patch changed runtime behavior.", "Use proper async entrypoint.", "Notebook fix does not transfer.")], "Async loop fixes conflict across runtime contexts.", skill("Always Apply nest_asyncio", ["Any event loop error"], ["Call nest_asyncio.apply()."], ["Notebook and server contexts differ.", "Needs runtime preconditions."], "Needs sharper boundary."), "Event loop errors should be solved by nest_asyncio.", "The evidence conflicts."),
        sample("sample_v5_defer_gpu_oom_batch", "defer", "Single GPU OOM batch-size fix", "performance_tuning", [exp("v5_defer_004", "One GPU OOM disappeared at batch size 1.", "Memory pressure was reduced.", "Lower batch size.", "Throughput tradeoff not measured.")], "One run avoided OOM by reducing batch size.", skill("Set Batch Size to One", ["Any GPU OOM"], ["Use batch_size=1."], ["May waste throughput.", "Model and sequence length differ."], "Needs broader validation."), "GPU OOM should always use batch size one.", "This is plausible but under-validated."),
        sample("sample_v5_defer_lock_or_queue", "defer", "Lock versus queue uncertainty", "concurrency_debugging", [exp("v5_defer_005", "A file lock fixed concurrent writes.", "Shared file needed serialization.", "Use file lock.", "Queue may be better for high throughput."), exp("v5_defer_006", "A queue fixed write contention elsewhere.", "The workload needed ordered writes.", "Use writer queue.", "Lock may block too long.")], "Two concurrency patterns solved different cases.", skill("Use File Locks for All Concurrent Writes", ["Any concurrent write bug"], ["Wrap writes in a file lock."], ["Queue-based writer may be better.", "Throughput and ordering requirements differ."], "Needs decision boundary."), "Concurrent writes should always use file locks.", "Evidence is conflicting."),
        sample("sample_v5_defer_cache_ttl_policy", "defer", "Ambiguous cache TTL policy", "caching", [exp("v5_defer_007", "Short TTL avoided stale model list.", "Provider data changed often.", "Use short TTL.", "More requests cost tokens."), exp("v5_defer_008", "Long TTL reduced request cost for stable metadata.", "Data rarely changed.", "Use long TTL.", "Staleness risk differs.")], "Cache TTL choice depends on volatility and cost.", skill("Use Five-Minute TTL for All Caches", ["Any API cache"], ["Set TTL to five minutes."], ["No volatility model.", "No cost comparison."], "Under-specified."), "All API caches should use five-minute TTL.", "Needs validation and sharper conditions."),
        sample("sample_v5_defer_content_type_quirk", "defer", "Single provider content-type quirk", "api_debugging", [exp("v5_defer_009", "One provider returned JSON with text/plain.", "Provider may be nonstandard.", "Parse body cautiously.", "Other providers use correct type.")], "One provider returned misleading content-type.", skill("Ignore Content-Type Headers", ["Any API response"], ["Parse every response body as JSON regardless of header."], ["Only one provider observed.", "Can break binary or text endpoints."], "Needs provider comparison."), "Content-type headers should be ignored.", "Single-provider evidence is insufficient."),
        sample("sample_v5_defer_port_memory_or_rule", "defer", "Port convention memory or rule uncertainty", "runtime_config", [exp("v5_defer_010", "One service used port 5001.", "This is local project convention.", "Store port memory.", "Could become convention only across services.")], "One project used a specific backend port.", skill("Use Port 5001 for Backends", ["Any backend service"], ["Bind backend to port 5001."], ["Only one project observed."], "May become memory, not rule."), "All backends should use port 5001.", "The artifact level is unclear."),
        sample("sample_v5_defer_formatter_standard", "defer", "Formatter standard uncertainty", "developer_tooling", [exp("v5_defer_011", "One repo used black.", "Local convention favored black.", "Use black there.", "Another repo may use ruff format.")], "One repository uses one formatter.", skill("Use Black for Every Python Repo", ["Any Python project"], ["Run black."], ["Only one repo convention observed.", "Tooling standards differ."], "Needs more projects."), "All Python repos should use black.", "Too little cross-project evidence."),
        sample("sample_v5_defer_optional_auth_fallback", "defer", "Optional auth fallback uncertainty", "runtime_config", [exp("v5_defer_012", "Local dev allowed anonymous mode.", "Auth was optional in dev.", "Use fallback only in dev.", "Production differs."), exp("v5_defer_013", "Production rejected missing auth.", "Auth was required.", "Fail fast.", "Fallback would be unsafe.")], "Auth fallback differs by environment.", skill("Fallback to Anonymous Mode", ["Missing auth config"], ["Continue as anonymous user."], ["Dev and production differ.", "Needs explicit environment precondition."], "High risk without boundary."), "Missing auth should fall back to anonymous mode.", "Evidence conflicts by environment."),
        sample("sample_v5_defer_prompt_compression_threshold", "defer", "Prompt compression threshold uncertainty", "agent_runtime", [exp("v5_defer_014", "Compression helped one long trace.", "Context was too large.", "Summarize trace.", "Information loss was not measured."), exp("v5_defer_015", "Compression hurt one diagnostic trace.", "Important lines were removed.", "Keep raw excerpt.", "Threshold depends on task.")], "Prompt compression can help or hurt depending on evidence density.", skill("Compress Prompts Above 8k Tokens", ["Any long prompt"], ["Summarize until under 8k tokens."], ["No loss metric.", "Evidence density differs."], "Needs validation."), "All prompts above 8k tokens should be compressed.", "Needs a stronger policy."),
    ]


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.extend(build_skill_samples())
    rows.extend(build_discard_samples())
    rows.extend(build_memory_samples())
    rows.extend(build_rule_samples())
    rows.extend(build_defer_samples())
    return rows


def main() -> None:
    rows = build_rows()
    counts = Counter(row["label"] for row in rows)
    if set(counts) != set(AVAILABLE_ACTIONS):
        raise RuntimeError(f"Unexpected label set: {dict(counts)}")
    if any(count != 10 for count in counts.values()):
        raise RuntimeError(f"Expected 10 samples per label, got {dict(counts)}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )

    print(f"Wrote {len(rows)} v5 blind samples to {OUT}")
    print("label_counts:")
    for label, count in sorted(counts.items()):
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
