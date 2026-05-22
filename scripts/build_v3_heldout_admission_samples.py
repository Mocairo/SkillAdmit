#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark" / "admission_samples" / "v3_heldout_admission_samples.jsonl"


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
        "source": "v3_heldout_curated",
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


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    rows.extend(
        [
            sample(
                "sample_v3_skill_openai_compatible_chat_payload",
                "distill_into_skill",
                "OpenAI-compatible chat payload repair",
                "api_debugging",
                ["v3_api_001", "v3_api_002", "v3_api_003"],
                [
                    exp("v3_api_001", "API returned 400 because messages was missing.", "The endpoint expects chat.completions-style messages.", "Send model and messages fields.", "Do not switch endpoints without checking API contract."),
                    exp("v3_api_002", "Request used prompt instead of messages.", "Payload shape was incompatible with chat endpoint.", "Convert prompt to messages list.", "Blindly adding fields can create mixed schemas."),
                    exp("v3_api_003", "Response parser expected text but chat response used choices[0].message.content.", "Client assumed a different response schema.", "Parse the OpenAI-compatible chat response.", "Only applies to chat-compatible endpoints."),
                ],
                "Several API failures came from using the wrong OpenAI-compatible chat payload or response schema.",
                skill(
                    "Repair OpenAI-Compatible Chat Payloads",
                    ["HTTP 400 from a chat/completions endpoint", "payload uses prompt instead of messages"],
                    ["Check endpoint type.", "Send model plus messages.", "Parse choices[0].message.content or streaming deltas.", "Rerun the request."],
                    ["Do not apply to non-chat endpoints without checking their schema."],
                    "Low risk when endpoint contract is known.",
                ),
                "For an OpenAI-compatible chat endpoint, verify request and response schemas before changing model settings.",
                "The repeated API failures support a stable procedural repair.",
            ),
            sample(
                "sample_v3_skill_env_file_loading",
                "distill_into_skill",
                "Environment variable loading repair",
                "runtime_config",
                ["v3_env_001", "v3_env_002", "v3_env_003"],
                [
                    exp("v3_env_001", "OPENAI_API_KEY existed in .env but os.getenv returned None.", "The process never loaded .env.", "Call load_dotenv from project root.", "Do not hardcode the key."),
                    exp("v3_env_002", "OPENAI_BASE_URL defaulted incorrectly despite .env value.", "Configuration file was not loaded before client creation.", "Load .env before reading env vars.", "Shell exports may hide the bug."),
                    exp("v3_env_003", "Model name fell back to a default.", "SKILLADMIT_MODEL was not loaded.", "Load .env and validate required env vars.", "Do not silently continue with wrong model."),
                ],
                "Several runtime failures were caused by reading environment variables before loading .env.",
                skill(
                    "Load and Validate Project .env Configuration",
                    ["Required env var is missing despite .env file", "client uses default base_url or model unexpectedly"],
                    ["Load .env from the project root.", "Read required variables.", "Fail fast if required values are missing.", "Print non-secret configuration for debugging."],
                    ["Do not print secrets.", "Do not hardcode API keys."],
                    "Low risk and broadly useful for API clients.",
                ),
                "Configuration loaders should validate required non-secret runtime settings before creating API clients.",
                "The cluster shows a reusable runtime-configuration repair.",
            ),
            sample(
                "sample_v3_skill_streaming_delta_reader",
                "distill_into_skill",
                "Streaming chat response reader",
                "api_debugging",
                ["v3_stream_001", "v3_stream_002", "v3_stream_003"],
                [
                    exp("v3_stream_001", "Non-streaming message.content was empty while streaming chunks contained content.", "The provider emits useful text in delta chunks.", "Read chunk.choices[0].delta.content.", "Need to handle usage-only chunks."),
                    exp("v3_stream_002", "Final usage chunk had no choices.", "Parser assumed choices is always non-empty.", "Skip chunks with empty choices and keep usage.", "Blind indexing crashes."),
                    exp("v3_stream_003", "SSE returned [DONE] after data chunks.", "Client must collect data lines.", "Append delta content until done.", "Only applies to streaming mode."),
                ],
                "Several provider responses required streaming delta parsing rather than non-streaming content access.",
                skill(
                    "Parse Streaming Chat Deltas",
                    ["stream=True response", "empty non-streaming content", "usage chunk has no choices"],
                    ["Iterate chunks.", "Record usage chunks separately.", "Skip empty choices.", "Append delta.content.", "Stop at stream completion."],
                    ["Only applies to streaming chat APIs."],
                    "Low risk for streaming clients.",
                ),
                "Streaming clients must handle content chunks and usage-only chunks separately.",
                "The repeated parsing failures support skill admission.",
            ),
            sample(
                "sample_v3_skill_http_timeout_diagnosis",
                "distill_into_skill",
                "HTTP timeout diagnosis",
                "api_debugging",
                ["v3_net_001", "v3_net_002", "v3_net_003"],
                [
                    exp("v3_net_001", "TLS handshake timed out through a proxy.", "The client inherited proxy settings.", "Check trust_env and proxy variables.", "Do not assume server outage immediately."),
                    exp("v3_net_002", "Direct request worked but SDK request timed out.", "HTTP client configuration differed.", "Compare proxy and timeout settings.", "Do not increase timeout blindly."),
                    exp("v3_net_003", "Connection succeeded after disabling environment proxy usage.", "The proxy path was the cause.", "Set trust_env deliberately.", "This may differ on networks that require a proxy."),
                ],
                "Several timeout failures came from HTTP client proxy or timeout configuration.",
                skill(
                    "Diagnose OpenAI-Compatible HTTP Timeouts",
                    ["ConnectTimeout or TLS handshake timeout", "SDK call times out before API response"],
                    ["Check proxy-related environment variables.", "Compare direct and SDK requests.", "Set HTTP client trust_env intentionally.", "Use explicit timeout values.", "Retry connection test."],
                    ["Do not disable proxies on networks that require them.", "Do not treat every timeout as provider failure."],
                    "Medium risk because proxy requirements vary by environment.",
                ),
                "For API timeouts, distinguish network/proxy configuration from provider-side failures before changing model logic.",
                "The cluster has a stable diagnostic procedure with environment caveats.",
            ),
            sample(
                "sample_v3_skill_json_output_repair",
                "distill_into_skill",
                "Structured JSON output repair",
                "agent_runtime",
                ["v3_json_001", "v3_json_002", "v3_json_003"],
                [
                    exp("v3_json_001", "Model produced almost-valid JSON with a truncated string.", "The intended patch was recoverable.", "Ask model to repair JSON only.", "Semantic patch errors still need validation."),
                    exp("v3_json_002", "Model wrapped JSON in markdown fences.", "Parser needed fence removal.", "Strip fences and parse object.", "Do not execute arbitrary text."),
                    exp("v3_json_003", "Model returned explanatory text around JSON.", "The JSON object could be extracted.", "Extract object and validate schema.", "Schema validation is still required."),
                ],
                "Several agent runs required structured-output cleanup before applying patches.",
                skill(
                    "Repair Structured JSON Patch Responses",
                    ["LLM output should be JSON but fails parsing", "Output contains a recoverable JSON object"],
                    ["Strip markdown fences.", "Extract a JSON object if present.", "If parsing fails, ask the model to return corrected JSON only.", "Validate schema before applying edits."],
                    ["Do not use this to accept semantically wrong patches.", "Verifier must still run after applying edits."],
                    "Medium risk without schema and verifier checks.",
                ),
                "Structured model outputs should be schema-validated and repaired before downstream execution.",
                "The repeated output-format failures justify a procedural runner skill.",
            ),
        ]
    )

    rows.extend(
        [
            sample(
                "sample_v3_discard_log_api_keys_for_debugging",
                "discard",
                "Logging secrets for API debugging",
                "runtime_config",
                ["v3_bad_secret_001", "v3_bad_secret_002"],
                [
                    exp("v3_bad_secret_001", "API auth failed.", "The key might be missing or invalid.", "Check presence and redacted prefix only.", "Printing the full key leaks secrets."),
                    exp("v3_bad_secret_002", "Config loader could not find OPENAI_API_KEY.", "The env var should be validated.", "Raise missing-key error.", "Dumping .env exposes credentials."),
                ],
                "Some API failures involve credentials.",
                skill(
                    "Print API Keys During Debugging",
                    ["Any authentication or missing-key error"],
                    ["Print the full API key.", "Print the full .env file.", "Compare secrets manually."],
                    ["Leaks credentials and violates safe debugging practice."],
                    "Actively harmful.",
                ),
                "When API auth fails, print all secrets so the issue is visible.",
                "The candidate leaks credentials and should be rejected.",
            ),
            sample(
                "sample_v3_discard_disable_ssl_verification",
                "discard",
                "Disabling TLS verification for network failures",
                "api_debugging",
                ["v3_bad_tls_001", "v3_bad_tls_002"],
                [
                    exp("v3_bad_tls_001", "TLS handshake failed.", "Proxy or certificate path may be misconfigured.", "Diagnose network settings.", "Disabling verification hides security failures."),
                    exp("v3_bad_tls_002", "HTTPS request failed from one environment.", "Environment trust store may differ.", "Check CA/proxy settings.", "verify=False is not a general repair."),
                ],
                "Network failures sometimes mention TLS.",
                skill(
                    "Disable SSL Verification for HTTPS Errors",
                    ["Any HTTPS or TLS error"],
                    ["Set verify=False.", "Retry the request."],
                    ["Bypasses TLS verification and can hide real network problems."],
                    "High risk workaround.",
                ),
                "For HTTPS errors, disable certificate verification globally.",
                "This is a dangerous workaround rather than admissible skill knowledge.",
            ),
            sample(
                "sample_v3_discard_hardcode_success_response",
                "discard",
                "Hardcoding API success",
                "api_debugging",
                ["v3_bad_api_001"],
                [
                    exp("v3_bad_api_001", "API response parsing failed.", "Client parsing logic is wrong.", "Fix parser.", "Hardcoding a response bypasses the API."),
                ],
                "One API task needs a response parser fix.",
                skill(
                    "Return Hardcoded API Responses",
                    ["Any API parsing failure"],
                    ["Skip the API response.", "Return a fixed success object.", "Rerun tests."],
                    ["Does not fix the client and may fake success."],
                    "Actively harmful.",
                ),
                "If API parsing fails, return a fake successful response.",
                "The candidate fabricates results and should be discarded.",
            ),
            sample(
                "sample_v3_discard_ignore_rate_limits",
                "discard",
                "Ignoring rate-limit failures",
                "api_debugging",
                ["v3_bad_rate_001", "v3_bad_rate_002"],
                [
                    exp("v3_bad_rate_001", "API returned 429.", "Request rate exceeded provider limits.", "Back off or reduce concurrency.", "Ignoring 429 causes repeated failures."),
                    exp("v3_bad_rate_002", "Batch requests failed intermittently with 429.", "Concurrency is too high.", "Throttle requests.", "Looping immediately worsens the problem."),
                ],
                "Some API calls can hit provider rate limits.",
                skill(
                    "Immediately Retry Rate-Limited Requests Forever",
                    ["HTTP 429"],
                    ["Retry immediately in a tight loop.", "Do not back off.", "Do not limit concurrency."],
                    ["Can amplify rate limits and waste budget."],
                    "Harmful operational pattern.",
                ),
                "For HTTP 429, retry immediately until success.",
                "The candidate is unsafe and inefficient.",
            ),
            sample(
                "sample_v3_discard_store_full_raw_traces_forever",
                "discard",
                "Storing every raw trace forever",
                "experience_management",
                ["v3_bad_memory_001", "v3_bad_memory_002"],
                [
                    exp("v3_bad_memory_001", "A long raw trace contains repeated command output.", "Most tokens are redundant.", "Summarize useful evidence.", "Keeping all text increases retrieval noise."),
                    exp("v3_bad_memory_002", "A failed trace contains transient API noise.", "It is not task knowledge.", "Separate runtime logs from memory.", "Storing everything pollutes future context."),
                ],
                "Agent traces can be long and noisy.",
                skill(
                    "Store Every Raw Agent Trace as Skill Context",
                    ["Any completed agent run"],
                    ["Store the full raw trace.", "Always retrieve it for similar tasks."],
                    ["No filtering, summarization, or admission control."],
                    "High token cost and noise risk.",
                ),
                "All raw traces should always be stored and retrieved.",
                "This directly contradicts admission control and should be rejected.",
            ),
        ]
    )

    rows.extend(
        [
            sample(
                "sample_v3_memory_current_base_url",
                "store_as_memory",
                "Current provider base URL",
                "runtime_config",
                ["v3_mem_config_001"],
                [
                    exp("v3_mem_config_001", "The current API endpoint is token-plan-cn.xiaomimimo.com/v1.", "This is the user's current provider setting.", "Store as project config.", "Not transferable to other providers."),
                ],
                "This project currently uses OPENAI_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1.",
                skill(
                    "Use Xiaomi Token Plan Endpoint",
                    ["Any OpenAI-compatible task"],
                    ["Set base_url to the Xiaomi endpoint."],
                    ["Only valid for this user's current credentials and provider."],
                    "Environment-specific.",
                ),
                "All OpenAI-compatible experiments should use this endpoint.",
                "The fact is useful but tied to one user's environment.",
            ),
            sample(
                "sample_v3_memory_trace_file_location",
                "store_as_memory",
                "Current trace file location",
                "project_artifact",
                ["v3_mem_path_001"],
                [
                    exp("v3_mem_path_001", "The latest LLM traces are in benchmark/agent_runs/llm_coding_agent_v0/trajectories.jsonl.", "This is repository state.", "Store exact path.", "Other projects use different paths."),
                ],
                "The current trajectory file is benchmark/agent_runs/llm_coding_agent_v0/trajectories.jsonl.",
                skill(
                    "Open Current SkillAdmit Trajectory File",
                    ["Need current SkillAdmit traces"],
                    ["Open benchmark/agent_runs/llm_coding_agent_v0/trajectories.jsonl."],
                    ["Only applies to this repository state."],
                    "Not transferable.",
                ),
                "All agent projects store trajectories at this exact path.",
                "This is a useful project-specific memory.",
            ),
            sample(
                "sample_v3_memory_current_runner_name",
                "store_as_memory",
                "Current runner identifier",
                "project_artifact",
                ["v3_mem_runner_001"],
                [
                    exp("v3_mem_runner_001", "The current real agent runner is llm_coding_agent_v0.", "This identifies the experimental artifact.", "Record runner name.", "Not a general algorithm."),
                ],
                "The current real LLM runner is named llm_coding_agent_v0.",
                skill(
                    "Use llm_coding_agent_v0 for All Runs",
                    ["Any future experiment"],
                    ["Use runner name llm_coding_agent_v0."],
                    ["Runner name may change as the project evolves."],
                    "Project-specific.",
                ),
                "All future agent experiments should use llm_coding_agent_v0.",
                "The runner name is local project state.",
            ),
            sample(
                "sample_v3_memory_current_python_env",
                "store_as_memory",
                "Current Python environment",
                "runtime_environment",
                ["v3_mem_env_001"],
                [
                    exp("v3_mem_env_001", "The project ran under conda env skilladmit.", "This matters for reproduction.", "Record env name and Python version.", "Not a task-solving process."),
                ],
                "The current project uses conda env skilladmit with Python 3.10.",
                skill(
                    "Create skilladmit Conda Env",
                    ["Any project setup"],
                    ["Create conda env named skilladmit with Python 3.10."],
                    ["Only applies to this local project setup."],
                    "Environment-specific.",
                ),
                "Every project should use a conda env named skilladmit.",
                "This is reproducibility metadata, not a reusable skill.",
            ),
            sample(
                "sample_v3_memory_current_dataset_size",
                "store_as_memory",
                "Current v1/v2 sample counts",
                "benchmark_metadata",
                ["v3_mem_count_001"],
                [
                    exp("v3_mem_count_001", "v1 and v2 currently have 25 samples each.", "This is current benchmark metadata.", "Record sample counts.", "Counts will change."),
                ],
                "At this stage, v1_mixed and v2_heldout each contain 25 admission samples.",
                skill(
                    "Assume SkillAdmit Has 25 Samples",
                    ["Any SkillAdmit evaluation"],
                    ["Use 25 as the dataset size."],
                    ["The dataset will change as samples are added."],
                    "Stale quickly.",
                ),
                "SkillAdmitBench always has 25 samples.",
                "The count is useful project memory but not a stable rule.",
            ),
        ]
    )

    rows.extend(
        [
            sample(
                "sample_v3_rule_never_print_secrets",
                "promote_to_rule",
                "Secret-safe debugging",
                "runtime_config",
                ["v3_rule_secret_001", "v3_rule_secret_002"],
                [
                    exp("v3_rule_secret_001", "Auth debugging needs checking key presence.", "Full key value is sensitive.", "Print only whether key exists.", "Full key logging leaks credentials."),
                    exp("v3_rule_secret_002", "Config debugging needs base URL and model.", "Those are non-secret.", "Print non-secret config.", "Secrets must be redacted."),
                ],
                "Credential-related failures require careful logging.",
                skill(
                    "Redact Secrets During Configuration Debugging",
                    ["Debugging API key or env config"],
                    ["Check whether secret exists.", "Print non-secret config.", "Never print full key values."],
                    ["This is a global safety constraint."],
                    "Low risk.",
                ),
                "Never print full API keys or secrets in logs; only report presence or redacted values.",
                "This should constrain all API-debugging and agent-runtime workflows.",
            ),
            sample(
                "sample_v3_rule_keep_test_contract",
                "promote_to_rule",
                "Keep benchmark contract intact",
                "software_debugging",
                ["v3_rule_contract_001", "v3_rule_contract_002"],
                [
                    exp("v3_rule_contract_001", "Tests reveal source bug.", "Changing tests would invalidate the task.", "Patch source.", "Test edits fake success."),
                    exp("v3_rule_contract_002", "verifier.sh defines acceptance.", "Changing verifier changes the benchmark.", "Keep verifier intact.", "Verifier edits corrupt evaluation."),
                ],
                "Debug tasks rely on tests and verifier as the contract.",
                skill(
                    "Respect Test and Verifier Contract",
                    ["Any benchmark bug fix"],
                    ["Do not change tests or verifier.", "Fix source code.", "Rerun verifier."],
                    ["Only override if task explicitly asks for test changes."],
                    "Low risk.",
                ),
                "Do not modify tests or verifier scripts unless explicitly instructed.",
                "This is a cross-task rule.",
            ),
            sample(
                "sample_v3_rule_budget_aware_validation",
                "promote_to_rule",
                "Budget-aware validation before admission",
                "experience_management",
                ["v3_rule_budget_001", "v3_rule_budget_002"],
                [
                    exp("v3_rule_budget_001", "Generating a skill costs tokens.", "Admission should consider future reuse.", "Estimate utility before storing.", "Blind skill creation wastes budget."),
                    exp("v3_rule_budget_002", "Validation tasks cost tokens too.", "Validation should be budgeted.", "Use validation when risk is high.", "Unbounded validation is expensive."),
                ],
                "Experience admission consumes generation and validation budget.",
                skill(
                    "Check Admission Utility and Cost",
                    ["Candidate memory, skill, or rule"],
                    ["Estimate future utility.", "Estimate token and validation cost.", "Prefer admission only when expected utility is positive."],
                    ["This is a global admission rule rather than a task repair."],
                    "Low risk.",
                ),
                "Admission should consider expected future utility, token cost, validation cost, and risk.",
                "This rule applies across memory, skill, and rule levels.",
            ),
            sample(
                "sample_v3_rule_distinguish_runtime_logs_from_skills",
                "promote_to_rule",
                "Runtime logs versus task knowledge",
                "agent_runtime",
                ["v3_rule_runtime_001", "v3_rule_runtime_002"],
                [
                    exp("v3_rule_runtime_001", "API timeout may be infrastructure noise.", "It may justify runner logging.", "Do not store as task skill.", "Wrong layer pollutes skill bank."),
                    exp("v3_rule_runtime_002", "Malformed JSON may be parser issue.", "It belongs to runner robustness.", "Separate from domain repair.", "Wrong layer confuses future retrieval."),
                ],
                "Some useful experiences belong to agent infrastructure, not task solving.",
                skill(
                    "Separate Runtime Events from Domain Skills",
                    ["Agent runtime errors", "API timeouts", "formatting failures"],
                    ["Classify event layer.", "Store runtime issues separately.", "Do not admit as domain skill."],
                    ["This is an admission rule."],
                    "Low risk.",
                ),
                "Do not store runtime/API/parser noise as domain task-solving skills.",
                "This is a general experience-management rule.",
            ),
            sample(
                "sample_v3_rule_require_scope_and_limitations",
                "promote_to_rule",
                "Require scope and limitations",
                "experience_management",
                ["v3_rule_scope_001", "v3_rule_scope_002"],
                [
                    exp("v3_rule_scope_001", "A skill without preconditions overgeneralized.", "Scope was missing.", "Add trigger and limitations.", "Unscoped skill causes negative transfer."),
                    exp("v3_rule_scope_002", "A safe skill became unsafe when shortened.", "Limitations were removed.", "Keep limitations with skill.", "Missing constraints cause misuse."),
                ],
                "Skill candidates need scope and limitations to avoid negative transfer.",
                skill(
                    "Require Scope for Admitted Skills",
                    ["Any candidate skill"],
                    ["Check trigger.", "Check limitations.", "Reject or defer if scope is unclear."],
                    ["This is a cross-skill admission rule."],
                    "Low risk.",
                ),
                "Do not admit a skill unless it has explicit triggers, scope, and limitations.",
                "This is a broad admission constraint.",
            ),
        ]
    )

    rows.extend(
        [
            sample(
                "sample_v3_defer_one_timeout_fix",
                "defer",
                "One timeout fixed by disabling proxy",
                "api_debugging",
                ["v3_defer_timeout_001"],
                [
                    exp("v3_defer_timeout_001", "One API timeout disappeared after disabling environment proxy usage.", "Proxy may have caused it.", "Set trust_env false.", "Some networks require proxy."),
                ],
                "One timeout was fixed by changing proxy handling.",
                skill(
                    "Disable Environment Proxy for API Timeouts",
                    ["Any API timeout"],
                    ["Set trust_env=false.", "Retry request."],
                    ["Only one environment observed.", "Some environments need proxies."],
                    "Needs broader validation.",
                ),
                "API timeouts should be solved by disabling proxy usage.",
                "One success is insufficient for general admission.",
            ),
            sample(
                "sample_v3_defer_conflicting_streaming_modes",
                "defer",
                "Conflicting streaming and non-streaming behavior",
                "api_debugging",
                ["v3_defer_stream_001", "v3_defer_stream_002"],
                [
                    exp("v3_defer_stream_001", "Streaming returned content but non-streaming content was empty.", "Streaming parser worked.", "Use stream=True.", "Provider-specific."),
                    exp("v3_defer_stream_002", "Another endpoint returned normal non-streaming content.", "Non-streaming parser worked.", "Use normal response.", "Different providers differ."),
                ],
                "Different OpenAI-compatible endpoints may behave differently.",
                skill(
                    "Always Use Streaming for Chat APIs",
                    ["Any OpenAI-compatible chat call"],
                    ["Set stream=True.", "Parse deltas."],
                    ["Some endpoints work fine without streaming."],
                    "Needs provider comparison.",
                ),
                "All OpenAI-compatible APIs should be called in streaming mode.",
                "The evidence conflicts across providers, so admission should be deferred.",
            ),
            sample(
                "sample_v3_defer_small_rate_limit_policy",
                "defer",
                "Small rate-limit policy evidence",
                "api_debugging",
                ["v3_defer_rate_001"],
                [
                    exp("v3_defer_rate_001", "One batch hit HTTP 429.", "Concurrency may be too high.", "Reduce request rate.", "No tested backoff schedule yet."),
                ],
                "One run hit a provider rate limit.",
                skill(
                    "Use Fixed Ten-Second Backoff for Rate Limits",
                    ["HTTP 429"],
                    ["Sleep 10 seconds.", "Retry request."],
                    ["Only one rate-limit event observed.", "No comparison with exponential backoff."],
                    "Needs validation.",
                ),
                "HTTP 429 should always use a ten-second backoff.",
                "The idea is plausible but too specific and under-validated.",
            ),
            sample(
                "sample_v3_defer_ambiguous_dependency_or_unused_import",
                "defer",
                "Ambiguous dependency versus unused import",
                "python_import_debug",
                ["v3_defer_import_001", "v3_defer_import_002"],
                [
                    exp("v3_defer_import_001", "An absent optional module was unused.", "Removal worked.", "Remove import.", "May not hold when dependency is required."),
                    exp("v3_defer_import_002", "An absent module was required by runtime path.", "Removal would break behavior.", "Add dependency or stub contract.", "Contradicts removal-only strategy."),
                ],
                "Missing imports can be unused or required.",
                skill(
                    "Remove Missing Imports Unless Tests Fail",
                    ["ModuleNotFoundError"],
                    ["Remove import.", "Run tests.", "If tests fail, try another repair."],
                    ["Trial-and-error policy lacks precondition.", "May hide required dependency."],
                    "Needs clearer decision boundary.",
                ),
                "Missing imports are probably unused if tests pass after removal.",
                "The admission decision should wait for stronger preconditions.",
            ),
            sample(
                "sample_v3_defer_unclear_config_skill_or_memory",
                "defer",
                "Configuration setup as memory or skill",
                "runtime_config",
                ["v3_defer_config_001", "v3_defer_config_002"],
                [
                    exp("v3_defer_config_001", "One project used .env for OpenAI-compatible API.", "This is project setup.", "Store config.", "Could be a reusable setup pattern."),
                    exp("v3_defer_config_002", "Another script used shell exports directly.", "Setup style differs.", "Respect local convention.", "Not enough projects observed."),
                ],
                "API configuration can be stored in .env or shell environment.",
                skill(
                    "Standardize All API Projects on .env",
                    ["Any API client project"],
                    ["Create .env.", "Load it at startup.", "Use environment variables."],
                    ["Only a small number of projects observed."],
                    "Useful but needs more cross-project evidence.",
                ),
                "All API client projects should use .env files.",
                "This could become a setup skill or rule, but current evidence is insufficient.",
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
    print(f"Wrote {len(rows)} v3 held-out samples to {OUT}")
    print("label_counts:")
    for label, count in sorted(counts.items()):
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
