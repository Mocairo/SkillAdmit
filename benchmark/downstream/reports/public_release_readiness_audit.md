# Public Release Readiness Audit

Generated at UTC: `2026-05-23T13:26:29.090219+00:00`

Public-release readiness audit for repository hygiene. This is not new empirical evidence; it checks whether the repo is safe and recoverable to publish.

## Summary

| metric | value |
| --- | --- |
| total_checks | 7 |
| passed_checks | 7 |
| failed_checks | 0 |
| status | pass |

## Checks

| check | status | summary | details |
| --- | --- | --- | --- |
| R1_no_dirty_sensitive_or_local_paths | pass | Git status does not expose dirty sensitive, cache, local agent-run, or LLM workspace paths. | {'dirty_risk_lines': [], 'status_line_count': 23} |
| R2_expected_local_artifacts_ignored | pass | .env, local agent runs, workspaces, and cache paths are ignored by Git. | {'ignore_rows': [{'path': '.env', 'ignored': True, 'rule': '.gitignore:1:.env\t.env'}, {'path': '__pycache__/', 'ignored': True, 'rule': '.gitignore:2:__pycache__/\t__pycache__/... |
| R3_no_forbidden_tracked_paths | pass | No tracked .env, pycache, pytest cache, local agent run, or LLM workspace paths. | {'forbidden_tracked_paths': []} |
| R4_no_obvious_tracked_secrets | pass | No obvious credential patterns were found in tracked text files. | {'secret_hits': [], 'hit_count': 0} |
| R5_no_tracked_file_over_threshold | pass | No tracked file exceeds 2000000 bytes. | {'large_files': []} |
| R6_regeneration_scripts_exist | pass | All script paths referenced in the artifact-index regeneration order exist. | {'missing_regen_scripts': []} |
| R7_release_docs_name_local_secret_boundary | pass | README and handoff docs explicitly keep runtime secrets in ignored local .env. | {} |

## Top Tracked Files

| path | bytes | MiB |
| --- | --- | --- |
| benchmark/downstream/llm_runs/llm_downstream_hard_v3_transfer_mimo_v2_5_tree_30x8/trajectories.jsonl | 1393917 | 1.329 |
| benchmark/downstream/llm_runs/llm_downstream_hard_v3_transfer_mimo_v2_5_strict_30x8/trajectories.jsonl | 1362786 | 1.3 |
| benchmark/downstream/llm_runs/llm_downstream_hard_v3_tree_core_30x2/trajectories.jsonl | 1351208 | 1.289 |
| benchmark/downstream/llm_runs/llm_downstream_hard_v3_strict_30x8/trajectories.jsonl | 1284469 | 1.225 |
| benchmark/downstream/llm_runs/llm_downstream_hard_v4_transfer_mimo_v2_5_strict_24x8/trajectories.jsonl | 1200834 | 1.145 |
| benchmark/downstream/llm_runs/llm_downstream_hard_v4_transfer_mimo_v2_5_tree_24x8/trajectories.jsonl | 1116894 | 1.065 |
| benchmark/downstream/llm_runs/llm_downstream_hard_v4_tree_24x8/trajectories.jsonl | 1067703 | 1.018 |
| benchmark/downstream/llm_runs/llm_downstream_hard_v4_strict_24x8/trajectories.jsonl | 1056579 | 1.008 |
| benchmark/downstream/llm_runs/llm_downstream_hard_v2_full_25x6/trajectories.jsonl | 921828 | 0.879 |
| benchmark/downstream/results/downstream_validation_v0.jsonl | 523448 | 0.499 |
| benchmark/downstream/llm_runs/llm_downstream_hard_v2_tree_25x2/trajectories.jsonl | 278599 | 0.266 |
| benchmark/downstream/reports/hard_v2_strategy_matrix.json | 154134 | 0.147 |
| benchmark/downstream/llm_runs/llm_downstream_hard_v2_replication_selected_precondition_25/trajectories.jsonl | 147508 | 0.141 |
| benchmark/downstream/llm_runs/llm_downstream_hard_v2_selected_precondition_25/trajectories.jsonl | 146859 | 0.14 |
| benchmark/downstream/llm_runs/llm_downstream_hard_v2_replication_tree_selected_25/trajectories.jsonl | 139687 | 0.133 |

## Regeneration Order

| step | name | command | script_exists |
| --- | --- | --- | --- |
| 1 | check_hard_v2 | `python scripts/check_downstream_hard_v2_tasks.py` | True |
| 2 | check_hard_v3 | `python scripts/check_downstream_hard_v3_tasks.py` | True |
| 3 | build_hard_v4 | `python scripts/build_downstream_hard_v4_tasks.py` | True |
| 4 | check_hard_v4 | `python scripts/check_downstream_hard_v4_tasks.py` | True |
| 5 | admission_regression | `python scripts/run_admission_regression.py` | True |
| 6 | summarize_hard_v2 | `python scripts/summarize_hard_v2_results.py --assert-current-hard-v2` | True |
| 7 | export_hard_v2 | `python scripts/export_hard_v2_evidence_package.py --assert-current-hard-v2` | True |
| 8 | summarize_hard_v3 | `python scripts/summarize_hard_v3_results.py --assert-current-hard-v3` | True |
| 9 | export_hard_v3 | `python scripts/export_hard_v3_evidence_package.py --assert-current-hard-v3` | True |
| 10 | export_hard_v4_scaffold | `python scripts/export_hard_v4_scaffold_manifest.py --run-checker --assert-current-hard-v4-scaffold` | True |
| 11 | summarize_hard_v4 | `python scripts/summarize_hard_v4_results.py --assert-current-hard-v4` | True |
| 12 | export_hard_v4 | `python scripts/export_hard_v4_evidence_package.py --assert-current-hard-v4` | True |
| 13 | export_cross_synthesis | `python scripts/export_downstream_cross_version_synthesis.py --assert-current-synthesis` | True |
| 14 | export_boundary_synthesis | `python scripts/export_downstream_boundary_synthesis.py --assert-current-boundary-synthesis` | True |
| 15 | export_paper_section | `python scripts/export_downstream_paper_section.py --assert-current-paper-section` | True |
| 16 | export_claim_defense | `python scripts/export_downstream_claim_defense_matrix.py --assert-current-claim-defense` | True |
| 17 | export_model_transfer_protocol | `python scripts/export_model_transfer_replication_protocol.py --assert-current-protocol` | True |
| 18 | export_model_transfer_evidence | `python scripts/export_model_transfer_evidence_package.py --assert-current-model-transfer` | True |
| 19 | export_model_transfer_cross_model | `python scripts/export_model_transfer_cross_model_synthesis.py --assert-current-cross-model` | True |
| 20 | export_model_transfer_addendum | `python scripts/export_model_transfer_paper_addendum.py --assert-current-addendum` | True |
| 21 | export_artifacts_index | `python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index` | True |
| 22 | audit_paper_claim_consistency | `python scripts/audit_paper_claim_consistency.py --assert-current-audit` | True |
| 23 | audit_reporting_hygiene | `python scripts/audit_reporting_hygiene.py --assert-current-hygiene` | True |
| 24 | audit_public_release_readiness | `python scripts/audit_public_release_readiness.py --assert-current-release` | True |
| 25 | audit_reproduction_guide | `python scripts/audit_reproduction_guide.py --assert-current-reproduction-guide` | True |
| 26 | audit_release_candidate | `python scripts/audit_release_candidate.py --assert-current-release-candidate` | True |

## Release Notes

| topic | value |
| --- | --- |
| commit_do_not_include | .env, benchmark/downstream/llm_runs/*/workspaces/, benchmark/agent_runs/, __pycache__/, .pytest_cache/ |
| primary_reproduction_command | `python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index` |
| final_release_checks | `python scripts/audit_paper_claim_consistency.py --assert-current-audit`<br>`python scripts/audit_reporting_hygiene.py --assert-current-hygiene`<br>`python scripts/audit_public_release_readiness.py --assert-current-release`<br>`python scripts/audit_reproduction_guide.py --assert-current-reproduction-guide`<br>`python scripts/audit_release_candidate.py --assert-current-release-candidate` |

## Source Files

| name | path | sha256 |
| --- | --- | --- |
| gitignore | `.gitignore` | `19ca3946fd901b14` |
| readme | `README.md` | `d6657d08f67fd06d` |
| artifact_index | `benchmark/downstream/reports/paper_artifacts_index.json` | `3aed8b46ba5c9871` |

