# LLM Downstream Validation v0

This report summarizes a real LLM smoke/downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_experience | 23 | 25 | 0.920 | 2 | 0 | 25 | 0 | 51548 | 2061.9 | 24.08 |
| skilladmit_selected | 25 | 25 | 1.000 | 0 | 0 | 25 | 0 | 57597 | 2303.9 | 26.89 |

## Caveat

This is an LLM-based validation runner, but small smoke runs are not full downstream evidence.
Use the same script on all 25 downstream tasks and all target strategies for a paper-grade run.
