# SkillAdmit Paper Evaluation Status

Last updated: 2026-05-23

## 1. Current Honest Evaluation Result

Current frozen controller:

```text
skilladmit.controllers.rule_based_controller_v6_frozen
```

Current clean blind sample file:

```text
benchmark/admission_samples/v7_blind_admission_samples.jsonl
```

Result:

```text
samples:  50
correct:  49
accuracy: 0.980
macro_f1: 0.980
```

Only error:

```text
sample_v7_skill_grpc_deadline_idempotent_retry
gold: distill_into_skill
pred: promote_to_rule
```

Interpretation:

```text
The current controller is strong on v7, but still has a boundary error between
scoped reusable skills and global rules.
```

Do not tune on v7 and still call v7 held-out.

## 2. Baseline Comparison

Baseline report:

```text
benchmark/reports/v7_admission_baselines.md
benchmark/reports/v7_admission_baselines.json
```

Summary on v7:

```text
always_discard:            10/50, accuracy 0.200, macro_f1 0.067
always_store_as_memory:    10/50, accuracy 0.200, macro_f1 0.067
always_distill_into_skill: 10/50, accuracy 0.200, macro_f1 0.067
always_promote_to_rule:    10/50, accuracy 0.200, macro_f1 0.067
always_defer:              10/50, accuracy 0.200, macro_f1 0.067
keyword_level_baseline:    49/50, accuracy 0.980, macro_f1 0.980
v6_frozen_controller:      49/50, accuracy 0.980, macro_f1 0.980
```

Important interpretation:

```text
The always baselines are beaten decisively. However, keyword_level_baseline
matches the controller on v7, although it fails on a different sample.
```

This is a warning sign. The current v7 benchmark still contains enough explicit
surface wording that a simple keyword baseline can perform very well. This does
not invalidate the engineering pipeline, but it means a paper should not claim
that v7 proves deep semantic admission reasoning.

The next stronger benchmark should include:

```text
less label-obvious wording
more paraphrased candidates
independently authored samples
randomized or template-varied phrasing
LLM-as-judge baseline
downstream validation beyond label accuracy
```

## 3. Cost Accounting

Cost report:

```text
benchmark/reports/llm_cost_summary.md
benchmark/reports/llm_cost_summary.json
```

Observed real LLM coding-agent trajectory cost:

```text
tasks:                     20
successes:                 20
success_rate:              1.000
prompt_tokens:             14916
completion_tokens:         24083
total_tokens:              38999
avg_tokens_per_task:       1950.0
total_model_latency_sec:   483.382
avg_model_latency_sec:     24.169
```

Cost by template:

```text
T1_missing_third_party_package:              4 tasks,  4841 tokens, avg 1210.2
T2_local_module_mistaken_as_missing_package: 4 tasks, 14721 tokens, avg 3680.2
T3_relative_import_executed_as_script:       4 tasks,  6317 tokens, avg 1579.2
T4_wrong_current_working_directory:          4 tasks,  8464 tokens, avg 2116.0
T5_broken_package_structure:                 4 tasks,  4656 tokens, avg 1164.0
```

Admission artifact cost:

```text
admitted_artifacts:                      5
source_tokens_admitted_artifacts:        38999
avg_source_tokens_per_admitted_artifact: 7799.8
```

Parameterised break-even estimate:

```text
assumed tokens_saved_per_artifact_use:      500
assumed expected_uses_per_future_task:      1.0
estimated_saved_tokens_per_future_task:     2500
break_even_future_tasks:                    15.60
break_even_uses_per_artifact:               15.60
```

This is not a measured downstream saving yet. It is only an accounting estimate.

## 4. What Can Be Claimed Now

Reasonable claim:

```text
SkillAdmit now has a reproducible admission benchmark pipeline with real LLM
agent trajectories, balanced admission labels, frozen-controller evaluation,
simple baselines, and initial token-cost accounting.
```

Also reasonable:

```text
The current controller strongly beats trivial always-action baselines on v7.
```

Not yet reasonable:

```text
The current controller proves semantic admission reasoning.
The current token accounting proves downstream token savings.
The current benchmark is immune to keyword matching.
```

## 5. Downstream Validation v0

A first executable downstream validation has been added.

Protocol:

```text
docs/downstream_validation_v0.md
```

Scripts:

```text
scripts/build_downstream_py_import_tasks.py
scripts/run_downstream_validation.py
```

Outputs:

```text
benchmark/downstream/results/downstream_validation_v0.jsonl
benchmark/downstream/results/downstream_validation_v0_summary.json
benchmark/downstream/results/downstream_validation_v0_report.md
```

Result:

