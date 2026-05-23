# LLM Downstream Validation Report

Run name: `llm_downstream_hard_v4_transfer_mimo_v2_5_strict_24x8`

Tasks directory: `/home/lijx/workspace/skilladmit/benchmark/downstream_hard_v4/tasks`

Models: `mimo-v2.5`

Rows: 192

This report summarizes a real LLM downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bad_dependency_rule | 18 | 24 | 0.750 | 5 | 0 | 12 | 0 | 71628 | 2984.5 | 23.65 |
| distilled_skills_all | 19 | 24 | 0.792 | 5 | 0 | 23 | 0 | 77720 | 3238.3 | 20.08 |
| forced_bad_artifact | 0 | 24 | 0.000 | 24 | 24 | 24 | 0 | 0 | 0.0 | 0.00 |
| no_experience | 18 | 24 | 0.750 | 6 | 4 | 24 | 0 | 63619 | 2650.8 | 20.69 |
| promoted_rules | 20 | 24 | 0.833 | 4 | 1 | 24 | 0 | 75981 | 3165.9 | 24.56 |
| raw_memory | 18 | 24 | 0.750 | 6 | 0 | 24 | 0 | 78604 | 3275.2 | 19.58 |
| skilladmit_selected | 21 | 24 | 0.875 | 3 | 0 | 24 | 0 | 64041 | 2668.4 | 19.19 |
| skilladmit_selected_with_precondition_only | 20 | 24 | 0.833 | 4 | 1 | 24 | 0 | 74966 | 3123.6 | 21.79 |

## Caveat

This is a runner-level summary, not a standalone paper claim.
Interpret the numbers with the protocol document for the specific task suite and executor setting.
