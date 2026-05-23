# Model-Transfer Evidence Package

Generated at UTC: `2026-05-23T11:37:24.226464+00:00`

Model-transfer evidence package for the predeclared hard_v3/hard_v4 replication matrix. This is post-run evidence, not prompt tuning.

Transfer model: `mimo-v2.5`. Baseline model label for later cross-model synthesis: `mimo-v2.5-pro`.

## Run Completion

| run_id | run_name | models | rows | expected | parse_errors | summary_sha256 | trajectories_sha256 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MT1_hard_v3_tree | llm_downstream_hard_v3_transfer_mimo_v2_5_tree_30x8 | mimo-v2.5 | 240 | 240 | 0 | `796fab16f8459aa4` | `5812d1f9f377888c` |
| MT2_hard_v3_strict | llm_downstream_hard_v3_transfer_mimo_v2_5_strict_30x8 | mimo-v2.5 | 240 | 240 | 0 | `724eb502e7e4f7eb` | `c60e3ec39ff5a850` |
| MT3_hard_v4_tree | llm_downstream_hard_v4_transfer_mimo_v2_5_tree_24x8 | mimo-v2.5 | 192 | 192 | 0 | `1708e23957a4aebf` | `a496aa253bfe215e` |
| MT4_hard_v4_strict | llm_downstream_hard_v4_transfer_mimo_v2_5_strict_24x8 | mimo-v2.5 | 192 | 192 | 0 | `b4e74dd55ff2c34c` | `26797f7286b623fe` |

## Primary Strategy Table

| suite | setting | strategy | model | success | neg | public_hidden | adherence | tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hard_v3 | tree-aware | No experience | mimo-v2.5 | 29/30 | 1 | 0 | 30/30 | 74743 |
| hard_v3 | tree-aware | SkillAdmit-selected | mimo-v2.5 | 29/30 | 1 | 1 | 30/30 | 69501 |
| hard_v3 | tree-aware | Selected + tree + preconditions | mimo-v2.5 | 29/30 | 1 | 1 | 30/30 | 76365 |
| hard_v3 | tree-aware | Raw memory | mimo-v2.5 | 30/30 | 0 | 0 | 30/30 | 90762 |
| hard_v3 | tree-aware | All distilled skills | mimo-v2.5 | 28/30 | 2 | 0 | 29/30 | 91349 |
| hard_v3 | tree-aware | Promoted rules | mimo-v2.5 | 29/30 | 1 | 0 | 30/30 | 80244 |
| hard_v3 | tree-aware | Bad dependency rule | mimo-v2.5 | 29/30 | 1 | 0 | 9/30 | 71658 |
| hard_v3 | tree-aware | Forced bad artifact | mimo-v2.5 | 0/30 | 30 | 30 | 30/30 | 0 |
| hard_v3 | strict visible | No experience | mimo-v2.5 | 28/30 | 2 | 0 | 30/30 | 75266 |
| hard_v3 | strict visible | SkillAdmit-selected | mimo-v2.5 | 29/30 | 1 | 0 | 29/30 | 76964 |
| hard_v3 | strict visible | Selected + preconditions only | mimo-v2.5 | 29/30 | 1 | 0 | 30/30 | 92936 |
| hard_v3 | strict visible | Raw memory | mimo-v2.5 | 30/30 | 0 | 0 | 30/30 | 96811 |
| hard_v3 | strict visible | All distilled skills | mimo-v2.5 | 29/30 | 1 | 0 | 30/30 | 102654 |
| hard_v3 | strict visible | Promoted rules | mimo-v2.5 | 26/30 | 4 | 1 | 30/30 | 89566 |
| hard_v3 | strict visible | Bad dependency rule | mimo-v2.5 | 29/30 | 1 | 0 | 10/30 | 83647 |
| hard_v3 | strict visible | Forced bad artifact | mimo-v2.5 | 0/30 | 30 | 30 | 30/30 | 0 |
| hard_v4 | tree-aware | No experience | mimo-v2.5 | 23/24 | 1 | 0 | 24/24 | 55349 |
| hard_v4 | tree-aware | SkillAdmit-selected | mimo-v2.5 | 24/24 | 0 | 0 | 24/24 | 59210 |
| hard_v4 | tree-aware | Selected + tree + preconditions | mimo-v2.5 | 24/24 | 0 | 0 | 24/24 | 62050 |
| hard_v4 | tree-aware | Raw memory | mimo-v2.5 | 24/24 | 0 | 0 | 24/24 | 73337 |
| hard_v4 | tree-aware | All distilled skills | mimo-v2.5 | 24/24 | 0 | 0 | 22/24 | 76408 |
| hard_v4 | tree-aware | Promoted rules | mimo-v2.5 | 24/24 | 0 | 0 | 24/24 | 59895 |
| hard_v4 | tree-aware | Bad dependency rule | mimo-v2.5 | 21/24 | 3 | 3 | 6/24 | 57645 |
| hard_v4 | tree-aware | Forced bad artifact | mimo-v2.5 | 0/24 | 24 | 24 | 24/24 | 0 |
| hard_v4 | strict visible | No experience | mimo-v2.5 | 18/24 | 6 | 4 | 24/24 | 63619 |
| hard_v4 | strict visible | SkillAdmit-selected | mimo-v2.5 | 21/24 | 3 | 0 | 24/24 | 64041 |
| hard_v4 | strict visible | Selected + preconditions only | mimo-v2.5 | 20/24 | 4 | 1 | 24/24 | 74966 |
| hard_v4 | strict visible | Raw memory | mimo-v2.5 | 18/24 | 6 | 0 | 24/24 | 78604 |
| hard_v4 | strict visible | All distilled skills | mimo-v2.5 | 19/24 | 5 | 0 | 23/24 | 77720 |
| hard_v4 | strict visible | Promoted rules | mimo-v2.5 | 20/24 | 4 | 1 | 24/24 | 75981 |
| hard_v4 | strict visible | Bad dependency rule | mimo-v2.5 | 18/24 | 5 | 0 | 12/24 | 71628 |
| hard_v4 | strict visible | Forced bad artifact | mimo-v2.5 | 0/24 | 24 | 24 | 24/24 | 0 |

