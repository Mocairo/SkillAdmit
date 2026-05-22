# Downstream Validation v0

This is a controlled proxy experiment for artifact reuse on future Python import/debug tasks.
It uses real verifiers but deterministic strategy runners, not LLM calls.

| strategy | successes | tasks | success_rate | negative_transfer | avg_actions |
| --- | ---: | ---: | ---: | ---: | ---: |
| bad_dependency_stub | 5 | 25 | 0.200 | 10 | 4.0 |
| distilled_skill | 25 | 25 | 1.000 | 0 | 4.0 |
| no_experience | 0 | 25 | 0.000 | 0 | 4.0 |
| promoted_rule_only | 0 | 25 | 0.000 | 0 | 4.0 |
| raw_memory_replay | 0 | 25 | 0.000 | 0 | 4.0 |
| skilladmit_selected | 25 | 25 | 1.000 | 0 | 5.0 |

## By Template

### bad_dependency_stub

| template | success | fail |
| --- | ---: | ---: |
| T1_unused_missing_import | 5 | 0 |
| T2_local_module_import | 0 | 5 |
| T3_script_relative_import | 0 | 5 |
| T4_cwd_sensitive_path | 0 | 5 |
| T5_package_internal_import | 0 | 5 |

### distilled_skill

| template | success | fail |
| --- | ---: | ---: |
| T1_unused_missing_import | 5 | 0 |
| T2_local_module_import | 5 | 0 |
| T3_script_relative_import | 5 | 0 |
| T4_cwd_sensitive_path | 5 | 0 |
| T5_package_internal_import | 5 | 0 |

### no_experience

| template | success | fail |
| --- | ---: | ---: |
| T1_unused_missing_import | 0 | 5 |
| T2_local_module_import | 0 | 5 |
| T3_script_relative_import | 0 | 5 |
| T4_cwd_sensitive_path | 0 | 5 |
| T5_package_internal_import | 0 | 5 |

### promoted_rule_only

| template | success | fail |
| --- | ---: | ---: |
| T1_unused_missing_import | 0 | 5 |
| T2_local_module_import | 0 | 5 |
| T3_script_relative_import | 0 | 5 |
| T4_cwd_sensitive_path | 0 | 5 |
| T5_package_internal_import | 0 | 5 |

### raw_memory_replay

| template | success | fail |
| --- | ---: | ---: |
| T1_unused_missing_import | 0 | 5 |
| T2_local_module_import | 0 | 5 |
| T3_script_relative_import | 0 | 5 |
| T4_cwd_sensitive_path | 0 | 5 |
| T5_package_internal_import | 0 | 5 |

### skilladmit_selected

| template | success | fail |
| --- | ---: | ---: |
| T1_unused_missing_import | 5 | 0 |
| T2_local_module_import | 5 | 0 |
| T3_script_relative_import | 5 | 0 |
| T4_cwd_sensitive_path | 5 | 0 |
| T5_package_internal_import | 5 | 0 |

## Interpretation

- `no_experience` and `promoted_rule_only` do not contain concrete repair procedures, so they should not be expected to solve tasks by themselves.
- `raw_memory_replay` tests exact trace replay without abstraction; failures indicate poor transfer of raw traces to renamed future tasks.
- `bad_dependency_stub` is a negative-transfer baseline for the bad rule: treat missing modules as dependencies.
- `distilled_skill` and `skilladmit_selected` test generalized repair procedures selected from admitted skills.

This is not the final downstream experiment. It is a reproducible v0 proxy that should later be replaced or complemented with an LLM agent that consumes the same artifacts as context.
