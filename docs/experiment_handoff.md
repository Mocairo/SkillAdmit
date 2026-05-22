# SkillAdmit Experiment Handoff

Last updated: 2026-05-22

This document is for continuing the SkillAdmit experiment in a fresh Codex
conversation. It records the current runnable state, what each major file does,
how to reproduce results, and what should not be claimed yet.

## 1. Current Goal

SkillAdmit studies whether agent experience should be admitted as one of five
actions:

```text
discard
store_as_memory
distill_into_skill
promote_to_rule
defer
```

The current repository implements a small executable benchmark around Python
import/debug tasks plus curated admission samples. The immediate engineering
goal is to keep the full admission pipeline reproducible while expanding the
benchmark beyond hand-curated development cases.

## 2. Environment

Use the existing conda environment:

```bash
conda activate skilladmit
cd /home/lijx/workspace/skilladmit
```

Known working Python version:

```text
Python 3.10.20
```

The LLM connection uses `.env`:

```text
OPENAI_API_KEY=<secret, do not print>
OPENAI_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
SKILLADMIT_MODEL=mimo-v2.5-pro
```

Do not print or copy the real API key into logs, documents, or prompts.

## 3. Main File Map

Benchmark generation:

```text
scripts/generate_py_import_tasks.py
```

Generates 20 synthetic Python import/debug tasks under:

```text
benchmark/tasks/
```

Task sanity checks:

```text
scripts/check_initial_failures.py
scripts/apply_gold_fixes.py
scripts/build_task_manifest.py
```

These verify that generated tasks fail initially, pass after gold fixes, and
produce `benchmark/task_manifest.jsonl`.

Real LLM runner:

```text
scripts/run_llm_coding_agent.py
```

Runs a single-shot OpenAI-compatible JSON-patch coding agent on generated tasks.
The current run with `mimo-v2.5-pro` solved 20/20 tasks.

LLM trajectory processing:

```text
scripts/build_llm_trajectories.py
scripts/build_llm_clusters.py
scripts/build_llm_artifacts.py
scripts/build_llm_admission_samples.py
```

These convert raw LLM runs into trajectory summaries, clusters, candidate
artifacts, and positive `distill_into_skill` admission samples.

Curated admission data:

```text
scripts/build_curated_non_skill_samples.py
scripts/build_curated_non_skill_v1_samples.py
scripts/build_v0_mixed_admission_samples.py
scripts/build_v1_mixed_admission_samples.py
scripts/build_v2_heldout_admission_samples.py
scripts/build_v3_heldout_admission_samples.py
scripts/build_v4_blind_admission_samples.py
scripts/build_v5_blind_admission_samples.py
scripts/build_v6_blind_admission_samples.py
scripts/build_v7_blind_admission_samples.py
```

These build mixed admission datasets covering all five labels.

Admission controller:

```text
skilladmit/controllers/rule_based_controller.py
skilladmit/controllers/rule_based_controller_v3_frozen.py
skilladmit/controllers/rule_based_controller_v4_dev.py
skilladmit/controllers/rule_based_controller_v4_frozen.py
skilladmit/controllers/rule_based_controller_v5_dev.py
skilladmit/controllers/rule_based_controller_v5_frozen.py
skilladmit/controllers/rule_based_controller_v6_dev.py
skilladmit/controllers/rule_based_controller_v6_frozen.py
```

Current deterministic baseline controller. It is a hand-designed baseline, not
the final research method. The default controller currently mirrors
`rule_based_controller_v6_dev.py`; `rule_based_controller_v6_frozen.py` is the
controller used for the current clean v7 blind result.

Evaluation:

```text
skilladmit/eval/evaluate_admission.py
scripts/evaluate_controller_module.py
scripts/evaluate_admission_baselines.py
scripts/inspect_admission_errors.py
scripts/inspect_frozen_controller_errors.py
scripts/run_admission_regression.py
scripts/summarize_admission_costs.py
scripts/build_downstream_py_import_tasks.py
scripts/run_downstream_validation.py
scripts/run_llm_downstream_validation.py
scripts/summarize_hard_v2_results.py
scripts/export_hard_v2_evidence_package.py
```