## Selected Versus No Experience

| suite | setting | selected | no_experience | success_delta | token_delta |
| --- | --- | --- | --- | --- | --- |
| hard_v3 | tree-aware | 29/30 | 29/30 | 0 | -5242 |
| hard_v3 | strict visible | 29/30 | 28/30 | 1 | 1698 |
| hard_v4 | tree-aware | 24/24 | 23/24 | 1 | 3861 |
| hard_v4 | strict visible | 21/24 | 18/24 | 3 | 422 |

## Context Comparisons

| suite | setting | comparison | left_success | right_success | success_delta | token_delta |
| --- | --- | --- | --- | --- | --- | --- |
| hard_v3 | tree-aware | tree precondition context vs selected | 29/30 | 29/30 | 0 | 6864 |
| hard_v4 | tree-aware | tree precondition context vs selected | 24/24 | 24/24 | 0 | 2840 |
| hard_v3 | strict visible | strict precondition-only vs selected | 29/30 | 29/30 | 0 | 15972 |
| hard_v4 | strict visible | strict precondition-only vs selected | 20/24 | 21/24 | -1 | 10925 |
| hard_v3 | strict visible | strict precondition-only vs no_experience | 29/30 | 28/30 | 1 | 17670 |
| hard_v4 | strict visible | strict precondition-only vs no_experience | 20/24 | 18/24 | 2 | 11347 |

## Forced Bad Artifact Aggregate

| suite | setting | success | negative_transfer | public_hidden |
| --- | --- | --- | --- | --- |
| hard_v3 | tree-aware | 0/30 | 30 | 30 |
| hard_v3 | strict visible | 0/30 | 30 | 30 |
| hard_v4 | tree-aware | 0/24 | 24 | 24 |
| hard_v4 | strict visible | 0/24 | 24 | 24 |

Total: `0/108` success, `108` public-pass/hidden-fail cases.

## Artifact Adherence

| suite | setting | strategy | success | adherence | adherence_rate | public_hidden |
| --- | --- | --- | --- | --- | --- | --- |
| hard_v3 | tree-aware | SkillAdmit-selected | 29/30 | 30/30 | 1.0 | 1 |
| hard_v3 | tree-aware | Selected + tree + preconditions | 29/30 | 30/30 | 1.0 | 1 |
| hard_v3 | tree-aware | Raw memory | 30/30 | 30/30 | 1.0 | 0 |
| hard_v3 | tree-aware | All distilled skills | 28/30 | 29/30 | 0.9667 | 0 |
| hard_v3 | tree-aware | Promoted rules | 29/30 | 30/30 | 1.0 | 0 |
| hard_v3 | tree-aware | Bad dependency rule | 29/30 | 9/30 | 0.3 | 0 |
| hard_v3 | tree-aware | Forced bad artifact | 0/30 | 30/30 | 1.0 | 30 |
| hard_v3 | strict visible | SkillAdmit-selected | 29/30 | 29/30 | 0.9667 | 0 |
| hard_v3 | strict visible | Selected + preconditions only | 29/30 | 30/30 | 1.0 | 0 |
| hard_v3 | strict visible | Raw memory | 30/30 | 30/30 | 1.0 | 0 |
| hard_v3 | strict visible | All distilled skills | 29/30 | 30/30 | 1.0 | 0 |
| hard_v3 | strict visible | Promoted rules | 26/30 | 30/30 | 1.0 | 1 |
| hard_v3 | strict visible | Bad dependency rule | 29/30 | 10/30 | 0.3333 | 0 |
| hard_v3 | strict visible | Forced bad artifact | 0/30 | 30/30 | 1.0 | 30 |
| hard_v4 | tree-aware | SkillAdmit-selected | 24/24 | 24/24 | 1.0 | 0 |
| hard_v4 | tree-aware | Selected + tree + preconditions | 24/24 | 24/24 | 1.0 | 0 |
| hard_v4 | tree-aware | Raw memory | 24/24 | 24/24 | 1.0 | 0 |
| hard_v4 | tree-aware | All distilled skills | 24/24 | 22/24 | 0.9167 | 0 |
| hard_v4 | tree-aware | Promoted rules | 24/24 | 24/24 | 1.0 | 0 |
| hard_v4 | tree-aware | Bad dependency rule | 21/24 | 6/24 | 0.25 | 3 |
| hard_v4 | tree-aware | Forced bad artifact | 0/24 | 24/24 | 1.0 | 24 |
| hard_v4 | strict visible | SkillAdmit-selected | 21/24 | 24/24 | 1.0 | 0 |
| hard_v4 | strict visible | Selected + preconditions only | 20/24 | 24/24 | 1.0 | 1 |
| hard_v4 | strict visible | Raw memory | 18/24 | 24/24 | 1.0 | 0 |
| hard_v4 | strict visible | All distilled skills | 19/24 | 23/24 | 0.9583 | 0 |
| hard_v4 | strict visible | Promoted rules | 20/24 | 24/24 | 1.0 | 1 |
| hard_v4 | strict visible | Bad dependency rule | 18/24 | 12/24 | 0.5 | 0 |
| hard_v4 | strict visible | Forced bad artifact | 0/24 | 24/24 | 1.0 | 24 |

