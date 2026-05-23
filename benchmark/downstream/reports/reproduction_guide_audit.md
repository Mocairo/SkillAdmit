# Reproduction Guide Audit

Generated at UTC: `2026-05-23T13:25:26.479760+00:00`

Public reproduction-guide audit for SkillAdmit. It checks that the public entry guide matches the generated downstream evidence boundary and avoids unsupported claims.

## Summary

| metric | value |
| --- | --- |
| total_checks | 13 |
| passed_checks | 13 |
| failed_checks | 0 |
| status | pass |

## Aggregate Roles

| layer | aggregate | public_hidden | role |
| --- | --- | --- | --- |
| current_main_boundary | 0/133 | 133 | hard_v2/hard_v3/hard_v4 downstream validation |
| model_transfer_addendum | 0/216 | 216 | two-model hard_v3/hard_v4 sensitivity layer |
| historical_two_boundary | 0/85 |  | historical hard_v2/hard_v3 synthesis only |

## Checks

| check | status | summary | details |
| --- | --- | --- | --- |
| RG1_guide_is_discoverable | pass | README points to the reproduction guide and the guide exists. | {'guide_exists': True, 'readme_links_guide': True} |
| RG2_commands_present_and_scripts_exist | pass | Required report-regeneration and audit commands are present and their scripts exist. | {'missing_commands': [], 'missing_scripts': []} |
| RG3_artifact_index_exposes_guide | pass | Artifact index exposes the reproduction guide and the guide audit command. | {'has_group': True, 'has_audit_command': True} |
| RG4_main_boundary_aggregate_matches_report | pass | Guide reports the current hard_v2/hard_v3/hard_v4 main boundary aggregate. | {'report_forced_bad': '0/133', 'report_public_hidden': 133} |
| RG5_addendum_aggregate_matches_report | pass | Guide reports the model-transfer addendum aggregate without merging it into the main boundary. | {'report_forced_bad': '0/216', 'report_public_hidden': 216} |
| RG6_layer_roles_are_separated | pass | Guide separates current, addendum, and historical aggregate roles. | {} |
| RG7_claim_guardrails_present | pass | Guide includes unsupported-claim guardrails. | {} |
| RG8_no_retuning_rule_present | pass | Guide states the frozen-boundary no-retuning rule. | {} |
| RG9_secret_and_no_api_boundary_present | pass | Guide states the local-secret boundary and avoids accidental API reruns. | {} |
| RG10_guide_declares_not_new_evidence | pass | Guide is explicitly marked as a reproduction entry, not an evidence source. | {} |
| RG11_readme_names_reader_entry_points | pass | README names the public reproduction guide, artifact index, main boundary, and transfer addendum. | {} |
| RG12_readme_preserves_public_claim_boundary | pass | README exposes the aggregate roles and unsupported-claim guardrails. | {} |
| RG13_public_surface_avoids_local_paths | pass | README and reproduction guide avoid machine-specific absolute paths. | {'forbidden_public_surface_hits': []} |

## Checked Commands

| command | present_in_guide | script_exists |
| --- | --- | --- |
| `python scripts/check_downstream_hard_v2_tasks.py` | True | True |
| `python scripts/check_downstream_hard_v3_tasks.py` | True | True |
| `python scripts/build_downstream_hard_v4_tasks.py` | True | True |
| `python scripts/check_downstream_hard_v4_tasks.py` | True | True |
| `python scripts/run_admission_regression.py` | True | True |
| `python scripts/summarize_hard_v2_results.py --assert-current-hard-v2` | True | True |
| `python scripts/export_hard_v2_evidence_package.py --assert-current-hard-v2` | True | True |
| `python scripts/summarize_hard_v3_results.py --assert-current-hard-v3` | True | True |
| `python scripts/export_hard_v3_evidence_package.py --assert-current-hard-v3` | True | True |
| `python scripts/export_hard_v4_scaffold_manifest.py --run-checker --assert-current-hard-v4-scaffold` | True | True |
| `python scripts/summarize_hard_v4_results.py --assert-current-hard-v4` | True | True |
| `python scripts/export_hard_v4_evidence_package.py --assert-current-hard-v4` | True | True |
| `python scripts/export_downstream_cross_version_synthesis.py --assert-current-synthesis` | True | True |
| `python scripts/export_downstream_boundary_synthesis.py --assert-current-boundary-synthesis` | True | True |
| `python scripts/export_downstream_paper_section.py --assert-current-paper-section` | True | True |
| `python scripts/export_downstream_claim_defense_matrix.py --assert-current-claim-defense` | True | True |
| `python scripts/export_model_transfer_replication_protocol.py --assert-current-protocol` | True | True |
| `python scripts/export_model_transfer_evidence_package.py --assert-current-model-transfer` | True | True |
| `python scripts/export_model_transfer_cross_model_synthesis.py --assert-current-cross-model` | True | True |
| `python scripts/export_model_transfer_paper_addendum.py --assert-current-addendum` | True | True |
| `python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index` | True | True |
| `python scripts/audit_paper_claim_consistency.py --assert-current-audit` | True | True |
| `python scripts/audit_reporting_hygiene.py --assert-current-hygiene` | True | True |
| `python scripts/audit_public_release_readiness.py --assert-current-release` | True | True |
| `python scripts/audit_reproduction_guide.py --assert-current-reproduction-guide` | True | True |
| `python scripts/audit_release_candidate.py --assert-current-release-candidate` | True | True |

## Next Recommended Step

Use this audit with the claim, reporting, and release audits before public README edits or release pushes.

## Source Files

| name | path | exists | sha256 | bytes |
| --- | --- | --- | --- | --- |
| reproduction_guide | `docs/reproduction_guide.md` | True | `0918a129516c446c` | 6853 |
| readme | `README.md` | True | `d6657d08f67fd06d` | 5210 |
| artifact_index | `benchmark/downstream/reports/paper_artifacts_index.json` | True | `3aed8b46ba5c9871` | 52836 |
| boundary_synthesis | `benchmark/downstream/reports/downstream_boundary_synthesis.json` | True | `b5e58a54217563fb` | 45450 |
| cross_model_synthesis | `benchmark/downstream/reports/model_transfer_cross_model_synthesis.json` | True | `4e6df53551a1e8f2` | 68222 |