`run_admission_regression.py` is the fastest way to verify that controller edits
do not break existing admission datasets.

`summarize_hard_v2_results.py` is the hard_v2 downstream evidence ledger. It
reads hard_v2 run summaries and trajectories, writes a strategy/template/failure
matrix, and records SHA-256 hashes so summary rewrites are detectable.

`export_hard_v2_evidence_package.py` builds paper-facing hard_v2 evidence
exports from the ledger: compact Markdown tables, LaTeX tables, a JSON evidence
package, failure taxonomy, derived comparisons, source hashes, and explicit
supported/unsupported claim lists.

## 4. Reproduce Current Admission Results

Run:

```bash
python scripts/run_admission_regression.py
```

Current verified result:

```text
checked_files: 9
min_accuracy:  1.000
passed_files:  9
failed_files:  0
```

The checked files are:

```text
benchmark/admission_samples/seed_admission_samples.jsonl
benchmark/admission_samples/llm_coding_agent_v0_admission_samples.jsonl
benchmark/admission_samples/v0_mixed_admission_samples.jsonl
benchmark/admission_samples/v1_mixed_admission_samples.jsonl
benchmark/admission_samples/v2_heldout_admission_samples.jsonl
benchmark/admission_samples/v3_heldout_admission_samples.jsonl
benchmark/admission_samples/v4_blind_admission_samples.jsonl
benchmark/admission_samples/v5_blind_admission_samples.jsonl
benchmark/admission_samples/v6_blind_admission_samples.jsonl
```

Each currently reaches 100% under the rule-based controller.

## 5. Important Scientific Caveat

Do not claim that the current 100% regression result proves generalization.

The controller has been adjusted after observing errors on v1, v2, v3, v4, v5,
and v6. That means these files are now regression/development sets, even if some
filenames still contain `heldout` or `blind`.

Correct interpretation:

```text
The current controller is consistent with all existing curated regression sets.
```

Incorrect interpretation:

```text
The current controller generalizes to a true unseen held-out benchmark.
```

For a defensible paper result, freeze the controller first, then create a new
blind evaluation set. If errors on that set are used to tune the controller,
rename that set as a development set and create another fresh held-out set.

## 6. Current Controller Boundary

The controller currently scores five labels using approximate signals:

```text
context_specificity
transferability
stability
overgeneralization_risk
rule_generality
evidence_sufficiency
harmful_skill_risk
guardrail_rule_signal
insufficient_evidence_signal
memory_specific_signal
runner_noise_signal
```

The latest fixes addressed these failure modes:

```text
dangerous workarounds should become discard
project/environment facts should become store_as_memory
global constraints should become promote_to_rule
under-specified or provider-conflicting cases should become defer
procedural, validated repairs should remain distill_into_skill
```

## 7. V4 Frozen Result And Later Use

V4 was the first useful frozen stress test. It was created after freezing the
v3 controller with these files:

```text
skilladmit/controllers/rule_based_controller_v3_frozen.py
scripts/build_v4_blind_admission_samples.py
scripts/evaluate_frozen_controller.py
scripts/inspect_frozen_controller_errors.py
docs/v4_blind_eval_protocol.md
```

File purposes:

```text
rule_based_controller_v3_frozen.py
  Frozen snapshot of the controller after v1/v2/v3 regression tuning.

build_v4_blind_admission_samples.py
  Generates 50 balanced v4 admission samples, 10 for each action.

evaluate_frozen_controller.py
  Evaluates v4 with the frozen controller, not the mutable current controller.

inspect_frozen_controller_errors.py
  Reads frozen prediction output and prints detailed errors for analysis.

v4_blind_eval_protocol.md
  Records the v4 protocol, result, caveats, and recommended use.
```

V4 frozen result:

```text
samples:  50
correct:  27
accuracy: 0.540
```

V4 was later used for controller development, so it is now a regression/dev set,
not clean held-out evidence for the current controller.

## 8. V5 Frozen Result And Later Use

V4 has now been used as a development set. The improved controller lives in:

```text
skilladmit/controllers/rule_based_controller_v4_dev.py
```

At that stage, the default controller mirrored this v4 development controller:

```text
skilladmit/controllers/rule_based_controller.py
```

The frozen controller used for the next blind evaluation is:

```text
skilladmit/controllers/rule_based_controller_v4_frozen.py
```

V5 generation and evaluation files:

```text
scripts/build_v5_blind_admission_samples.py
docs/v5_blind_eval_protocol.md
benchmark/admission_samples/v5_blind_admission_samples.jsonl
benchmark/admission_samples/v5_frozen_controller_predictions.jsonl
```

V5 frozen result:

```text
samples:  50
correct:  30
accuracy: 0.600
```

Interpretation:

```text
The v4_frozen controller generalizes well to procedural skills and most
discard examples, but remains weak on promote_to_rule and store_as_memory when
the wording differs from development sets.
```

Do not tune `rule_based_controller_v4_frozen.py` on v5 and still call v5
held-out. If v5 is used for improvement, create `rule_based_controller_v5_dev.py`
and later evaluate on a fresh v6 blind set.

## 9. V6 Frozen Result And Later Use

V5 has now been used as development data. The improved controller lives in:

```text
skilladmit/controllers/rule_based_controller_v5_dev.py
```

At that stage, the default controller mirrored this v5 development controller:

```text
skilladmit/controllers/rule_based_controller.py
```

The frozen controller used for the v6 blind evaluation is:

```text
skilladmit/controllers/rule_based_controller_v5_frozen.py
```

V6 generation and evaluation files:

```text
scripts/build_v6_blind_admission_samples.py
docs/v6_blind_eval_protocol.md
benchmark/admission_samples/v6_blind_admission_samples.jsonl
benchmark/admission_samples/v6_frozen_controller_predictions.jsonl
```

V6 frozen result:

```text
samples:  50
correct:  33
accuracy: 0.660
```

V6 confusion:

```text
gold=defer
  pred=defer: 4
  pred=discard: 1
  pred=distill_into_skill: 4
  pred=promote_to_rule: 1

gold=discard
  pred=discard: 10

gold=distill_into_skill
  pred=distill_into_skill: 10

gold=promote_to_rule
  pred=discard: 2
  pred=distill_into_skill: 5
  pred=promote_to_rule: 3

gold=store_as_memory
  pred=discard: 4
  pred=store_as_memory: 6
```

Interpretation:

```text
The v5_frozen controller is strong on discard and distill_into_skill, but still
weak on promote_to_rule, store_as_memory, and some defer cases under fresh v6
wording.
```

Do not tune `rule_based_controller_v5_frozen.py` on v6 and still call v6
held-out. If v6 is used for improvement, create `rule_based_controller_v6_dev.py`
and later evaluate on a fresh v7 blind set.

V6 was later used for controller development, so it is now a regression/dev set,
not clean held-out evidence for the current controller.

## 10. V7 Status

V6 has now been used as development data. The improved controller lives in:

```text
skilladmit/controllers/rule_based_controller_v6_dev.py
```

The default controller currently mirrors this v6 development controller:

```text
skilladmit/controllers/rule_based_controller.py
```

The frozen controller used for the current blind evaluation is:

```text
skilladmit/controllers/rule_based_controller_v6_frozen.py
```

V7 generation and evaluation files:

```text
scripts/build_v7_blind_admission_samples.py
docs/v7_blind_eval_protocol.md
benchmark/admission_samples/v7_blind_admission_samples.jsonl
benchmark/admission_samples/v7_frozen_controller_predictions.jsonl
```

V7 frozen result:

```text
samples:  50
correct:  49
accuracy: 0.980
```

V7 confusion:

```text
gold=defer
  pred=defer: 10

gold=discard
  pred=discard: 10

gold=distill_into_skill
  pred=distill_into_skill: 9
  pred=promote_to_rule: 1

gold=promote_to_rule
  pred=promote_to_rule: 10

gold=store_as_memory
  pred=store_as_memory: 10
```

Only observed error:

```text
sample_v7_skill_grpc_deadline_idempotent_retry
gold: distill_into_skill
pred: promote_to_rule
```

