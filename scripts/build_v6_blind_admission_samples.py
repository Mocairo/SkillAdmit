#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark" / "admission_samples" / "v6_blind_admission_samples.jsonl"

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
        "source": "v6_blind_curated_after_v5_freeze",
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
            "sample_v6_skill_k8s_configmap_mount",
            "distill_into_skill",
            "Kubernetes ConfigMap mount repair",
            "deployment_debugging",
            [
                exp("v6_skill_k8s_001", "Pod started but app config file was missing.", "ConfigMap was mounted at a different path than the app expected.", "Align volumeMount mountPath with app config path.", "Do not bake mutable config into the image."),
                exp("v6_skill_k8s_002", "Container saw an empty directory where config should exist.", "Volume mount shadowed the image directory.", "Mount the specific file with subPath.", "subPath updates require pod restart."),
                exp("v6_skill_k8s_003", "Deployment used env var but app read a file.", "Config delivery mode mismatched app expectations.", "Choose env var or file mount consistently.", "Secrets need secret volumes, not ConfigMaps."),
            ],
            "Several deployment failures came from Kubernetes config delivery mismatches.",
            skill(
                "Repair Kubernetes Config Mount Mismatches",
                ["pod runs but expected config file or env var is missing", "ConfigMap path does not match app configuration loader"],
                ["Inspect the app's expected config source.", "Inspect ConfigMap keys and volume mounts.", "Align mountPath or env mapping.", "Use subPath for single-file mounts when appropriate.", "Restart and verify inside the pod."],
                ["Do not put secrets into ConfigMaps.", "Do not bake environment-specific config into the image."],
                "Medium risk because mount semantics can shadow image files.",
            ),
            "Kubernetes config repairs should align the app's config loader with the declared ConfigMap or Secret delivery mode.",
            "The cluster shows a reusable deployment repair procedure.",
        ),
        sample(
            "sample_v6_skill_parquet_schema_evolution",
            "distill_into_skill",
            "Parquet schema evolution repair",
            "data_loading",
            [
                exp("v6_skill_parquet_001", "Reader failed after a nullable column was added.", "The reader expected an older schema.", "Project missing columns with defaults and validate types.", "Do not silently coerce incompatible types."),
                exp("v6_skill_parquet_002", "Batch job failed when int column became long.", "Schema evolution changed physical type.", "Add explicit type normalization.", "Range and precision must be checked."),
                exp("v6_skill_parquet_003", "Partition files had different optional columns.", "Dataset schema needed unification.", "Unify schema before loading partitions.", "Unknown columns still need review."),
            ],
            "Several Parquet ingestion failures came from controlled schema evolution.",
            skill(
                "Repair Parquet Schema Evolution Loads",
                ["Parquet partitions or versions have compatible but non-identical schemas", "new nullable columns or widened numeric types break readers"],
                ["Inspect file schemas.", "Unify compatible schemas explicitly.", "Fill missing nullable columns with defaults.", "Normalize safe type widenings.", "Validate incompatible changes loudly."],
                ["Do not coerce incompatible semantic types silently."],
                "Medium risk when type changes are not audited.",
            ),
            "Parquet readers should handle compatible schema evolution explicitly and reject incompatible changes.",
            "The repeated failures support a data-loading skill.",
        ),
        sample(
            "sample_v6_skill_embedding_dimension_check",
            "distill_into_skill",
            "Embedding dimension mismatch repair",
            "retrieval_debugging",
            [
                exp("v6_skill_vec_001", "Vector index rejected 1024-dimensional embeddings.", "The index was built for 768-dimensional vectors.", "Rebuild index or use the matching embedding model.", "Do not pad vectors to hide mismatch."),
                exp("v6_skill_vec_002", "Search returned bad results after model swap.", "Stored vectors and query vectors came from different models.", "Version the embedding model with the index.", "Mixed vector spaces are invalid."),
                exp("v6_skill_vec_003", "Retriever crashed on dimension assertion.", "Index metadata and query vector length differed.", "Check metadata before querying.", "Do not disable dimension checks."),
            ],
            "Several retrieval bugs came from mismatched embedding models and vector dimensions.",
            skill(
                "Repair Embedding Dimension Mismatches",
                ["vector index dimension differs from query embedding dimension", "embedding model changed after index creation"],
                ["Read index dimension metadata.", "Read current embedding model output dimension.", "Use a matching model or rebuild the index.", "Version model identity with vector artifacts.", "Rerun retrieval validation."],
                ["Do not pad, truncate, or disable dimension checks as a shortcut."],
                "Low risk when vector artifacts are rebuilt consistently.",
            ),
            "Embedding indexes and query encoders must share the same vector space and dimension.",
            "The cluster supports a reusable retrieval-debugging skill.",
        ),
        sample(
            "sample_v6_skill_cron_timezone",
            "distill_into_skill",
            "Cron timezone scheduling repair",
            "scheduling_debugging",
            [
                exp("v6_skill_cron_001", "Daily job fired at UTC midnight instead of local morning.", "Scheduler timezone differed from business timezone.", "Set scheduler timezone explicitly.", "Do not assume server localtime."),
                exp("v6_skill_cron_002", "DST transition skipped one expected run.", "Timezone-aware schedule handling was missing.", "Use timezone-aware cron library.", "DST rules must be tested."),
                exp("v6_skill_cron_003", "Container schedule differed from host schedule.", "Container timezone was UTC.", "Configure timezone or convert schedule deliberately.", "Changing host timezone is too broad."),
            ],
            "Several scheduled-job bugs came from implicit timezone assumptions.",
            skill(
                "Repair Timezone-Aware Cron Scheduling",
                ["cron or scheduled job fires at the wrong local time", "job behavior changes around DST or container timezone"],
                ["Identify the required business timezone.", "Configure scheduler timezone explicitly.", "Test UTC/local conversion.", "Add DST boundary tests.", "Avoid relying on host localtime."],
                ["Do not guess the business timezone."],
                "Medium risk if business timezone is unspecified.",
            ),
            "Scheduled jobs should declare their intended timezone and test DST boundaries.",
            "The evidence supports a scheduling repair skill.",
        ),
        sample(
            "sample_v6_skill_cors_preflight",
            "distill_into_skill",
            "CORS preflight repair",
            "web_api_debugging",
            [
                exp("v6_skill_cors_001", "Browser blocked POST because OPTIONS returned 404.", "Preflight request was not handled.", "Add OPTIONS handler with allowed methods.", "Do not allow every origin blindly."),
                exp("v6_skill_cors_002", "Authorization header triggered failed preflight.", "Allowed headers omitted Authorization.", "Allow the required header for trusted origins.", "Credentials require exact origin."),
                exp("v6_skill_cors_003", "Frontend worked with curl but failed in browser.", "Browser enforced CORS preflight.", "Configure CORS response for the browser path.", "Server-to-server calls do not prove browser success."),
            ],
            "Several browser API failures came from missing or incomplete CORS preflight handling.",
            skill(
                "Repair Browser CORS Preflight Handling",
                ["browser request fails while curl succeeds", "OPTIONS preflight fails before POST or Authorization request"],
                ["Reproduce the browser preflight.", "Allow required methods and headers.", "Restrict allowed origins deliberately.", "Handle credentials rules correctly.", "Retest from the browser path."],
                ["Do not use wildcard origins with credentials.", "Do not disable browser security as a fix."],
                "Medium risk because permissive CORS is unsafe.",
            ),
            "Browser API debugging should distinguish CORS preflight from backend route failure.",
            "The cluster supports skill admission.",
        ),
        sample(
            "sample_v6_skill_protobuf_oneof",
            "distill_into_skill",
            "Protobuf oneof parsing repair",
            "serialization_debugging",
            [
                exp("v6_skill_proto_001", "Parser treated unset oneof field as empty string.", "Presence semantics were ignored.", "Use WhichOneof before reading.", "Default values do not imply presence."),
                exp("v6_skill_proto_002", "New message variant was dropped during conversion.", "oneof branch was not handled.", "Add branch-specific conversion.", "Unknown variants should fail or preserve raw payload."),
                exp("v6_skill_proto_003", "JSON conversion lost which field was set.", "The adapter flattened oneof incorrectly.", "Preserve active field identity.", "Do not infer branch from default value."),
            ],
            "Several serialization failures came from ignoring Protobuf oneof presence semantics.",
            skill(
                "Repair Protobuf Oneof Handling",
                ["Protobuf oneof field is parsed incorrectly", "default value is confused with active oneof branch"],
                ["Check active oneof branch explicitly.", "Handle each known branch.", "Preserve unknown variants or fail clearly.", "Test default-value cases.", "Validate JSON adapters preserve presence."],
                ["Do not infer oneof presence from default scalar values."],
                "Low risk when schema branches are explicit.",
            ),
            "Protobuf oneof adapters must preserve active-field identity.",
            "The repeated failures justify a serialization skill.",
        ),
        sample(
            "sample_v6_skill_git_lfs_pointer",
            "distill_into_skill",
            "Git LFS pointer repair",
            "data_setup",
            [
                exp("v6_skill_lfs_001", "Image loader read a small text pointer file.", "Git LFS content was not fetched.", "Run git lfs pull or document dataset fetch.", "Do not treat pointer as real data."),
                exp("v6_skill_lfs_002", "Model checkpoint file contained LFS pointer text.", "Large artifact was missing.", "Fetch LFS artifact before loading.", "Do not commit expanded artifact accidentally."),
                exp("v6_skill_lfs_003", "Checksum failed because file was an LFS pointer.", "The expected binary was absent.", "Check pointer header and fetch content.", "Offline setups need clear error."),
            ],
            "Several data setup failures came from Git LFS pointer files being used as real artifacts.",
            skill(
                "Repair Git LFS Pointer Artifacts",
                ["large data or model file contains Git LFS pointer text", "loader receives a tiny text file instead of expected binary"],
                ["Inspect the file header.", "Confirm it is a Git LFS pointer.", "Fetch LFS content or report missing artifact.", "Validate file size/checksum.", "Document offline setup requirements."],
                ["Do not parse pointer text as data.", "Do not commit large fetched artifacts accidentally."],
                "Low risk when pointer header is confirmed.",
            ),
            "Large artifacts tracked by Git LFS must be fetched before loading.",
            "The cluster supports skill admission.",
        ),
        sample(
            "sample_v6_skill_redis_ttl",
            "distill_into_skill",
            "Redis TTL preservation repair",
            "cache_debugging",
            [
                exp("v6_skill_redis_001", "Updating a Redis value removed its expiration.", "SET without options cleared TTL.", "Use SET with keep-ttl behavior or reapply TTL.", "Do not make keys permanent accidentally."),
                exp("v6_skill_redis_002", "Session keys never expired after refresh.", "Refresh path overwrote keys without TTL.", "Preserve or reset intended TTL.", "Security-sensitive sessions need explicit expiry."),
                exp("v6_skill_redis_003", "Cache grew unbounded after writes.", "TTL was lost on update.", "Check TTL before and after update.", "Persistent keys may be intentional for some namespaces."),
            ],
            "Several cache bugs came from Redis updates dropping expiration metadata.",
            skill(
                "Repair Redis TTL Loss on Update",
                ["Redis key loses expiration after update", "session or cache key becomes persistent unexpectedly"],
                ["Inspect update command.", "Check current TTL semantics.", "Use keep-ttl or explicitly reapply intended TTL.", "Validate TTL after update.", "Respect namespaces that should be persistent."],
                ["Do not assign TTL to keys that are intentionally persistent."],
                "Medium risk when key lifecycle is unclear.",
            ),
            "Redis update paths should preserve intended expiration semantics.",
            "The repeated bug pattern supports a cache repair skill.",
        ),
        sample(
            "sample_v6_skill_multiline_regex",
            "distill_into_skill",
            "Multiline regex parsing repair",
            "text_processing",
            [
                exp("v6_skill_regex_001", "Parser failed when stack trace spanned multiple lines.", "Regex did not use multiline/dotall semantics.", "Use explicit flags or structured parser.", "Do not make pattern overly greedy."),
                exp("v6_skill_regex_002", "Log block extraction stopped at first newline.", "The pattern assumed single-line records.", "Handle multiline blocks deliberately.", "Boundary markers must be tested."),
                exp("v6_skill_regex_003", "Greedy multiline pattern swallowed two records.", "Fix needed non-greedy boundary.", "Use explicit start/end delimiters.", "Regex should not replace real parser if format is complex."),
            ],
            "Several text parsing failures came from implicit single-line regex assumptions.",
            skill(
                "Repair Multiline Regex Parsing",
                ["parser fails on multiline log or stack-trace blocks", "regex stops at first newline or greedily spans records"],
                ["Identify record boundaries.", "Use multiline/dotall flags only where needed.", "Prefer non-greedy patterns with explicit delimiters.", "Add tests with adjacent records.", "Consider structured parsing for complex formats."],
                ["Do not use a broad greedy pattern without boundary tests."],
                "Medium risk because regex can overmatch.",
            ),
            "Multiline text parsers should make newline and boundary semantics explicit.",
            "The cluster supports a reusable parser skill.",
        ),
        sample(
            "sample_v6_skill_multipart_boundary",
            "distill_into_skill",
            "Multipart upload boundary repair",
            "api_debugging",
            [
                exp("v6_skill_upload_001", "Upload failed because Content-Type lacked boundary.", "Client manually set multipart header.", "Let the HTTP library set Content-Type.", "Do not hardcode boundary."),
                exp("v6_skill_upload_002", "Server could not parse uploaded file.", "Boundary and body encoding mismatched.", "Pass files through the library multipart API.", "Streaming uploads need special handling."),
                exp("v6_skill_upload_003", "Curl upload worked but SDK upload failed.", "SDK overwritten headers incorrectly.", "Remove manual multipart header.", "Auth headers still need preserving."),
            ],
            "Several upload failures came from incorrect multipart boundary handling.",
            skill(
                "Repair Multipart Upload Boundary Handling",
                ["multipart upload fails with missing or invalid boundary", "manual Content-Type header conflicts with HTTP library body encoding"],
                ["Use the HTTP client's multipart file API.", "Do not manually set multipart Content-Type boundary.", "Preserve auth headers.", "Retest with server-side parser.", "Handle streaming files deliberately."],
                ["Do not hardcode a boundary string."],
                "Low risk when delegated to the HTTP library.",
            ),
            "Multipart clients should let the HTTP library generate boundary-compatible headers.",
            "The repeated upload failures support skill admission.",
        ),
    ]


