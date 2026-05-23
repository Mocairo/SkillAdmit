# LLM Downstream Validation Report

Run name: `llm_downstream_hard_v4_transfer_mimo_v2_5_tree_24x8`

Tasks directory: `/home/lijx/workspace/skilladmit/benchmark/downstream_hard_v4/tasks`

Models: `mimo-v2.5`

Rows: 192

This report summarizes a real LLM downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bad_dependency_rule | 21 | 24 | 0.875 | 3 | 3 | 6 | 0 | 57645 | 2401.9 | 17.14 |
| distilled_skills_all | 24 | 24 | 1.000 | 0 | 0 | 22 | 0 | 76408 | 3183.7 | 18.40 |
| forced_bad_artifact | 0 | 24 | 0.000 | 24 | 24 | 24 | 0 | 0 | 0.0 | 0.00 |
| no_experience | 23 | 24 | 0.958 | 1 | 0 | 24 | 0 | 55349 | 2306.2 | 15.98 |
| promoted_rules | 24 | 24 | 1.000 | 0 | 0 | 24 | 0 | 59895 | 2495.6 | 16.83 |
| raw_memory | 24 | 24 | 1.000 | 0 | 0 | 24 | 0 | 73337 | 3055.7 | 16.72 |
| skilladmit_selected | 24 | 24 | 1.000 | 0 | 0 | 24 | 0 | 59210 | 2467.1 | 16.26 |
| skilladmit_selected_with_precondition_context | 24 | 24 | 1.000 | 0 | 0 | 24 | 0 | 62050 | 2585.4 | 14.75 |

## Caveat

This is a runner-level summary, not a standalone paper claim.
Interpret the numbers with the protocol document for the specific task suite and executor setting.
