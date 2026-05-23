# Paper Artifacts Index

Generated at UTC: `2026-05-23T10:23:38.998112+00:00`

One-stop index for paper-facing SkillAdmit artifacts. Use it to choose the correct evidence, table, script, and claim boundary for downstream validation writing.

## Key Current Facts

| fact | value |
| --- | --- |
| hard_v2_tree_selected | 25/25 |
| hard_v2_tree_no_experience | 23/25 |
| hard_v3_tree_selected | 29/30 |
| hard_v3_tree_no_experience | 29/30 |
| hard_v3_strict_precondition_only | 30/30 |
| hard_v4_tree_selected | 24/24 |
| hard_v4_tree_no_experience | 24/24 |
| hard_v4_strict_selected | 22/24 |
| hard_v4_strict_no_experience | 24/24 |
| hard_v4_forced_bad_total_successes | 0 |
| hard_v4_forced_bad_total_tasks | 48 |
| hard_v4_forced_bad_total_public_passed_hidden_failed | 48 |
| boundary_forced_bad_total_success | 0/133 |
| boundary_forced_bad_total_tasks | 133 |
| boundary_forced_bad_total_public_passed_hidden_failed | 133 |
| boundary_selected_superiority_consistent | False |
| boundary_selected_token_savings_consistent | False |
| forced_bad_total_successes | 0 |
| forced_bad_total_tasks | 85 |
| forced_bad_total_public_passed_hidden_failed | 85 |
| selected_superiority_consistent | False |
| selected_token_savings_supported | False |
| model_transfer_model | mimo-v2.5 |
| model_transfer_forced_bad_total_success | 0/108 |
| model_transfer_forced_bad_total_tasks | 108 |
| model_transfer_forced_bad_total_public_passed_hidden_failed | 108 |
| model_transfer_selected_superiority_consistent | False |
| cross_model_forced_bad_combined_success | 0/216 |
| cross_model_forced_bad_public_passed_hidden_failed | 216 |
| cross_model_selected_superiority_model_general | False |
| cross_model_hard_v4_strict_selected_delta_reversed | True |
| claim_count | 10 |
| paper_section_result_paragraphs | 6 |

## Artifact Groups

| group | title | role | use in paper | do not use for |
| --- | --- | --- | --- | --- |
| G1_admission_context | Admission Context | Supporting context for admission benchmark status and baseline caveats. | Use to describe the frozen admission pipeline, v7 baseline caveat, and token accounting context. | Do not use v7 admission accuracy as the main downstream-utility proof. |
| G2_hard_v2_evidence | Hard v2 Evidence | Primary downstream evidence for tree-aware selected utility and strict visible-file boundary. | Use for hard_v2 results, including 25/25 tree-aware selected and strict visible-file caveats. | Do not flatten strict visible-file and tree-aware hard_v2 into one selected-wins leaderboard. |
| G3_hard_v3_evidence | Hard v3 Evidence | Fresh downstream boundary evidence and artifact-adherence caveats. | Use for hard_v3 boundary claims: selected ties no_experience in tree-aware and is not best in strict visible-file. | Do not use hard_v3 to claim universal SkillAdmit-selected superiority or selected token savings. |
| G4_cross_version_synthesis | Cross-Version Synthesis | Primary paper-facing synthesis of hard_v2 and hard_v3 claim boundaries. | Use for the top-level downstream story and forced_bad_artifact aggregate. | Do not merge hard_v2 and hard_v3 into a single anonymous leaderboard. |
| G5_boundary_synthesis | Boundary Synthesis | Three-boundary synthesis covering hard_v2, hard_v3, and hard_v4. | Use for the high-level paper boundary story: conditional positive, generalization boundary, stricter boundary, and 0/133 forced-bad evidence. | Do not use boundary synthesis as a substitute for the underlying suite-specific evidence packages. |
| G6_paper_section | Draftable Paper Section | Generated evaluation-section prose tied to the frozen three-boundary synthesis. | Use as the starting point for writing the downstream validation subsection. | Do not edit this prose into stronger claims without updating evidence and assertions. |
| G7_claim_defense | Claim Defense Matrix | Reviewer-facing claim-by-claim evidence map and forbidden wording ledger. | Use during paper revision and reviewer response drafting. | Do not treat reviewer-response wording as new experimental evidence. |
| G8_reporting_handoff | Reporting and Handoff | Human-readable state tracking and cross-session recovery anchors. | Use to recover the current project state and avoid repeating frozen experiments. | Do not cite progress logs as primary empirical evidence when paper-facing tables exist. |
| G9_hard_v4_scaffold | Hard v4 Scaffold | Frozen task scaffold and deterministic verifier boundary for hard_v4. | Use to document the frozen hard_v4 task boundary and hidden-verifier design. | Do not cite scaffold mechanics as model-performance evidence. |
| G10_hard_v4_evidence | Hard v4 Evidence | Fresh downstream boundary evidence that narrows selected-utility claims. | Use for hard_v4 boundary claims: tree-aware saturation, strict selected underperformance, and 0/48 forced-bad transfer. | Do not use hard_v4 to claim SkillAdmit-selected superiority or selected token savings. |
| G11_model_transfer_evidence | Model-Transfer Evidence | Second-model replication evidence over the frozen hard_v3/hard_v4 matrices. | Use to report the completed mimo-v2.5 transfer matrix: 864 rows, 0/108 forced-bad success, and model-sensitive selected deltas. | Do not use one transfer model to claim model-general selected superiority or selected token savings. |
| G12_model_transfer_cross_model | Model-Transfer Cross-Model Synthesis | Baseline-versus-transfer synthesis over hard_v3/hard_v4 downstream evidence. | Use to separate replicated findings from model-sensitive findings: forced-bad replicates across models, while hard_v4 strict selected reverses sign between baseline and transfer. | Do not merge model-transfer synthesis into the hard_v2/hard_v3/hard_v4 boundary aggregate. |

