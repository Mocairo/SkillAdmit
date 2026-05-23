# Release Candidate Audit

Generated at UTC: `2026-05-23T13:26:27.567687+00:00`

Final public release-candidate audit for SkillAdmit. This audit is not new empirical evidence; it aggregates existing public checks and verifies that the release surface stays inside the frozen downstream claim boundary.

## Summary

| metric | value |
| --- | --- |
| total_checks | 10 |
| passed_checks | 10 |
| failed_checks | 0 |
| status | pass |

## Aggregate Roles

| layer | role |
| --- | --- |
| current_main_boundary | 0/133 hard_v2/hard_v3/hard_v4 forced_bad_artifact |
| model_transfer_addendum | 0/216 hard_v3/hard_v4 two-model forced_bad_artifact |
| historical_two_boundary | 0/85 hard_v2/hard_v3 forced_bad_artifact |

## Source Audits

| audit | total | passed | failed | status |
| --- | --- | --- | --- | --- |
| paper_claim_consistency | 13 | 13 | 0 | pass |
| reporting_hygiene | 8 | 8 | 0 | pass |
| public_release_readiness | 7 | 7 | 0 | pass |
| reproduction_guide | 13 | 13 | 0 | pass |

## Checks

| check | status | summary | details |
| --- | --- | --- | --- |
| RC1_source_audits_pass | pass | All source audits pass with the expected check counts. | {'audit_rows': [{'name': 'paper_claim_consistency', 'total_checks': 13, 'passed_checks': 13, 'failed_checks': 0, 'status': 'pass'}, {'name': 'reporting_hygiene', 'total_checks':... |
| RC2_boundary_facts_stable | pass | Main boundary, model-transfer addendum, and historical aggregate facts remain separated. | {'boundary': '0/133', 'cross_model': '0/216', 'historical_tasks': 85, 'selected_superiority_consistent': False, 'selected_token_savings_consistent': False} |
| RC3_artifact_index_registers_release_candidate | pass | Artifact index keeps the evidence groups stable and registers the release-candidate audit command. | {'artifact_group_count': 14, 'has_release_candidate_command': True} |
| RC4_public_docs_explain_entrypoints_and_boundaries | pass | README and reproduction guide expose entry points and aggregate roles. | {} |
| RC5_public_surface_has_no_local_paths | pass | Public entry files do not contain machine-specific local paths. | {'public_surface_hits': []} |
| RC6_git_status_has_no_sensitive_or_local_paths | pass | Git status does not expose dirty sensitive, local-run, cache, or workspace paths. | {'dirty_risk_lines': [], 'status_line_count': 23} |
| RC7_no_frozen_eval_boundary_files_changed | pass | Git status does not include frozen task suites, LLM run workspaces, or local agent runs. | {'frozen_status_lines': []} |
| RC8_no_forbidden_tracked_paths | pass | No tracked .env, cache, workspace, or local agent-run paths. | {'forbidden_tracked_paths': []} |
| RC9_final_release_command_registered | pass | Final release-candidate command is visible in README, reproduction guide, and release notes. | {'readme': True, 'guide': True, 'release_notes': True} |
| RC10_release_candidate_is_not_evidence | pass | Release-candidate audit is framed as public-release hygiene, not empirical evidence. | {} |

## Release Candidate Command

`python scripts/audit_release_candidate.py --assert-current-release-candidate`

## Next Recommended Step

If this audit and the deterministic downstream checkers pass, the next step is a public push or release tag, not more hard_v2/hard_v3/hard_v4 tuning.

## Source Files

| name | path | exists | sha256 | bytes |
| --- | --- | --- | --- | --- |
| readme | `README.md` | True | `d6657d08f67fd06d` | 5210 |
| reproduction_guide | `docs/reproduction_guide.md` | True | `0918a129516c446c` | 6853 |
| artifact_index | `benchmark/downstream/reports/paper_artifacts_index.json` | True | `3aed8b46ba5c9871` | 52836 |
| paper_claim_consistency_audit | `benchmark/downstream/reports/paper_claim_consistency_audit.json` | True | `dc57b94ee82a2fa6` | 12492 |
| reporting_hygiene_audit | `benchmark/downstream/reports/reporting_hygiene_audit.json` | True | `6c3b4060bcc6d4b0` | 8156 |
| public_release_readiness_audit | `benchmark/downstream/reports/public_release_readiness_audit.json` | True | `917f56b44c8888da` | 13663 |
| reproduction_guide_audit | `benchmark/downstream/reports/reproduction_guide_audit.json` | True | `40778fcbc0d2b5a2` | 11304 |