```text
bad_dependency_stub:   5/25  success_rate=0.200  negative_transfer=10
distilled_skill:      25/25  success_rate=1.000  negative_transfer=0
no_experience:         0/25  success_rate=0.000  negative_transfer=0
promoted_rule_only:    0/25  success_rate=0.000  negative_transfer=0
raw_memory_replay:     0/25  success_rate=0.000  negative_transfer=0
skilladmit_selected:  25/25  success_rate=1.000  negative_transfer=0
```

Interpretation:

```text
The downstream machinery works end to end. Distilled skills transfer in this
controlled task family; raw memory replay and rule-only artifacts do not solve
future tasks by themselves; the overgeneralized dependency baseline creates
negative transfer.
```

Caveat:

```text
This is a deterministic proxy experiment, not the final LLM-agent downstream
result.
```

## 6. LLM Downstream Validation v0

A real LLM downstream runner has been added.

Protocol:

```text
docs/llm_downstream_validation_v0.md
```

Runner:

```text
scripts/run_llm_downstream_validation.py
```

Smoke outputs:

```text
benchmark/downstream/llm_runs/llm_downstream_v0_smoke_5x2/
benchmark/downstream/llm_runs/llm_downstream_v0_smoke_bad_raw_5x2/
```

Smoke result:

```text
no_experience:       5/5 success_rate=1.000 negative_transfer=0 total_tokens=7789
skilladmit_selected: 5/5 success_rate=1.000 negative_transfer=0 total_tokens=8112
raw_memory:          5/5 success_rate=1.000 negative_transfer=0 total_tokens=8927
bad_dependency_rule: 5/5 success_rate=1.000 negative_transfer=0 total_tokens=11044
```

Interpretation:

```text
The real LLM downstream runner is operational. However, the current smoke tasks
are too easy for the model: no_experience already solves all five sampled
families. Therefore this run does not prove artifact benefit.
```

## 7. LLM Downstream Hard v1

A harder real LLM downstream setting has been added after the first smoke proved
too easy.

Protocol:

```text
docs/llm_downstream_hard_v1.md
```

Generator:

```text
scripts/build_downstream_hard_v1_tasks.py
```

Runner:

```text
scripts/run_llm_downstream_validation.py
```

Task sanity:

```text
initial_passed: 0/5
initial_failed: 5/5
gold_like_repairs_passed: 5/5
```

Main result:

```text
no_experience:       4/5 success_rate=0.800 negative_transfer=1 total_tokens=9530
skilladmit_selected: 5/5 success_rate=1.000 negative_transfer=0 total_tokens=15903
```

Additional result:

```text
raw_memory:           5/5 success_rate=1.000 negative_transfer=0 total_tokens=13140
promoted_rules:       5/5 success_rate=1.000 negative_transfer=0 total_tokens=16218
distilled_skills_all: 5/5 success_rate=1.000 negative_transfer=0 total_tokens=17515
bad_dependency_rule:  5/5 success_rate=1.000 negative_transfer=0 total_tokens=13923
```

Interpretation:

```text
Hard v1 provides the first real-LLM downstream signal where no_experience is not
perfect. The important case is hard_py_import_004: no_experience created a
top-level adapters/ package that passed public pytest but failed hidden
validation; skilladmit_selected used the package-internal import repair and
passed.
```

Caveat:

```text
This is useful small-scale evidence, not a final downstream claim. It has only
five tasks, and the bad_dependency_rule condition did not create negative
transfer because the model ignored the bad artifact.
```

## 8. Previously Recommended Downstream Step

The paper-critical step after hard v1 was scaled harder LLM-based downstream
validation. That target has now been completed as hard_v2; section 9 records the
current result and caveats.

A stronger downstream validation should compare:

```text
no experience
raw memory
distilled skill
promoted rule
SkillAdmit-selected artifact
```

on future debug tasks, measuring:

```text
success rate
tokens used
commands/actions used
negative-transfer failures
verifier pass rate
```

This should use a task suite where no_experience is not already perfect. That is
more valuable now than tuning v7 from 49/50 to 50/50 or polishing the
deterministic downstream proxy.

Immediate target:

```text
hard_v2 with 25 tasks
visible-file budgets
hidden verifier checks
several cases where no_experience tends to create masking stubs
forced_bad_artifact condition for negative-transfer evidence
```

## 9. LLM Downstream Hard v2

Hard v2 has been implemented.

Protocol:

```text
docs/llm_downstream_hard_v2.md
```

Task sanity:

```text
total: 25
initial_failed: 25
gold_passed: 25
forced_public_passed: 25
forced_verifier_failed: 25
```

Forced bad-artifact baseline:

```text
forced_bad_artifact: 0/25
success_rate: 0.000
negative_transfer: 25
public_passed_hidden_failed: 25
```

Real LLM canary:

