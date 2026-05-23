# Downstream Boundary Synthesis

Generated at UTC: `2026-05-23T05:33:33.739619+00:00`

This report combines hard_v2, hard_v3, and hard_v4 paper-facing evidence packages. It is a boundary-synthesis artifact, not a new LLM run and not a prompt-tuning step.

## Executive Boundary

hard_v2 gives a positive tree-aware result for SkillAdmit-selected; hard_v3 narrows that story; hard_v4 rejects selected superiority in strict visible-file mode and saturates tree-aware mode. The stable cross-boundary result is negative transfer from forced harmful artifacts: 0/133 success with 133 public-pass/hidden-fail cases.

## Suite Roles

| suite | role |
| --- | --- |
| hard_v2 | conditional positive evidence: tree-aware selected beats no_experience, while strict visible-file exposes selected-only limitations |
| hard_v3 | generalization boundary: selected no longer dominates tree-aware, while precondition-only is strong in strict visible-file |
| hard_v4 | stricter boundary: tree-aware saturates and strict visible-file rejects ordinary selected superiority |

## Primary Boundary Table

| suite | setting | strategy | success | neg | public_hidden | adherence | tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hard_v2 | strict visible | Bad dependency rule | 22/25 | 2 | 0 |  | 75724 |
| hard_v2 | strict visible | All distilled skills | 25/25 | 0 | 0 |  | 84986 |
| hard_v2 | strict visible | No experience | 24/25 | 0 | 0 |  | 59272 |
| hard_v2 | strict visible | Promoted rules | 21/25 | 4 | 1 |  | 77858 |
| hard_v2 | strict visible | Raw memory | 22/25 | 3 | 0 |  | 56941 |
| hard_v2 | strict visible | SkillAdmit-selected | 23/25 | 2 | 0 |  | 66608 |
| hard_v2 | tree-aware | No experience | 23/25 | 2 | 0 |  | 51548 |
| hard_v2 | tree-aware | SkillAdmit-selected | 25/25 | 0 | 0 |  | 57597 |
| hard_v2 | tree-aware + preconditions | Selected + tree + preconditions | 25/25 | 0 | 0 |  | 67504 |
| hard_v2 | strict + preconditions only | Selected + preconditions only | 24/25 | 1 | 0 |  | 72316 |
| hard_v2 | forced harmful artifact | Forced bad artifact | 0/25 | 25 | 25 |  | 0 |
| hard_v3 | tree-aware | Bad dependency rule | 30/30 | 0 | 0 | 4/30 | 68671 |
| hard_v3 | tree-aware | All distilled skills | 30/30 | 0 | 0 | 30/30 | 75603 |
| hard_v3 | tree-aware | Forced bad artifact | 0/30 | 30 | 30 | 30/30 | 0 |
| hard_v3 | tree-aware | No experience | 29/30 | 1 | 0 | 30/30 | 70208 |
| hard_v3 | tree-aware | Promoted rules | 29/30 | 1 | 1 | 30/30 | 73114 |
| hard_v3 | tree-aware | Raw memory | 30/30 | 0 | 0 | 30/30 | 68753 |
| hard_v3 | tree-aware | SkillAdmit-selected | 29/30 | 1 | 0 | 30/30 | 69291 |
| hard_v3 | tree-aware | Selected + tree + preconditions | 29/30 | 1 | 0 | 30/30 | 74559 |
| hard_v3 | strict visible | Bad dependency rule | 30/30 | 0 | 0 | 11/30 | 75920 |
| hard_v3 | strict visible | All distilled skills | 29/30 | 1 | 1 | 26/30 | 83366 |
| hard_v3 | strict visible | Forced bad artifact | 0/30 | 30 | 30 | 30/30 | 0 |
| hard_v3 | strict visible | No experience | 28/30 | 0 | 0 | 30/30 | 74153 |
| hard_v3 | strict visible | Promoted rules | 29/30 | 1 | 0 | 30/30 | 80112 |
| hard_v3 | strict visible | Raw memory | 30/30 | 0 | 0 | 30/30 | 73789 |
| hard_v3 | strict visible | SkillAdmit-selected | 29/30 | 1 | 0 | 30/30 | 71390 |
| hard_v3 | strict visible | Selected + preconditions only | 30/30 | 0 | 0 | 30/30 | 82615 |
| hard_v4 | tree-aware | Bad dependency rule | 24/24 | 0 | 0 | 7/24 | 51974 |
| hard_v4 | tree-aware | All distilled skills | 24/24 | 0 | 0 | 21/24 | 68776 |
| hard_v4 | tree-aware | Forced bad artifact | 0/24 | 24 | 24 | 24/24 | 0 |
| hard_v4 | tree-aware | No experience | 24/24 | 0 | 0 | 24/24 | 46685 |
| hard_v4 | tree-aware | Promoted rules | 24/24 | 0 | 0 | 24/24 | 58813 |
| hard_v4 | tree-aware | Raw memory | 24/24 | 0 | 0 | 24/24 | 53406 |
| hard_v4 | tree-aware | SkillAdmit-selected | 24/24 | 0 | 0 | 24/24 | 48682 |
| hard_v4 | tree-aware | Selected + tree + preconditions | 24/24 | 0 | 0 | 24/24 | 63586 |
| hard_v4 | strict visible | Bad dependency rule | 24/24 | 0 | 0 | 4/24 | 63789 |
| hard_v4 | strict visible | All distilled skills | 24/24 | 0 | 0 | 21/24 | 69049 |
| hard_v4 | strict visible | Forced bad artifact | 0/24 | 24 | 24 | 24/24 | 0 |
| hard_v4 | strict visible | No experience | 24/24 | 0 | 0 | 24/24 | 53055 |
| hard_v4 | strict visible | Promoted rules | 23/24 | 1 | 0 | 23/24 | 69221 |
| hard_v4 | strict visible | Raw memory | 23/24 | 1 | 0 | 24/24 | 65070 |
| hard_v4 | strict visible | SkillAdmit-selected | 22/24 | 2 | 0 | 24/24 | 58450 |
| hard_v4 | strict visible | Selected + preconditions only | 23/24 | 1 | 0 | 24/24 | 69961 |

