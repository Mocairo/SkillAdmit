#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark" / "admission_samples" / "v7_blind_admission_samples.jsonl"


def skill(
    name: str,
    trigger: list[str],
    steps: list[str],
    limitations: list[str],
    risk: str = "Low risk when the stated preconditions hold.",
) -> dict[str, Any]:
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
    rationale: str,
    memory: str,
    candidate_skill: dict[str, Any],
    rule: str,
    experiences: list[dict[str, str]],
    tags: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "sample_id": sample_id,
        "cluster_id": sample_id.replace("sample_", "cluster_"),
        "cluster_name": cluster_name,
        "task_ids": [item["task_id"] for item in experiences],
        "tags": tags or [],
        "label": label,
        "label_rationale": rationale,
        "candidate_memory": memory,
        "candidate_skill": candidate_skill,
        "candidate_rule": rule,
        "experience_cluster": experiences,
    }


def build_skill_samples() -> list[dict[str, Any]]:
    rows = [
        sample(
            "sample_v7_skill_docker_healthcheck_exec",
            "distill_into_skill",
            "Docker healthcheck command repaired",
            "The cluster shows a reusable procedure for shell-vs-exec healthcheck failures.",
            "Docker healthcheck commands failed because the command form did not match shell features.",
            skill(
                "Repair Docker Healthcheck Command Form",
                ["Container healthcheck uses pipes, redirects, or shell operators"],
                ["Inspect the healthcheck command form.", "Use shell form only when shell features are required.", "Rerun container healthcheck validation."],
                ["Do not change the application endpoint without evidence."],
            ),
            "When a healthcheck command uses shell syntax, choose command form deliberately rather than rewriting the endpoint.",
            [
                exp("v7_skill_001", "Healthcheck with && failed in exec form.", "Shell operator was not interpreted.", "Use CMD-SHELL for shell operators.", "Low risk after command-form check."),
                exp("v7_skill_002", "Healthcheck with curl pipe failed.", "Pipe required shell execution.", "Use shell form and preserve endpoint.", "Still check container base image shell."),
                exp("v7_skill_003", "Simple argv healthcheck worked in exec form.", "No shell expansion needed.", "Keep exec form.", "Wrong form can hide endpoint bugs."),
            ],
        ),
        sample(
            "sample_v7_skill_s3_pagination",
            "distill_into_skill",
            "S3 pagination continuation repaired",
            "The trajectories support a reusable pagination repair procedure.",
            "List operations returned only the first page of objects.",
            skill(
                "Repair Continuation-Token Pagination",
                ["Object listing returns incomplete results", "Response contains a continuation token"],
                ["Inspect response pagination fields.", "Loop until the continuation token is absent.", "Add a regression check with more than one page."],
                ["Do not raise page size alone as the fix."],
            ),
            "If an API returns a continuation token, consume pages until the token is exhausted.",
            [
                exp("v7_skill_004", "Only 1000 objects were processed.", "Continuation token was ignored.", "Loop over continuation token.", "Large buckets need test coverage."),
                exp("v7_skill_005", "Second page contained missing reports.", "Single request was incomplete.", "Accumulate all pages.", "Memory use should be bounded."),
                exp("v7_skill_006", "Page-size increase still missed data.", "Page size is not a correctness fix.", "Use pagination protocol.", "Endpoint-specific fields must be checked."),
            ],
        ),
        sample(
            "sample_v7_skill_sqlalchemy_rollback",
            "distill_into_skill",
            "SQLAlchemy session recovery repaired",
            "This is a stable reusable repair for failed transaction state.",
            "After IntegrityError, later queries failed because the session stayed in failed state.",
            skill(
                "Rollback SQLAlchemy Session After Failed Transaction",
                ["SQLAlchemy session raises after an earlier IntegrityError"],
                ["Catch the specific database exception at the transaction boundary.", "Call rollback before reusing the session.", "Verify later queries still work."],
                ["Do not swallow the original database error silently."],
            ),
            "After a failed SQLAlchemy transaction, rollback before reusing the session.",
            [
                exp("v7_skill_007", "A duplicate insert poisoned the session.", "Rollback was missing.", "Rollback after IntegrityError.", "Do not hide the duplicate error."),
                exp("v7_skill_008", "Later select failed after previous write error.", "Session was still invalid.", "Rollback at boundary.", "Transaction scope must be clear."),
                exp("v7_skill_009", "Retry succeeded after rollback.", "Session state was repaired.", "Add rollback and validation.", "Retried writes need idempotency."),
            ],
        ),
        sample(
            "sample_v7_skill_jwt_clock_skew",
            "distill_into_skill",
            "JWT leeway handling repaired",
            "The cluster supports a bounded procedure for clock-skew failures.",
            "JWT validation failed near token boundary times across machines.",
            skill(
                "Apply Bounded JWT Clock-Skew Leeway",
                ["JWT validation fails near exp or nbf boundary", "Server clocks differ slightly"],
                ["Check exact validation error.", "Add a small explicit leeway.", "Keep expiration validation enabled."],
                ["Do not disable expiration checks."],
            ),
            "For boundary-time JWT failures, use bounded leeway while preserving expiration validation.",
            [
                exp("v7_skill_010", "Token failed one second before nbf on another host.", "Clock skew caused boundary failure.", "Add small leeway.", "Leeway must be bounded."),
                exp("v7_skill_011", "Expired token was still rejected after leeway.", "Expiration validation stayed active.", "Keep exp verification.", "Too much leeway weakens security."),
                exp("v7_skill_012", "CI host differed by a few seconds.", "Host clock skew was observed.", "Use explicit leeway.", "Investigate large drift separately."),
            ],
        ),
        sample(
            "sample_v7_skill_nginx_forwarded_proto",
            "distill_into_skill",
            "Reverse-proxy scheme propagation repaired",
            "This is a reusable proxy-debugging repair.",
            "App generated http redirects behind an https reverse proxy.",
            skill(
                "Preserve Original Scheme Through Reverse Proxy",
                ["Application behind proxy generates wrong scheme", "Proxy terminates TLS"],
                ["Inspect forwarded headers.", "Set X-Forwarded-Proto at the proxy.", "Configure the app to trust the proxy only in the deployment boundary."],
                ["Do not hardcode https inside application business logic."],
            ),
            "For proxy-terminated TLS, propagate original scheme through trusted forwarded headers.",
            [
                exp("v7_skill_013", "OAuth callback used http behind TLS proxy.", "Original scheme was lost.", "Set X-Forwarded-Proto.", "Trust boundary matters."),
                exp("v7_skill_014", "Generated absolute URLs had wrong scheme.", "Proxy header was missing.", "Forward original protocol.", "Do not trust arbitrary client headers."),
                exp("v7_skill_015", "Local direct run should stay http.", "Hardcoding https would break local.", "Configure proxy-aware mode.", "Environment boundary must be explicit."),
            ],
        ),
        sample(
            "sample_v7_skill_pandas_nullable_int",
            "distill_into_skill",
            "Nullable integer parsing repaired",
            "The cluster provides a stable data-cleaning procedure.",
            "CSV integer columns with missing values became floats and broke ID comparisons.",
            skill(
                "Use Nullable Integer Dtype for Missing Integer Columns",
                ["Pandas integer column contains missing values", "IDs are converted to floats"],
                ["Inspect missing values.", "Use nullable integer dtype such as Int64.", "Verify IDs round-trip without .0 suffix."],
                ["Do not fill missing IDs with arbitrary zero values."],
            ),
            "When integer identifiers contain missing values, preserve semantics with nullable integer dtype.",
            [
                exp("v7_skill_016", "IDs became 12.0 after CSV load.", "NaN forced float dtype.", "Use Int64 dtype.", "Missing values remain explicit."),
                exp("v7_skill_017", "Join failed because keys changed representation.", "Float conversion altered IDs.", "Preserve nullable integer.", "Check downstream serialization."),
                exp("v7_skill_018", "Zero fill caused false matches.", "Sentinel value was unsafe.", "Keep NA as missing.", "Domain-specific imputation is separate."),
            ],
        ),
        sample(
            "sample_v7_skill_npm_workspace_import",
            "distill_into_skill",
            "NPM workspace package import repaired",
            "The examples show a reusable package-linking procedure.",
            "Local workspace package import failed because workspace metadata was incomplete.",
            skill(
                "Repair NPM Workspace Local Package Imports",
                ["Import fails for a local workspace package", "Package exists inside the monorepo"],
                ["Check workspace globs.", "Check package name in package.json.", "Install from the workspace root.", "Rerun the package test."],
                ["Do not publish or install a similarly named public package first."],
            ),
            "For monorepo local packages, check workspace metadata before installing from the registry.",
            [
                exp("v7_skill_019", "Local package existed but was not linked.", "Workspace glob missed the directory.", "Fix workspace glob.", "Registry package would be wrong."),
                exp("v7_skill_020", "Package name mismatched import.", "package.json name was wrong.", "Align local package name.", "Avoid public package confusion."),
                exp("v7_skill_021", "Install from subdirectory missed workspace links.", "Root install was required.", "Run install at workspace root.", "Package manager differs."),
            ],
        ),
        sample(
            "sample_v7_skill_grpc_deadline_idempotent_retry",
            "distill_into_skill",
            "gRPC deadline retry bounded",
            "The cluster supports a scoped retry procedure.",
            "Transient gRPC deadline errors succeeded with bounded retry for idempotent reads.",
            skill(
                "Retry Idempotent gRPC Deadline Failures",
                ["gRPC DEADLINE_EXCEEDED on idempotent read operations"],
                ["Confirm the method is idempotent.", "Add bounded retry with jitter.", "Keep the original deadline budget visible."],
                ["Do not retry non-idempotent writes blindly."],
            ),
            "Retry deadline failures only when method idempotency and budget are explicit.",
            [
                exp("v7_skill_022", "Read RPC timed out under transient load.", "Idempotent retry was safe.", "Add bounded retry.", "Budget must be capped."),
                exp("v7_skill_023", "Write RPC duplicate would be unsafe.", "Idempotency precondition matters.", "Do not retry blindly.", "Operation type must be known."),
                exp("v7_skill_024", "Jitter reduced retry collision.", "Immediate retry amplified load.", "Use jitter.", "Backoff schedule should be tested."),
            ],
        ),
        sample(
            "sample_v7_skill_mime_type_upload",
            "distill_into_skill",
            "Upload MIME type repaired",
            "The cluster shows a reusable upload-debugging procedure.",
            "File uploads were rejected because content type was missing or generic.",
            skill(
                "Set Correct MIME Type for File Uploads",
                ["Upload endpoint rejects file type", "File bytes are valid but Content-Type is generic"],
                ["Inspect server validation.", "Set the file MIME type explicitly.", "Verify server accepts valid files and rejects invalid ones."],
                ["Do not disable file type validation."],
            ),
            "For upload type failures, preserve validation and send accurate MIME metadata.",
            [
                exp("v7_skill_025", "PDF upload sent application/octet-stream.", "Server required application/pdf.", "Set MIME type.", "Do not bypass validation."),
                exp("v7_skill_026", "Image upload lacked content type.", "Multipart metadata was incomplete.", "Add content type field.", "Validate file bytes too."),
                exp("v7_skill_027", "Invalid file remained rejected.", "Validation still worked.", "Keep validator active.", "MIME alone is not trust."),
            ],
        ),
        sample(
            "sample_v7_skill_kafka_offset_commit_after_process",
            "distill_into_skill",
            "Kafka offset commit order repaired",
            "The examples support a reusable ordering procedure.",
            "Messages were lost because offsets were committed before processing completed.",
            skill(
                "Commit Kafka Offsets After Successful Processing",
                ["Consumer loses messages after crash", "Offsets are committed before processing finishes"],
                ["Inspect commit timing.", "Commit after durable processing succeeds.", "Test crash between processing and commit."],
                ["Do not disable commits without a replacement recovery plan."],
            ),
            "For consumer correctness, commit offsets after successful durable processing.",
            [
                exp("v7_skill_028", "Crash after early commit lost work.", "Commit happened too soon.", "Move commit after processing.", "Duplicates still need idempotency."),
                exp("v7_skill_029", "Manual commit fixed loss case.", "Processing became durable first.", "Commit after success.", "At-least-once behavior expected."),
                exp("v7_skill_030", "No commit caused endless replay.", "Commit cannot just be removed.", "Use correct commit point.", "Recovery semantics must be stated."),
            ],
        ),
    ]
    return rows