def build_discard_samples() -> list[dict[str, Any]]:
    return [
        sample("sample_v6_discard_allow_all_cors_credentials", "discard", "Permissive CORS with credentials", "web_security", [exp("v6_bad_cors_001", "Browser preflight failed for one trusted frontend.", "CORS should allow the trusted origin.", "Configure exact allowed origin.", "Wildcard with credentials is unsafe.")], "One browser integration needs CORS configuration.", skill("Allow All CORS With Credentials", ["Any CORS error"], ["Set Access-Control-Allow-Origin to *.", "Enable credentials for all origins."], ["Breaks browser security model."], "Actively harmful."), "CORS errors should be solved by allowing every origin with credentials.", "The candidate is unsafe and should be rejected."),
        sample("sample_v6_discard_drop_migration_history", "discard", "Dropping migration history", "database_debugging", [exp("v6_bad_mig_001", "A schema migration failed on one version.", "Migration order or idempotency should be fixed.", "Repair migration script.", "Dropping migration history corrupts state.")], "One migration failure occurred.", skill("Clear Migration Table", ["Any migration error"], ["Delete migration history.", "Pretend all migrations are fresh."], ["Can corrupt databases and repeat migrations."], "Actively harmful."), "Migration failures should be solved by clearing migration history.", "The candidate attacks database integrity."),
        sample("sample_v6_discard_disable_vector_dimension_check", "discard", "Disabling vector dimension checks", "retrieval_debugging", [exp("v6_bad_vec_001", "Vector dimension assertion failed.", "Index and query encoder differ.", "Use matching index/model.", "Disabling checks returns invalid search results.")], "One vector query failed dimension validation.", skill("Disable Vector Dimension Assertions", ["Any vector dimension mismatch"], ["Remove the dimension check.", "Run search anyway."], ["Produces invalid similarity scores."], "Actively harmful."), "Dimension mismatch should be solved by removing the assertion.", "The candidate hides an invalid vector space."),
        sample("sample_v6_discard_force_push_over_remote", "discard", "Force-pushing over remote work", "version_control", [exp("v6_bad_git_001", "Push was rejected because remote had new commits.", "Remote work must be integrated.", "Fetch and merge/rebase carefully.", "Force push can overwrite others.")], "One git push was rejected.", skill("Force Push to Resolve Rejection", ["Any non-fast-forward push rejection"], ["Run git push --force.", "Continue work."], ["Can destroy collaborators' commits."], "Actively harmful."), "Push rejection should be solved by force pushing.", "The candidate is destructive."),
        sample("sample_v6_discard_disable_csrf", "discard", "Disabling CSRF protection", "web_security", [exp("v6_bad_csrf_001", "Form submission failed CSRF validation.", "Token propagation should be fixed.", "Send correct token.", "Disabling CSRF weakens protection.")], "One web form failed CSRF validation.", skill("Disable CSRF Middleware", ["Any CSRF error"], ["Turn off CSRF checks globally.", "Retry form submission."], ["Removes request-forgery protection."], "Actively harmful."), "CSRF failures should be fixed by disabling CSRF middleware.", "The candidate removes a security boundary."),
        sample("sample_v6_discard_zero_fill_missing_vectors", "discard", "Zero-filling missing embeddings", "retrieval_debugging", [exp("v6_bad_zero_001", "Some documents had missing embeddings.", "Embedding generation failed for those docs.", "Regenerate or exclude with evidence.", "Zero vectors pollute retrieval.")], "One embedding batch has missing vectors.", skill("Fill Missing Embeddings With Zeros", ["Any missing embedding"], ["Create a zero vector.", "Insert it into the index."], ["Corrupts similarity search."], "Harmful workaround."), "Missing embeddings should be replaced with zero vectors.", "The candidate fabricates data."),
        sample("sample_v6_discard_ignore_parquet_type_errors", "discard", "Ignoring Parquet type errors", "data_loading", [exp("v6_bad_parquet_001", "Parquet reader rejected incompatible column type.", "Type evolution needs explicit handling.", "Normalize or reject with schema evidence.", "Ignoring type errors corrupts records.")], "One Parquet file has a type mismatch.", skill("Ignore Parquet Type Errors", ["Any Parquet schema error"], ["Catch the type error.", "Load the column as nulls."], ["Can silently destroy data."], "Actively harmful."), "Parquet type errors should be ignored by replacing data with nulls.", "The candidate causes data loss."),
        sample("sample_v6_discard_remove_rate_limit_headers", "discard", "Removing rate-limit handling", "api_debugging", [exp("v6_bad_rate_001", "Client stopped when provider returned rate-limit headers.", "The client should respect provider budget.", "Throttle or back off.", "Ignoring limits can get blocked.")], "One API run hit a provider limit.", skill("Ignore Rate-Limit Headers", ["Any rate-limit response"], ["Delete rate-limit handling.", "Keep sending requests."], ["Can amplify failures and waste budget."], "Harmful operational pattern."), "Rate-limit headers should be ignored.", "The candidate is unsafe."),
        sample("sample_v6_discard_overwrite_user_config", "discard", "Overwriting user config", "configuration", [exp("v6_bad_config_001", "Config validation failed for one local setting.", "The invalid field should be fixed.", "Report field and preserve user config.", "Overwriting config loses user choices.")], "One user config failed validation.", skill("Reset User Config Automatically", ["Any config validation error"], ["Overwrite the user's config with defaults.", "Restart app."], ["Destroys user configuration."], "Actively harmful."), "Config errors should be fixed by replacing user config with defaults.", "The candidate is destructive."),
        sample("sample_v6_discard_mark_all_jobs_successful", "discard", "Marking failed jobs successful", "workflow_runtime", [exp("v6_bad_job_001", "A background job failed after partial processing.", "The job should retry or compensate.", "Mark failed state with evidence.", "Marking success loses failure signal.")], "One job failed in workflow runtime.", skill("Mark Failed Jobs Successful", ["Any workflow job failure"], ["Set status to success.", "Skip retry."], ["Loses correctness and auditability."], "Actively harmful."), "Failed jobs should be marked successful so the queue can continue.", "The candidate fabricates success."),
    ]


