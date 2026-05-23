# Downstream Claim Defense Matrix

Generated at UTC: `2026-05-23T06:12:44.291834+00:00`

SkillAdmit has conditional downstream utility evidence and strong negative-transfer evidence: hard_v2 supports tree-aware selected utility, hard_v3 bounds universal selected-superiority claims, hard_v4 adds a stricter boundary, and forced bad artifacts fail 0/133 with 133 public-pass/hidden-fail cases.

## Overview

| claim_id | status | claim | evidence |
| --- | --- | --- | --- |
| C1_downstream_hidden_verifier_is_required | supported_design_claim | SkillAdmit should be evaluated with downstream hidden-verifier tasks, not admission labels alone. | hard_v2, hard_v3, and hard_v4 use hidden verifiers, and forced bad artifacts create 133 public-pass/hidden-fail cases across 133 tasks. |
| C2_hard_v2_tree_selected_positive | supported_conditional_claim | In hard_v2 tree-aware downstream validation, SkillAdmit-selected context improves success over no_experience. | hard_v2 tree-aware selected is 25/25 versus 23/25 for no_experience; selected was replicated with success values [25, 25]. |
| C3_hard_v2_strict_visible_boundary | boundary_claim | Strict visible-file hard_v2 does not support a SkillAdmit-selected win. | In strict visible-file hard_v2, selected is 23/25, no_experience is 24/25, and all distilled skills are 25/25. |
| C4_hard_v3_generalization_boundary | boundary_claim | hard_v3 and hard_v4 do not support universal SkillAdmit-selected superiority. | In hard_v3 tree-aware, selected and no_experience are both 29/30. In strict visible-file hard_v3, selected is 29/30 while precondition-on... |
| C5_repo_tree_and_preconditions_are_context_variables | conditional_claim | Repository tree and precondition context are important variables, but neither is universally sufficient or ... | hard_v2 strict precondition-only is unstable with success values [24, 23]; hard_v3 strict precondition-only reaches 30/30, while hard_v4 ... |
| C6_forced_bad_artifacts_negative_transfer | strong_supported_claim | When harmful admitted artifacts are forced into execution, they cause systematic negative transfer. | Forced bad artifacts are 0/133 success across hard_v2, hard_v3, and hard_v4, with 133 public-pass/hidden-fail cases. |
| C7_bad_dependency_rule_is_not_safe | caveat_claim | Ordinary bad_dependency_rule success does not prove bad advice is safe, because adherence is low on hard_v3... | hard_v3 bad_dependency_rule succeeds at 30/30 and 30/30, but artifact adherence is 4/30 and 11/30. hard_v4 adherence is 7/24 and 4/24. |
| C8_raw_memory_is_a_serious_baseline_not_a_policy | boundary_claim | Raw memory is a serious downstream baseline, but current evidence does not make it a safe admission policy. | Raw memory is 22/25 in hard_v2 strict visible-file, but 30/30 and 30/30 in hard_v3, and 24/24 / 23/24 in hard_v4. |
| C9_selected_token_savings_not_supported | not_supported_claim | The current three-boundary evidence does not support SkillAdmit-selected token savings. | Selected token deltas versus no_experience are mixed across the six hard_v2/hard_v3/hard_v4 comparisons: hard_v2 tree +6049, hard_v2 stri... |
| C10_all_skills_is_strong_but_not_the_target_policy | boundary_claim | All-skills context is a strong comparison condition, but it is not the same as an admitted selected artifac... | All-skills reaches 25/25 in hard_v2 strict and 30/30 in hard_v3 tree-aware. In hard_v4, all-skills reaches 24/24 tree-aware and 24/24 str... |

## Global Red Lines

- Do not claim universal SkillAdmit-selected superiority.
- Do not claim cross-version SkillAdmit-selected token savings.
- Do not claim precondition-only generally replaces repository-tree context.
- Do not claim raw memory is a safe admission policy from hard_v3 success alone.
- Do not claim bad dependency advice is safe when the model often ignored it.
- Do not tune hard_v2, hard_v3, or hard_v4 failures while treating them as clean evidence.

## Claim Cards

### C1_downstream_hidden_verifier_is_required

Status: `supported_design_claim`

