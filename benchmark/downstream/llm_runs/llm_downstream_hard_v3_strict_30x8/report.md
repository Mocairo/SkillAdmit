# LLM Downstream Validation Report

Run name: `llm_downstream_hard_v3_strict_30x8`

Tasks directory: `/home/lijx/workspace/skilladmit/benchmark/downstream_hard_v3/tasks`

Rows: 240

This report summarizes a real LLM downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bad_dependency_rule | 30 | 30 | 1.000 | 0 | 0 | 11 | 0 | 75920 | 2530.7 | 29.80 |
| distilled_skills_all | 29 | 30 | 0.967 | 1 | 1 | 26 | 0 | 83366 | 2778.9 | 22.49 |
| forced_bad_artifact | 0 | 30 | 0.000 | 30 | 30 | 30 | 0 | 0 | 0.0 | 0.00 |
| no_experience | 28 | 30 | 0.933 | 0 | 0 | 30 | 0 | 74153 | 2471.8 | 30.07 |
| promoted_rules | 29 | 30 | 0.967 | 1 | 0 | 30 | 0 | 80112 | 2670.4 | 28.90 |
| raw_memory | 30 | 30 | 1.000 | 0 | 0 | 30 | 0 | 73789 | 2459.6 | 15.96 |
| skilladmit_selected | 29 | 30 | 0.967 | 1 | 0 | 30 | 0 | 71390 | 2379.7 | 24.69 |
| skilladmit_selected_with_precondition_only | 30 | 30 | 1.000 | 0 | 0 | 30 | 0 | 82615 | 2753.8 | 26.70 |

## Caveat

This is a runner-level summary, not a standalone paper claim.
Interpret the numbers with the protocol document for the specific task suite and executor setting.
