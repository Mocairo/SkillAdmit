# LLM Downstream Validation Report

Run name: `llm_downstream_hard_v4_tree_24x8`

Tasks directory: `/home/lijx/workspace/skilladmit/benchmark/downstream_hard_v4/tasks`

Rows: 192

This report summarizes a real LLM downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bad_dependency_rule | 24 | 24 | 1.000 | 0 | 0 | 7 | 0 | 51974 | 2165.6 | 19.88 |
| distilled_skills_all | 24 | 24 | 1.000 | 0 | 0 | 21 | 0 | 68776 | 2865.7 | 20.87 |
| forced_bad_artifact | 0 | 24 | 0.000 | 24 | 24 | 24 | 0 | 0 | 0.0 | 0.00 |
| no_experience | 24 | 24 | 1.000 | 0 | 0 | 24 | 0 | 46685 | 1945.2 | 16.32 |
| promoted_rules | 24 | 24 | 1.000 | 0 | 0 | 24 | 0 | 58813 | 2450.5 | 22.86 |
| raw_memory | 24 | 24 | 1.000 | 0 | 0 | 24 | 0 | 53406 | 2225.2 | 10.39 |
| skilladmit_selected | 24 | 24 | 1.000 | 0 | 0 | 24 | 0 | 48682 | 2028.4 | 16.16 |
| skilladmit_selected_with_precondition_context | 24 | 24 | 1.000 | 0 | 0 | 24 | 0 | 63586 | 2649.4 | 21.67 |

## Caveat

This is a runner-level summary, not a standalone paper claim.
Interpret the numbers with the protocol document for the specific task suite and executor setting.