Claim: SkillAdmit should be evaluated with downstream hidden-verifier tasks, not admission labels alone.

Evidence summary: hard_v2, hard_v3, and hard_v4 use hidden verifiers, and forced bad artifacts create 133 public-pass/hidden-fail cases across 133 tasks.

Allowed wording:
- We complement admission accuracy with downstream hidden-verifier validation.
- Public tests are insufficient for evaluating admitted experience.

Forbidden wording:
- Admission accuracy alone proves downstream utility.
- Passing public tests is enough to validate an admitted artifact.

Required qualifiers:
- Say downstream evidence is complementary and sharper for utility, not a replacement for all admission metrics.
- Mention hidden verification and public-pass/hidden-fail cases.

Reviewer risk: A reviewer may ask why admission accuracy is not enough.

Reviewer response: Admission labels test classification, while downstream tasks test whether admitted artifacts change future agent behavior under hidden verification. The forced bad-artifact controls show public tests can be fooled.

Evidence rows:

| source | setting/group | strategy | success | adherence | public_hidden | tokens | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hard_v2_evidence_package | forced harmful artifact | Forced bad artifact | 0/25 |  | 25 | 0 | forced harmful artifact control |
| hard_v3_evidence_package | tree-aware | Forced bad artifact | 0/30 |  | 30 | 0 | tree-aware forced harmful artifact control |
| hard_v3_evidence_package | strict visible | Forced bad artifact | 0/30 |  | 30 | 0 | strict visible-file forced harmful artifact control |
| hard_v4_evidence_package | tree-aware | Forced bad artifact | 0/24 |  | 24 | 0 | tree-aware hard_v4 forced harmful artifact control |
| hard_v4_evidence_package | strict visible | Forced bad artifact | 0/24 |  | 24 | 0 | strict hard_v4 forced harmful artifact control |

### C2_hard_v2_tree_selected_positive

Status: `supported_conditional_claim`

Claim: In hard_v2 tree-aware downstream validation, SkillAdmit-selected context improves success over no_experience.

Evidence summary: hard_v2 tree-aware selected is 25/25 versus 23/25 for no_experience; selected was replicated with success values [25, 25].

Allowed wording:
- On hard_v2 with repo-tree context, SkillAdmit-selected reached 25/25 versus 23/25 for no_experience.
- hard_v2 provides positive evidence for tree-aware selected utility.

Forbidden wording:
- SkillAdmit-selected universally beats no_experience.
- The hard_v2 result proves selected is best under every executor setting.

Required qualifiers:
- Keep the tree-aware executor qualifier.
- Report strict visible-file hard_v2 separately.

Reviewer risk: A reviewer may point to strict visible-file hard_v2 where selected is worse.

Reviewer response: That objection is correct and is part of the claim boundary. The positive claim is limited to the tree-aware coding-agent setting, while strict visible-file is reported as a separate boundary.

Evidence rows:

| source | setting/group | strategy | success | adherence | public_hidden | tokens | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hard_v2_evidence_package | tree-aware | SkillAdmit-selected | 25/25 |  | 0 | 57597 | tree-aware selected |
| hard_v2_evidence_package | tree-aware | No experience | 23/25 |  | 0 | 51548 | tree-aware no_experience |
| hard_v2_evidence_package | tree_aware_skilladmit_selected |  | [25, 25] |  |  | [57597, 52144] | replication stability group |

### C3_hard_v2_strict_visible_boundary

Status: `boundary_claim`

Claim: Strict visible-file hard_v2 does not support a SkillAdmit-selected win.

Evidence summary: In strict visible-file hard_v2, selected is 23/25, no_experience is 24/25, and all distilled skills are 25/25.

Allowed wording:
- Strict visible-file hard_v2 is a boundary where selected-only context is insufficient.
- All-skills is strongest in strict visible-file hard_v2, but it is more token-expensive.

Forbidden wording:
- SkillAdmit-selected wins hard_v2 overall.
- Selection is always better than providing all skills.

Required qualifiers:
- Separate strict visible-file and tree-aware settings.
- Do not collapse hard_v2 into one leaderboard.

Reviewer risk: A reviewer may accuse the paper of cherry-picking tree-aware hard_v2.

