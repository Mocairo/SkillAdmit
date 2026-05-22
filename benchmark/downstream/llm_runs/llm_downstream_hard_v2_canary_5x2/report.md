# LLM Downstream Validation v0

This report summarizes a real LLM smoke/downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_experience | 4 | 5 | 0.800 | 1 | 1 | 5 | 0 | 12775 | 2555.0 | 37.57 |
| skilladmit_selected | 5 | 5 | 1.000 | 0 | 0 | 5 | 0 | 13840 | 2768.0 | 36.78 |

## Caveat

This is an LLM-based validation runner, but small smoke runs are not full downstream evidence.
Use the same script on all 25 downstream tasks and all target strategies for a paper-grade run.
