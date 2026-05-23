# Paper Claim Consistency Audit

Generated at UTC: `2026-05-23T13:25:26.276055+00:00`

Consistency audit for the paper-facing hard_v2/hard_v3/hard_v4 downstream claim layer. This is a reporting-hygiene artifact, not new empirical evidence.

## Summary

| metric | value |
| --- | --- |
| total_checks | 13 |
| passed_checks | 13 |
| failed_checks | 0 |
| status | pass |

## Key Facts

| fact | value |
| --- | --- |
| forced_bad_total_success | 0/133 |
| forced_bad_total_tasks | 133 |
| forced_bad_total_public_passed_hidden_failed | 133 |
| forced_bad_phrase | 0/133 success with 133 public-pass/hidden-fail cases |
| hard_v4_strict_selected | 22/24 |
| hard_v4_strict_no_experience | 24/24 |
| selected_superiority_consistent | False |
| selected_token_savings_consistent | False |
| model_transfer_forced_bad_combined_success | 0/216 |
| model_transfer_forced_bad_public_passed_hidden_failed | 216 |
| model_transfer_hard_v4_strict_reversed | True |

## Checks

| check | status | summary | details |
| --- | --- | --- | --- |
| A1_boundary_forced_bad_aggregate | pass | Boundary synthesis keeps the three-suite forced_bad aggregate at 0/133. | {'forced_bad_total_success': '0/133', 'forced_bad_total_tasks': 133, 'forced_bad_total_public_passed_hidden_failed': 133, 'forced_bad_negative_transfer_consistent': True} |
| A2_paper_section_source_boundary | pass | Paper section is generated from downstream_boundary_synthesis.json, not the older cross-version synthesis. | {'paper_source_path': 'benchmark/downstream/reports/downstream_boundary_synthesis.json', 'expected_source_path': 'benchmark/downstream/reports/downstream_boundary_synthesis.json... |
| A3_paper_derived_values_match_boundary | pass | Paper section derived values, result count, and claim-limit count match the three-boundary source. | {'mismatches': {}, 'result_paragraphs': 6, 'claim_limits': 7} |
| A4_claim_defense_claim_set | pass | Claim-defense matrix keeps the expected ten paper-facing claim cards. | {'claim_count': 10, 'missing_claim_ids': []} |
| A5_claim_defense_source_packages | pass | Claim-defense matrix cites hard_v2, hard_v3, hard_v4, boundary synthesis, and paper section. | {'source_packages': ['hard_v2_evidence_package', 'hard_v3_evidence_package', 'hard_v4_evidence_package', 'downstream_boundary_synthesis', 'downstream_paper_eval_section']} |
| A6_c6_c9_evidence_sources | pass | C6 uses hard_v4 plus boundary synthesis, and C9 treats selected token savings as unsupported. | {'c6_sources': ['downstream_boundary_synthesis', 'hard_v2_evidence_package', 'hard_v3_evidence_package', 'hard_v4_evidence_package'], 'c9_status': 'not_supported_claim', 'c9_sou... |
| A7_artifact_index_key_facts | pass | Artifact index key facts match the current three-boundary reporting layer. | {'mismatches': {}} |
| A8_required_three_boundary_phrases | pass | Current report text contains the core three-boundary facts and guardrail wording. | {'missing_phrases': []} |
| A9_no_old_0_85_in_current_three_boundary_reports | pass | Current boundary, paper-section, and claim-defense reports do not reuse the old 0/85 aggregate. | {'old_0_85_occurrences': 0} |
| A10_guardrail_wording_present | pass | Generated paper artifacts preserve the no-universal-selected, no-token-savings, and no-retuning guardrails. | {'guardrail_text': 'Do not claim SkillAdmit-selected universally dominates no_experience.\nDo not claim SkillAdmit-selected is the universal best downstream context.\nDo not cla... |
| A11_hard_v4_boundary_is_explicit | pass | hard_v4 is stated as a stricter boundary, not a selected-utility win. | {'paper_summary': 'Overall, downstream validation gives a sharper claim boundary than admission accuracy alone. hard_v2 supports SkillAdmit-selected utility in a tree-aware codi... |
| A12_text_artifact_presence | pass | All Markdown/docs inputs used for paper-facing consistency checks exist. | {'boundary_synthesis_md': 'benchmark/downstream/reports/downstream_boundary_synthesis.md', 'paper_section_md': 'benchmark/downstream/reports/downstream_paper_eval_section.md', '... |
| A13_model_transfer_addendum_guardrails | pass | Model-transfer addendum preserves replication facts and does not overclaim selected superiority. | {'forced_bad_combined_success': '0/216', 'forced_bad_public_hidden': 216, 'hard_v4_strict_reversed': True, 'selected_superiority_model_general': False} |

## Claim Boundary

Supported:
- conditional downstream utility under specific settings
- hidden-verifier downstream validation is necessary
- forced harmful artifacts produce systematic negative transfer

Not supported:
- universal SkillAdmit-selected superiority
- cross-boundary selected token savings
- precondition-only generally replacing repository-tree context
- hard_v4 selected utility

## Next Recommended Step

If continuing experiments, use model-transfer reporting hygiene or a new predeclared hard_v5 boundary. Do not tune hard_v2, hard_v3, or hard_v4 from observed failures.

## Source Files

| name | path | exists | sha256 | bytes |
| --- | --- | --- | --- | --- |
| boundary_synthesis | `benchmark/downstream/reports/downstream_boundary_synthesis.json` | True | `b5e58a54217563fb` | 45450 |
| paper_section | `benchmark/downstream/reports/downstream_paper_eval_section.json` | True | `f026bad7830e2a84` | 7062 |
| claim_defense | `benchmark/downstream/reports/downstream_claim_defense_matrix.json` | True | `09f38bb09aa273ea` | 41180 |
| artifacts_index | `benchmark/downstream/reports/paper_artifacts_index.json` | True | `3aed8b46ba5c9871` | 52836 |
| model_transfer_addendum | `benchmark/downstream/reports/model_transfer_paper_addendum.json` | True | `56594365d4feb838` | 8044 |
| boundary_synthesis_md | `benchmark/downstream/reports/downstream_boundary_synthesis.md` | True | `a9360eea565f3f41` | 12399 |
| paper_section_md | `benchmark/downstream/reports/downstream_paper_eval_section.md` | True | `19df606b4bd5459b` | 6712 |
| claim_defense_md | `benchmark/downstream/reports/downstream_claim_defense_matrix.md` | True | `67b226ce7fb63072` | 24680 |
| artifacts_index_md | `benchmark/downstream/reports/paper_artifacts_index.md` | True | `26e10926e119715a` | 33967 |
| model_transfer_addendum_md | `benchmark/downstream/reports/model_transfer_paper_addendum.md` | True | `b03471c40abfc7bb` | 5668 |
| experiment_handoff | `docs/experiment_handoff.md` | True | `9d814c47db2a93d1` | 60877 |
| paper_eval_status | `docs/paper_eval_status.md` | True | `62039af9cec2dec9` | 42478 |
| progress_log | `docs/progress_log.md` | True | `64522aefb1a07d5b` | 114731 |
| readme | `README.md` | True | `d6657d08f67fd06d` | 5210 |
