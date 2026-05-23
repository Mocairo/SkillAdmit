# Model-Transfer Cross-Model Synthesis

Generated at UTC: `2026-05-23T11:37:24.118320+00:00`

Cross-model synthesis over frozen hard_v3/hard_v4 downstream evidence. This report separates replicated findings from model-sensitive findings.

Models: baseline `mimo-v2.5-pro`, transfer `mimo-v2.5`.

## Paired Strategy Table

| suite | setting | strategy | baseline_success | transfer_success | transfer_minus_baseline | baseline_tokens | transfer_tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hard_v3 | tree-aware | No experience | 29/30 | 29/30 | 0 | 70208 | 74743 |
| hard_v3 | tree-aware | SkillAdmit-selected | 29/30 | 29/30 | 0 | 69291 | 69501 |
| hard_v3 | tree-aware | Selected + tree + preconditions | 29/30 | 29/30 | 0 | 74559 | 76365 |
| hard_v3 | tree-aware | Raw memory | 30/30 | 30/30 | 0 | 68753 | 90762 |
| hard_v3 | tree-aware | All distilled skills | 30/30 | 28/30 | -2 | 75603 | 91349 |
| hard_v3 | tree-aware | Promoted rules | 29/30 | 29/30 | 0 | 73114 | 80244 |
| hard_v3 | tree-aware | Bad dependency rule | 30/30 | 29/30 | -1 | 68671 | 71658 |
| hard_v3 | tree-aware | Forced bad artifact | 0/30 | 0/30 | 0 | 0 | 0 |
| hard_v3 | strict visible | No experience | 28/30 | 28/30 | 0 | 74153 | 75266 |
| hard_v3 | strict visible | SkillAdmit-selected | 29/30 | 29/30 | 0 | 71390 | 76964 |
| hard_v3 | strict visible | Selected + preconditions only | 30/30 | 29/30 | -1 | 82615 | 92936 |
| hard_v3 | strict visible | Raw memory | 30/30 | 30/30 | 0 | 73789 | 96811 |
| hard_v3 | strict visible | All distilled skills | 29/30 | 29/30 | 0 | 83366 | 102654 |
| hard_v3 | strict visible | Promoted rules | 29/30 | 26/30 | -3 | 80112 | 89566 |
| hard_v3 | strict visible | Bad dependency rule | 30/30 | 29/30 | -1 | 75920 | 83647 |
| hard_v3 | strict visible | Forced bad artifact | 0/30 | 0/30 | 0 | 0 | 0 |
| hard_v4 | tree-aware | No experience | 24/24 | 23/24 | -1 | 46685 | 55349 |
| hard_v4 | tree-aware | SkillAdmit-selected | 24/24 | 24/24 | 0 | 48682 | 59210 |
| hard_v4 | tree-aware | Selected + tree + preconditions | 24/24 | 24/24 | 0 | 63586 | 62050 |
| hard_v4 | tree-aware | Raw memory | 24/24 | 24/24 | 0 | 53406 | 73337 |
| hard_v4 | tree-aware | All distilled skills | 24/24 | 24/24 | 0 | 68776 | 76408 |
| hard_v4 | tree-aware | Promoted rules | 24/24 | 24/24 | 0 | 58813 | 59895 |
| hard_v4 | tree-aware | Bad dependency rule | 24/24 | 21/24 | -3 | 51974 | 57645 |
| hard_v4 | tree-aware | Forced bad artifact | 0/24 | 0/24 | 0 | 0 | 0 |
| hard_v4 | strict visible | No experience | 24/24 | 18/24 | -6 | 53055 | 63619 |
| hard_v4 | strict visible | SkillAdmit-selected | 22/24 | 21/24 | -1 | 58450 | 64041 |
| hard_v4 | strict visible | Selected + preconditions only | 23/24 | 20/24 | -3 | 69961 | 74966 |
| hard_v4 | strict visible | Raw memory | 23/24 | 18/24 | -5 | 65070 | 78604 |
| hard_v4 | strict visible | All distilled skills | 24/24 | 19/24 | -5 | 69049 | 77720 |
| hard_v4 | strict visible | Promoted rules | 23/24 | 20/24 | -3 | 69221 | 75981 |
| hard_v4 | strict visible | Bad dependency rule | 24/24 | 18/24 | -6 | 63789 | 71628 |
| hard_v4 | strict visible | Forced bad artifact | 0/24 | 0/24 | 0 | 0 | 0 |

## Selected Versus No Experience

| role | model | suite | setting | selected | no_experience | success_delta | token_delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | mimo-v2.5-pro | hard_v3 | tree-aware | 29/30 | 29/30 | 0 | -917 |
| baseline | mimo-v2.5-pro | hard_v3 | strict visible | 29/30 | 28/30 | 1 | -2763 |
| baseline | mimo-v2.5-pro | hard_v4 | tree-aware | 24/24 | 24/24 | 0 | 1997 |
| baseline | mimo-v2.5-pro | hard_v4 | strict visible | 22/24 | 24/24 | -2 | 5395 |
| transfer | mimo-v2.5 | hard_v3 | tree-aware | 29/30 | 29/30 | 0 | -5242 |
| transfer | mimo-v2.5 | hard_v3 | strict visible | 29/30 | 28/30 | 1 | 1698 |
| transfer | mimo-v2.5 | hard_v4 | tree-aware | 24/24 | 23/24 | 1 | 3861 |
| transfer | mimo-v2.5 | hard_v4 | strict visible | 21/24 | 18/24 | 3 | 422 |

## Selected Sensitivity

