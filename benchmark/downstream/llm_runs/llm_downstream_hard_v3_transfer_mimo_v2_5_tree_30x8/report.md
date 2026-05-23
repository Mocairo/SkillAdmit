# LLM Downstream Validation Report

Run name: `llm_downstream_hard_v3_transfer_mimo_v2_5_tree_30x8`

Tasks directory: `/home/lijx/workspace/skilladmit/benchmark/downstream_hard_v3/tasks`

Models: `mimo-v2.5`

Rows: 240

This report summarizes a real LLM downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bad_dependency_rule | 29 | 30 | 0.967 | 1 | 0 | 9 | 0 | 71658 | 2388.6 | 17.22 |
| distilled_skills_all | 28 | 30 | 0.933 | 2 | 0 | 29 | 0 | 91349 | 3045.0 | 16.84 |
| forced_bad_artifact | 0 | 30 | 0.000 | 30 | 30 | 30 | 0 | 0 | 0.0 | 0.00 |
| no_experience | 29 | 30 | 0.967 | 1 | 0 | 30 | 0 | 74743 | 2491.4 | 18.32 |
| promoted_rules | 29 | 30 | 0.967 | 1 | 0 | 30 | 0 | 80244 | 2674.8 | 18.38 |
| raw_memory | 30 | 30 | 1.000 | 0 | 0 | 30 | 0 | 90762 | 3025.4 | 15.74 |
| skilladmit_selected | 29 | 30 | 0.967 | 1 | 1 | 30 | 0 | 69501 | 2316.7 | 14.83 |
| skilladmit_selected_with_precondition_context | 29 | 30 | 0.967 | 1 | 1 | 30 | 0 | 76365 | 2545.5 | 14.88 |

## Caveat

This is a runner-level summary, not a standalone paper claim.
Interpret the numbers with the protocol document for the specific task suite and executor setting.
