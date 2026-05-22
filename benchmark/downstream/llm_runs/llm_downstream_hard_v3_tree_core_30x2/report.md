# LLM Downstream Validation Report

Run name: `llm_downstream_hard_v3_tree_core_30x2`

Tasks directory: `/home/lijx/workspace/skilladmit/benchmark/downstream_hard_v3/tasks`

Rows: 120

This report summarizes a real LLM downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| forced_bad_artifact | 0 | 30 | 0.000 | 30 | 30 | 30 | 0 | 0 | 0.0 | 0.00 |
| no_experience | 29 | 30 | 0.967 | 1 | 0 | 30 | 0 | 70208 | 2340.3 | 32.69 |
| skilladmit_selected | 29 | 30 | 0.967 | 1 | 0 | 30 | 0 | 69291 | 2309.7 | 25.40 |
| skilladmit_selected_with_precondition_context | 29 | 30 | 0.967 | 1 | 0 | 30 | 0 | 74559 | 2485.3 | 24.14 |

## Caveat

This is a runner-level summary, not a standalone paper claim.
Interpret the numbers with the protocol document for the specific task suite and executor setting.
