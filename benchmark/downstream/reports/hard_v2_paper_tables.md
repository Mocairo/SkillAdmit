# Hard v2 Evidence Package

Generated at: `2026-05-22T05:36:13.500710+00:00`

## Primary Strategy Table

| setting | strategy | success | negative_transfer | public_hidden | tokens |
| --- | --- | --- | --- | --- | --- |
| strict visible | No experience | 24/25 | 0 | 0 | 59272 |
| strict visible | SkillAdmit-selected | 23/25 | 2 | 0 | 66608 |
| strict visible | Raw memory | 22/25 | 3 | 0 | 56941 |
| strict visible | Promoted rules | 21/25 | 4 | 1 | 77858 |
| strict visible | Bad dependency rule | 22/25 | 2 | 0 | 75724 |
| strict visible | All distilled skills | 25/25 | 0 | 0 | 84986 |
| tree-aware | No experience | 23/25 | 2 | 0 | 51548 |
| tree-aware | SkillAdmit-selected | 25/25 | 0 | 0 | 57597 |
| tree-aware + preconditions | Selected + tree + preconditions | 25/25 | 0 | 0 | 67504 |
| strict + preconditions only | Selected + preconditions only | 24/25 | 1 | 0 | 72316 |
| forced harmful artifact | Forced bad artifact | 0/25 | 25 | 25 | 0 |

## Stability Table

| group | successes | tokens | failure tasks |
| --- | --- | --- | --- |
| tree_aware_skilladmit_selected | [25, 25] | [57597, 52144] | llm_downstream_hard_v2_tree_25x2: none; llm_downstream_hard_v2_replication_tree_selected_25: none |
| tree_aware_selected_precondition_context | [25, 25] | [67504, 64150] | llm_downstream_hard_v2_selected_precondition_25: none; llm_downstream_hard_v2_replication_selected_precondition_25: none |
| strict_precondition_only | [24, 23] | [72316, 77487] | llm_downstream_hard_v2_precondition_only_25: hard_v2_py_import_012; llm_downstream_hard_v2_replication_precondition_only_25: hard_v2_py_import_012, hard_v2_py_import_018 |

## Failure Taxonomy

| setting | strategy | template | failures |
| --- | --- | --- | --- |
| canary_visible_file | no_experience | T4_cwd_sensitive_path_hard | 1 |
| forced_bad_standalone | forced_bad_artifact | T1_unused_missing_import_hard | 5 |
| forced_bad_standalone | forced_bad_artifact | T2_local_module_import_hard | 5 |
| forced_bad_standalone | forced_bad_artifact | T3_script_relative_import_hard | 5 |
| forced_bad_standalone | forced_bad_artifact | T4_cwd_sensitive_path_hard | 5 |
| forced_bad_standalone | forced_bad_artifact | T5_package_internal_import_hard | 5 |
| replication_strict_precondition_only | skilladmit_selected_with_precondition_only | T3_script_relative_import_hard | 1 |
| replication_strict_precondition_only | skilladmit_selected_with_precondition_only | T4_cwd_sensitive_path_hard | 1 |
| strict_precondition_only | skilladmit_selected_with_precondition_only | T3_script_relative_import_hard | 1 |
| strict_visible_file | bad_dependency_rule | T2_local_module_import_hard | 1 |
| strict_visible_file | bad_dependency_rule | T3_script_relative_import_hard | 1 |
| strict_visible_file | bad_dependency_rule | T4_cwd_sensitive_path_hard | 1 |
| strict_visible_file | forced_bad_artifact | T1_unused_missing_import_hard | 5 |
| strict_visible_file | forced_bad_artifact | T2_local_module_import_hard | 5 |
| strict_visible_file | forced_bad_artifact | T3_script_relative_import_hard | 5 |
| strict_visible_file | forced_bad_artifact | T4_cwd_sensitive_path_hard | 5 |
| strict_visible_file | forced_bad_artifact | T5_package_internal_import_hard | 5 |
| strict_visible_file | no_experience | T2_local_module_import_hard | 1 |
| strict_visible_file | promoted_rules | T2_local_module_import_hard | 1 |
| strict_visible_file | promoted_rules | T4_cwd_sensitive_path_hard | 2 |
| strict_visible_file | promoted_rules | T5_package_internal_import_hard | 1 |
| strict_visible_file | raw_memory | T4_cwd_sensitive_path_hard | 3 |
| strict_visible_file | skilladmit_selected | T4_cwd_sensitive_path_hard | 2 |
| tree_aware | no_experience | T3_script_relative_import_hard | 1 |
| tree_aware | no_experience | T4_cwd_sensitive_path_hard | 1 |

## Derived Comparisons

- `tree_aware_selected_success_delta_vs_no_experience`: 2
- `tree_aware_selected_token_delta_vs_no_experience`: 6049
- `selected_precondition_token_delta_vs_tree_selected`: 9907
- `selected_precondition_token_delta_vs_all_skills`: -17482
- `strict_precondition_only_success_delta_vs_strict_selected`: 1

## Supported Claims

- Hard v2 is a validated 25-task downstream suite with fail-first, gold-pass, forced-public-pass, and forced-hidden-fail checks.
- Forced harmful artifacts produce systematic negative transfer: 0/25 success with 25 public-pass/hidden-fail cases.
- In the tree-aware coding-agent setting, SkillAdmit-selected reached 25/25 while no_experience reached 23/25 in the original hard_v2 tree-aware run.
- Tree-aware SkillAdmit-selected is stable across the two completed full 25-task calls: 25/25 and 25/25.
- Tree-aware selected + precondition context is also stable across two completed calls: 25/25 and 25/25.
- Strict precondition-only is a weaker ablation, not a replacement for repo-tree context: 24/25 on the first run and 23/25 on replication.

## Unsupported Claims

- SkillAdmit-selected dominates every baseline under every prompt setting.
- SkillAdmit-selected has demonstrated token savings over no_experience on hard_v2.
- Selected + precondition context is more accurate than ordinary tree-aware selected.
- Precondition text alone can replace repository-tree context.
- Admission-label accuracy alone proves downstream utility.
- The current v7 admission set remains clean held-out evidence after error inspection or tuning.
