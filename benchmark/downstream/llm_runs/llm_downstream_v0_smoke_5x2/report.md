# LLM Downstream Validation v0

This report summarizes a real LLM smoke/downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_experience | 5 | 5 | 1.000 | 0 | 0 | 7789 | 1557.8 | 15.14 |
| skilladmit_selected | 5 | 5 | 1.000 | 0 | 0 | 8112 | 1622.4 | 13.78 |

## Caveat

This is an LLM-based validation runner, but small smoke runs are not full downstream evidence.
Use the same script on all 25 downstream tasks and all target strategies for a paper-grade run.
