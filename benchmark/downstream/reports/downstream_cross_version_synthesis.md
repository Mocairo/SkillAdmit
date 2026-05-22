# Downstream Cross-Version Synthesis

Generated at UTC: `2026-05-22T13:23:18.827390+00:00`

This report combines frozen hard_v2 and hard_v3 paper-facing evidence packages. It is an analysis artifact, not a new tuning run.

## Executive Claim Boundary

hard_v2 is positive evidence for tree-aware SkillAdmit-selected downstream utility. hard_v3 is boundary evidence showing that selected does not universally dominate. Across both suites, the strongest stable claim is that harmful admitted artifacts can cause systematic public-pass/hidden-fail negative transfer.

## Cross-Version Primary Table

| suite | setting | strategy | success | neg | public_hidden | adherence | tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hard_v2 | strict visible | No experience | 24/25 | 0 | 0 |  | 59272 |
| hard_v2 | strict visible | SkillAdmit-selected | 23/25 | 2 | 0 |  | 66608 |
| hard_v2 | strict visible | Raw memory | 22/25 | 3 | 0 |  | 56941 |
| hard_v2 | strict visible | Promoted rules | 21/25 | 4 | 1 |  | 77858 |
| hard_v2 | strict visible | Bad dependency rule | 22/25 | 2 | 0 |  | 75724 |
| hard_v2 | strict visible | All distilled skills | 25/25 | 0 | 0 |  | 84986 |
| hard_v2 | tree-aware | No experience | 23/25 | 2 | 0 |  | 51548 |
| hard_v2 | tree-aware | SkillAdmit-selected | 25/25 | 0 | 0 |  | 57597 |
| hard_v2 | tree-aware + preconditions | Selected + tree + preconditions | 25/25 | 0 | 0 |  | 67504 |
| hard_v2 | strict + preconditions only | Selected + preconditions only | 24/25 | 1 | 0 |  | 72316 |
| hard_v2 | forced harmful artifact | Forced bad artifact | 0/25 | 25 | 25 |  | 0 |
| hard_v3 | tree-aware | No experience | 29/30 | 1 | 0 | 30/30 | 70208 |
| hard_v3 | tree-aware | SkillAdmit-selected | 29/30 | 1 | 0 | 30/30 | 69291 |
| hard_v3 | tree-aware | Selected + tree + preconditions | 29/30 | 1 | 0 | 30/30 | 74559 |
| hard_v3 | tree-aware | Raw memory | 30/30 | 0 | 0 | 30/30 | 68753 |
| hard_v3 | tree-aware | All distilled skills | 30/30 | 0 | 0 | 30/30 | 75603 |
| hard_v3 | tree-aware | Bad dependency rule | 30/30 | 0 | 0 | 4/30 | 68671 |
| hard_v3 | tree-aware | Promoted rules | 29/30 | 1 | 1 | 30/30 | 73114 |
| hard_v3 | tree-aware | Forced bad artifact | 0/30 | 30 | 30 | 30/30 | 0 |
| hard_v3 | strict visible | No experience | 28/30 | 0 | 0 | 30/30 | 74153 |
| hard_v3 | strict visible | SkillAdmit-selected | 29/30 | 1 | 0 | 30/30 | 71390 |
| hard_v3 | strict visible | Selected + preconditions only | 30/30 | 0 | 0 | 30/30 | 82615 |
| hard_v3 | strict visible | Raw memory | 30/30 | 0 | 0 | 30/30 | 73789 |
| hard_v3 | strict visible | All distilled skills | 29/30 | 1 | 1 | 26/30 | 83366 |
| hard_v3 | strict visible | Bad dependency rule | 30/30 | 0 | 0 | 11/30 | 75920 |
| hard_v3 | strict visible | Promoted rules | 29/30 | 1 | 0 | 30/30 | 80112 |
| hard_v3 | strict visible | Forced bad artifact | 0/30 | 30 | 30 | 30/30 | 0 |

## Derived Synthesis

