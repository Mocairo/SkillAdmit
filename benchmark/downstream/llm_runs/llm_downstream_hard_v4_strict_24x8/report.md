# LLM Downstream Validation Report

Run name: `llm_downstream_hard_v4_strict_24x8`

Tasks directory: `/home/lijx/workspace/skilladmit/benchmark/downstream_hard_v4/tasks`

Rows: 192

This report summarizes a real LLM downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bad_dependency_rule | 24 | 24 | 1.000 | 0 | 0 | 4 | 0 | 63789 | 2657.9 | 28.60 |
| distilled_skills_all | 24 | 24 | 1.000 | 0 | 0 | 21 | 0 | 69049 | 2877.0 | 21.52 |
| forced_bad_artifact | 0 | 24 | 0.000 | 24 | 24 | 24 | 0 | 0 | 0.0 | 0.00 |
| no_experience | 24 | 24 | 1.000 | 0 | 0 | 24 | 0 | 53055 | 2210.6 | 22.58 |
| promoted_rules | 23 | 24 | 0.958 | 1 | 0 | 23 | 0 | 69221 | 2884.2 | 30.12 |
| raw_memory | 23 | 24 | 0.958 | 1 | 0 | 24 | 0 | 65070 | 2711.2 | 18.60 |
| skilladmit_selected | 22 | 24 | 0.917 | 2 | 0 | 24 | 0 | 58450 | 2435.4 | 23.59 |
| skilladmit_selected_with_precondition_only | 23 | 24 | 0.958 | 1 | 0 | 24 | 0 | 69961 | 2915.0 | 26.77 |

## Caveat

This is a runner-level summary, not a standalone paper claim.
Interpret the numbers with the protocol document for the specific task suite and executor setting.