## Primary Files By Group

### G1_admission_context - Admission Context

| role | path | exists | sha256 | bytes |
| --- | --- | --- | --- | --- |
| primary | `benchmark/reports/v7_admission_baselines.md` | True | `22960509de9b3ae7` | 14817 |
| primary | `benchmark/reports/v7_admission_baselines.json` | True | `ed051957b16aa28f` | 44474 |
| primary | `benchmark/reports/llm_cost_summary.md` | True | `6180b9f1ff9021ff` | 1661 |
| primary | `benchmark/reports/llm_cost_summary.json` | True | `ef312b1019006778` | 3568 |
| support | `docs/paper_eval_status.md` | True | `b97ee46c3ebabe83` | 35398 |
| support | `docs/experiment_handoff.md` | True | `27e3e3fdb744a799` | 53579 |

Regeneration commands:
- `python scripts/run_admission_regression.py`

### G2_hard_v2_evidence - Hard v2 Evidence

| role | path | exists | sha256 | bytes |
| --- | --- | --- | --- | --- |
| primary | `benchmark/downstream/reports/hard_v2_evidence_package.json` | True | `7deb038d4adfc285` | 18140 |
| primary | `benchmark/downstream/reports/hard_v2_paper_tables.md` | True | `df8baa4287bc66c9` | 5392 |
| primary | `benchmark/downstream/reports/hard_v2_paper_tables.tex` | True | `8af23c87a828d9ea` | 1670 |
| support | `benchmark/downstream/reports/hard_v2_strategy_matrix.md` | True | `1e2d6d716b8f0428` | 37490 |
| support | `benchmark/downstream/reports/hard_v2_strategy_matrix.json` | True | `daf5030589d26ad4` | 154134 |
| support | `docs/paper_eval_status.md` | True | `b97ee46c3ebabe83` | 35398 |

Regeneration commands:
- `python scripts/check_downstream_hard_v2_tasks.py`
- `python scripts/summarize_hard_v2_results.py --assert-current-hard-v2`
- `python scripts/export_hard_v2_evidence_package.py --assert-current-hard-v2`

### G3_hard_v3_evidence - Hard v3 Evidence

