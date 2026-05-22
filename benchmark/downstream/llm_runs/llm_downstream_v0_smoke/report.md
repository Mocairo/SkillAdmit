# LLM Downstream Validation v0

This report summarizes a real LLM smoke/downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_experience | 2 | 2 | 1.000 | 0 | 0 | 1784 | 892.0 | 7.98 |
| skilladmit_selected | 2 | 2 | 1.000 | 0 | 0 | 2186 | 1093.0 | 6.41 |

## Caveat

This is an LLM-based validation runner, but small smoke runs are not full downstream evidence.
Use the same script on all 25 downstream tasks and all target strategies for a paper-grade run.