Interpretation:

```text
The v6_frozen controller generalizes well to v7, but still over-promotes one
scoped reusable retry procedure into a global rule.
```

Do not tune `rule_based_controller_v6_frozen.py` on v7 and still call v7
held-out. If v7 is used for improvement, create `rule_based_controller_v7_dev.py`
and later evaluate on a fresh v8 blind set.

## 11. Recommended Next Steps

## 11. Baselines And Cost Reports

Baseline evaluator:

```text
scripts/evaluate_admission_baselines.py
```

Purpose:

```text
Evaluate trivial always-action baselines, a simple keyword baseline, and an
optional controller module on one or more admission sample files.
```

Current baseline reports:

```text
benchmark/reports/v7_admission_baselines.md
benchmark/reports/v7_admission_baselines.json
```

V7 baseline summary:

```text
always_* baselines:       10/50, accuracy 0.200, macro_f1 0.067
keyword_level_baseline:   49/50, accuracy 0.980, macro_f1 0.980
v6_frozen_controller:     49/50, accuracy 0.980, macro_f1 0.980
```

Important caveat:

```text
The keyword baseline matching the controller is a warning sign. The current v7
set is useful for pipeline testing, but a stronger paper benchmark needs less
surface-obvious wording and independently authored samples.
```

Cost summarizer:

```text
scripts/summarize_admission_costs.py
```

Purpose:

```text
Summarize observed token/latency cost from real LLM trajectories and estimate
break-even reuse under explicit token-saving assumptions.
```

Current cost reports:

```text
benchmark/reports/llm_cost_summary.md
benchmark/reports/llm_cost_summary.json
```

Cost summary:

```text
real LLM coding-agent tasks:       20
successful tasks:                  20
total tokens:                      38999
avg tokens per task:               1950.0
admitted artifacts:                5
avg source tokens per artifact:    7799.8
default break-even future tasks:   15.60
```

Paper-facing status report:

```text
docs/paper_eval_status.md
```

Purpose:

```text
Summarize the honest v7 result, baseline comparison, cost accounting, and what
can or cannot be claimed yet.
```

## 12. Downstream Validation v0

Downstream validation protocol:

```text
docs/downstream_validation_v0.md
```

Task generator:

```text
scripts/build_downstream_py_import_tasks.py
```

Purpose:

```text
Generate 25 future Python import/debug tasks under benchmark/downstream/tasks/.
```

Strategy runner:

```text
scripts/run_downstream_validation.py
```

Purpose:

```text
Compare no_experience, bad_dependency_stub, raw_memory_replay,
promoted_rule_only, distilled_skill, and skilladmit_selected on the downstream
tasks using real verifiers.
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

Caveat:

```text
This is a deterministic proxy experiment. The next stronger version should run
a real LLM coding agent with artifact context.
```

## 13. Recommended Next Steps

## 13. LLM Downstream Validation v0

LLM downstream protocol:

```text
docs/llm_downstream_validation_v0.md
```

Runner:

```text
scripts/run_llm_downstream_validation.py
```

Purpose:

```text
Run an OpenAI-compatible chat model on downstream tasks with strategy-specific
artifact contexts, apply the model's JSON patch, and execute the real verifier.
```

Use the `skilladmit` conda environment:

```bash
conda activate skilladmit
cd /home/lijx/workspace/skilladmit
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
The real LLM downstream runner works, but these smoke tasks are too easy for
the current model because no_experience already solves 5/5. The next benchmark
must be harder or budget-constrained before claiming artifact benefit.
```

## 14. LLM Downstream Hard v1

Hard downstream validation was added after the easy smoke showed no gap between
conditions.

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

Important runner additions:

```text
--tasks-dir
--use-task-visible-files
--max-files
```

Outputs:

```text
benchmark/downstream_hard_v1/tasks/
benchmark/downstream/llm_runs/llm_downstream_hard_v1_smoke_5x2/
benchmark/downstream/llm_runs/llm_downstream_hard_v1_extra_5x4/
```

Sanity check:

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
Hard v1 is the first real-LLM downstream setting where no_experience is not
already perfect. The concrete failure is hard_py_import_004: no_experience
created a top-level adapters/ stub, which passed public pytest but failed the
hidden verifier. skilladmit_selected used the package-internal import repair and
passed.

This is useful but still small-scale evidence. Do not claim broad downstream
superiority from hard v1 alone.
```