| role | path | exists | sha256 | bytes |
| --- | --- | --- | --- | --- |
| primary | `benchmark/downstream/reports/hard_v3_evidence_package.json` | True | `894b8f7a1f7ac296` | 27042 |
| primary | `benchmark/downstream/reports/hard_v3_paper_tables.md` | True | `e9fae8f672df3ef8` | 7203 |
| primary | `benchmark/downstream/reports/hard_v3_paper_tables.tex` | True | `bd6187913ca355f8` | 2067 |
| support | `benchmark/downstream/reports/hard_v3_strategy_matrix.md` | True | `bceafdf069b46393` | 30895 |
| support | `benchmark/downstream/reports/hard_v3_strategy_matrix.json` | True | `b4c670caf50341c9` | 137329 |
| support | `docs/paper_eval_status.md` | True | `b97ee46c3ebabe83` | 35398 |

Regeneration commands:
- `python scripts/check_downstream_hard_v3_tasks.py`
- `python scripts/summarize_hard_v3_results.py --assert-current-hard-v3`
- `python scripts/export_hard_v3_evidence_package.py --assert-current-hard-v3`

### G4_cross_version_synthesis - Cross-Version Synthesis

| role | path | exists | sha256 | bytes |
| --- | --- | --- | --- | --- |
| primary | `benchmark/downstream/reports/downstream_cross_version_synthesis.json` | True | `e5d5bf0e8545fb09` | 19857 |
| primary | `benchmark/downstream/reports/downstream_cross_version_synthesis.md` | True | `68ec9eae519166ce` | 7497 |
| primary | `benchmark/downstream/reports/downstream_cross_version_synthesis.tex` | True | `9104d43051644fa1` | 4055 |
| support | `benchmark/downstream/reports/hard_v2_evidence_package.json` | True | `7deb038d4adfc285` | 18140 |
| support | `benchmark/downstream/reports/hard_v3_evidence_package.json` | True | `894b8f7a1f7ac296` | 27042 |
| support | `docs/paper_eval_status.md` | True | `b97ee46c3ebabe83` | 35398 |

Regeneration commands:
- `python scripts/export_downstream_cross_version_synthesis.py --assert-current-synthesis`

### G5_boundary_synthesis - Boundary Synthesis

| role | path | exists | sha256 | bytes |
| --- | --- | --- | --- | --- |
| primary | `benchmark/downstream/reports/downstream_boundary_synthesis.json` | True | `b5e58a54217563fb` | 45450 |
| primary | `benchmark/downstream/reports/downstream_boundary_synthesis.md` | True | `a9360eea565f3f41` | 12399 |
| primary | `benchmark/downstream/reports/downstream_boundary_synthesis.tex` | True | `f3381009be7d3ada` | 5205 |
| support | `benchmark/downstream/reports/hard_v2_evidence_package.json` | True | `7deb038d4adfc285` | 18140 |
| support | `benchmark/downstream/reports/hard_v3_evidence_package.json` | True | `894b8f7a1f7ac296` | 27042 |
| support | `benchmark/downstream/reports/hard_v4_evidence_package.json` | True | `c7e729993e44503b` | 22128 |

Regeneration commands:
- `python scripts/export_downstream_boundary_synthesis.py --assert-current-boundary-synthesis`

### G6_paper_section - Draftable Paper Section

| role | path | exists | sha256 | bytes |
| --- | --- | --- | --- | --- |
| primary | `benchmark/downstream/reports/downstream_paper_eval_section.json` | True | `f026bad7830e2a84` | 7062 |
| primary | `benchmark/downstream/reports/downstream_paper_eval_section.md` | True | `19df606b4bd5459b` | 6712 |
| primary | `benchmark/downstream/reports/downstream_paper_eval_section.tex` | True | `a1a1361a512173e9` | 6491 |
| support | `benchmark/downstream/reports/downstream_boundary_synthesis.json` | True | `b5e58a54217563fb` | 45450 |
| support | `benchmark/downstream/reports/downstream_claim_defense_matrix.md` | True | `67b226ce7fb63072` | 24680 |

Regeneration commands:
- `python scripts/export_downstream_paper_section.py --assert-current-paper-section`

### G7_claim_defense - Claim Defense Matrix