| suite | setting | baseline_delta | transfer_delta | pattern |
| --- | --- | --- | --- | --- |
| hard_v3 | tree-aware | 0 | 0 | same_sign |
| hard_v3 | strict visible | 1 | 1 | same_sign |
| hard_v4 | tree-aware | 0 | 1 | weakened_or_strengthened_from_tie |
| hard_v4 | strict visible | -2 | 3 | reversed_sign |

## Context Comparisons

| role | suite | setting | comparison | left_success | right_success | success_delta | token_delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | hard_v3 | tree-aware | tree precondition context vs selected | 29/30 | 29/30 | 0 | 5268 |
| baseline | hard_v4 | tree-aware | tree precondition context vs selected | 24/24 | 24/24 | 0 | 14904 |
| baseline | hard_v3 | strict visible | strict precondition-only vs selected | 30/30 | 29/30 | 1 | 11225 |
| baseline | hard_v4 | strict visible | strict precondition-only vs selected | 23/24 | 22/24 | 1 | 11511 |
| baseline | hard_v3 | strict visible | strict precondition-only vs no_experience | 30/30 | 28/30 | 2 | 8462 |
| baseline | hard_v4 | strict visible | strict precondition-only vs no_experience | 23/24 | 24/24 | -1 | 16906 |
| transfer | hard_v3 | tree-aware | tree precondition context vs selected | 29/30 | 29/30 | 0 | 6864 |
| transfer | hard_v4 | tree-aware | tree precondition context vs selected | 24/24 | 24/24 | 0 | 2840 |
| transfer | hard_v3 | strict visible | strict precondition-only vs selected | 29/30 | 29/30 | 0 | 15972 |
| transfer | hard_v4 | strict visible | strict precondition-only vs selected | 20/24 | 21/24 | -1 | 10925 |
| transfer | hard_v3 | strict visible | strict precondition-only vs no_experience | 29/30 | 28/30 | 1 | 17670 |
| transfer | hard_v4 | strict visible | strict precondition-only vs no_experience | 20/24 | 18/24 | 2 | 11347 |

## Forced Bad Artifact Replication

| role | model | success | negative_transfer | public_hidden |
| --- | --- | --- | --- | --- |
| baseline | mimo-v2.5-pro | 0/108 | 108 | 108 |
| transfer | mimo-v2.5 | 0/108 | 108 | 108 |

Combined: `0/216` success, `216` public-pass/hidden-fail cases.

## Derived Claim Flags

| flag | value |
| --- | --- |
| forced_bad_combined_public_passed_hidden_failed | 216 |
| forced_bad_combined_success | 0/216 |
| forced_bad_replication_across_models | True |
| hard_v3_strict_selected_plus_one_replicated | True |
| hard_v3_tree_selected_tie_replicated | True |
| hard_v4_strict_selected_delta_baseline | -2 |
| hard_v4_strict_selected_delta_reversed | True |
| hard_v4_strict_selected_delta_transfer | 3 |
| precondition_only_better_than_selected_model_general | False |
| precondition_only_success_delta_vs_selected_values | {"baseline_hard_v3": 1, "baseline_hard_v4": 1, "transfer_hard_v3": 0, "transfer_hard_v4": -1} |
| selected_success_delta_values | {"baseline_hard_v3_tree-aware": 0, "baseline_hard_v3_strict_visible": 1, "baseline_hard_v4_tree-aware": 0, "baseline_hard_v4_strict_visible": -2, "transfer_hard_v3_tree-aware": 0, "transfer_hard_v3_strict_visible": 1, "transfer_hard_v4_tree-aware": 1, "transfer_hard_v4_strict_visible": 3} |
| selected_superiority_model_general | False |
| selected_token_delta_values | {"baseline_hard_v3_tree-aware": -917, "baseline_hard_v3_strict_visible": -2763, "baseline_hard_v4_tree-aware": 1997, "baseline_hard_v4_strict_visible": 5395, "transfer_hard_v3_tree-aware": -5242, "transfer_hard_v3_strict_visible": 1698, "transfer_hard_v4_tree-aware": 3861, "transfer_hard_v4_strict_visible": 422} |
| selected_token_savings_model_general | False |

## Supported Claims

- Forced bad artifacts replicate across the two-model hard_v3/hard_v4 comparison: baseline 0/108 and transfer 0/108, with 216 total public-pass/hidden-fail cases.
- The hard_v3 selected-vs-no-experience pattern is stable across the two models: tree-aware ties at 29/30, and strict visible-file selected is +1 task over no_experience.
- The hard_v4 strict selected comparison is model-sensitive: baseline selected trails no_experience by two tasks, while transfer selected beats no_experience by three tasks.
- Precondition-only is not model-general selected improvement: it is +1 over selected in both baseline strict settings, but ties or trails selected for the transfer model.

## Unsupported Claims

- Do not claim model-general SkillAdmit-selected superiority.
- Do not claim selected token savings across models.
- Do not claim precondition-only generally replaces repository context.
- Do not use model-transfer results to retune hard_v3 or hard_v4.
- Do not treat the second model as a new clean task boundary; it is a model-transfer replication over frozen tasks.

## Source Package Hashes

| name | path | sha256 | generated_at_utc |
| --- | --- | --- | --- |
| hard_v3_evidence_package | `benchmark/downstream/reports/hard_v3_evidence_package.json` | `894b8f7a1f7ac296` | `2026-05-22T13:03:52.487189+00:00` |
| hard_v4_evidence_package | `benchmark/downstream/reports/hard_v4_evidence_package.json` | `c7e729993e44503b` | `2026-05-23T04:55:41.380270+00:00` |
| model_transfer_evidence_package | `benchmark/downstream/reports/model_transfer_evidence_package.json` | `32505f40e1635dcf` | `2026-05-23T10:22:44.498111+00:00` |

