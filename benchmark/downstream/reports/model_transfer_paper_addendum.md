# Model-Transfer Paper Addendum

Generated at UTC: `2026-05-23T11:37:24.064015+00:00`

This addendum is generated from the frozen cross-model synthesis. Do not use this addendum to claim model-general selected superiority.

## One-Paragraph Summary

A second-model replication with mimo-v2.5 strengthens the negative-transfer claim but not a universal selected-utility claim. Forced harmful artifacts fail on both the baseline and transfer hard_v3/hard_v4 slices, yielding 0/216 combined success with 216 public-pass/hidden-fail cases. hard_v3 selected-vs-no_experience patterns replicate, but hard_v4 strict visible-file reverses sign: baseline selected is -2 tasks against no_experience, while transfer selected is +3 tasks. Therefore the correct paper claim is model sensitivity plus replicated harmful-artifact negative transfer, not model-general selected superiority.

## Protocol Summary

The model-transfer experiment reruns the frozen hard_v3 and hard_v4 downstream matrices with a second model, mimo-v2.5, and compares it with the baseline label mimo-v2.5-pro. The task files, strategies, prompts, visible-file settings, repository-tree settings, and hidden verifiers are not changed from observed outcomes.

This addendum is intentionally separate from the main three-boundary downstream section. hard_v2/hard_v3/hard_v4 remain the primary clean task-boundary story; the transfer run is a model-sensitivity and replication check over a subset of those frozen boundaries.

## Results

The most stable result is negative transfer from forced harmful artifacts. The baseline hard_v3/hard_v4 slice gives 0/108, and the transfer model gives 0/108. Combined across the two models, forced bad artifacts solve 0/216 tasks and produce 216 public-pass/hidden-fail cases.

The hard_v3 selected-vs-no_experience pattern replicates. In tree-aware hard_v3, selected ties no_experience for both models: 29/30 vs 29/30 for the baseline model and 29/30 vs 29/30 for the transfer model. In strict hard_v3, selected is +1 task over no_experience for both models.

The hard_v4 strict selected comparison is model-sensitive. The baseline model has selected below no_experience by 2 tasks, while the transfer model has selected above no_experience by 3 tasks. This sign reversal is the key reason the transfer experiment should not be used to claim model-general SkillAdmit-selected superiority.

Precondition-only context is also not model-general improvement over selected context. In the baseline strict settings it is +1 over selected for both hard_v3 and hard_v4, but under the transfer model it ties selected in hard_v3 and trails selected by one task in hard_v4.

Token efficiency remains outside the supported claim set. Selected token deltas are mixed across models and settings, and the transfer protocol was not designed as a cost-controlled token-efficiency study.

## Selected Sensitivity

| suite | setting | baseline_delta | transfer_delta | pattern |
| --- | --- | --- | --- | --- |
| hard_v3 | tree-aware | 0 | 0 | same_sign |
| hard_v3 | strict visible | 1 | 1 | same_sign |
| hard_v4 | tree-aware | 0 | 1 | weakened_or_strengthened_from_tie |
| hard_v4 | strict visible | -2 | 3 | reversed_sign |

## Forced Bad Replication

| role | model | success | negative_transfer | public_hidden |
| --- | --- | --- | --- | --- |
| baseline | mimo-v2.5-pro | 0/108 | 108 | 108 |
| transfer | mimo-v2.5 | 0/108 | 108 | 108 |

## Strict Precondition-Only Versus Selected

| role | suite | precondition_only | selected | success_delta | token_delta |
| --- | --- | --- | --- | --- | --- |
| baseline | hard_v3 | 30/30 | 29/30 | 1 | 11225 |
| baseline | hard_v4 | 23/24 | 22/24 | 1 | 11511 |
| transfer | hard_v3 | 29/30 | 29/30 | 0 | 15972 |
| transfer | hard_v4 | 20/24 | 21/24 | -1 | 10925 |

## Table Captions

| label | caption |
| --- | --- |
| tab:model-transfer-selected | Selected-vs-no_experience sensitivity across baseline and transfer models. hard_v3 patterns replicate, while hard_v4 strict visible-file reverses sign. |
| tab:model-transfer-negative-transfer | Forced harmful-artifact replication across models. The combined result is 0/216 with 216 public-pass/hidden-fail cases. |

## Allowed Wording

- A second-model replication over frozen hard_v3/hard_v4 preserves the forced harmful-artifact negative-transfer result.
- Selected context shows model-sensitive downstream utility rather than model-general superiority.
- The hard_v4 strict selected comparison reverses sign between the baseline and transfer models.

## Forbidden Wording

- SkillAdmit-selected is model-generally superior.
- SkillAdmit-selected saves tokens across models.
- The transfer model creates a new clean task boundary.
- Precondition-only generally replaces repository-tree context.
- The transfer run justifies retuning hard_v3 or hard_v4.

## Derived Cross-Model Flags

| flag | value |
| --- | --- |
| forced_bad_combined_success | 0/216 |
| forced_bad_combined_public_passed_hidden_failed | 216 |
| forced_bad_replication_across_models | True |
| hard_v3_tree_selected_tie_replicated | True |
| hard_v3_strict_selected_plus_one_replicated | True |
| hard_v4_strict_selected_delta_baseline | -2 |
| hard_v4_strict_selected_delta_transfer | 3 |
| hard_v4_strict_selected_delta_reversed | True |
| selected_superiority_model_general | False |
| selected_token_savings_model_general | False |
| precondition_only_better_than_selected_model_general | False |

## Source

| field | value |
| --- | --- |
| path | `benchmark/downstream/reports/model_transfer_cross_model_synthesis.json` |
| sha256 | `fc575fd01e288008` |
| generated_at_utc | `2026-05-23T10:22:44.566296+00:00` |