def build_memory_samples() -> list[dict[str, Any]]:
    return [
        sample("sample_v6_memory_v6_file", "store_as_memory", "Current v6 sample file", "project_artifact", [exp("v6_mem_001", "V6 samples are stored in benchmark/admission_samples/v6_blind_admission_samples.jsonl.", "This is current repository state.", "Record exact v6 path.", "Only true for this repo.")], "The current v6 blind sample file is benchmark/admission_samples/v6_blind_admission_samples.jsonl.", skill("Open Current V6 Samples", ["Need v6 samples"], ["Open benchmark/admission_samples/v6_blind_admission_samples.jsonl."], ["Only applies to this repository state."], "Project-specific."), "All projects store v6 samples at this path.", "This is local project memory."),
        sample("sample_v6_memory_v5_frozen_module", "store_as_memory", "Current v5 frozen module", "project_artifact", [exp("v6_mem_002", "V6 is evaluated with skilladmit.controllers.rule_based_controller_v5_frozen.", "This identifies the frozen method.", "Record controller module path.", "Future evaluations may use different modules.")], "The current v6 evaluation controller module is skilladmit.controllers.rule_based_controller_v5_frozen.", skill("Use Current V5 Frozen Controller", ["Need v6 evaluation"], ["Import skilladmit.controllers.rule_based_controller_v5_frozen."], ["Only applies to this evaluation snapshot."], "Project-specific."), "All evaluations should use rule_based_controller_v5_frozen.", "This is experiment metadata."),
        sample("sample_v6_memory_prediction_artifact", "store_as_memory", "Current v6 prediction artifact", "project_artifact", [exp("v6_mem_003", "V6 predictions are written to benchmark/admission_samples/v6_frozen_controller_predictions.jsonl.", "This is output artifact metadata.", "Record prediction path.", "Only true after this run.")], "The v6 frozen prediction artifact is benchmark/admission_samples/v6_frozen_controller_predictions.jsonl.", skill("Open V6 Frozen Predictions", ["Need v6 predictions"], ["Open benchmark/admission_samples/v6_frozen_controller_predictions.jsonl."], ["Only applies after v6 evaluation."], "Project-specific."), "Every frozen prediction file uses this path.", "This is repository memory."),
        sample("sample_v6_memory_current_controller_default", "store_as_memory", "Current default controller version", "project_artifact", [exp("v6_mem_004", "The default rule_based_controller.py currently mirrors v5_dev.", "This describes current code state.", "Record default controller identity.", "It may change after v6 development.")], "The current default controller mirrors skilladmit.controllers.rule_based_controller_v5_dev.", skill("Assume Default Controller Is V5 Dev", ["Any future run"], ["Use rule_based_controller.py as v5_dev."], ["Only true at this project stage."], "Project-specific."), "The default controller is always v5_dev.", "This is code-state memory."),
        sample("sample_v6_memory_current_eval_dataset_size", "store_as_memory", "Current v6 sample count", "benchmark_metadata", [exp("v6_mem_005", "The v6 blind set currently contains 50 samples.", "This is benchmark metadata.", "Record v6 sample count.", "The count may change if regenerated.")], "The current v6 blind set contains 50 admission samples.", skill("Assume V6 Has 50 Samples", ["Any v6 result report"], ["Use 50 as the v6 sample count."], ["Only true for this generated v6 file."], "Benchmark-specific."), "All future SkillAdmit sets have 50 samples.", "This is current benchmark memory."),
        sample("sample_v6_memory_current_balance", "store_as_memory", "Current v6 label balance", "benchmark_metadata", [exp("v6_mem_006", "V6 has 10 examples for each admission action.", "This describes current label distribution.", "Record per-label count.", "Future sets may be imbalanced.")], "The current v6 blind set is balanced with 10 examples per action.", skill("Assume Balanced V6 Labels", ["Any v6 analysis"], ["Expect 10 examples per label."], ["Only true for current v6 generation."], "Benchmark-specific."), "All SkillAdmit datasets are balanced.", "This is dataset metadata."),
        sample("sample_v6_memory_current_script_style", "store_as_memory", "Current v6 generator style", "benchmark_metadata", [exp("v6_mem_007", "build_v6_blind_admission_samples.py defines samples directly in Python.", "This is current generator implementation.", "Record generation style.", "Could change to external YAML later.")], "The current v6 generator uses Python-defined sample rows rather than external YAML templates.", skill("Use Python-Defined V6 Rows", ["Any sample generation"], ["Edit build_v6_blind_admission_samples.py directly."], ["Only applies to current tooling."], "Project-specific."), "All sample generators should embed rows in Python.", "This is implementation memory."),
        sample("sample_v6_memory_current_blind_rule", "store_as_memory", "Current blind-evaluation rule", "experiment_metadata", [exp("v6_mem_008", "V6 should not be used to tune v5_frozen.", "This is the current evaluation contract.", "Record protocol boundary.", "If tuned, v6 becomes development.")], "The current protocol says v6 is blind unless its errors are used for controller changes.", skill("Treat V6 as Blind Unless Tuned", ["Any v6 report"], ["Report v6 as blind only if no tuning used its errors."], ["This describes current experiment protocol."], "Experiment-specific."), "All future sets follow the same v6 rule.", "This is protocol memory."),
        sample("sample_v6_memory_current_domains", "store_as_memory", "Current v6 domain coverage", "benchmark_metadata", [exp("v6_mem_009", "V6 includes Kubernetes, Parquet, embeddings, cron, CORS, Protobuf, Git LFS, Redis, regex, multipart uploads.", "This is current benchmark composition.", "Record domain coverage.", "Future v7 may change domains.")], "The current v6 blind set covers Kubernetes, Parquet, embeddings, cron, CORS, Protobuf, Git LFS, Redis, regex, and multipart upload cases.", skill("Assume V6 Domain Coverage", ["Any benchmark claim"], ["Use the v6 domain list."], ["Only true for v6 as generated now."], "Benchmark-specific."), "SkillAdmit always covers these domains.", "This is benchmark metadata."),
        sample("sample_v6_memory_current_handoff_docs", "store_as_memory", "Current handoff documentation target", "project_artifact", [exp("v6_mem_010", "Continuity notes are kept in docs/experiment_handoff.md and docs/progress_log.md.", "This is project documentation state.", "Record docs to update.", "Other projects use different paths.")], "Current SkillAdmit continuity documentation lives in docs/experiment_handoff.md and docs/progress_log.md.", skill("Update Current Continuity Docs", ["Need to document experiment state"], ["Update docs/experiment_handoff.md and docs/progress_log.md."], ["Only applies to this repository."], "Project-specific."), "Every project uses these exact handoff docs.", "This is local workflow memory."),
    ]