Reviewer response: The defense is to report strict visible-file explicitly as a negative boundary. The paper should say tree-aware selected helps, not that selected wins every hard_v2 setting.

Evidence rows:

| source | setting/group | strategy | success | adherence | public_hidden | tokens | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hard_v2_evidence_package | strict visible | SkillAdmit-selected | 23/25 |  | 0 | 66608 | strict visible-file selected |
| hard_v2_evidence_package | strict visible | No experience | 24/25 |  | 0 | 59272 | strict visible-file no_experience |
| hard_v2_evidence_package | strict visible | All distilled skills | 25/25 |  | 0 | 84986 | strict visible-file all distilled skills |

### C4_hard_v3_generalization_boundary

Status: `boundary_claim`

Claim: hard_v3 and hard_v4 do not support universal SkillAdmit-selected superiority.

Evidence summary: In hard_v3 tree-aware, selected and no_experience are both 29/30. In strict visible-file hard_v3, selected is 29/30 while precondition-only and raw memory are 30/30. In hard_v4 strict visible-file, selected is 22/24 while no_experience is 24/24.

Allowed wording:
- hard_v3 and hard_v4 are generalization boundaries for the selected-superiority claim.
- SkillAdmit-selected can help in some settings, but the current evidence does not make it universally best.

Forbidden wording:
- hard_v3 proves SkillAdmit-selected superiority.
- hard_v4 proves SkillAdmit-selected superiority.
- SkillAdmit-selected is the best hard_v3 condition.

Required qualifiers:
- State that hard_v3 and hard_v4 weaken the universal claim.
- Mention tree-aware ties, strict non-best results, and hard_v4 strict underperformance.

Reviewer risk: A reviewer may ask why hard_v3 or hard_v4 is included if selected does not win.

Reviewer response: It is included exactly as a clean downstream boundary. A credible evaluation should report where the mechanism generalizes and where it does not.

Evidence rows:

| source | setting/group | strategy | success | adherence | public_hidden | tokens | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hard_v3_evidence_package | tree-aware | SkillAdmit-selected | 29/30 |  | 0 | 69291 | tree-aware selected |
| hard_v3_evidence_package | tree-aware | No experience | 29/30 |  | 0 | 70208 | tree-aware no_experience |
| hard_v3_evidence_package | strict visible | SkillAdmit-selected | 29/30 |  | 0 | 71390 | strict visible-file selected |
| hard_v3_evidence_package | strict visible | Selected + preconditions only | 30/30 |  | 0 | 82615 | strict precondition-only |
| hard_v3_evidence_package | strict visible | Raw memory | 30/30 |  | 0 | 73789 | strict raw memory |
| hard_v4_evidence_package | tree-aware | SkillAdmit-selected | 24/24 |  | 0 | 48682 | hard_v4 tree-aware selected |
| hard_v4_evidence_package | tree-aware | No experience | 24/24 |  | 0 | 46685 | hard_v4 tree-aware no_experience |
| hard_v4_evidence_package | strict visible | SkillAdmit-selected | 22/24 |  | 0 | 58450 | hard_v4 strict selected |
| hard_v4_evidence_package | strict visible | No experience | 24/24 |  | 0 | 53055 | hard_v4 strict no_experience |

### C5_repo_tree_and_preconditions_are_context_variables

Status: `conditional_claim`

Claim: Repository tree and precondition context are important variables, but neither is universally sufficient or necessary.

Evidence summary: hard_v2 strict precondition-only is unstable with success values [24, 23]; hard_v3 strict precondition-only reaches 30/30, while hard_v4 strict precondition-only reaches 23/24 and still trails no_experience at 24/24.

Allowed wording:
- Repo tree and preconditions should be treated as task-context variables.
- hard_v2 suggests tree-aware context can be more reliable than precondition text alone; hard_v3 shows precondition-only can be sufficient on another suite; hard_v4 shows it can still trail no_experience.

Forbidden wording:
- Precondition-only replaces repository tree.
- Repository tree is always necessary.

Required qualifiers:
- Report suite-specific differences.
- Do not turn hard_v2, hard_v3, or hard_v4 alone into a universal context rule.

Reviewer risk: A reviewer may ask whether the mechanism is really SkillAdmit or just extra context.

