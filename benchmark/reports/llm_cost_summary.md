# SkillAdmit Cost Summary

This report summarizes observed token and latency cost from the current real LLM trajectory run.

## Inputs

- trajectories: `benchmark/trajectories/llm_coding_agent_v0_trajectories.jsonl`
- admission samples: `benchmark/admission_samples/llm_coding_agent_v0_admission_samples.jsonl`

## LLM Trajectory Cost

- tasks: 20
- successes: 20
- success_rate: 1.000
- prompt_tokens: 14916
- completion_tokens: 24083
- total_tokens: 38999
- avg_tokens_per_task: 1950.0
- avg_tokens_per_success: 1950.0
- total_model_latency_seconds: 483.382
- avg_model_latency_seconds: 24.169

## Cost By Template

| template | tasks | successes | total_tokens | avg_tokens |
| --- | ---: | ---: | ---: | ---: |
| T1_missing_third_party_package | 4 | 4 | 4841 | 1210.2 |
| T2_local_module_mistaken_as_missing_package | 4 | 4 | 14721 | 3680.2 |
| T3_relative_import_executed_as_script | 4 | 4 | 6317 | 1579.2 |
| T4_wrong_current_working_directory | 4 | 4 | 8464 | 2116.0 |
| T5_broken_package_structure | 4 | 4 | 4656 | 1164.0 |

## Admission Artifact Cost

- admission_samples: 5
- admitted_artifacts: 5
- source_tokens_all_samples: 38999
- source_tokens_admitted_artifacts: 38999
- avg_source_tokens_per_admitted_artifact: 7799.8

## Break-Even Estimate

This estimate is parameterized. It is not a measured downstream result yet.

- tokens_saved_per_artifact_use: 500.0
- expected_uses_per_future_task: 1.00
- estimated_saved_tokens_per_future_task: 2500.0
- break_even_future_tasks: 15.60
- break_even_uses_per_artifact: 15.60

## Caveat

This is only an accounting report. A paper result still needs measured downstream reuse, not just assumed savings.