| role | path | exists | sha256 | bytes |
| --- | --- | --- | --- | --- |
| primary | `benchmark/downstream/reports/downstream_claim_defense_matrix.json` | True | `09f38bb09aa273ea` | 41180 |
| primary | `benchmark/downstream/reports/downstream_claim_defense_matrix.md` | True | `67b226ce7fb63072` | 24680 |
| primary | `benchmark/downstream/reports/downstream_claim_defense_matrix.tex` | True | `8c4cb516baba4ccc` | 3063 |
| support | `benchmark/downstream/reports/downstream_boundary_synthesis.json` | True | `b5e58a54217563fb` | 45450 |
| support | `benchmark/downstream/reports/downstream_paper_eval_section.json` | True | `f026bad7830e2a84` | 7062 |

Regeneration commands:
- `python scripts/export_downstream_claim_defense_matrix.py --assert-current-claim-defense`

### G8_reporting_handoff - Reporting and Handoff

| role | path | exists | sha256 | bytes |
| --- | --- | --- | --- | --- |
| primary | `docs/paper_eval_status.md` | True | `b97ee46c3ebabe83` | 35398 |
| primary | `docs/experiment_handoff.md` | True | `27e3e3fdb744a799` | 53579 |
| primary | `docs/progress_log.md` | True | `06459c65389c6fc6` | 105337 |

### G9_hard_v4_scaffold - Hard v4 Scaffold

| role | path | exists | sha256 | bytes |
| --- | --- | --- | --- | --- |
| primary | `benchmark/downstream/reports/hard_v4_scaffold_manifest.json` | True | `1e7d9adb0b9e9dc9` | 20700 |
| primary | `benchmark/downstream/reports/hard_v4_scaffold_manifest.md` | True | `02e98f97171e796e` | 5034 |
| primary | `benchmark/downstream/reports/hard_v4_scaffold_manifest.tex` | True | `8871fc0df34cab6f` | 496 |
| support | `docs/llm_downstream_hard_v4.md` | True | `c682a7c91829b412` | 12262 |
| support | `docs/paper_eval_status.md` | True | `b97ee46c3ebabe83` | 35398 |
| support | `docs/experiment_handoff.md` | True | `27e3e3fdb744a799` | 53579 |

Regeneration commands:
- `python scripts/build_downstream_hard_v4_tasks.py`
- `python scripts/check_downstream_hard_v4_tasks.py`
- `python scripts/export_hard_v4_scaffold_manifest.py --run-checker --assert-current-hard-v4-scaffold`

### G10_hard_v4_evidence - Hard v4 Evidence

| role | path | exists | sha256 | bytes |
| --- | --- | --- | --- | --- |
| primary | `benchmark/downstream/reports/hard_v4_evidence_package.json` | True | `c7e729993e44503b` | 22128 |
| primary | `benchmark/downstream/reports/hard_v4_paper_tables.md` | True | `5d04261323974b6b` | 6411 |
| primary | `benchmark/downstream/reports/hard_v4_paper_tables.tex` | True | `36499f481e3a49cf` | 2414 |
| support | `benchmark/downstream/reports/hard_v4_strategy_matrix.md` | True | `ee9eba7a9677ce92` | 27181 |
| support | `benchmark/downstream/reports/hard_v4_strategy_matrix.json` | True | `00401c79ed1b226d` | 115415 |
| support | `docs/llm_downstream_hard_v4.md` | True | `c682a7c91829b412` | 12262 |

Regeneration commands:
- `python scripts/check_downstream_hard_v4_tasks.py`
- `python scripts/summarize_hard_v4_results.py --assert-current-hard-v4`
- `python scripts/export_hard_v4_evidence_package.py --assert-current-hard-v4`

### G11_model_transfer_evidence - Model-Transfer Evidence

| role | path | exists | sha256 | bytes |
| --- | --- | --- | --- | --- |
| primary | `benchmark/downstream/reports/model_transfer_evidence_package.json` | True | `32505f40e1635dcf` | 58893 |
| primary | `benchmark/downstream/reports/model_transfer_evidence_package.md` | True | `7d423d9b66e46b32` | 11645 |
| primary | `benchmark/downstream/reports/model_transfer_evidence_package.tex` | True | `ec3fe8515ee6de01` | 4668 |
| support | `benchmark/downstream/reports/model_transfer_replication_protocol.json` | True | `ae3893cb2d81b943` | 8593 |
| support | `benchmark/downstream/reports/model_transfer_replication_protocol.md` | True | `b6f23a607ecb700a` | 6239 |
| support | `benchmark/downstream/reports/hard_v3_evidence_package.json` | True | `894b8f7a1f7ac296` | 27042 |
| support | `benchmark/downstream/reports/hard_v4_evidence_package.json` | True | `c7e729993e44503b` | 22128 |