def build_discard_samples() -> list[dict[str, Any]]:
    specs = [
        ("sample_v7_discard_disable_csrf", "Disable CSRF protection globally", "Turn off CSRF middleware for all POST routes.", "Disabling CSRF to make a form submit is a harmful workaround."),
        ("sample_v7_discard_log_bearer_tokens", "Log bearer tokens for debugging", "Print Authorization headers and bearer tokens in request logs.", "Logging bearer tokens leaks credentials."),
        ("sample_v7_discard_drop_constraints", "Drop database constraints to import data", "Remove foreign-key and uniqueness constraints before import.", "Dropping constraints hides corrupt data and breaks invariants."),
        ("sample_v7_discard_mark_migrations_applied", "Mark migrations applied without running them", "Insert migration rows manually so startup succeeds.", "This fabricates schema state."),
        ("sample_v7_discard_force_latest_lockfile", "Delete lockfile and upgrade everything", "Remove the lockfile and install latest packages.", "Latest dependency drift can create unrelated regressions."),
        ("sample_v7_discard_swallow_kafka_commit_errors", "Ignore Kafka commit failures", "Catch commit exceptions and continue processing.", "This hides delivery failures."),
        ("sample_v7_discard_commit_base64_secrets", "Commit base64 encoded secrets", "Base64 encode secrets and store them in the repository.", "Encoding is not secret management."),
        ("sample_v7_discard_cors_credentials_wildcard", "Use wildcard CORS with credentials", "Allow wildcard origins while sending credentials.", "This weakens browser-origin protection."),
        ("sample_v7_discard_truncate_data_to_fit_schema", "Truncate data to fit schema", "Cut strings and arrays until validation passes.", "This destroys user data."),
        ("sample_v7_discard_disable_rate_limits", "Disable rate limits globally", "Remove rate limiting middleware to avoid 429 errors.", "This removes abuse protection."),
    ]
    rows = []
    for i, (sample_id, name, step, rationale) in enumerate(specs, start=1):
        rows.append(
            sample(
                sample_id,
                "discard",
                name,
                rationale,
                "The candidate is a harmful operational shortcut.",
                skill(
                    name,
                    ["Any failing production workflow"],
                    [step, "Report success."],
                    ["This avoids the symptom instead of repairing the root cause."],
                    "Actively harmful.",
                ),
                step,
                [
                    exp(
                        f"v7_bad_{i:03d}",
                        "A failure exposed a real contract or safety issue.",
                        "The proposed fix weakens the system.",
                        "Reject the candidate.",
                        rationale,
                    )
                ],
                tags=["negative_transfer", "bad_skill"],
            )
        )
    return rows