```text
no_experience:       4/5 success_rate=0.800 negative_transfer=1 public_passed_hidden_failed=1 total_tokens=12775
skilladmit_selected: 5/5 success_rate=1.000 negative_transfer=0 public_passed_hidden_failed=0 total_tokens=13840
```

Interpretation:

```text
Hard v2 establishes a stronger downstream scaffold: 25 validated tasks plus a
deterministic harmful-artifact baseline. The real LLM canary again shows that
SkillAdmit-selected context can prevent a public-pass/hidden-fail masking
repair.
```

Caveat:

```text
The full 25-task real LLM comparison has now been run. Results differ by
executor context: strict visible-file prompts and tree-aware prompts should be
reported separately.
```

Full strict visible-file run:

```text
distilled_skills_all: 25/25 success_rate=1.000 negative_transfer=0 total_tokens=84986
no_experience:        24/25 success_rate=0.960 negative_transfer=0 total_tokens=59272
skilladmit_selected:  23/25 success_rate=0.920 negative_transfer=2 total_tokens=66608
raw_memory:           22/25 success_rate=0.880 negative_transfer=3 total_tokens=56941
bad_dependency_rule:  22/25 success_rate=0.880 negative_transfer=2 total_tokens=75724
promoted_rules:       21/25 success_rate=0.840 negative_transfer=4 total_tokens=77858
forced_bad_artifact:   0/25 success_rate=0.000 negative_transfer=25 public_passed_hidden_failed=25
```

Tree-aware run:

```text
no_experience:       23/25 success_rate=0.920 negative_transfer=2 total_tokens=51548
skilladmit_selected: 25/25 success_rate=1.000 negative_transfer=0 total_tokens=57597
```

Selected + precondition context run:

```text
skilladmit_selected_with_precondition_context:
  25/25 success_rate=1.000 negative_transfer=0
  public_passed_hidden_failed=0
  artifact_adherence=25/25
  parse_errors=0
  total_tokens=67504
```

Strict precondition-only ablation, first run:

```text
skilladmit_selected_with_precondition_only:
  24/25 success_rate=0.960 negative_transfer=1
  public_passed_hidden_failed=0
  artifact_adherence=25/25
  parse_errors=0
  included_repo_tree=0/25
  total_tokens=72316
```

Paper-facing interpretation:

```text
Hard v2 gives stronger downstream evidence than admission accuracy alone.

In a strict visible-file setting, giving all distilled skills is strongest but
token-expensive; selected-only can fail when the executor lacks enough
precondition context.

In a tree-aware setting closer to a real coding agent, SkillAdmit-selected
context improves success over no experience: 25/25 vs 23/25.

The selected+precondition variant also reaches 25/25. It is cheaper than giving
all distilled skills (67504 vs 84986 tokens) and makes the key path/import
preconditions explicit, but it is not cheaper than ordinary tree-aware selected
(67504 vs 57597 tokens).

Replication strengthens the tree-aware conclusion: tree-aware selected was 25/25
in both runs, and tree-aware selected+precondition was also 25/25 in both runs.

Replication weakens the precondition-only story: the strict precondition-only
condition was 24/25 on the first run and 23/25 on replication. It fails T3
script-mode relative-import handling consistently and can still fail T4
cwd-sensitive path handling. This is direct evidence that precondition text helps
less reliably than repository-tree context.

The forced_bad_artifact baseline shows that admitting harmful artifacts can
produce systematic negative transfer: 0/25 with 25 public-pass/hidden-fail
cases.
```

Remaining caveat:

```text
Do not claim token savings yet. The strongest positive SkillAdmit-selected
result uses slightly more tokens than no_experience in the tree-aware setting.
The precondition-context variant strengthens interpretability and guardrail
explicitness, not raw success over ordinary tree-aware selected, because both
reach 25/25 on this run.
The precondition-only ablation should not be reported as a new best condition:
it is less accurate, less stable, and more token-expensive than tree-aware
selected.
```

Stability summary:

```text
tree-aware selected:
  25/25, tokens=57597
  25/25, tokens=52144

tree-aware selected+precondition:
  25/25, tokens=67504
  25/25, tokens=64150

strict precondition-only:
  24/25, tokens=72316, failures=hard_v2_py_import_012
  23/25, tokens=77487, failures=hard_v2_py_import_012 and hard_v2_py_import_018
```

Evidence ledger:

```text
benchmark/downstream/reports/hard_v2_strategy_matrix.json
benchmark/downstream/reports/hard_v2_strategy_matrix.md
```

Generated by:

```text
scripts/summarize_hard_v2_results.py
```

Purpose:

```text
Keep the hard_v2 downstream evidence in one auditable matrix. The report records
strategy-level results, template-level results, failure cases, and SHA-256 hashes
for each run's summary and trajectory files.
```

Paper-facing evidence package:

```text
benchmark/downstream/reports/hard_v2_evidence_package.json
benchmark/downstream/reports/hard_v2_paper_tables.md
benchmark/downstream/reports/hard_v2_paper_tables.tex
```

Generated by:

```text
scripts/export_hard_v2_evidence_package.py --assert-current-hard-v2
```

Current export:

```text
primary_rows: 11
stability_rows: 3
failure_taxonomy_rows: 25
```

Use this package for paper tables rather than hand-copying from an individual
`summary.json`. It contains explicit supported and unsupported claims so the
paper does not overstate token savings, universal superiority, or
precondition-only reliability.

## 10. LLM Downstream Hard v3

Hard v3 has been added as the next clean downstream validation boundary after
hard_v2.

Protocol:

```text
docs/llm_downstream_hard_v3.md
```

Scripts:

```text
scripts/build_downstream_hard_v3_tasks.py
scripts/check_downstream_hard_v3_tasks.py
```

Task directory:

```text
benchmark/downstream_hard_v3/tasks/
```

Current deterministic scaffold:

```text
30 tasks = 6 templates x 5 variants

initial_failed: 30/30
gold_passed: 30/30
forced_public_passed: 30/30
forced_verifier_failed: 30/30
```

Current tree-aware core LLM run:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v3_tree_core_30x2/
```

Result:

```text
forced_bad_artifact:
  0/30 success_rate=0.000
  negative_transfer=30
  public_passed_hidden_failed=30
  parse_errors=0
  total_tokens=0

no_experience:
  29/30 success_rate=0.967
  negative_transfer=1
  public_passed_hidden_failed=0
  parse_errors=0
  total_tokens=70208

skilladmit_selected:
  29/30 success_rate=0.967
  negative_transfer=1
  public_passed_hidden_failed=0
  parse_errors=0
  total_tokens=69291

skilladmit_selected_with_precondition_context:
  29/30 success_rate=0.967
  negative_transfer=1
  public_passed_hidden_failed=0
  parse_errors=0
  total_tokens=74559
```

Failure distribution:

```text
no_experience:
  hard_v3_agent_013, T3_dual_use_command_module

skilladmit_selected:
  hard_v3_agent_027, T6_template_resource_cwd_path

skilladmit_selected_with_precondition_context:
  hard_v3_agent_027, T6_template_resource_cwd_path

forced_bad_artifact:
  all 30 tasks, all public-pass/hidden-fail negative transfer
```

Current full hard_v3 strategy matrix:

```text
benchmark/downstream/reports/hard_v3_strategy_matrix.json
benchmark/downstream/reports/hard_v3_strategy_matrix.md
benchmark/downstream/reports/hard_v3_evidence_package.json
benchmark/downstream/reports/hard_v3_paper_tables.md
benchmark/downstream/reports/hard_v3_paper_tables.tex
```

Generated by:

```text
scripts/summarize_hard_v3_results.py --assert-current-hard-v3
scripts/export_hard_v3_evidence_package.py --assert-current-hard-v3
```

Matrix summary:

```text
tree-aware:
  bad_dependency_rule:                            30/30, tokens=68671, artifact_adherence=4/30
  distilled_skills_all:                           30/30, tokens=75603
  forced_bad_artifact:                             0/30, public_hidden=30
  no_experience:                                  29/30, tokens=70208
  promoted_rules:                                 29/30, public_hidden=1, tokens=73114
  raw_memory:                                     30/30, tokens=68753
  skilladmit_selected:                            29/30, tokens=69291
  skilladmit_selected_with_precondition_context:  29/30, tokens=74559

strict visible-file:
  bad_dependency_rule:                            30/30, tokens=75920, artifact_adherence=11/30
  distilled_skills_all:                           29/30, public_hidden=1, tokens=83366
  forced_bad_artifact:                             0/30, public_hidden=30
  no_experience:                                  28/30, tokens=74153
  promoted_rules:                                 29/30, tokens=80112
  raw_memory:                                     30/30, tokens=73789
  skilladmit_selected:                            29/30, tokens=71390
  skilladmit_selected_with_precondition_only:     30/30, tokens=82615
```

Current hard_v3 paper export:

```text
primary_rows: 16
artifact_adherence_rows: 14
non_forced_failures: 9
```

Interpretation:

```text
Hard v3 now provides a first real LLM downstream result on a fresh task boundary.
The result is deliberately narrower than hard_v2's positive tree-aware selected
claim: selected does not beat no_experience in aggregate on the hard_v3
tree-aware run. Both are 29/30.

The strict visible-file result gives a different boundary: selected is 29/30,
no_experience is 28/30, and selected+precondition-only is 30/30. This supports
the idea that explicit preconditions can help, but it does not make ordinary
SkillAdmit-selected the best condition.

Raw memory reaches 30/30 in both hard_v3 settings. This is a real downstream
observation, but it should not be inflated into an admission-policy claim
without considering memory cost, specificity, and harmful-memory controls.