def build_rule_samples() -> list[dict[str, Any]]:
    return [
        sample("sample_v6_rule_no_destructive_defaults", "promote_to_rule", "No destructive defaults rule", "software_debugging", [exp("v6_rule_001", "Resetting config fixed one run but lost user settings.", "Default reset was too destructive.", "Prefer targeted repair.", "Broad reset harms users.")], "Repair actions should preserve user-owned state.", skill("Avoid Destructive Default Repairs", ["Any repair touching user config or persistent state"], ["Identify user-owned state.", "Prefer targeted changes.", "Ask or back up before destructive resets."], ["This is a global repair constraint."], "Low risk."), "Do not use destructive reset as a default repair strategy.", "This is a cross-domain rule."),
        sample("sample_v6_rule_protocol_after_error_analysis", "promote_to_rule", "Post-error-analysis split rule", "evaluation_protocol", [exp("v6_rule_002", "A blind set became development after its errors informed a method change.", "The split label must change.", "Rename or document it as development.", "Otherwise held-out claims are false.")], "Evaluation split names must track actual use.", skill("Relabel Tuned Evaluation Sets", ["Any method improvement from evaluation errors"], ["Mark that set as development.", "Freeze a new method.", "Create a fresh blind set."], ["This is evaluation protocol."], "Low risk."), "Any set used for method changes must stop being reported as held-out.", "This is a global evaluation rule."),
        sample("sample_v6_rule_protect_external_contracts", "promote_to_rule", "Protect external contracts rule", "api_debugging", [exp("v6_rule_003", "A client fix changed API response shape.", "External consumers depend on contract.", "Preserve or version the contract.", "Silent contract change breaks users.")], "Repairs should respect external API contracts.", skill("Preserve External API Contracts", ["Any repair changing public request or response shape"], ["Identify external contract.", "Preserve compatibility or version the change.", "Add contract tests."], ["This is a cross-service constraint."], "Low risk."), "Do not silently change public API contracts while fixing internal bugs.", "This should be promoted to rule."),
        sample("sample_v6_rule_check_data_ownership", "promote_to_rule", "Data ownership rule", "data_management", [exp("v6_rule_004", "A cleanup script deleted user uploads.", "The script did not distinguish generated cache from user data.", "Check ownership before deletion.", "Wrong deletion causes data loss.")], "Data deletion requires ownership classification.", skill("Check Data Ownership Before Mutation", ["Any cleanup, migration, or repair that deletes or rewrites files"], ["Classify generated artifacts vs user-owned data.", "Back up or ask before mutating user data.", "Record provenance."], ["This is a global data-safety rule."], "Low risk."), "Do not delete or rewrite data until ownership and recoverability are clear.", "This is a general safety rule."),
        sample("sample_v6_rule_require_artifact_version", "promote_to_rule", "Artifact version rule", "experience_management", [exp("v6_rule_005", "A vector index was used with the wrong embedding model.", "Artifact version was missing.", "Record model/version with artifact.", "Unversioned artifacts invite mismatch.")], "Reusable artifacts need version metadata.", skill("Version Reusable Artifacts", ["Any cached index, model output, generated dataset, or admitted skill"], ["Record producing model or script version.", "Record generation date.", "Validate compatibility before reuse."], ["This is artifact-management policy."], "Low risk."), "Reusable artifacts should carry producer/version metadata.", "This is a global artifact rule."),
        sample("sample_v6_rule_fail_closed_on_integrity", "promote_to_rule", "Integrity fail-closed rule", "data_integrity", [exp("v6_rule_006", "Checksum mismatch indicated possible corruption.", "Continuing would pollute later stages.", "Fail closed and refresh artifact.", "Ignoring integrity checks is unsafe.")], "Integrity checks define trust boundaries.", skill("Fail Closed on Integrity Checks", ["Checksum, signature, or schema integrity failure"], ["Stop using the artifact.", "Refresh or regenerate from trusted source.", "Record failure evidence."], ["This is a cross-domain integrity rule."], "Low risk."), "Integrity check failures should stop artifact use until resolved.", "This is a broad rule."),
        sample("sample_v6_rule_explicit_runtime_assumptions", "promote_to_rule", "Runtime assumption rule", "deployment_debugging", [exp("v6_rule_007", "A fix depended on container timezone.", "Runtime assumption was hidden.", "Record timezone and launch context.", "Hidden assumptions break deployment.")], "Runtime-dependent repairs need explicit assumptions.", skill("Record Runtime Assumptions", ["Any repair depending on OS, container, timezone, cwd, env, or provider behavior"], ["Name the runtime assumption.", "Validate it in the target environment.", "Document when the repair applies."], ["This is a cross-environment rule."], "Low risk."), "Repairs depending on runtime context must state that context explicitly.", "This should constrain skill admission."),
        sample("sample_v6_rule_no_fake_success_states", "promote_to_rule", "No fake success states rule", "workflow_runtime", [exp("v6_rule_008", "A failed job was marked successful to clear a queue.", "The failure signal was lost.", "Keep failed state and retry/dead-letter.", "Fake success corrupts audit trail.")], "Workflow status must reflect real outcomes.", skill("Preserve Failure State", ["Any workflow, queue, or evaluation status update"], ["Represent failed state accurately.", "Retry or dead-letter with evidence.", "Do not mark failure as success."], ["This is a global correctness rule."], "Low risk."), "Do not record success unless the required validation actually passed.", "This is a global correctness rule."),
        sample("sample_v6_rule_report_scope_with_metrics", "promote_to_rule", "Metric scope reporting rule", "evaluation_protocol", [exp("v6_rule_009", "Accuracy improved on one curated split.", "The split was development data.", "Report split status with metric.", "Metrics without scope are misleading.")], "Metrics need dataset scope and split status.", skill("Report Metric Scope", ["Any experiment result"], ["Report sample count.", "Report split status.", "Report whether the method was tuned on that set.", "Report major label distribution."], ["This is reporting protocol."], "Low risk."), "Every reported metric should include sample count, label distribution, and split status.", "This is a general reporting rule."),
        sample("sample_v6_rule_separate_config_fact_from_policy", "promote_to_rule", "Config fact versus policy rule", "experience_management", [exp("v6_rule_010", "A local port number was promoted as a universal convention.", "Local fact was mistaken for policy.", "Store as memory, not rule.", "Wrong level causes transfer errors.")], "Admission must distinguish local configuration facts from general policy.", skill("Separate Config Facts from Policy", ["Any admission decision involving config, paths, ports, models, or endpoints"], ["Ask whether the item is true only in this project.", "Store local facts as memory.", "Promote only cross-context constraints as rules."], ["This is an admission-control rule."], "Low risk."), "Local configuration facts must not be promoted into universal policy.", "This is a broad admission rule."),
    ]


