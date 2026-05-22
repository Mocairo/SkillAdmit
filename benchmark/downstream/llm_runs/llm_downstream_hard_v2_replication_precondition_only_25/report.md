# LLM Downstream Validation v0

This report summarizes a real LLM smoke/downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| skilladmit_selected_with_precondition_only | 23 | 25 | 0.920 | 2 | 1 | 25 | 0 | 77487 | 3099.5 | 35.78 |

## Caveat

This is an LLM-based validation runner, but small smoke runs are not full downstream evidence.
Use the same script on all 25 downstream tasks and all target strategies for a paper-grade run.