Reviewer response: The matrix separates artifact selection from execution context. Current evidence supports conditional utility, while repo tree and preconditions remain explicit variables rather than hidden assumptions.

Evidence rows:

| source | setting/group | strategy | success | adherence | public_hidden | tokens | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hard_v2_evidence_package | tree-aware | SkillAdmit-selected | 25/25 |  | 0 | 57597 | hard_v2 tree-aware selected |
| hard_v2_evidence_package | strict + preconditions only | Selected + preconditions only | 24/25 |  | 0 | 72316 | hard_v2 strict precondition-only |
| hard_v2_evidence_package | strict_precondition_only |  | [24, 23] |  |  | [72316, 77487] | precondition-only stability group |
| hard_v3_evidence_package | strict visible | Selected + preconditions only | 30/30 |  | 0 | 82615 | hard_v3 strict precondition-only |
| hard_v4_evidence_package | tree-aware | Selected + tree + preconditions | 24/24 |  | 0 | 63586 | hard_v4 tree-aware selected + preconditions |
| hard_v4_evidence_package | strict visible | Selected + preconditions only | 23/24 |  | 0 | 69961 | hard_v4 strict precondition-only |
| downstream_boundary_synthesis |  |  |  |  |  |  | precondition-only is suite-dependent versus no_experience |

### C6_forced_bad_artifacts_negative_transfer

Status: `strong_supported_claim`

Claim: When harmful admitted artifacts are forced into execution, they cause systematic negative transfer.

Evidence summary: Forced bad artifacts are 0/133 success across hard_v2, hard_v3, and hard_v4, with 133 public-pass/hidden-fail cases.

Allowed wording:
- Forced harmful artifacts produce systematic negative transfer: 0/133 success with 133 public-pass/hidden-fail cases.
- The negative-transfer control supports the need for admission hygiene.

Forbidden wording:
- SkillAdmit proves all admitted artifacts are safe.
- Bad experience is harmless if public tests pass.

Required qualifiers:
- Say harmful artifacts damage behavior when executed.
- Use forced_bad_artifact as the clean negative-transfer control.

Reviewer risk: A reviewer may ask whether negative transfer is deterministic or model-specific.

Reviewer response: The forced artifact is a controlled downstream condition: it demonstrates the behavioral hazard of executing known-bad experience. It now holds across hard_v2, hard_v3, and hard_v4.

Evidence rows:

| source | setting/group | strategy | success | adherence | public_hidden | tokens | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hard_v2_evidence_package | forced harmful artifact | Forced bad artifact | 0/25 |  | 25 | 0 | hard_v2 forced bad artifact |
| hard_v3_evidence_package | tree-aware | Forced bad artifact | 0/30 |  | 30 | 0 | hard_v3 tree-aware forced bad artifact |
| hard_v3_evidence_package | strict visible | Forced bad artifact | 0/30 |  | 30 | 0 | hard_v3 strict forced bad artifact |
| hard_v4_evidence_package | tree-aware | Forced bad artifact | 0/24 |  | 24 | 0 | hard_v4 tree-aware forced bad artifact |
| hard_v4_evidence_package | strict visible | Forced bad artifact | 0/24 |  | 24 | 0 | hard_v4 strict forced bad artifact |
| downstream_boundary_synthesis |  |  |  |  | 133 |  | three-boundary forced bad aggregate |

### C7_bad_dependency_rule_is_not_safe

Status: `caveat_claim`

Claim: Ordinary bad_dependency_rule success does not prove bad advice is safe, because adherence is low on hard_v3 and hard_v4.

Evidence summary: hard_v3 bad_dependency_rule succeeds at 30/30 and 30/30, but artifact adherence is 4/30 and 11/30. hard_v4 adherence is 7/24 and 4/24.

Allowed wording:
- The model often succeeds by ignoring harmful advice.
- Use forced_bad_artifact, not ordinary bad_dependency_rule success, as negative-transfer evidence.

Forbidden wording:
- Bad dependency advice is safe.
- The model can always ignore harmful experience.

Required qualifiers:
- Mention artifact adherence when discussing bad_dependency_rule.
- Separate ignored bad advice from forced executed bad artifacts.