Regeneration commands:
- `python scripts/export_model_transfer_evidence_package.py --assert-current-model-transfer`

### G12_model_transfer_cross_model - Model-Transfer Cross-Model Synthesis

| role | path | exists | sha256 | bytes |
| --- | --- | --- | --- | --- |
| primary | `benchmark/downstream/reports/model_transfer_cross_model_synthesis.json` | True | `fc575fd01e288008` | 68222 |
| primary | `benchmark/downstream/reports/model_transfer_cross_model_synthesis.md` | True | `f21e836c2239352d` | 9166 |
| primary | `benchmark/downstream/reports/model_transfer_cross_model_synthesis.tex` | True | `c6389b9aa76b7f11` | 4149 |
| support | `benchmark/downstream/reports/hard_v3_evidence_package.json` | True | `894b8f7a1f7ac296` | 27042 |
| support | `benchmark/downstream/reports/hard_v4_evidence_package.json` | True | `c7e729993e44503b` | 22128 |
| support | `benchmark/downstream/reports/model_transfer_evidence_package.json` | True | `32505f40e1635dcf` | 58893 |

Regeneration commands:
- `python scripts/export_model_transfer_cross_model_synthesis.py --assert-current-cross-model`

## Regeneration Order

| step | name | command | script exists |
| --- | --- | --- | --- |
| 1 | check_hard_v2 | `python scripts/check_downstream_hard_v2_tasks.py` | True |
| 2 | check_hard_v3 | `python scripts/check_downstream_hard_v3_tasks.py` | True |
| 3 | build_hard_v4 | `python scripts/build_downstream_hard_v4_tasks.py` | True |
| 4 | check_hard_v4 | `python scripts/check_downstream_hard_v4_tasks.py` | True |
| 5 | admission_regression | `python scripts/run_admission_regression.py` | True |
| 6 | summarize_hard_v2 | `python scripts/summarize_hard_v2_results.py --assert-current-hard-v2` | True |
| 7 | export_hard_v2 | `python scripts/export_hard_v2_evidence_package.py --assert-current-hard-v2` | True |
| 8 | summarize_hard_v3 | `python scripts/summarize_hard_v3_results.py --assert-current-hard-v3` | True |
| 9 | export_hard_v3 | `python scripts/export_hard_v3_evidence_package.py --assert-current-hard-v3` | True |
| 10 | export_hard_v4_scaffold | `python scripts/export_hard_v4_scaffold_manifest.py --run-checker --assert-current-hard-v4-scaffold` | True |
| 11 | summarize_hard_v4 | `python scripts/summarize_hard_v4_results.py --assert-current-hard-v4` | True |
| 12 | export_hard_v4 | `python scripts/export_hard_v4_evidence_package.py --assert-current-hard-v4` | True |
| 13 | export_cross_synthesis | `python scripts/export_downstream_cross_version_synthesis.py --assert-current-synthesis` | True |
| 14 | export_boundary_synthesis | `python scripts/export_downstream_boundary_synthesis.py --assert-current-boundary-synthesis` | True |
| 15 | export_paper_section | `python scripts/export_downstream_paper_section.py --assert-current-paper-section` | True |
| 16 | export_claim_defense | `python scripts/export_downstream_claim_defense_matrix.py --assert-current-claim-defense` | True |
| 17 | export_model_transfer_protocol | `python scripts/export_model_transfer_replication_protocol.py --assert-current-protocol` | True |
| 18 | export_model_transfer_evidence | `python scripts/export_model_transfer_evidence_package.py --assert-current-model-transfer` | True |
| 19 | export_model_transfer_cross_model | `python scripts/export_model_transfer_cross_model_synthesis.py --assert-current-cross-model` | True |
| 20 | export_artifacts_index | `python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index` | True |
| 21 | audit_paper_claim_consistency | `python scripts/audit_paper_claim_consistency.py --assert-current-audit` | True |