## Derived Claim Flags

| flag | value |
| --- | --- |
| bad_dependency_adherence_values | {"hard_v3_tree-aware": "9/30", "hard_v3_strict_visible": "10/30", "hard_v4_tree-aware": "6/24", "hard_v4_strict_visible": "12/24"} |
| context_success_delta_values | {"hard_v3_tree-aware_tree_precondition_context_vs_selected": 0, "hard_v4_tree-aware_tree_precondition_context_vs_selected": 0, "hard_v3_strict_visible_strict_precondition_only_vs_selected": 0, "hard_v4_strict_visible_strict_precondition_only_vs_selected": -1, "hard_v3_strict_visible_strict_precondition_only_vs_no_experience": 1, "hard_v4_strict_visible_strict_precondition_only_vs_no_experience": 2} |
| context_token_delta_values | {"hard_v3_tree-aware_tree_precondition_context_vs_selected": 6864, "hard_v4_tree-aware_tree_precondition_context_vs_selected": 2840, "hard_v3_strict_visible_strict_precondition_only_vs_selected": 15972, "hard_v4_strict_visible_strict_precondition_only_vs_selected": 10925, "hard_v3_strict_visible_strict_precondition_only_vs_no_experience": 17670, "hard_v4_strict_visible_strict_precondition_only_vs_no_experience": 11347} |
| forced_bad_negative_transfer_replicated | True |
| forced_bad_total_public_passed_hidden_failed | 108 |
| forced_bad_total_success | 0/108 |
| forced_bad_total_tasks | 108 |
| selected_success_delta_values | {"hard_v3_tree-aware_selected_success_delta_vs_no_experience": 0, "hard_v3_strict_visible_selected_success_delta_vs_no_experience": 1, "hard_v4_tree-aware_selected_success_delta_vs_no_experience": 1, "hard_v4_strict_visible_selected_success_delta_vs_no_experience": 3} |
| selected_superiority_consistent | False |
| selected_token_delta_values | {"hard_v3_tree-aware_selected_token_delta_vs_no_experience": -5242, "hard_v3_strict_visible_selected_token_delta_vs_no_experience": 1698, "hard_v4_tree-aware_selected_token_delta_vs_no_experience": 3861, "hard_v4_strict_visible_selected_token_delta_vs_no_experience": 422} |
| selected_token_savings_consistent | False |

## Supported Claims

- The predeclared transfer matrix completed with model mimo-v2.5: hard_v3 and hard_v4, tree-aware and strict visible-file settings, 864 total strategy-task rows, and zero parse errors.
- Forced bad artifacts replicate as systematic negative transfer under the transfer model: 0/108 success with 108 public-pass/hidden-fail cases.
- SkillAdmit-selected is model-sensitive rather than universally dominant: it ties no_experience in hard_v3 tree-aware, improves by one task in hard_v3 strict and hard_v4 tree-aware, and improves by three tasks in hard_v4 strict for this transfer model.
- Precondition context is not a universal replacement for ordinary selected context: strict precondition-only ties selected in hard_v3 and trails it in hard_v4 for this transfer model.
- Bad-dependency-rule success remains hard to interpret without artifact adherence: adherence is low in every transfer setting.

## Unsupported Claims

- Do not claim model-general SkillAdmit-selected superiority from one transfer model.
- Do not claim SkillAdmit-selected token savings; token deltas are mixed and protocol-dependent.
- Do not claim precondition-only replaces repository-tree context.
- Do not treat raw memory or all-skills as deployable admission policies.
- Do not tune hard_v3 or hard_v4 prompts, tasks, strategies, or hidden verifiers from these outcomes.
- Do not cite the pre-run protocol as model-performance evidence; cite this evidence package instead.

## Protocol Source

| field | value |
| --- | --- |
| path | `benchmark/downstream/reports/model_transfer_replication_protocol.json` |
| sha256 | `ae3893cb2d81b943` |
| protocol_id | model_transfer_replication_v0 |
| expected_total_rows | 864 |

