# LLM Downstream Validation v0

This report summarizes a real LLM smoke/downstream run with artifact contexts.

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens | avg_latency_sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bad_dependency_rule | 22 | 25 | 0.880 | 2 | 0 | 3 | 0 | 75724 | 3029.0 | 50.33 |
| distilled_skills_all | 25 | 25 | 1.000 | 0 | 0 | 25 | 0 | 84986 | 3399.4 | 42.57 |
| forced_bad_artifact | 0 | 25 | 0.000 | 25 | 25 | 25 | 0 | 0 | 0.0 | 0.00 |
| no_experience | 24 | 25 | 0.960 | 0 | 0 | 25 | 0 | 59272 | 2370.9 | 31.15 |
| promoted_rules | 21 | 25 | 0.840 | 4 | 1 | 25 | 0 | 77858 | 3114.3 | 42.61 |
| raw_memory | 22 | 25 | 0.880 | 3 | 0 | 25 | 0 | 56941 | 2277.6 | 16.51 |
| skilladmit_selected | 23 | 25 | 0.920 | 2 | 0 | 25 | 0 | 66608 | 2664.3 | 35.70 |

## Caveat

This is an LLM-based validation runner, but small smoke runs are not full downstream evidence.
Use the same script on all 25 downstream tasks and all target strategies for a paper-grade run.