## Table Index

| table | paper role | primary artifacts | allowed claim | avoid |
| --- | --- | --- | --- | --- |
| T_admission_context | Optional setup table, not the main downstream claim. | `benchmark/reports/v7_admission_baselines.md`<br>`benchmark/reports/v7_admission_baselines.json` | v7 admission is frozen and useful context, but keyword baseline caveat limits semantic claims. | Do not claim v7 admission accuracy alone proves downstream utility. |
| T_hard_v2 | Hard v2 primary result table. | `benchmark/downstream/reports/hard_v2_paper_tables.md`<br>`benchmark/downstream/reports/hard_v2_paper_tables.tex`<br>`benchmark/downstream/reports/hard_v2_evidence_package.json` | hard_v2 supports tree-aware selected utility and exposes strict visible-file boundary. | Do not collapse hard_v2 settings into selected universally wins. |
| T_hard_v3 | Hard v3 boundary and artifact-adherence table. | `benchmark/downstream/reports/hard_v3_paper_tables.md`<br>`benchmark/downstream/reports/hard_v3_paper_tables.tex`<br>`benchmark/downstream/reports/hard_v3_evidence_package.json` | hard_v3 bounds selected-superiority and strengthens negative-transfer evidence. | Do not claim hard_v3 proves selected superiority or token savings. |
| T_hard_v4 | Hard v4 boundary table. | `benchmark/downstream/reports/hard_v4_paper_tables.md`<br>`benchmark/downstream/reports/hard_v4_paper_tables.tex`<br>`benchmark/downstream/reports/hard_v4_evidence_package.json` | hard_v4 shows tree-aware saturation, strict selected underperformance, and 0/48 forced-bad transfer. | Do not claim hard_v4 proves selected utility, selected token savings, or bad-advice safety. |
| T_cross_version | Main downstream synthesis table. | `benchmark/downstream/reports/downstream_cross_version_synthesis.md`<br>`benchmark/downstream/reports/downstream_cross_version_synthesis.tex`<br>`benchmark/downstream/reports/downstream_cross_version_synthesis.json` | hard_v2 is positive tree-aware evidence; hard_v3 is generalization boundary; forced bad is 0/85. | Do not read the synthesis as a single global leaderboard. |
| T_boundary_synthesis | Three-boundary synthesis table. | `benchmark/downstream/reports/downstream_boundary_synthesis.md`<br>`benchmark/downstream/reports/downstream_boundary_synthesis.tex`<br>`benchmark/downstream/reports/downstream_boundary_synthesis.json` | hard_v2/hard_v3/hard_v4 together show conditional positive evidence, generalization boundary, stricter boundary, and 0/133 forced-bad evidence. | Do not use the boundary synthesis as a selected-wins leaderboard or as a substitute for evidence packages. |
| T_model_transfer | Optional model-transfer replication table. | `benchmark/downstream/reports/model_transfer_evidence_package.md`<br>`benchmark/downstream/reports/model_transfer_cross_model_synthesis.md`<br>`benchmark/downstream/reports/model_transfer_evidence_package.json`<br>`benchmark/downstream/reports/model_transfer_cross_model_synthesis.json` | mimo-v2.5 transfer replicates forced-bad negative transfer and reveals model-sensitive selected deltas. | Do not claim model-general selected superiority or selected token savings from one transfer model. |
| T_claim_defense_appendix | Appendix or internal reviewer-response table. | `benchmark/downstream/reports/downstream_claim_defense_matrix.md`<br>`benchmark/downstream/reports/downstream_claim_defense_matrix.tex`<br>`benchmark/downstream/reports/downstream_claim_defense_matrix.json` | Use to police wording and prepare reviewer responses. | Do not cite defense wording as if it were an additional experiment. |

## Claim To Artifact Map