The strong hard_v3 paper-facing signal is negative transfer. The forced bad
artifact condition is 0/30 in both settings and every failure is
public-pass/hidden-fail, which directly supports the idea that admitting harmful
experience can systematically damage downstream behavior even when public tests
pass.
```

Current claim boundary:

```text
Do not claim that SkillAdmit-selected beats no_experience on hard_v3. In the
tree-aware run they are tied at 29/30. In the strict visible-file run selected
is only +1 over no_experience and is not the best condition.

Do not claim that selected+precondition-context improves tree-aware hard_v3
accuracy over ordinary selected. Both are 29/30 and both fail
hard_v3_agent_027.

Do not claim hard_v3 token savings for SkillAdmit-selected. Ordinary selected
uses slightly fewer tokens than no_experience in both settings, but the strongest
success conditions are raw-memory or selected+precondition-only, and
selected+precondition-only is token-expensive.

Do not claim hard_v3 proves repo-tree necessity. Strict precondition-only reaches
30/30 on hard_v3, which differs from hard_v2 and should be framed as a
task-suite-specific boundary.

Do not claim bad_dependency_rule is safe because it reaches 30/30. Its artifact
adherence is low, so this mostly shows that the model can ignore bad advice.
The forced_bad_artifact condition is the harmful-experience control.

Do not tune prompts or strategy text from hard_v3_agent_013 or hard_v3_agent_027
unless hard_v3 is explicitly reclassified as development data.
```

## 11. Cross-Version Downstream Synthesis

Paper-facing synthesis report:

```text
benchmark/downstream/reports/downstream_cross_version_synthesis.json
benchmark/downstream/reports/downstream_cross_version_synthesis.md
benchmark/downstream/reports/downstream_cross_version_synthesis.tex
```

Generated by:

```text
scripts/export_downstream_cross_version_synthesis.py --assert-current-synthesis
```

Current export:

```text
primary_rows: 27
forced_bad_total_tasks: 85
forced_bad_total_successes: 0
forced_bad_total_public_passed_hidden_failed: 85
selected_superiority_consistent: False
selected_token_savings_supported: False
repo_tree_necessity_universal: False
```

Best current paper framing:

```text
The downstream validation story is not "SkillAdmit-selected always wins".

The stronger and more defensible claim is:
  SkillAdmit can admit useful coding-agent experience, and hard_v2 shows this
  under a tree-aware downstream executor. However, hard_v3 shows that the
  benefit is conditional: selected context does not universally dominate
  no_experience, raw_memory, all-skills, or explicit precondition variants.

The most stable safety claim is:
  harmful admitted artifacts cause systematic public-pass/hidden-fail negative
  transfer when forced into the executor: 0/85 success across hard_v2 and
  hard_v3 forced controls.
```

Do not flatten hard_v2 and hard_v3 into one leaderboard. Report them as two
downstream boundaries with different roles:

```text
hard_v2: positive tree-aware selected evidence.
hard_v3: generalization boundary and negative-transfer evidence.
```

## 12. Paper Section Export

Paper-ready evaluation section:

```text
benchmark/downstream/reports/downstream_paper_eval_section.json
benchmark/downstream/reports/downstream_paper_eval_section.md
benchmark/downstream/reports/downstream_paper_eval_section.tex
```

Generated by:

```text
scripts/export_downstream_paper_section.py --assert-current-paper-section
```

Current export:

```text
research_questions: 3
result_paragraphs: 5
claim_limits: 7
forced_bad_total_tasks: 85
```

Best use:

```text
Use the generated section as the starting point for the downstream validation
subsection in the paper. Edit prose style if needed, but preserve the claim
limits: no universal selected superiority, no cross-version token-savings
claim, and no proof that precondition-only or raw memory are safe admission
policies.
```

## 13. Claim Defense Matrix

Reviewer-facing claim matrix:

```text
benchmark/downstream/reports/downstream_claim_defense_matrix.json
benchmark/downstream/reports/downstream_claim_defense_matrix.md
benchmark/downstream/reports/downstream_claim_defense_matrix.tex
```

Generated by:

```text
scripts/export_downstream_claim_defense_matrix.py --assert-current-claim-defense
```

Current export:

```text
claim_count: 10
global_red_lines: 6
```

Purpose:

```text
Use this matrix as the paper's guardrail during revision. It records each
allowed downstream claim, its evidence rows, forbidden stronger claims, required
qualifiers, and likely reviewer response.
```

## 14. Paper Artifacts Index

Top-level artifact index:

```text
benchmark/downstream/reports/paper_artifacts_index.json
benchmark/downstream/reports/paper_artifacts_index.md
benchmark/downstream/reports/paper_artifacts_index.tex
```

Generated by:

```text
scripts/export_paper_artifacts_index.py --assert-current-artifacts-index
```

Current export:

```text
artifact_groups: 10
table_index: 7
claim_map: 10
forced_bad_total_tasks: 85
hard_v4_forced_bad_total_tasks: 48
boundary_forced_bad_total_tasks: 133
```

Purpose:

```text
Use this as the navigation layer for paper writing. It separates primary
evidence packages, synthesis reports, generated drafting aids, claim-defense
tables, and handoff logs. It also records files that should not be cited as
primary evidence, such as individual llm_runs summary.json files.
```

## 15. Hard v4 Downstream Status

Hard v4 is now a completed fresh downstream boundary. It should be used as
boundary evidence, not as a SkillAdmit-selected success claim.

Protocol and scripts:

```text
docs/llm_downstream_hard_v4.md
scripts/build_downstream_hard_v4_tasks.py
scripts/check_downstream_hard_v4_tasks.py
scripts/export_hard_v4_scaffold_manifest.py
scripts/summarize_hard_v4_results.py
scripts/export_hard_v4_evidence_package.py
```

Current deterministic scaffold validation:

```text
tasks_dir: benchmark/downstream_hard_v4/tasks/
tasks: 24
templates: 6
variants_per_template: 4
files: 244
initial_failed: 24/24
gold_passed: 24/24
forced_public_passed: 24/24
forced_verifier_failed: 24/24
```

Scaffold manifest:

```text
benchmark/downstream/reports/hard_v4_scaffold_manifest.json
benchmark/downstream/reports/hard_v4_scaffold_manifest.md
benchmark/downstream/reports/hard_v4_scaffold_manifest.tex
```

LLM runs:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v4_tree_24x8/
benchmark/downstream/llm_runs/llm_downstream_hard_v4_strict_24x8/
```