## 15. Recommended Next Steps

The next recommended experimental step is not more controller keyword tuning.
The benchmark machinery is now strong enough to support paper-facing comparisons:

```text
add baselines: always_distill, always_store_raw_memory, always_defer, LLM-as-judge
add harder LLM-based downstream validation where no_experience is not already perfect
add cost analysis: artifact creation tokens, future tokens saved, break-even point
add independently authored or randomized samples for a stronger final benchmark
```

The next method should move beyond flat phrase matching. A stronger design would
first classify the candidate artifact as one of:

```text
local fact
reusable procedure
global constraint
harmful workaround
insufficient or conflicting evidence
```

and only then choose the final admission action.

If controller tuning continues anyway:

```text
use v7 only as development data
preserve v7_frozen_controller_predictions.jsonl as the honest v7 result
build v8_blind_admission_samples.jsonl before the next generalization claim
```

For downstream validation, the next best step is:

```text
build hard_v2 with 25 tasks
keep visible-file budgets and hidden verifier checks
add a forced_bad_artifact condition if negative-transfer evidence is needed
then run no_experience vs skilladmit_selected vs raw_memory vs promoted_rules
vs distilled_skills_all vs forced_bad_artifact
```

Only after hard_v2 should smaller models be treated as sensitivity analysis.

## 16. LLM Downstream Hard v2

Hard v2 has been implemented.

Protocol:

```text
docs/llm_downstream_hard_v2.md
```

Generator:

```text
scripts/build_downstream_hard_v2_tasks.py
```

Checker:

```text
scripts/check_downstream_hard_v2_tasks.py
```

Runner:

```text
scripts/run_llm_downstream_validation.py
```

Important runner additions:

```text
forced_bad_artifact
skilladmit_selected_with_precondition_only
skilladmit_selected_with_precondition_context
public_tests_after_edit
public_passed_hidden_failed
artifact_adherence
--include-repo-tree
--resume
```

Task sanity:

```text
total: 25
initial_failed: 25
gold_passed: 25
forced_public_passed: 25
forced_verifier_failed: 25
```

Forced bad-artifact result:

```text
forced_bad_artifact: 0/25 success_rate=0.000 negative_transfer=25 public_passed_hidden_failed=25
```

Real LLM canary:

```text
no_experience:       4/5 success_rate=0.800 negative_transfer=1 public_passed_hidden_failed=1 total_tokens=12775
skilladmit_selected: 5/5 success_rate=1.000 negative_transfer=0 public_passed_hidden_failed=0 total_tokens=13840
```

Key canary failure:

```text
no_experience on hard_v2_py_import_016 duplicated runner_alpha/data/alpha.txt.
Public pytest passed, but hidden verifier rejected the masking repair.
skilladmit_selected passed.
```

Current status:

```text
Hard v2 full downstream runs have been completed in both strict visible-file and
tree-aware settings.
```

Full strict visible-file run:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v2_full_25x6/
```

Result:

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
benchmark/downstream/llm_runs/llm_downstream_hard_v2_tree_25x2/
```

Result:

```text
no_experience:       23/25 success_rate=0.920 negative_transfer=2 total_tokens=51548
skilladmit_selected: 25/25 success_rate=1.000 negative_transfer=0 total_tokens=57597
```

Selected + precondition context run:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v2_selected_precondition_25/
```

Strategy:

```text
skilladmit_selected_with_precondition_context
```

Runner behavior:

```text
provides the selected SkillAdmit skill
automatically includes repository tree paths
adds compact skill-specific precondition and guardrail context
```

Result:

```text
skilladmit_selected_with_precondition_context: 25/25 success_rate=1.000 negative_transfer=0 public_passed_hidden_failed=0 total_tokens=67504
artifact_adherence: 25/25
parse_errors: 0
```

Comparison:

```text
no_experience tree-aware:                      23/25, total_tokens=51548
skilladmit_selected tree-aware:                25/25, total_tokens=57597
skilladmit_selected_with_precondition_context: 25/25, total_tokens=67504
distilled_skills_all strict:                   25/25, total_tokens=84986
```

Strict precondition-only ablation:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v2_precondition_only_25/
```

