# LLM Downstream Validation v0

This report summarizes a real LLM smoke/downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bad_dependency_rule | 5 | 5 | 1.000 | 0 | 0 | 13923 | 2784.6 | 37.65 |
| distilled_skills_all | 5 | 5 | 1.000 | 0 | 0 | 17515 | 3503.0 | 36.22 |
| promoted_rules | 5 | 5 | 1.000 | 0 | 0 | 16218 | 3243.6 | 41.91 |
| raw_memory | 5 | 5 | 1.000 | 0 | 0 | 13140 | 2628.0 | 21.90 |

## Caveat

This is an LLM-based validation runner, but small smoke runs are not full downstream evidence.
Use the same script on all 25 downstream tasks and all target strategies for a paper-grade run.