## Selected Versus No Experience

| suite | setting | selected | no_experience | success_delta | token_delta |
| --- | --- | --- | --- | --- | --- |
| hard_v2 | tree-aware | 25/25 | 23/25 | 2 | 6049 |
| hard_v2 | strict visible | 23/25 | 24/25 | -1 | 7336 |
| hard_v3 | tree-aware | 29/30 | 29/30 | 0 | -917 |
| hard_v3 | strict visible | 29/30 | 28/30 | 1 | -2763 |
| hard_v4 | tree-aware | 24/24 | 24/24 | 0 | 1997 |
| hard_v4 | strict visible | 22/24 | 24/24 | -2 | 5395 |

## Context Comparisons

| suite | comparison | left_success | right_success | success_delta | token_delta |
| --- | --- | --- | --- | --- | --- |
| hard_v2 | tree-aware precondition context vs selected | 25/25 | 25/25 | 0 | 9907 |
| hard_v3 | tree-aware precondition context vs selected | 29/30 | 29/30 | 0 | 5268 |
| hard_v4 | tree-aware precondition context vs selected | 24/24 | 24/24 | 0 | 14904 |
| hard_v2 | strict precondition-only vs selected | 24/25 | 23/25 | 1 | 5708 |
| hard_v3 | strict precondition-only vs selected | 30/30 | 29/30 | 1 | 11225 |
| hard_v4 | strict precondition-only vs selected | 23/24 | 22/24 | 1 | 11511 |
| hard_v2 | strict precondition-only vs no_experience | 24/25 | 24/25 | 0 | 13044 |
| hard_v3 | strict precondition-only vs no_experience | 30/30 | 28/30 | 2 | 8462 |
| hard_v4 | strict precondition-only vs no_experience | 23/24 | 24/24 | -1 | 16906 |

## Forced Bad Artifact Aggregate

| suite | success | negative_transfer | public_hidden |
| --- | --- | --- | --- |
| hard_v2 | 0/25 | 25 | 25 |
| hard_v3 | 0/60 | 60 | 60 |
| hard_v4 | 0/48 | 48 | 48 |

Total: `0/133` success, `133` public-pass/hidden-fail cases.

## Artifact Adherence Caveats

| suite | setting | strategy | success | adherence | adherence_rate | public_hidden |
| --- | --- | --- | --- | --- | --- | --- |
| hard_v2 | strict visible | bad_dependency_rule | 22/25 |  | None | 0 |
| hard_v2 | strict visible | distilled_skills_all | 25/25 |  | None | 0 |
| hard_v2 | forced harmful artifact | forced_bad_artifact | 0/25 |  | None | 25 |
| hard_v3 | tree-aware | bad_dependency_rule | 30/30 | 4/30 | 0.1333 | 0 |
| hard_v3 | tree-aware | distilled_skills_all | 30/30 | 30/30 | 1.0 | 0 |
| hard_v3 | tree-aware | forced_bad_artifact | 0/30 | 30/30 | 1.0 | 30 |
| hard_v3 | strict visible | bad_dependency_rule | 30/30 | 11/30 | 0.3667 | 0 |
| hard_v3 | strict visible | distilled_skills_all | 29/30 | 26/30 | 0.8667 | 1 |
| hard_v3 | strict visible | forced_bad_artifact | 0/30 | 30/30 | 1.0 | 30 |
| hard_v4 | tree-aware | bad_dependency_rule | 24/24 | 7/24 | 0.2917 | 0 |
| hard_v4 | tree-aware | distilled_skills_all | 24/24 | 21/24 | 0.875 | 0 |
| hard_v4 | tree-aware | forced_bad_artifact | 0/24 | 24/24 | 1.0 | 24 |
| hard_v4 | strict visible | bad_dependency_rule | 24/24 | 4/24 | 0.1667 | 0 |
| hard_v4 | strict visible | distilled_skills_all | 24/24 | 21/24 | 0.875 | 0 |
| hard_v4 | strict visible | forced_bad_artifact | 0/24 | 24/24 | 1.0 | 24 |