Strategy:

```text
skilladmit_selected_with_precondition_only
```

Runner behavior:

```text
provides the selected SkillAdmit skill
adds compact skill-specific precondition and guardrail context
does not automatically include repository tree paths
```

Result:

```text
skilladmit_selected_with_precondition_only: 24/25 success_rate=0.960 negative_transfer=1 public_passed_hidden_failed=0 total_tokens=72316
artifact_adherence: 25/25
parse_errors: 0
included_repo_tree: 0/25
```

First-run failure:

```text
hard_v2_py_import_012
template: T3_script_relative_import_hard
reason: the model left a module-level relative import in place, so its fallback
inside if __name__ == "__main__" was never reached
```

Important interpretation:

```text
Strict visible-file setting:
  all-skills is strongest but expensive
  selected-only can fail when the executor lacks file-location context

Strict selected + precondition-only:
  first run improved selected-only to 24/25, but replication dropped to 23/25
  and failed both T3 script-mode import and one T4 cwd-sensitive path task; it
  does not replace tree-aware context

Tree-aware setting:
  selected skill context beats no experience, 25/25 vs 23/25

Selected + precondition context:
  keeps 25/25 and remains cheaper than all-skills, but costs more than ordinary
  tree-aware selected; do not claim token savings over selected-only
```

Hard v2 matrix report:

```text
benchmark/downstream/reports/hard_v2_strategy_matrix.json
benchmark/downstream/reports/hard_v2_strategy_matrix.md
```

Generated by:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/summarize_hard_v2_results.py \
  --assert-current-hard-v2
```

Purpose:

```text
Create a durable comparison table across all hard_v2 run directories. It records
strategy rows, template rows, failure rows, and source SHA-256 hashes for each
summary/trajectory file.
```

Current matrix:

```text
runs: 9
strategy_rows: 17
template_rows: 85
failures: 69
```

Stability groups:

```text
tree_aware_skilladmit_selected:
  successes: [25, 25]
  tokens:    [57597, 52144]

tree_aware_selected_precondition_context:
  successes: [25, 25]
  tokens:    [67504, 64150]

strict_precondition_only:
  successes: [24, 23]
  tokens:    [72316, 77487]
  failure tasks: hard_v2_py_import_012, then hard_v2_py_import_012 and hard_v2_py_import_018
```

New utility:

```text
scripts/inspect_llm_downstream_run.py
```

Use it like:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/inspect_llm_downstream_run.py \
  --run-name llm_downstream_hard_v2_tree_25x2
```

Hard v2 evidence package:

```text
benchmark/downstream/reports/hard_v2_evidence_package.json
benchmark/downstream/reports/hard_v2_paper_tables.md
benchmark/downstream/reports/hard_v2_paper_tables.tex
```

Generated by:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_hard_v2_evidence_package.py \
  --assert-current-hard-v2
```

Purpose:

```text
Create paper-facing tables and claim-boundary checks from the completed hard_v2
downstream evidence. This is a reporting/export step, not a new API run.
```

Current export:

```text
primary_rows: 11
stability_rows: 3
failure_taxonomy_rows: 25
```

Key derived comparisons:

```text
tree-aware SkillAdmit-selected improves success over no_experience by +2 tasks,
but uses +6049 tokens.
selected+precondition uses 17482 fewer tokens than all-skills but 9907 more
tokens than ordinary tree-aware selected.
strict precondition-only improves strict selected by +1 task on the first run,
but replication drops to 23/25, so it is not stable evidence.
```

## 17. Rule for Future Work

Every new code file should be documented when created:

```text
what the file does
why it is needed
its inputs
its outputs
who should run or import it
```

This is required so the experiment remains recoverable across Codex sessions.