Reviewer risk: A reviewer may argue that bad_dependency_rule success weakens the negative-transfer story.

Reviewer response: It does not: low adherence means the condition often did not execute the bad advice. The forced condition answers the causal question and fails 0/133.

Evidence rows:

| source | setting/group | strategy | success | adherence | public_hidden | tokens | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hard_v3_evidence_package | tree-aware | Bad dependency rule | 30/30 | 4/30 |  | 68671 | tree-aware bad_dependency_rule with low adherence |
| hard_v3_evidence_package | strict visible | Bad dependency rule | 30/30 | 11/30 |  | 75920 | strict bad_dependency_rule with low adherence |
| hard_v2_evidence_package | strict visible | Bad dependency rule | 22/25 |  | 0 | 75724 | hard_v2 strict bad_dependency_rule |
| hard_v3_evidence_package | tree-aware | Forced bad artifact | 0/30 |  | 30 | 0 | forced control remains harmful |
| hard_v4_evidence_package | tree-aware | Bad dependency rule | 24/24 | 7/24 |  | 51974 | hard_v4 tree-aware bad_dependency_rule with low adherence |
| hard_v4_evidence_package | strict visible | Bad dependency rule | 24/24 | 4/24 |  | 63789 | hard_v4 strict bad_dependency_rule with low adherence |
| hard_v4_evidence_package | tree-aware | Forced bad artifact | 0/24 |  | 24 | 0 | hard_v4 forced control remains harmful |

### C8_raw_memory_is_a_serious_baseline_not_a_policy

Status: `boundary_claim`

Claim: Raw memory is a serious downstream baseline, but current evidence does not make it a safe admission policy.

Evidence summary: Raw memory is 22/25 in hard_v2 strict visible-file, but 30/30 and 30/30 in hard_v3, and 24/24 / 23/24 in hard_v4.

Allowed wording:
- Raw memory must be reported as a serious comparison condition.
- hard_v3 raw-memory success is a baseline result, not an admission-policy proof.

Forbidden wording:
- Raw memory is safe because it reaches 30/30 on hard_v3.
- SkillAdmit is unnecessary because raw memory wins one suite.

Required qualifiers:
- Discuss memory cost, specificity, and harmful-memory risk before making policy claims.
- Keep raw memory as a baseline unless a separate policy evaluation is run.

Reviewer risk: A reviewer may ask why SkillAdmit matters if raw memory reaches 30/30 on hard_v3.

Reviewer response: The honest answer is that hard_v3 makes raw memory a strong baseline. It does not settle admission policy because it omits cost, specificity, and harmful-memory controls.

Evidence rows:

| source | setting/group | strategy | success | adherence | public_hidden | tokens | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hard_v2_evidence_package | strict visible | Raw memory | 22/25 |  | 0 | 56941 | hard_v2 strict raw memory |
| hard_v3_evidence_package | tree-aware | Raw memory | 30/30 |  | 0 | 68753 | hard_v3 tree-aware raw memory |
| hard_v3_evidence_package | strict visible | Raw memory | 30/30 |  | 0 | 73789 | hard_v3 strict raw memory |
| hard_v4_evidence_package | tree-aware | Raw memory | 24/24 |  | 0 | 53406 | hard_v4 tree-aware raw memory |
| hard_v4_evidence_package | strict visible | Raw memory | 23/24 |  | 0 | 65070 | hard_v4 strict raw memory |

### C9_selected_token_savings_not_supported

Status: `not_supported_claim`

Claim: The current three-boundary evidence does not support SkillAdmit-selected token savings.

Evidence summary: Selected token deltas versus no_experience are mixed across the six hard_v2/hard_v3/hard_v4 comparisons: hard_v2 tree +6049, hard_v2 strict +7336, hard_v3 tree -917, hard_v3 strict -2763, hard_v4 tree +1997, and hard_v4 strict +5395.

Allowed wording:
- Token savings are not a supported paper claim.
- The current evidence focuses on success, hidden-verifier safety, and negative transfer.

Forbidden wording:
- SkillAdmit-selected reduces token cost.
- Selection is more efficient across downstream tasks.

Required qualifiers:
- If token cost is mentioned, frame it as inconclusive or mixed.
- Do not use small hard_v3 token decreases to override hard_v2 increases.