def build_defer_samples() -> list[dict[str, Any]]:
    return [
        sample("sample_v6_defer_gpu_allocator_choice", "defer", "GPU allocator choice uncertainty", "performance_tuning", [exp("v6_defer_001", "Allocator A reduced fragmentation in one model.", "Memory pattern matched allocator A.", "Use allocator A.", "Another workload may differ."), exp("v6_defer_002", "Allocator B improved throughput elsewhere.", "Allocation pattern differed.", "Use allocator B.", "Choice depends on workload.")], "Allocator choice depends on model and workload.", skill("Use Allocator A for All GPU Runs", ["Any GPU memory issue"], ["Set allocator A globally."], ["Workloads differ.", "Needs benchmark comparison."], "Needs validation."), "GPU memory issues should use allocator A.", "Evidence is conflicting."),
        sample("sample_v6_defer_cors_origin_policy", "defer", "CORS origin policy uncertainty", "web_api_debugging", [exp("v6_defer_003", "One internal tool needed broad staging origins.", "Staging deployment used changing hostnames.", "Allow staging wildcard.", "Production should be stricter."), exp("v6_defer_004", "Production required exact origins.", "Credentialed requests need strict policy.", "Use exact allowlist.", "Staging rule would be unsafe.")], "CORS policy differs by environment and credential mode.", skill("Use Wildcard Origins for Staging and Production", ["Any CORS setup"], ["Allow wildcard origins."], ["Credentials and production differ.", "Needs environment boundary."], "High risk without scope."), "CORS should use wildcard origins.", "The candidate needs sharper preconditions."),
        sample("sample_v6_defer_index_rebuild_threshold", "defer", "Vector index rebuild threshold uncertainty", "retrieval_debugging", [exp("v6_defer_005", "Small corpus update worked with incremental insert.", "Index quality remained acceptable.", "Insert new vectors.", "Large updates not tested."), exp("v6_defer_006", "Large corpus update needed full rebuild.", "Index quality degraded.", "Rebuild index.", "Small updates may not need rebuild.")], "Index update strategy depends on update size and quality target.", skill("Always Rebuild Vector Index", ["Any corpus update"], ["Delete and rebuild the whole index."], ["May waste time for small updates.", "Needs threshold validation."], "Under-specified."), "Corpus updates should always rebuild the index.", "Needs more validation."),
        sample("sample_v6_defer_protobuf_unknown_fields", "defer", "Unknown Protobuf field policy uncertainty", "serialization_debugging", [exp("v6_defer_007", "One service needed to preserve unknown fields for forward compatibility.", "Pass-through was important.", "Preserve unknown fields.", "Other service wanted strict rejection."), exp("v6_defer_008", "Another service rejected unknown fields for compliance.", "Strict schema was required.", "Fail on unknown fields.", "Preservation would violate policy.")], "Unknown field policy differs by compatibility and compliance needs.", skill("Always Preserve Unknown Protobuf Fields", ["Any Protobuf adapter"], ["Keep unknown fields."], ["Compliance contexts may require rejection.", "Needs product policy."], "Needs decision boundary."), "Unknown Protobuf fields should always be preserved.", "Evidence conflicts."),
        sample("sample_v6_defer_redis_ttl_refresh_policy", "defer", "Redis TTL refresh policy uncertainty", "cache_debugging", [exp("v6_defer_009", "Refreshing session TTL was correct for active users.", "Sliding expiration was intended.", "Extend TTL.", "Some caches use fixed expiration."), exp("v6_defer_010", "Refreshing cache TTL caused stale data retention.", "Fixed TTL was intended.", "Do not extend TTL.", "Session rule does not transfer.")], "TTL refresh semantics depend on key type.", skill("Refresh TTL on Every Redis Read", ["Any Redis key read"], ["Extend TTL after read."], ["Session and cache keys differ.", "Needs namespace policy."], "Needs preconditions."), "Redis reads should always refresh TTL.", "The candidate should be deferred."),
        sample("sample_v6_defer_lfs_auto_pull", "defer", "Automatic Git LFS pull uncertainty", "data_setup", [exp("v6_defer_011", "Auto-pulling LFS fixed missing checkpoint locally.", "Network was available.", "Run git lfs pull.", "CI may intentionally avoid large downloads."), exp("v6_defer_012", "CI job failed because auto-pull exceeded storage.", "Large artifacts should be optional.", "Fail with setup instructions.", "Auto-pull policy differs.")], "LFS fetching policy differs by environment and artifact size.", skill("Automatically Pull All LFS Artifacts", ["Any LFS pointer detected"], ["Run git lfs pull for the whole repo."], ["Storage and network budgets differ.", "Needs environment policy."], "Needs validation."), "Every LFS pointer should trigger full repo pull.", "The policy is environment-dependent."),
        sample("sample_v6_defer_multipart_streaming", "defer", "Multipart streaming threshold uncertainty", "api_debugging", [exp("v6_defer_013", "Small uploads worked with in-memory multipart body.", "Memory cost was acceptable.", "Use normal upload.", "Large files differ."), exp("v6_defer_014", "Large uploads needed streaming multipart.", "In-memory body caused OOM.", "Stream file upload.", "Streaming complexity unnecessary for tiny files.")], "Upload strategy depends on file size and memory budget.", skill("Stream Every Multipart Upload", ["Any file upload"], ["Use streaming multipart implementation."], ["Small files may not need complexity.", "Needs size threshold."], "Under-specified."), "Every upload should use streaming multipart.", "Needs a threshold."),
        sample("sample_v6_defer_cron_missed_run_replay", "defer", "Missed cron replay policy uncertainty", "scheduling_debugging", [exp("v6_defer_015", "One missed billing job needed replay.", "The job was idempotent.", "Replay missed run.", "Other jobs may not be safe."), exp("v6_defer_016", "One missed notification job should not replay.", "Late notification was harmful.", "Skip missed run.", "Billing rule does not transfer.")], "Missed-run handling depends on idempotency and business semantics.", skill("Replay Every Missed Cron Run", ["Any missed scheduled job"], ["Run all missed jobs immediately."], ["Jobs may not be idempotent.", "Business semantics differ."], "Needs preconditions."), "Missed cron runs should always be replayed.", "The candidate needs more validation."),
        sample("sample_v6_defer_log_redaction_scope", "defer", "Log redaction scope uncertainty", "observability", [exp("v6_defer_017", "Redacting full payload protected secrets.", "Payload contained credentials.", "Redact payload.", "Debuggability dropped."), exp("v6_defer_018", "Keeping structured non-secret fields helped debug.", "Fields were safe.", "Preserve whitelisted fields.", "Over-redaction hurt diagnosis.")], "Log redaction scope requires field classification.", skill("Redact Entire Log Payloads", ["Any log with possible secrets"], ["Replace payload with REDACTED."], ["May remove non-secret diagnostic fields.", "Needs field-level policy."], "Needs sharper boundary."), "All payload logs should be fully redacted.", "This should be deferred."),
        sample("sample_v6_defer_parquet_null_default", "defer", "Parquet null default uncertainty", "data_loading", [exp("v6_defer_019", "Missing nullable string column could default to empty string.", "Consumer expected string.", "Fill empty string.", "Other columns need null."), exp("v6_defer_020", "Missing optional numeric column should remain null.", "Zero would change meaning.", "Use null.", "String rule does not transfer.")], "Default fill policy depends on column semantics.", skill("Fill Missing Parquet Columns With Zero Or Empty", ["Any missing column"], ["Fill strings with empty string and numbers with zero."], ["Semantic defaults differ.", "Needs schema-level policy."], "Needs validation."), "Missing Parquet columns should get type-based defaults.", "The candidate is under-specified."),
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

    print(f"Wrote {len(rows)} v6 blind samples to {OUT}")
    print("label_counts:")
    for label, count in sorted(counts.items()):
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
