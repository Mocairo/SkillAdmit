# Reporting Hygiene Audit

Generated at UTC: `2026-05-23T11:39:24.734269+00:00`

Public reporting hygiene audit for SkillAdmit downstream artifacts. It checks aggregate separation, legacy wording, overclaim guardrails, and handoff consistency.

## Summary

| metric | value |
| --- | --- |
| total_checks | 8 |
| passed_checks | 8 |
| failed_checks | 0 |
| status | pass |

## Aggregate Roles

| layer | aggregate | role |
| --- | --- | --- |
| historical_two_boundary | 0/85 | legacy hard_v2/hard_v3 synthesis only |
| current_main_boundary | 0/133 | current hard_v2/hard_v3/hard_v4 downstream boundary |
| model_transfer_addendum | 0/216 | two-model hard_v3/hard_v4 replication/addendum layer |

## Checks

| check | status | summary | details |
| --- | --- | --- | --- |
| H1_main_boundary_uses_0_133 | pass | Current main reporting layer is anchored to the hard_v2/hard_v3/hard_v4 0/133 boundary. | {'boundary': '0/133', 'paper': '0/133', 'claim_positive_contains_0_133': True, 'index': '0/133'} |
| H2_no_0_85_in_current_main_reports | pass | Current main reports do not reuse the legacy hard_v2/hard_v3 0/85 aggregate. | {'0/85_occurrences': 0} |
| H3_model_transfer_stays_addendum | pass | Model-transfer 0/216 evidence is present in the addendum and absent from the main three-boundary reports. | {'addendum_forced_bad': '0/216', 'main_0_216_occurrences': 0, 'selected_superiority_model_general': False} |
| H4_cross_version_marked_historical | pass | Artifact index labels the 0/85 hard_v2/hard_v3 synthesis as historical, not current top-level evidence. | {'cross_version_lines': ['| G4_cross_version_synthesis | Cross-Version Synthesis | Historical two-boundary synthesis of hard_v2 and hard_v3 claim boundaries.... |
| H5_index_0_85_mentions_are_legacy | pass | Any 0/85 mention in the artifact index is explicitly legacy or historical. | {'0/85_lines': ['| G4_cross_version_synthesis | Cross-Version Synthesis | Historical two-boundary synthesis of hard_v2 and hard_v3 claim boundaries. | Use on... |
| H6_no_positive_token_or_model_general_overclaim | pass | Current main/addendum reports do not positively claim token savings or model-general selected superiority. | {'disallowed_hits': []} |
| H7_no_retuning_guardrail_present | pass | No-retuning guardrails are present for the main boundary and the transfer addendum. | {'main_guardrail': True, 'addendum_forbidden_retuning': True} |
| H8_handoff_records_three_layers | pass | Handoff docs record the main boundary, model-transfer addendum, and their separation. | {'mentions_0_133_boundary': True, 'mentions_0_216': True, 'mentions_addendum': True} |

## Next Recommended Step

Use the hygiene audit before public commits or paper edits. If a new experiment is needed, predeclare a hard_v5 boundary instead of tuning hard_v3/hard_v4 failures.

## Source Files

| name | path | exists | sha256 | bytes |
| --- | --- | --- | --- | --- |
| boundary_synthesis | `benchmark/downstream/reports/downstream_boundary_synthesis.json` | True | `b5e58a54217563fb` | 45450 |
| paper_section | `benchmark/downstream/reports/downstream_paper_eval_section.json` | True | `f026bad7830e2a84` | 7062 |
| claim_defense | `benchmark/downstream/reports/downstream_claim_defense_matrix.json` | True | `09f38bb09aa273ea` | 41180 |
| model_transfer_addendum | `benchmark/downstream/reports/model_transfer_paper_addendum.json` | True | `56594365d4feb838` | 8044 |
| artifact_index | `benchmark/downstream/reports/paper_artifacts_index.json` | True | `5831022b8141dba4` | 50659 |
| boundary_synthesis_md | `benchmark/downstream/reports/downstream_boundary_synthesis.md` | True | `a9360eea565f3f41` | 12399 |
| paper_section_md | `benchmark/downstream/reports/downstream_paper_eval_section.md` | True | `19df606b4bd5459b` | 6712 |
| claim_defense_md | `benchmark/downstream/reports/downstream_claim_defense_matrix.md` | True | `67b226ce7fb63072` | 24680 |
| model_transfer_addendum_md | `benchmark/downstream/reports/model_transfer_paper_addendum.md` | True | `b03471c40abfc7bb` | 5668 |
| artifact_index_md | `benchmark/downstream/reports/paper_artifacts_index.md` | True | `029f2674291553cd` | 32621 |
| readme | `README.md` | True | `72a08cbf4e1e3735` | 3164 |
| experiment_handoff | `docs/experiment_handoff.md` | True | `4af6fae986de5697` | 55963 |
| paper_eval_status | `docs/paper_eval_status.md` | True | `306ceec14fe45a66` | 37657 |
| progress_log | `docs/progress_log.md` | True | `2e5a1b93cad2bd8a` | 107625 |

