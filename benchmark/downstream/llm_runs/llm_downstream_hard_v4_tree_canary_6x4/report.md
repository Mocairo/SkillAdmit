# LLM Downstream Validation Report

Run name: `llm_downstream_hard_v4_tree_canary_6x4`

Tasks directory: `/home/lijx/workspace/skilladmit/benchmark/downstream_hard_v4/tasks`

Rows: 24

This report summarizes a real LLM downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| forced_bad_artifact | 0 | 6 | 0.000 | 6 | 6 | 6 | 0 | 0 | 0.0 | 0.00 |
| no_experience | 6 | 6 | 1.000 | 0 | 0 | 6 | 0 | 10171 | 1695.2 | 14.76 |
| skilladmit_selected | 6 | 6 | 1.000 | 0 | 0 | 6 | 0 | 12449 | 2074.8 | 17.59 |
| skilladmit_selected_with_precondition_context | 6 | 6 | 1.000 | 0 | 0 | 6 | 0 | 15809 | 2634.8 | 23.30 |

## Caveat

This is a runner-level summary, not a standalone paper claim.
Interpret the numbers with the protocol document for the specific task suite and executor setting.
