# LLM Downstream Validation Report

Run name: `llm_downstream_hard_v4_strict_canary_6x4`

Tasks directory: `/home/lijx/workspace/skilladmit/benchmark/downstream_hard_v4/tasks`

Rows: 24

This report summarizes a real LLM downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| forced_bad_artifact | 0 | 6 | 0.000 | 6 | 6 | 6 | 0 | 0 | 0.0 | 0.00 |
| no_experience | 6 | 6 | 1.000 | 0 | 0 | 6 | 0 | 13576 | 2262.7 | 24.53 |
| skilladmit_selected | 6 | 6 | 1.000 | 0 | 0 | 6 | 0 | 14119 | 2353.2 | 24.61 |
| skilladmit_selected_with_precondition_only | 6 | 6 | 1.000 | 0 | 0 | 6 | 0 | 18154 | 3025.7 | 30.98 |

## Caveat

This is a runner-level summary, not a standalone paper claim.
Interpret the numbers with the protocol document for the specific task suite and executor setting.
