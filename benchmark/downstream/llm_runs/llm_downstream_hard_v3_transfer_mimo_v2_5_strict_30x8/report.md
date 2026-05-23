# LLM Downstream Validation Report

Run name: `llm_downstream_hard_v3_transfer_mimo_v2_5_strict_30x8`

Tasks directory: `/home/lijx/workspace/skilladmit/benchmark/downstream_hard_v3/tasks`

Models: `mimo-v2.5`

Rows: 240

This report summarizes a real LLM downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bad_dependency_rule | 29 | 30 | 0.967 | 1 | 0 | 10 | 0 | 83647 | 2788.2 | 21.53 |
| distilled_skills_all | 29 | 30 | 0.967 | 1 | 0 | 30 | 0 | 102654 | 3421.8 | 21.61 |
| forced_bad_artifact | 0 | 30 | 0.000 | 30 | 30 | 30 | 0 | 0 | 0.0 | 0.00 |
| no_experience | 28 | 30 | 0.933 | 2 | 0 | 30 | 0 | 75266 | 2508.9 | 19.73 |
| promoted_rules | 26 | 30 | 0.867 | 4 | 1 | 30 | 0 | 89566 | 2985.5 | 22.76 |
| raw_memory | 30 | 30 | 1.000 | 0 | 0 | 30 | 0 | 96811 | 3227.0 | 19.26 |
| skilladmit_selected | 29 | 30 | 0.967 | 1 | 0 | 29 | 0 | 76964 | 2565.5 | 18.37 |
| skilladmit_selected_with_precondition_only | 29 | 30 | 0.967 | 1 | 0 | 30 | 0 | 92936 | 3097.9 | 21.58 |

## Caveat

This is a runner-level summary, not a standalone paper claim.
Interpret the numbers with the protocol document for the specific task suite and executor setting.