def build_memory_samples() -> list[dict[str, Any]]:
    specs = [
        ("sample_v7_memory_current_v6_frozen", "Current frozen controller path", "The current frozen controller for v7 evaluation is skilladmit.controllers.rule_based_controller_v6_frozen.", "The file path is useful continuation memory, not a general skill."),
        ("sample_v7_memory_current_regression_scope", "Current regression scope", "The default regression script now checks seed, LLM, v0, v1, v2, v3, v4, v5, and v6.", "The regression scope is repository state."),
        ("sample_v7_memory_current_v7_output", "Current v7 output path", "V7 blind samples are written to benchmark/admission_samples/v7_blind_admission_samples.jsonl.", "The output path is benchmark metadata."),
        ("sample_v7_memory_current_project_root", "Current project root", "The SkillAdmit project root is /home/lijx/workspace/skilladmit.", "The path is local environment memory."),
        ("sample_v7_memory_current_docs", "Current handoff document", "The continuation document is docs/experiment_handoff.md.", "The document path is repository-specific."),
        ("sample_v7_memory_current_python_env", "Current Python environment", "The known working environment is the conda env named skilladmit with Python 3.10.20.", "This is reproducibility metadata."),
        ("sample_v7_memory_current_model_endpoint", "Current model endpoint setting", "The project reads OPENAI_BASE_URL and SKILLADMIT_MODEL from .env.", "This is project configuration memory."),
        ("sample_v7_memory_current_v7_balance", "Current v7 label balance", "The v7 generator emits 50 samples, 10 per admission label.", "The count is an evaluation snapshot."),
        ("sample_v7_memory_current_protocol", "Current blind protocol", "If v7 errors are used for tuning, v7 becomes development data and v8 is needed.", "This is current experiment protocol state."),
        ("sample_v7_memory_current_prediction_file", "Current v7 prediction output", "The v7 frozen predictions should be saved to benchmark/admission_samples/v7_frozen_controller_predictions.jsonl.", "The prediction file is repository convention."),
    ]
    rows = []
    for i, (sample_id, name, memory, rationale) in enumerate(specs, start=1):
        rows.append(
            sample(
                sample_id,
                "store_as_memory",
                name,
                rationale,
                memory,
                skill(
                    f"Assume {name}",
                    ["Any future project"],
                    [memory],
                    ["Only true for this repository state or this local environment."],
                    "Project-specific.",
                ),
                f"All projects should use this fact: {memory}",
                [
                    exp(
                        f"v7_mem_{i:03d}",
                        memory,
                        "This describes current repository or environment state.",
                        "Store as memory for continuation.",
                        "It may become stale after future edits.",
                    )
                ],
                tags=["context_specific", "memory"],
            )
        )
    return rows