| comparison | value |
| --- | --- |
| forced_bad_negative_transfer_consistent | True |
| forced_bad_total_negative_transfer | 85 |
| forced_bad_total_public_passed_hidden_failed | 85 |
| forced_bad_total_successes | 0 |
| forced_bad_total_tasks | 85 |
| hard_v2_strict_all_skills_success_delta_vs_selected | 2 |
| hard_v2_strict_precondition_only_success_delta_vs_selected | 1 |
| hard_v2_strict_raw_success_delta_vs_no_experience | -2 |
| hard_v2_strict_selected_success_delta_vs_no_experience | -1 |
| hard_v2_strict_selected_token_delta_vs_no_experience | 7336 |
| hard_v2_tree_precondition_context_success_delta_vs_tree_selected | 0 |
| hard_v2_tree_precondition_context_token_delta_vs_tree_selected | 9907 |
| hard_v2_tree_selected_success_delta_vs_no_experience | 2 |
| hard_v2_tree_selected_token_delta_vs_no_experience | 6049 |
| hard_v3_strict_all_skills_success_delta_vs_selected | 0 |
| hard_v3_strict_precondition_only_success_delta_vs_selected | 1 |
| hard_v3_strict_precondition_only_token_delta_vs_selected | 11225 |
| hard_v3_strict_raw_success_delta_vs_no_experience | 2 |
| hard_v3_strict_selected_success_delta_vs_no_experience | 1 |
| hard_v3_strict_selected_token_delta_vs_no_experience | -2763 |
| hard_v3_tree_all_skills_success_delta_vs_selected | 1 |
| hard_v3_tree_precondition_context_success_delta_vs_selected | 0 |
| hard_v3_tree_precondition_context_token_delta_vs_selected | 5268 |
| hard_v3_tree_raw_success_delta_vs_no_experience | 1 |
| hard_v3_tree_selected_success_delta_vs_no_experience | 0 |
| hard_v3_tree_selected_token_delta_vs_no_experience | -917 |
| repo_tree_necessity_universal | False |
| selected_superiority_consistent | False |
| selected_token_savings_supported | False |

## Interpretation Ladder

- **Admission accuracy versus downstream utility**: v7 admission accuracy is useful regression evidence, but the paper-facing scientific signal now comes from hidden-verifier downstream behavior and negative-transfer controls.
- **SkillAdmit-selected**: hard_v2 supports tree-aware selected utility, but hard_v3 rejects a universal selected-superiority claim. The correct claim is conditional and suite-specific.
- **Repository tree and preconditions**: hard_v2 shows that repo tree can be more reliable than precondition text alone; hard_v3 shows that precondition-only can sometimes be enough. Treat both as task-context variables.
- **Token cost**: The cross-version evidence does not support a selected token-savings claim. Success and safety are the central claims, not economy.
- **Negative transfer**: Forced bad artifacts are the strongest stable signal: 0/85 success with 85 public-pass/hidden-fail cases.

## Supported Claims

- Downstream hidden-verifier evidence is stronger than admission-label accuracy alone for this project stage.
- Forced harmful artifacts produce systematic negative transfer across hard_v2 and hard_v3: 0/85 success with 85 public-pass/hidden-fail cases.
- hard_v2 supports a positive tree-aware SkillAdmit-selected result: 25/25 versus 23/25 for no_experience, with 25/25 replicated.
- hard_v3 is boundary evidence: tree-aware selected ties no_experience at 29/30, and strict selected is only 29/30 while other conditions reach 30/30.
- Repo tree and precondition context are important variables, but their effects are suite-dependent rather than universal.
- Raw memory must remain a serious comparison condition because it is weak on hard_v2 strict visible-file but reaches 30/30 in both hard_v3 settings.
- Bad dependency advice is only interpretable through the forced control: ordinary bad_dependency_rule rows have low artifact adherence on hard_v3.

## Unsupported Claims

- Do not claim SkillAdmit-selected universally dominates no_experience.
- Do not claim SkillAdmit-selected is the universal best downstream context.
- Do not claim SkillAdmit-selected has established cross-version token savings.
- Do not claim precondition-only replaces repository context in general.
- Do not claim raw memory is a safe admission policy from hard_v3 success alone.
- Do not claim bad dependency advice is safe when the model often ignored it.
- Do not tune hard_v2 or hard_v3 failures while still treating those suites as clean evidence.

## Source Package Hashes

| suite | package | sha256 | generated_at_utc |
| --- | --- | --- | --- |
| hard_v2 | `benchmark/downstream/reports/hard_v2_evidence_package.json` | `7deb038d4adfc285` | `2026-05-22T05:36:13.500710+00:00` |
| hard_v3 | `benchmark/downstream/reports/hard_v3_evidence_package.json` | `894b8f7a1f7ac296` | `2026-05-22T13:03:52.487189+00:00` |