Reviewer risk: A reviewer may ask whether SkillAdmit is cost-effective.

Reviewer response: The current downstream evidence was not designed as a cost-effectiveness study. A separate controlled token-cost evaluation would be needed.

Evidence rows:

| source | setting/group | strategy | success | adherence | public_hidden | tokens | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| downstream_boundary_synthesis |  |  |  |  |  |  | three-boundary selected token delta summary |

### C10_all_skills_is_strong_but_not_the_target_policy

Status: `boundary_claim`

Claim: All-skills context is a strong comparison condition, but it is not the same as an admitted selected artifact policy.

Evidence summary: All-skills reaches 25/25 in hard_v2 strict and 30/30 in hard_v3 tree-aware. In hard_v4, all-skills reaches 24/24 tree-aware and 24/24 strict, while selected reaches 24/24 and 22/24.

Allowed wording:
- All-skills is a strong upper-context comparison and should be reported.
- Selected experience is a policy target, not a claim that fewer artifacts always beat all available skills.

Forbidden wording:
- Selection always beats all-skills.
- All-skills success invalidates experience admission.

Required qualifiers:
- Distinguish policy selection from maximum-context baselines.
- Do not turn all-skills into the headline condition unless the paper is about context stuffing.

Reviewer risk: A reviewer may ask why not always provide every distilled skill.

Reviewer response: All-skills is a valid comparison but changes the policy question. SkillAdmit studies admission and selection; all-skills is useful as a high-context baseline with different cost and contamination risks.

Evidence rows:

| source | setting/group | strategy | success | adherence | public_hidden | tokens | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hard_v2_evidence_package | strict visible | All distilled skills | 25/25 |  | 0 | 84986 | hard_v2 strict all distilled skills |
| hard_v2_evidence_package | strict visible | SkillAdmit-selected | 23/25 |  | 0 | 66608 | hard_v2 strict selected |
| hard_v3_evidence_package | tree-aware | All distilled skills | 30/30 |  | 0 | 75603 | hard_v3 tree-aware all distilled skills |
| hard_v3_evidence_package | tree-aware | SkillAdmit-selected | 29/30 |  | 0 | 69291 | hard_v3 tree-aware selected |
| hard_v3_evidence_package | strict visible | All distilled skills | 29/30 |  | 1 | 83366 | hard_v3 strict all distilled skills |
| hard_v3_evidence_package | strict visible | SkillAdmit-selected | 29/30 |  | 0 | 71390 | hard_v3 strict selected |
| hard_v4_evidence_package | tree-aware | All distilled skills | 24/24 |  | 0 | 68776 | hard_v4 tree-aware all distilled skills |
| hard_v4_evidence_package | tree-aware | SkillAdmit-selected | 24/24 |  | 0 | 48682 | hard_v4 tree-aware selected |
| hard_v4_evidence_package | strict visible | All distilled skills | 24/24 |  | 0 | 69049 | hard_v4 strict all distilled skills |
| hard_v4_evidence_package | strict visible | SkillAdmit-selected | 22/24 |  | 0 | 58450 | hard_v4 strict selected |

## Source Packages

| name | path | sha256 | generated_at_utc |
| --- | --- | --- | --- |
| hard_v2_evidence_package | `benchmark/downstream/reports/hard_v2_evidence_package.json` | `7deb038d4adfc285` | `2026-05-22T05:36:13.500710+00:00` |
| hard_v3_evidence_package | `benchmark/downstream/reports/hard_v3_evidence_package.json` | `894b8f7a1f7ac296` | `2026-05-22T13:03:52.487189+00:00` |
| hard_v4_evidence_package | `benchmark/downstream/reports/hard_v4_evidence_package.json` | `c7e729993e44503b` | `2026-05-23T04:55:41.380270+00:00` |
| downstream_boundary_synthesis | `benchmark/downstream/reports/downstream_boundary_synthesis.json` | `b5e58a54217563fb` | `2026-05-23T05:33:33.739619+00:00` |
| downstream_paper_eval_section | `benchmark/downstream/reports/downstream_paper_eval_section.json` | `d670f1ff13a95fa6` | `2026-05-23T06:09:05.254849+00:00` |