def build_rule_samples() -> list[dict[str, Any]]:
    specs = [
        ("sample_v7_rule_security_not_functional_fix", "Security controls are not functional fixes", "Do not weaken security controls to make a functional test pass.", "This is a global safety constraint."),
        ("sample_v7_rule_preserve_public_contract", "Preserve public interface contracts", "Do not silently change public API or file-format contracts while repairing internals.", "This is a cross-domain compatibility rule."),
        ("sample_v7_rule_record_artifact_provenance", "Record artifact provenance", "Every admitted artifact should record source trajectories and validation result.", "This is a global traceability rule."),
        ("sample_v7_rule_compare_same_budget", "Use matched budgets for comparisons", "Compare admission methods under the same task budget and model budget.", "This is an evaluation protocol rule."),
        ("sample_v7_rule_keep_validators_active", "Keep validators active", "Repair invalid data or schema assumptions instead of turning validators off.", "This is a global integrity rule."),
        ("sample_v7_rule_do_not_hide_failures", "Preserve failure visibility", "Do not hide failed jobs, failed tests, or failed validations behind green status.", "This is a global correctness rule."),
        ("sample_v7_rule_state_runtime_assumptions", "State runtime assumptions", "Reusable skills must state runtime assumptions such as OS, shell, package manager, and deployment boundary.", "This is a cross-skill control rule."),
        ("sample_v7_rule_cache_requires_invalidation", "Cache with invalidation", "Only cache outputs when the invalidation key and freshness boundary are explicit.", "This is a global reliability rule."),
        ("sample_v7_rule_metric_without_scope_invalid", "Metrics need scope", "Report sample count, split, model, and date with every headline metric.", "This is an evaluation-reporting rule."),
        ("sample_v7_rule_preconditions_before_application", "Check preconditions before applying skills", "Apply a retrieved skill only after its trigger, limitations, and current task evidence match.", "This is a central admission rule."),
    ]
    rows = []
    for i, (sample_id, name, rule, rationale) in enumerate(specs, start=1):
        rows.append(
            sample(
                sample_id,
                "promote_to_rule",
                name,
                rationale,
                f"{name} should constrain future admissions and repairs.",
                skill(
                    name,
                    ["Any repair or admission decision in its scope"],
                    ["Check the constraint before applying a task-level skill.", "Reject or defer candidates that violate it."],
                    ["This is a rule-level constraint rather than a task-local repair procedure."],
                ),
                rule,
                [
                    exp(
                        f"v7_rule_{i:03d}",
                        "A repair or admission candidate looked locally useful.",
                        "The broader constraint determined whether it was safe to admit.",
                        "Promote the constraint to a rule.",
                        "Ignoring the constraint causes negative transfer.",
                    ),
                    exp(
                        f"v7_rule_{i+20:03d}",
                        "A second scenario showed the same constraint.",
                        "The issue crossed task domains.",
                        "Use the rule before task-specific skills.",
                        "This is not just local memory.",
                    ),
                ],
                tags=["guardrail", "rule"],
            )
        )
    return rows


