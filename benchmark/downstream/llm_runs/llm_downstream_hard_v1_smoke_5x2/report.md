# LLM Downstream Validation v0

This report summarizes a real LLM smoke/downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_experience | 4 | 5 | 0.800 | 1 | 0 | 9530 | 1906.0 | 21.89 |
| skilladmit_selected | 5 | 5 | 1.000 | 0 | 0 | 15903 | 3180.6 | 43.08 |

## Caveat

This is an LLM-based validation runner, but small smoke runs are not full downstream evidence.
Use the same script on all 25 downstream tasks and all target strategies for a paper-grade run.