| claim | status | primary artifact | supporting artifacts | allowed wording | forbidden wording |
| --- | --- | --- | --- | --- | --- |
| C1_downstream_hidden_verifier_is_required | supported_design_claim | `benchmark/downstream/reports/downstream_claim_defense_matrix.json` | `benchmark/downstream/reports/hard_v2_evidence_package.json`<br>`benchmark/downstream/reports/hard_v3_evidence_package.json`<br>`benchmark/downstream/reports/hard_v4_evidence_package.json` | We complement admission accuracy with downstream hidden-verifier validation. | Admission accuracy alone proves downstream utility. |
| C2_hard_v2_tree_selected_positive | supported_conditional_claim | `benchmark/downstream/reports/downstream_claim_defense_matrix.json` | `benchmark/downstream/reports/hard_v2_evidence_package.json` | On hard_v2 with repo-tree context, SkillAdmit-selected reached 25/25 versus 23/25 for no_experience. | SkillAdmit-selected universally beats no_experience. |
| C3_hard_v2_strict_visible_boundary | boundary_claim | `benchmark/downstream/reports/downstream_claim_defense_matrix.json` | `benchmark/downstream/reports/hard_v2_evidence_package.json` | Strict visible-file hard_v2 is a boundary where selected-only context is insufficient. | SkillAdmit-selected wins hard_v2 overall. |
| C4_hard_v3_generalization_boundary | boundary_claim | `benchmark/downstream/reports/downstream_claim_defense_matrix.json` | `benchmark/downstream/reports/hard_v3_evidence_package.json`<br>`benchmark/downstream/reports/hard_v4_evidence_package.json` | hard_v3 and hard_v4 are generalization boundaries for the selected-superiority claim. | hard_v3 proves SkillAdmit-selected superiority. |
| C5_repo_tree_and_preconditions_are_context_variables | conditional_claim | `benchmark/downstream/reports/downstream_claim_defense_matrix.json` | `benchmark/downstream/reports/hard_v2_evidence_package.json`<br>`benchmark/downstream/reports/hard_v3_evidence_package.json`<br>`benchmark/downstream/reports/hard_v4_evidence_package.json`<br>`benchmark/downstream/reports/downstream_boundary_synthesis.json` | Repo tree and preconditions should be treated as task-context variables. | Precondition-only replaces repository tree. |
| C6_forced_bad_artifacts_negative_transfer | strong_supported_claim | `benchmark/downstream/reports/downstream_claim_defense_matrix.json` | `benchmark/downstream/reports/hard_v2_evidence_package.json`<br>`benchmark/downstream/reports/hard_v3_evidence_package.json`<br>`benchmark/downstream/reports/hard_v4_evidence_package.json`<br>`benchmark/downstream/reports/downstream_boundary_synthesis.json` | Forced harmful artifacts produce systematic negative transfer: 0/133 success with 133 public-pass/hidden-fail cases. | SkillAdmit proves all admitted artifacts are safe. |
| C7_bad_dependency_rule_is_not_safe | caveat_claim | `benchmark/downstream/reports/downstream_claim_defense_matrix.json` | `benchmark/downstream/reports/hard_v3_evidence_package.json`<br>`benchmark/downstream/reports/hard_v2_evidence_package.json`<br>`benchmark/downstream/reports/hard_v4_evidence_package.json` | The model often succeeds by ignoring harmful advice. | Bad dependency advice is safe. |
| C8_raw_memory_is_a_serious_baseline_not_a_policy | boundary_claim | `benchmark/downstream/reports/downstream_claim_defense_matrix.json` | `benchmark/downstream/reports/hard_v2_evidence_package.json`<br>`benchmark/downstream/reports/hard_v3_evidence_package.json`<br>`benchmark/downstream/reports/hard_v4_evidence_package.json` | Raw memory must be reported as a serious comparison condition. | Raw memory is safe because it reaches 30/30 on hard_v3. |
| C9_selected_token_savings_not_supported | not_supported_claim | `benchmark/downstream/reports/downstream_claim_defense_matrix.json` | `benchmark/downstream/reports/downstream_boundary_synthesis.json` | Token savings are not a supported paper claim. | SkillAdmit-selected reduces token cost. |
| C10_all_skills_is_strong_but_not_the_target_policy | boundary_claim | `benchmark/downstream/reports/downstream_claim_defense_matrix.json` | `benchmark/downstream/reports/hard_v2_evidence_package.json`<br>`benchmark/downstream/reports/hard_v3_evidence_package.json`<br>`benchmark/downstream/reports/hard_v4_evidence_package.json` | All-skills is a strong upper-context comparison and should be reported. | Selection always beats all-skills. |