def build_defer_samples() -> list[dict[str, Any]]:
    specs = [
        ("sample_v7_defer_async_timeout_default", "Async timeout default uncertainty", "Use a universal 30 second timeout for every async task.", "Timeout choice depends on workload and user expectation."),
        ("sample_v7_defer_cache_ttl_policy", "Cache TTL policy uncertainty", "Cache all model responses for 24 hours.", "Freshness and cost trade off differently across tasks."),
        ("sample_v7_defer_compression_threshold", "Compression threshold uncertainty", "Compress every payload larger than 1 KB.", "Threshold depends on CPU, network, and payload type."),
        ("sample_v7_defer_vector_normalization", "Vector normalization uncertainty", "Normalize every embedding before storage.", "Some similarity metrics require normalization and others do not."),
        ("sample_v7_defer_retry_budget", "Retry budget uncertainty", "Retry every network call exactly three times.", "Retry count depends on idempotency, latency budget, and failure mode."),
        ("sample_v7_defer_batch_size_policy", "Batch size policy uncertainty", "Use batch size 128 for all ingestion jobs.", "Batch size depends on memory, model, and document length."),
        ("sample_v7_defer_timezone_display", "Timezone display uncertainty", "Display every timestamp in UTC.", "User-facing timezone policy differs by product and audience."),
        ("sample_v7_defer_masking_granularity", "Masking granularity uncertainty", "Mask all identifiers in debugging traces.", "Privacy and debuggability require a sharper boundary."),
        ("sample_v7_defer_schema_strictness", "Schema strictness uncertainty", "Reject every unknown JSON field.", "Forward compatibility and strict validation conflict by API type."),
        ("sample_v7_defer_parallelism_level", "Parallelism level uncertainty", "Use all CPU cores for every background job.", "Parallelism depends on workload, resource sharing, and rate limits."),
    ]
    rows = []
    for i, (sample_id, name, rule, rationale) in enumerate(specs, start=1):
        rows.append(
            sample(
                sample_id,
                "defer",
                name,
                "The candidate needs sharper preconditions and additional validation.",
                rationale,
                skill(
                    name,
                    ["Any related task"],
                    [rule],
                    ["Policy boundary is underspecified.", "Contexts differ.", "Needs more validation."],
                    "Risk depends on deployment context.",
                ),
                rule,
                [
                    exp(
                        f"v7_defer_{i:03d}",
                        "One environment benefited from the candidate.",
                        "The context-specific reason is not yet separated.",
                        "Collect more validation.",
                        rationale,
                    ),
                    exp(
                        f"v7_defer_{i+20:03d}",
                        "Another environment had a conflicting requirement.",
                        "The universal policy would be wrong.",
                        "Defer until decision boundary is explicit.",
                        "Negative-transfer risk remains.",
                    ),
                ],
                tags=["defer", "insufficient_evidence"],
            )
        )
    return rows


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
    expected = {
        "defer": 10,
        "discard": 10,
        "distill_into_skill": 10,
        "promote_to_rule": 10,
        "store_as_memory": 10,
    }
    if counts != expected:
        raise RuntimeError(f"Unexpected label counts: {dict(counts)}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")

    print(f"Wrote {len(rows)} v7 blind samples to {OUT}")
    print("label_counts:")
    for label, count in sorted(counts.items()):
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