Paper-facing evidence:

```text
benchmark/downstream/reports/hard_v4_strategy_matrix.json
benchmark/downstream/reports/hard_v4_strategy_matrix.md
benchmark/downstream/reports/hard_v4_evidence_package.json
benchmark/downstream/reports/hard_v4_paper_tables.md
benchmark/downstream/reports/hard_v4_paper_tables.tex
```

Current matrix:

```text
tree-aware:
  no_experience:                                  24/24, tokens=46685
  skilladmit_selected:                            24/24, tokens=48682
  skilladmit_selected_with_precondition_context:  24/24, tokens=63586
  raw_memory:                                     24/24, tokens=53406
  distilled_skills_all:                           24/24, tokens=68776
  bad_dependency_rule:                            24/24, tokens=51974, artifact_adherence=7/24
  promoted_rules:                                 24/24, tokens=58813
  forced_bad_artifact:                             0/24, public_hidden=24

strict visible-file:
  no_experience:                                  24/24, tokens=53055
  skilladmit_selected:                            22/24, tokens=58450
  skilladmit_selected_with_precondition_only:     23/24, tokens=69961
  raw_memory:                                     23/24, tokens=65070
  distilled_skills_all:                           24/24, tokens=69049
  bad_dependency_rule:                            24/24, tokens=63789, artifact_adherence=4/24
  promoted_rules:                                 23/24, tokens=69221
  forced_bad_artifact:                             0/24, public_hidden=24
```

Interpretation:

```text
Hard v4 does not support a SkillAdmit-selected downstream-success claim.
Tree-aware hard_v4 is saturated: all non-forced strategies reach 24/24.
Strict visible-file hard_v4 is worse for selected: no_experience reaches 24/24,
while ordinary selected reaches 22/24 and selected+precondition-only reaches
23/24.

The main hard_v4 evidence is the negative-transfer control. Forced bad artifacts
are 0/48 across the two hard_v4 settings, with 48 public-pass/hidden-fail
cases.

The ordinary bad_dependency_rule condition should not be interpreted as safe.
Its artifact adherence is only 7/24 tree-aware and 4/24 strict.
```

Next experimental step:

```text
Do not tune hard_v4 prompts or strategies from these failures. The next clean
experimental step is either model-transfer replication or a new predeclared
hard_v5 boundary. Do not claim selected utility or token savings from hard_v4.
```

## 16. Downstream Boundary Synthesis

The hard_v2/hard_v3/hard_v4 boundary synthesis is now exported separately from
the older hard_v2/hard_v3 cross-version synthesis.

Artifacts:

```text
benchmark/downstream/reports/downstream_boundary_synthesis.json
benchmark/downstream/reports/downstream_boundary_synthesis.md
benchmark/downstream/reports/downstream_boundary_synthesis.tex
```

Generated by:

```text
scripts/export_downstream_boundary_synthesis.py --assert-current-boundary-synthesis
```

Current synthesis:

```text
primary_rows: 43
selected_comparisons: 6
context_comparisons: 9
forced_bad_total: 0/133
public_passed_hidden_failed: 133
```

Paper-facing interpretation:

```text
hard_v2:
  conditional positive evidence for tree-aware SkillAdmit-selected

hard_v3:
  generalization boundary; selected does not universally dominate

hard_v4:
  stricter boundary; strict visible-file selected is below no_experience

forced_bad_artifact:
  0/133 across hard_v2, hard_v3, and hard_v4
```

This is now the strongest high-level downstream claim boundary. It should be
used to discipline paper wording, not to claim universal selected superiority.

## 17. Three-Boundary Paper Reporting Layer

The generated downstream paper section and claim-defense matrix now read the
hard_v2/hard_v3/hard_v4 boundary synthesis instead of the older hard_v2/hard_v3
cross-version synthesis.

Updated scripts:

```text
scripts/export_downstream_paper_section.py --assert-current-paper-section
scripts/export_downstream_claim_defense_matrix.py --assert-current-claim-defense
scripts/export_paper_artifacts_index.py --assert-current-artifacts-index
```

Updated paper-facing artifacts:

```text
benchmark/downstream/reports/downstream_paper_eval_section.json
benchmark/downstream/reports/downstream_paper_eval_section.md
benchmark/downstream/reports/downstream_paper_eval_section.tex
benchmark/downstream/reports/downstream_claim_defense_matrix.json
benchmark/downstream/reports/downstream_claim_defense_matrix.md
benchmark/downstream/reports/downstream_claim_defense_matrix.tex
benchmark/downstream/reports/paper_artifacts_index.json
benchmark/downstream/reports/paper_artifacts_index.md
benchmark/downstream/reports/paper_artifacts_index.tex
```

Current exports:

```text
paper_section:
  research_questions: 3
  result_paragraphs: 6
  claim_limits: 7
  forced_bad_total_tasks: 133

claim_defense:
  claim_count: 10
  global_red_lines: 6
  forced_bad: 0/133
  public-pass/hidden-fail: 133

paper_artifacts_index:
  artifact_groups: 10
  table_index: 7
  claim_map: 10
  paper_section_result_paragraphs: 6
```

Paper-facing boundary:

```text
The paper can now use a single generated section for the three-boundary
downstream story:

hard_v2:
  positive conditional evidence under tree-aware context

hard_v3:
  generalization boundary

hard_v4:
  stricter boundary against universal selected utility

forced_bad_artifact:
  systematic negative transfer, 0/133 with 133 public-pass/hidden-fail cases

The section must not be edited into a selected-wins or token-savings claim.
```

## 18. Paper Claim Consistency Audit

The paper-facing reporting layer now has a consistency audit.

Script:

```text
scripts/audit_paper_claim_consistency.py --assert-current-audit
```

Outputs:

```text
benchmark/downstream/reports/paper_claim_consistency_audit.json
benchmark/downstream/reports/paper_claim_consistency_audit.md
benchmark/downstream/reports/paper_claim_consistency_audit.tex
```

Current result:

```text
total_checks: 12
passed_checks: 12
failed_checks: 0
status: pass
```

Key audited facts:

```text
forced_bad_total_success: 0/133
forced_bad_total_public_passed_hidden_failed: 133
hard_v4_strict_selected: 22/24
hard_v4_strict_no_experience: 24/24
selected_superiority_consistent: False
selected_token_savings_consistent: False
```

Interpretation:

```text
This is a reporting-hygiene artifact. It checks that the generated paper
section, claim-defense matrix, artifact index, and boundary synthesis remain
consistent with the current three-boundary evidence. It is not additional model
evidence and should not be cited as a downstream performance result.
```

## 19. Model-Transfer Replication Protocol

The next clean experimental step is a predeclared model-transfer replication,
not another hard_v3/hard_v4 prompt or strategy pass.

Script:

```text
scripts/export_model_transfer_replication_protocol.py --assert-current-protocol
```

Outputs:

```text
benchmark/downstream/reports/model_transfer_replication_protocol.json
benchmark/downstream/reports/model_transfer_replication_protocol.md
benchmark/downstream/reports/model_transfer_replication_protocol.tex
```

Current protocol:

```text
protocol_id: model_transfer_replication_v0
run_specs: 4
expected_total_rows: 864
transfer_model_env: SKILLADMIT_TRANSFER_MODEL
baseline_model_label: mimo-v2.5-pro
```

Run matrix:

```text
hard_v3 tree-aware:          240 rows
hard_v3 strict visible-file: 240 rows
hard_v4 tree-aware:          192 rows
hard_v4 strict visible-file: 192 rows
```

Key boundary:

```text
The protocol is allowed to test model sensitivity, but it must not be used to
claim model-general SkillAdmit-selected superiority or selected token savings.
It is a pre-run registration artifact, not evidence.
```