## Do Not Cite As Primary Evidence

| artifact pattern | reason |
| --- | --- |
| benchmark/downstream/llm_runs/*/summary.json | Per-run summaries are useful for debugging but should not be the paper's primary evidence once matrix/evidence packages exist. |
| benchmark/downstream/llm_runs/*/trajectories.jsonl | Trajectories are provenance/debugging records; cite aggregated evidence packages instead. |
| benchmark/downstream_hard_v2/tasks/* and benchmark/downstream_hard_v3/tasks/* | Task files define the benchmark and verifiers; do not use inspected failures for prompt tuning while preserving clean evidence. |
| benchmark/downstream_hard_v4/tasks/* | hard_v4 task files define a frozen evaluation boundary; do not tune prompts or strategies from inspected hard_v4 failures. |
| docs/progress_log.md | Progress log is a handoff ledger, not a primary empirical table. |
| benchmark/downstream/reports/paper_claim_consistency_audit.* | Consistency audit reports are reporting-hygiene checks, not additional downstream evidence. |
| benchmark/downstream/reports/model_transfer_replication_protocol.* | Model-transfer protocol reports are pre-run registration artifacts, not model-performance evidence. |

## Next Experimental Boundary

Recommended: boundary-synthesis-driven paper revision, model-transfer write-up, or a predeclared hard_v5 boundary.

Avoid: Do not tune hard_v2/hard_v3/hard_v4 prompts or strategies from observed failures while still treating them as clean evidence.

## Source Inputs

| name | path | exists | sha256 | generated_at_utc |
| --- | --- | --- | --- | --- |
| v7_admission_baselines | `benchmark/reports/v7_admission_baselines.json` | True | `ed051957b16aa28f` |  |
| llm_cost_summary | `benchmark/reports/llm_cost_summary.json` | True | `ef312b1019006778` |  |
| hard_v2_evidence_package | `benchmark/downstream/reports/hard_v2_evidence_package.json` | True | `7deb038d4adfc285` | `2026-05-22T05:36:13.500710+00:00` |
| hard_v3_evidence_package | `benchmark/downstream/reports/hard_v3_evidence_package.json` | True | `894b8f7a1f7ac296` | `2026-05-22T13:03:52.487189+00:00` |
| hard_v4_evidence_package | `benchmark/downstream/reports/hard_v4_evidence_package.json` | True | `c7e729993e44503b` | `2026-05-23T04:55:41.380270+00:00` |
| downstream_cross_version_synthesis | `benchmark/downstream/reports/downstream_cross_version_synthesis.json` | True | `e5d5bf0e8545fb09` | `2026-05-22T13:23:18.827390+00:00` |
| downstream_boundary_synthesis | `benchmark/downstream/reports/downstream_boundary_synthesis.json` | True | `b5e58a54217563fb` | `2026-05-23T05:33:33.739619+00:00` |
| downstream_paper_eval_section | `benchmark/downstream/reports/downstream_paper_eval_section.json` | True | `f026bad7830e2a84` | `2026-05-23T06:49:54.471664+00:00` |
| downstream_claim_defense_matrix | `benchmark/downstream/reports/downstream_claim_defense_matrix.json` | True | `09f38bb09aa273ea` | `2026-05-23T06:49:54.699347+00:00` |
| hard_v4_scaffold_manifest | `benchmark/downstream/reports/hard_v4_scaffold_manifest.json` | True | `1e7d9adb0b9e9dc9` | `2026-05-22T15:03:42.737147+00:00` |
| model_transfer_evidence_package | `benchmark/downstream/reports/model_transfer_evidence_package.json` | True | `32505f40e1635dcf` | `2026-05-23T10:22:44.498111+00:00` |
| model_transfer_cross_model_synthesis | `benchmark/downstream/reports/model_transfer_cross_model_synthesis.json` | True | `fc575fd01e288008` | `2026-05-23T10:22:44.566296+00:00` |