## Derived Claim Flags

| flag | value |
| --- | --- |
| forced_bad_negative_transfer_consistent | True |
| forced_bad_total_public_passed_hidden_failed | 133 |
| forced_bad_total_success | 0/133 |
| forced_bad_total_tasks | 133 |
| selected_success_delta_values | {"hard_v2_tree-aware_selected_success_delta_vs_no_experience": 2, "hard_v2_strict_visible_selected_success_delta_vs_no_experience": -1, "hard_v3_tree-aware_selected_success_delta_vs_no_experience": 0, "hard_v3_strict_visible_selected_success_delta_vs_no_experience": 1, "hard_v4_tree-aware_selected_success_delta_vs_no_experience": 0, "hard_v4_strict_visible_selected_success_delta_vs_no_experience": -2} |
| selected_superiority_consistent | False |
| selected_token_delta_values | {"hard_v2_tree-aware_selected_token_delta_vs_no_experience": 6049, "hard_v2_strict_visible_selected_token_delta_vs_no_experience": 7336, "hard_v3_tree-aware_selected_token_delta_vs_no_experience": -917, "hard_v3_strict_visible_selected_token_delta_vs_no_experience": -2763, "hard_v4_tree-aware_selected_token_delta_vs_no_experience": 1997, "hard_v4_strict_visible_selected_token_delta_vs_no_experience": 5395} |
| selected_token_savings_consistent | False |
| strict_precondition_only_success_delta_vs_no_experience_values | {"hard_v2": 0, "hard_v3": 2, "hard_v4": -1} |
| strict_precondition_only_success_delta_vs_selected_values | {"hard_v2": 1, "hard_v3": 1, "hard_v4": 1} |
| strict_selected_negative_suites | ["hard_v2", "hard_v4"] |
| strict_selected_positive_suites | ["hard_v3"] |
| tree_precondition_context_success_delta_values | {"hard_v2": 0, "hard_v3": 0, "hard_v4": 0} |
| tree_selected_positive_suites | ["hard_v2"] |
| tree_selected_tied_suites | ["hard_v3", "hard_v4"] |

## Interpretation Ladder

- **Main result shape**: The evidence is not a monotonic selected-wins story. hard_v2 gives a positive tree-aware result, hard_v3 narrows that result, and hard_v4 rejects selected superiority under strict visible files.
- **Selected context**: Selected context should be presented as conditionally useful when the execution context exposes enough repository structure, not as a universal replacement for no_experience.
- **Preconditions**: Precondition text consistently helps over selected-only in strict settings, but it does not consistently beat no_experience and it adds tokens.
- **Negative transfer**: Forced bad artifacts are the strongest stable finding: 0/133 success with 133 public-pass/hidden-fail cases.
- **Paper positioning**: The defendable paper claim is not that SkillAdmit always improves success. The stronger claim is that experience admission needs downstream validation because useful, neutral, ignored, and harmful experience behave differently under hidden verifiers.

## Supported Claims

- Downstream validation is necessary because admission accuracy and keyword-like admission baselines are not enough to establish utility.
- SkillAdmit-selected utility is conditional: hard_v2 tree-aware is positive, hard_v3 tree-aware is tied, and hard_v4 tree-aware is saturated.
- Strict visible-file settings are not stable selected wins: hard_v2 selected is below no_experience, hard_v3 selected is above no_experience but not best, and hard_v4 selected is below no_experience.
- Precondition context is useful but not a universal replacement for repository context: strict precondition-only improves over selected in hard_v2, hard_v3, and hard_v4, but only hard_v3 makes it best.
- Forced harmful artifacts are the most stable cross-boundary finding: 0/133 success with 133 public-pass/hidden-fail cases across hard_v2, hard_v3, and hard_v4.
- Bad-dependency success must be interpreted through artifact adherence; low adherence means the model often succeeds by ignoring harmful advice.

## Unsupported Claims

- Do not claim SkillAdmit-selected universally improves downstream success.
- Do not claim SkillAdmit-selected is the best downstream context.
- Do not claim SkillAdmit-selected saves tokens cross-boundary.
- Do not claim precondition-only replaces repository-tree context.
- Do not claim raw memory or all-skills results are deployable admission policies.
- Do not claim bad dependency advice is safe.
- Do not tune hard_v2, hard_v3, or hard_v4 failures while still treating the affected suite as clean evidence.

## Source Package Hashes

| suite | package | sha256 | generated_at_utc |
| --- | --- | --- | --- |
| hard_v2 | `benchmark/downstream/reports/hard_v2_evidence_package.json` | `7deb038d4adfc285` | `2026-05-22T05:36:13.500710+00:00` |
| hard_v3 | `benchmark/downstream/reports/hard_v3_evidence_package.json` | `894b8f7a1f7ac296` | `2026-05-22T13:03:52.487189+00:00` |
| hard_v4 | `benchmark/downstream/reports/hard_v4_evidence_package.json` | `c7e729993e44503b` | `2026-05-23T04:55:41.380270+00:00` |