## 20. Model-Transfer Evidence Status

The predeclared model-transfer matrix has completed with `mimo-v2.5`. This is a
replication/sensitivity layer on top of the frozen hard_v3/hard_v4 task
boundary, not a replacement for the hard_v2/hard_v3/hard_v4 boundary synthesis.

Evidence scripts:

```text
scripts/export_model_transfer_evidence_package.py --assert-current-model-transfer
scripts/export_model_transfer_cross_model_synthesis.py --assert-current-cross-model
```

Evidence artifacts:

```text
benchmark/downstream/reports/model_transfer_evidence_package.json
benchmark/downstream/reports/model_transfer_evidence_package.md
benchmark/downstream/reports/model_transfer_evidence_package.tex
benchmark/downstream/reports/model_transfer_cross_model_synthesis.json
benchmark/downstream/reports/model_transfer_cross_model_synthesis.md
benchmark/downstream/reports/model_transfer_cross_model_synthesis.tex
```

Model-transfer facts:

```text
model: mimo-v2.5
rows: 864/864
parse_errors: 0
forced_bad_artifact: 0/108
forced_bad public-pass/hidden-fail: 108
```

Selected-vs-no_experience under transfer:

```text
hard_v3 tree-aware: 29/30 vs 29/30, delta 0
hard_v3 strict:     29/30 vs 28/30, delta +1
hard_v4 tree-aware: 24/24 vs 23/24, delta +1
hard_v4 strict:     21/24 vs 18/24, delta +3
```

Cross-model synthesis:

```text
baseline model label: mimo-v2.5-pro
transfer model: mimo-v2.5
forced_bad combined: 0/216
combined public-pass/hidden-fail: 216

hard_v3 tree-aware selected tie replicated: true
hard_v3 strict selected +1 replicated: true
hard_v4 strict selected delta reversed: true
```

Artifact-index status:

```text
artifact_groups: 12
table_index: 8
claim_map: 10
```

Paper-facing boundary:

```text
This strengthens the negative-transfer story and weakens any simple selected
superiority story. The strongest transferable result is harmful artifact
execution causing systematic hidden-verifier failure. The selected context
effect is conditional and model-sensitive.

Do not claim:
  model-general SkillAdmit-selected superiority
  selected token savings across models
  precondition-only replacing repository/tree context
  hard_v3/hard_v4 cleanliness after tuning from transfer failures
```

## 21. Model-Transfer Addendum Status

The model-transfer evidence now has a draftable paper addendum. This is meant
for an optional replication/sensitivity subsection or appendix, not as the main
evaluation section.

Script:

```text
scripts/export_model_transfer_paper_addendum.py --assert-current-addendum
```

Artifacts:

```text
benchmark/downstream/reports/model_transfer_paper_addendum.json
benchmark/downstream/reports/model_transfer_paper_addendum.md
benchmark/downstream/reports/model_transfer_paper_addendum.tex
```

Current facts:

```text
result_paragraphs: 5
selected_sensitivity_rows: 4
forced_bad_combined_success: 0/216
hard_v4_strict_selected_delta_reversed: true
```

Reporting integration:

```text
paper_artifacts_index:
  artifact_groups: 13
  table_index: 9
  claim_map: 10

paper_claim_consistency_audit:
  total_checks: 13
  status: pass
```

Use boundary:

```text
Allowed:
  report second-model sensitivity and replicated forced-bad negative transfer.

Forbidden:
  model-general selected superiority
  selected token savings across models
  replacing the main hard_v2/hard_v3/hard_v4 boundary synthesis
```

## 22. Reporting Hygiene Audit

The public reporting layer now has an executable hygiene audit. This is separate
from the paper-claim consistency audit: it specifically checks that old,
current, and model-transfer aggregates are not mixed into an over-strong paper
claim.

Script:

```text
scripts/audit_reporting_hygiene.py --assert-current-hygiene
```

Artifacts:

```text
benchmark/downstream/reports/reporting_hygiene_audit.json
benchmark/downstream/reports/reporting_hygiene_audit.md
benchmark/downstream/reports/reporting_hygiene_audit.tex
```

Aggregate roles:

```text
0/85:
  historical hard_v2/hard_v3 cross-version synthesis only

0/133:
  current hard_v2/hard_v3/hard_v4 main downstream boundary

0/216:
  model-transfer hard_v3/hard_v4 addendum layer
```

Current result:

```text
total_checks: 8
passed_checks: 8
failed_checks: 0
status: pass
```

Paper-facing implication:

```text
Use downstream_boundary_synthesis as the main paper evidence.
Use model_transfer_paper_addendum only as a replication/sensitivity addendum.
Treat downstream_cross_version_synthesis as a historical hard_v2/hard_v3 report.
```
