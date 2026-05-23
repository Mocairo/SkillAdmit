# SkillAdmit Experiment Handoff

Last updated: 2026-05-23

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
scripts/summarize_hard_v3_results.py
scripts/export_hard_v3_evidence_package.py
scripts/summarize_hard_v4_results.py
scripts/export_hard_v4_evidence_package.py
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

`summarize_hard_v3_results.py` and `export_hard_v3_evidence_package.py` do the
same for hard_v3, with extra emphasis on artifact adherence and claim boundaries
because hard_v3 is boundary evidence rather than a simple selected-win result.

`summarize_hard_v4_results.py` and `export_hard_v4_evidence_package.py` do the
same for hard_v4. hard_v4 is even more boundary-heavy: tree-aware is saturated,
and strict visible-file rejects ordinary selected superiority.

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

## 17. LLM Downstream Hard v3

Hard v3 has been added as the next clean downstream validation boundary.

Protocol:

```text
docs/llm_downstream_hard_v3.md
```

Generator:

```text
scripts/build_downstream_hard_v3_tasks.py
```

Checker:

```text
scripts/check_downstream_hard_v3_tasks.py
```

Task directory:

```text
benchmark/downstream_hard_v3/tasks/
```

Stage boundaries:

```text
Stage 1: deterministic scaffold/freeze step.
Stage 2: tree-aware core LLM comparison after freezing the task suite.

Neither stage is a prompt-tuning step.
```

Task design:

```text
30 tasks = 6 templates x 5 variants

T1_optional_integration_import
T2_application_package_local_import
T3_dual_use_command_module
T4_repo_config_cwd_path
T5_plugin_registry_internal_import
T6_template_resource_cwd_path
```

Current deterministic check:

```text
total: 30
initial_failed: 30
gold_passed: 30
forced_public_passed: 30
forced_verifier_failed: 30
```

Current tree-aware core LLM run:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v3_tree_core_30x2/
```

Final cleaned summary:

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

API hygiene note:

```text
Two intermediate selected+precondition rows were API failures
(hard_v3_agent_016 APIConnectionError and hard_v3_agent_017 APITimeoutError).
They were removed from the trajectory file and rerun. Both passed, and the
final summary has parse_errors=0.
```

Regression checks after adding hard_v3:

```text
scripts/check_downstream_hard_v2_tasks.py:
  total: 25
  initial_failed: 25
  gold_passed: 25
  forced_public_passed: 25
  forced_verifier_failed: 25

scripts/run_admission_regression.py:
  checked_files: 9
  min_accuracy: 1.000
  passed_files: 9
  failed_files: 0
```

Current hard_v3 claim boundary:

```text
hard_v3 now supports a deterministic scaffold claim and a first tree-aware core
LLM result.

It does not support a SkillAdmit-selected superiority claim: no_experience,
skilladmit_selected, and selected+precondition are all 29/30 in the current
hard_v3 tree-aware run.

It does not support a hard_v3 token-savings claim. Ordinary selected used 917
fewer tokens than no_experience in this single run, but this is too small and
unreplicated; selected+precondition used more tokens than both.

The strong supported hard_v3 claim is negative-transfer control:
forced_bad_artifact is 0/30 with 30 public-pass/hidden-fail cases.
```

Command to reproduce or resume the completed tree-aware core run:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/run_llm_downstream_validation.py \
  --run-name llm_downstream_hard_v3_tree_core_30x2 \
  --tasks-dir benchmark/downstream_hard_v3/tasks \
  --use-task-visible-files \
  --include-repo-tree \
  --resume \
  --strategy no_experience \
  --strategy skilladmit_selected \
  --strategy forced_bad_artifact \
  --strategy skilladmit_selected_with_precondition_context
```

Do not use hard_v3 model failures for prompt or strategy tuning before deciding
whether the current task suite remains the clean evaluation boundary.

Completed hard_v3 matrix extension:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v3_tree_core_30x2/
  setting: tree-aware
  rows: 240
  strategies:
    bad_dependency_rule
    distilled_skills_all
    forced_bad_artifact
    no_experience
    promoted_rules
    raw_memory
    skilladmit_selected
    skilladmit_selected_with_precondition_context

benchmark/downstream/llm_runs/llm_downstream_hard_v3_strict_30x8/
  setting: strict visible-file
  rows: 240
  strategies:
    bad_dependency_rule
    distilled_skills_all
    forced_bad_artifact
    no_experience
    promoted_rules
    raw_memory
    skilladmit_selected
    skilladmit_selected_with_precondition_only
```

Hard v3 strategy matrix report:

```text
benchmark/downstream/reports/hard_v3_strategy_matrix.json
benchmark/downstream/reports/hard_v3_strategy_matrix.md
```

Generated by:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/summarize_hard_v3_results.py \
  --assert-current-hard-v3
```

Hard v3 paper-facing evidence package:

```text
benchmark/downstream/reports/hard_v3_evidence_package.json
benchmark/downstream/reports/hard_v3_paper_tables.md
benchmark/downstream/reports/hard_v3_paper_tables.tex
```

Generated by:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_hard_v3_evidence_package.py \
  --assert-current-hard-v3
```

Current export:

```text
primary_rows: 16
artifact_adherence_rows: 14
non_forced_failures: 9
```

Current hard_v3 matrix summary:

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

Updated hard_v3 interpretation:

```text
hard_v3 does not support a simple SkillAdmit-selected superiority claim.

In tree-aware, selected ties no_experience at 29/30, while raw_memory,
bad_dependency_rule, and all-skills reach 30/30.

In strict visible-file, selected improves over no_experience by +1 task, but
precondition-only and raw_memory reach 30/30.

The bad_dependency_rule LLM condition should not be interpreted as safe bad
advice because artifact adherence is low. The forced_bad_artifact condition is
the actual negative-transfer control and is 0/30 with 30 public-pass/hidden-fail
cases in both settings.

Use `hard_v3_paper_tables.md` and `hard_v3_evidence_package.json` for paper
drafting rather than hand-copying from individual run summaries. The package
explicitly records supported and unsupported claims.
```

Reasonable next hard_v3 steps:

```text
Run a fresh replication of one of the completed settings if stability is needed.

Use the cross-version hard_v2/hard_v3 synthesis table for paper drafting:
hard_v2 is positive evidence for tree-aware selected on its suite, while hard_v3
is boundary evidence showing selected does not universally dominate.

Do not inspect hard_v3_agent_013 or hard_v3_agent_027 and then edit prompts to
fix them unless hard_v3 is explicitly converted into a development set.
```

Cross-version synthesis has now been exported:

```text
benchmark/downstream/reports/downstream_cross_version_synthesis.json
benchmark/downstream/reports/downstream_cross_version_synthesis.md
benchmark/downstream/reports/downstream_cross_version_synthesis.tex
```

Generated by:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_downstream_cross_version_synthesis.py \
  --assert-current-synthesis
```

Current synthesis:

```text
primary_rows: 27
forced_bad_total_tasks: 85
forced_bad_total_successes: 0
forced_bad_total_public_passed_hidden_failed: 85
selected_superiority_consistent: False
selected_token_savings_supported: False
repo_tree_necessity_universal: False
```

Use this report when writing the paper-level downstream section. It is the most
compact current statement of the honest claim boundary: hard_v2 supports
tree-aware selected utility, hard_v3 limits universal selected-superiority
claims, and forced bad artifacts consistently demonstrate negative transfer.

Paper-section exporter:

```text
scripts/export_downstream_paper_section.py
```

Generated outputs:

```text
benchmark/downstream/reports/downstream_paper_eval_section.json
benchmark/downstream/reports/downstream_paper_eval_section.md
benchmark/downstream/reports/downstream_paper_eval_section.tex
```

Generated by:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_downstream_paper_section.py \
  --assert-current-paper-section
```

Current paper section:

```text
research_questions: 3
result_paragraphs: 5
claim_limits: 7
forced_bad_total_tasks: 85
```

Use this when drafting the evaluation section. It is designed to be edited for
style, not for stronger claims.

Claim-defense matrix:

```text
scripts/export_downstream_claim_defense_matrix.py
```

Generated outputs:

```text
benchmark/downstream/reports/downstream_claim_defense_matrix.json
benchmark/downstream/reports/downstream_claim_defense_matrix.md
benchmark/downstream/reports/downstream_claim_defense_matrix.tex
```

Generated by:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_downstream_claim_defense_matrix.py \
  --assert-current-claim-defense
```

Current matrix:

```text
claim_count: 10
global_red_lines: 6
```

Use this before paper edits or reviewer response drafting. It maps each
downstream claim to evidence rows, allowed wording, forbidden wording, required
qualifiers, and a reviewer-response sketch.

Paper artifacts index:

```text
scripts/export_paper_artifacts_index.py
```

Generated outputs:

```text
benchmark/downstream/reports/paper_artifacts_index.json
benchmark/downstream/reports/paper_artifacts_index.md
benchmark/downstream/reports/paper_artifacts_index.tex
```

Generated by:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_paper_artifacts_index.py \
  --assert-current-artifacts-index
```

Current index:

```text
artifact_groups: 10
table_index: 7
claim_map: 10
forced_bad_total_tasks: 85
hard_v4_forced_bad_total_tasks: 48
boundary_forced_bad_total_tasks: 133
```

Use this as the top-level navigation document before writing the paper or
answering reviewer questions. It says which artifacts are primary evidence,
which are drafting aids, which are handoff context, and which files should not
be cited as primary evidence.

## 18. Hard v4 Downstream Evidence

Hard v4 has been added and run as a fresh downstream boundary. It is not a
continuation of hard_v3 tuning, and it should not be interpreted as a
SkillAdmit-selected win.

Protocol:

```text
docs/llm_downstream_hard_v4.md
```

Scripts:

```text
scripts/build_downstream_hard_v4_tasks.py
scripts/check_downstream_hard_v4_tasks.py
scripts/export_hard_v4_scaffold_manifest.py
scripts/summarize_hard_v4_results.py
scripts/export_hard_v4_evidence_package.py
```

Current deterministic scaffold:

```text
tasks_dir: benchmark/downstream_hard_v4/tasks/
24 tasks = 6 templates x 4 variants
244 files
initial_failed: 24/24
gold_passed: 24/24
forced_public_passed: 24/24
forced_verifier_failed: 24/24
```

Manifest:

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

Generated by:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/summarize_hard_v4_results.py \
  --assert-current-hard-v4

PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_hard_v4_evidence_package.py \
  --assert-current-hard-v4
```

Current hard_v4 matrix summary:

```text
tree-aware:
  bad_dependency_rule:                            24/24, tokens=51974, artifact_adherence=7/24
  distilled_skills_all:                           24/24, tokens=68776
  forced_bad_artifact:                             0/24, public_hidden=24
  no_experience:                                  24/24, tokens=46685
  promoted_rules:                                 24/24, tokens=58813
  raw_memory:                                     24/24, tokens=53406
  skilladmit_selected:                            24/24, tokens=48682
  skilladmit_selected_with_precondition_context:  24/24, tokens=63586

strict visible-file:
  bad_dependency_rule:                            24/24, tokens=63789, artifact_adherence=4/24
  distilled_skills_all:                           24/24, tokens=69049
  forced_bad_artifact:                             0/24, public_hidden=24
  no_experience:                                  24/24, tokens=53055
  promoted_rules:                                 23/24, tokens=69221
  raw_memory:                                     23/24, tokens=65070
  skilladmit_selected:                            22/24, tokens=58450
  skilladmit_selected_with_precondition_only:     23/24, tokens=69961
```

Current hard_v4 paper export:

```text
primary_rows: 16
artifact_adherence_rows: 14
non_forced_failures: 5
```

Interpretation:

```text
Tree-aware hard_v4 is saturated. Since no_experience and selected both reach
24/24, hard_v4 does not support a selected-success claim.

Strict visible-file hard_v4 is harsher: no_experience reaches 24/24 while
ordinary selected reaches 22/24. selected+precondition-only improves selected
to 23/24 but still trails no_experience and all-skills.

The strong hard_v4 signal is negative transfer, not selected utility. Forced
bad artifacts are 0/48 across the two settings, and all 48 failures are
public-pass/hidden-fail cases.

The ordinary bad_dependency_rule condition succeeds, but artifact adherence is
low: 7/24 tree-aware and 4/24 strict. This mostly shows that the model can
ignore harmful advice, not that harmful advice is safe.
```

Boundary:

```text
Do not tune hard_v2 or hard_v3 further.
Do not tune hard_v4 prompts or strategies from observed failures.
Do not claim SkillAdmit-selected helps on hard_v4.
Do not claim SkillAdmit-selected token savings on hard_v4.
Do not fold hard_v4 into hard_v2/hard_v3 synthesis without preserving boundary labels.
```

## 19. Downstream Boundary Synthesis

The hard_v2/hard_v3/hard_v4 boundary synthesis has been exported as a separate
artifact. It does not overwrite the older hard_v2/hard_v3 cross-version
synthesis.

Script:

```text
scripts/export_downstream_boundary_synthesis.py
```

Outputs:

```text
benchmark/downstream/reports/downstream_boundary_synthesis.json
benchmark/downstream/reports/downstream_boundary_synthesis.md
benchmark/downstream/reports/downstream_boundary_synthesis.tex
```

Generated by:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_downstream_boundary_synthesis.py \
  --assert-current-boundary-synthesis
```

Current synthesis facts:

```text
primary_rows: 43
selected_comparisons: 6
context_comparisons: 9
forced_bad_total: 0/133
public_passed_hidden_failed: 133
```

Selected versus no_experience:

```text
hard_v2 tree-aware:      25/25 vs 23/25, success_delta=+2
hard_v2 strict visible:  23/25 vs 24/25, success_delta=-1
hard_v3 tree-aware:      29/30 vs 29/30, success_delta=0
hard_v3 strict visible:  29/30 vs 28/30, success_delta=+1
hard_v4 tree-aware:      24/24 vs 24/24, success_delta=0
hard_v4 strict visible:  22/24 vs 24/24, success_delta=-2
```

Interpretation:

```text
The final downstream story is not that SkillAdmit-selected universally wins.
The defensible story is a boundary ladder:

hard_v2:
  conditional positive evidence under tree-aware context

hard_v3:
  generalization boundary and strong negative-transfer evidence

hard_v4:
  stricter boundary that rejects selected superiority in strict visible-file
  mode and keeps forced bad artifacts at 0/48

Across hard_v2, hard_v3, and hard_v4, forced bad artifacts are 0/133 with 133
public-pass/hidden-fail failures. This is currently the strongest stable
downstream-validation claim.
```

Use this for high-level paper positioning. Use the suite-specific evidence
packages for exact per-suite tables.

## 20. Three-Boundary Paper Reporting Layer

The downstream paper section, claim-defense matrix, and paper artifact index now
use the hard_v2/hard_v3/hard_v4 boundary synthesis as their high-level source.
The older hard_v2/hard_v3 cross-version synthesis is still retained as a legacy
two-suite artifact, but it is no longer the main source for generated paper
wording.

Updated scripts:

```text
scripts/export_downstream_paper_section.py
scripts/export_downstream_claim_defense_matrix.py
scripts/export_paper_artifacts_index.py
```

Updated outputs:

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

Current export facts:

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

paper_artifacts_index:
  artifact_groups: 10
  table_index: 7
  claim_map: 10
  paper_section_result_paragraphs: 6
```

Current paper-facing story:

```text
Do claim:
  SkillAdmit-selected has conditional downstream utility evidence.
  hard_v2 tree-aware is the clearest positive selected result.
  hard_v3 and hard_v4 bound universal selected-superiority claims.
  forced harmful artifacts create systematic negative transfer: 0/133.

Do not claim:
  selected universally dominates no_experience.
  selected saves tokens across downstream tasks.
  precondition-only generally replaces repository-tree context.
  raw memory or all-skills is a safe admission policy.
```

## 21. Paper Claim Consistency Audit

The paper-facing reporting layer now has an executable consistency audit.

Script:

```text
scripts/audit_paper_claim_consistency.py
```

Outputs:

```text
benchmark/downstream/reports/paper_claim_consistency_audit.json
benchmark/downstream/reports/paper_claim_consistency_audit.md
benchmark/downstream/reports/paper_claim_consistency_audit.tex
```

Generated by:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/audit_paper_claim_consistency.py \
  --assert-current-audit
```

Current audit:

```text
total_checks: 12
passed_checks: 12
failed_checks: 0
forced_bad: 0/133
public-pass/hidden-fail: 133
hard_v4 strict selected: 22/24
hard_v4 strict no_experience: 24/24
```

What it guards:

```text
The audit checks that the paper section, claim-defense matrix, artifact index,
and boundary synthesis still agree on the three-boundary story. It also checks
that current paper-facing reports do not reuse the old 0/85 aggregate, that C6
uses hard_v4 plus boundary synthesis, and that C9 remains a not-supported token
savings claim.
```

Use:

```text
Run this before paper drafting, reviewer-response editing, or any new boundary
experiment. Treat it as reporting hygiene, not as new downstream evidence.
```

## 22. Model-Transfer Replication Protocol

The next clean experimental boundary is predeclared model-transfer replication,
not hard_v3/hard_v4 prompt tuning.

Script:

```text
scripts/export_model_transfer_replication_protocol.py
```

Outputs:

```text
benchmark/downstream/reports/model_transfer_replication_protocol.json
benchmark/downstream/reports/model_transfer_replication_protocol.md
benchmark/downstream/reports/model_transfer_replication_protocol.tex
```

Generated by:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_model_transfer_replication_protocol.py \
  --assert-current-protocol
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
hard_v3 tree-aware:          30 tasks x 8 strategies = 240 rows
hard_v3 strict visible-file: 30 tasks x 8 strategies = 240 rows
hard_v4 tree-aware:          24 tasks x 8 strategies = 192 rows
hard_v4 strict visible-file: 24 tasks x 8 strategies = 192 rows
```

Runner update:

```text
scripts/run_llm_downstream_validation.py now supports --model and --base-url.
This allows transfer runs to use a second model without editing .env.
```

Use:

```text
Choose the transfer model before running.
Set SKILLADMIT_TRANSFER_MODEL or pass --model explicitly.
Run the four commands listed in model_transfer_replication_protocol.md.
Use --resume only for interruption recovery.
Do not inspect failures to change prompts, artifacts, strategies, or tasks.
```

Claim boundary:

```text
This protocol is pre-run registration, not model evidence. After completion, a
separate model-transfer evidence package is required before adding paper claims.
One transfer model can test sensitivity, but it still cannot prove
model-general SkillAdmit-selected superiority.
```

## 24. Completed Model-Transfer Evidence

The predeclared model-transfer run has now completed with `mimo-v2.5` over the
frozen hard_v3 and hard_v4 matrices. This is post-run evidence, not prompt
tuning and not a new task boundary.

New scripts:

```text
scripts/export_model_transfer_evidence_package.py
scripts/export_model_transfer_cross_model_synthesis.py
```

New reports:

```text
benchmark/downstream/reports/model_transfer_evidence_package.json
benchmark/downstream/reports/model_transfer_evidence_package.md
benchmark/downstream/reports/model_transfer_evidence_package.tex
benchmark/downstream/reports/model_transfer_cross_model_synthesis.json
benchmark/downstream/reports/model_transfer_cross_model_synthesis.md
benchmark/downstream/reports/model_transfer_cross_model_synthesis.tex
```

Completed transfer matrix:

```text
hard_v3 tree-aware:          240/240 rows
hard_v3 strict visible-file: 240/240 rows
hard_v4 tree-aware:          192/192 rows
hard_v4 strict visible-file: 192/192 rows
total_rows: 864
parse_errors: 0
```

Main transfer facts:

```text
forced_bad_artifact: 0/108
forced_bad_public_passed_hidden_failed: 108

hard_v3 tree-aware selected vs no_experience: 29/30 vs 29/30
hard_v3 strict selected vs no_experience: 29/30 vs 28/30
hard_v4 tree-aware selected vs no_experience: 24/24 vs 23/24
hard_v4 strict selected vs no_experience: 21/24 vs 18/24
```

Cross-model interpretation:

```text
Replicated:
  forced harmful artifacts fail 0/108 on the baseline hard_v3/hard_v4 slice
  and 0/108 on the transfer model, for 0/216 combined.

Stable selected pattern:
  hard_v3 tree-aware selected tie replicates.
  hard_v3 strict selected +1 over no_experience replicates.

Model-sensitive selected pattern:
  hard_v4 strict selected reverses sign:
    baseline: 22/24 selected vs 24/24 no_experience, delta -2
    transfer: 21/24 selected vs 18/24 no_experience, delta +3
```

Artifact-index status:

```text
artifact_groups: 12
table_index: 8
claim_map: 10
```

Current guardrail:

```text
Do not merge model-transfer evidence into the original hard_v2/hard_v3/hard_v4
0/133 boundary aggregate.
Do not claim model-general selected superiority from one transfer model.
Do not tune hard_v3 or hard_v4 from observed transfer failures.
```

## 25. Model-Transfer Paper Addendum

The model-transfer reporting layer now includes a draftable paper addendum. This
is optional paper text for a replication/sensitivity subsection, not a stronger
main downstream result.

Script:

```text
scripts/export_model_transfer_paper_addendum.py --assert-current-addendum
```

Outputs:

```text
benchmark/downstream/reports/model_transfer_paper_addendum.json
benchmark/downstream/reports/model_transfer_paper_addendum.md
benchmark/downstream/reports/model_transfer_paper_addendum.tex
```

Current addendum facts:

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

Use:

```text
Use model_transfer_paper_addendum.md as optional paper text if the paper needs
a second-model replication paragraph or appendix table.
Keep the main paper section anchored to downstream_boundary_synthesis.json.
Do not use the addendum to claim model-general SkillAdmit-selected superiority
or selected token savings.
```

## 26. Public Reporting Hygiene Audit

The reporting layer now has a separate hygiene audit for public-facing
artifacts. Its purpose is to keep the old, current, and transfer aggregates from
being mixed into one overstated result.

Script:

```text
scripts/audit_reporting_hygiene.py --assert-current-hygiene
```

Outputs:

```text
benchmark/downstream/reports/reporting_hygiene_audit.json
benchmark/downstream/reports/reporting_hygiene_audit.md
benchmark/downstream/reports/reporting_hygiene_audit.tex
```

Aggregate roles:

```text
0/85:
  legacy hard_v2/hard_v3 cross-version synthesis only

0/133:
  current hard_v2/hard_v3/hard_v4 main downstream boundary

0/216:
  model-transfer hard_v3/hard_v4 replication/addendum layer
```

Current audit:

```text
total_checks: 8
passed_checks: 8
failed_checks: 0
status: pass
```

Important wording correction:

```text
G4_cross_version_synthesis in the artifact index is now explicitly historical.
Do not call the 0/85 hard_v2/hard_v3 synthesis the current top-level story.
Use downstream_boundary_synthesis for the main paper boundary.
Use model_transfer_paper_addendum only for the optional second-model addendum.
```

## 27. Public Release Readiness Audit

The repository now has a release-readiness audit for public push hygiene. It is
an engineering check, not a downstream-evidence artifact.

Script:

```text
scripts/audit_public_release_readiness.py --assert-current-release
```

Outputs:

```text
benchmark/downstream/reports/public_release_readiness_audit.json
benchmark/downstream/reports/public_release_readiness_audit.md
benchmark/downstream/reports/public_release_readiness_audit.tex
```

Current checks:

```text
R1 no dirty sensitive/local paths in git status
R2 expected local artifacts are ignored
R3 no forbidden tracked paths
R4 no obvious tracked credential patterns
R5 no tracked file over 2,000,000 bytes
R6 artifact-index regeneration scripts exist
R7 docs state runtime secrets belong in ignored .env
```

Current result:

```text
total_checks: 7
passed_checks: 7
failed_checks: 0
tracked_file_count: 1650
```

Public-release rule:

```text
Do not commit .env.
Do not commit benchmark/downstream/llm_runs/*/workspaces/.
Do not commit benchmark/agent_runs/.
Do not commit __pycache__/ or .pytest_cache/.
Run the release-readiness audit after regenerating artifact index and reporting audits.
```

## 28. Public Reproduction Guide Audit

The repository now has a public reproduction guide and a machine-checkable audit
for that guide. This is a release/navigation artifact, not new downstream
evidence.

Guide:

```text
docs/reproduction_guide.md
```

Script:

```text
scripts/audit_reproduction_guide.py --assert-current-reproduction-guide
```

Outputs:

```text
benchmark/downstream/reports/reproduction_guide_audit.json
benchmark/downstream/reports/reproduction_guide_audit.md
benchmark/downstream/reports/reproduction_guide_audit.tex
```

Current result:

```text
total_checks: 12
passed_checks: 12
failed_checks: 0
status: pass
```

The guide is the recommended public entry point. It tells readers to keep these
layers separate:

```text
0/133:
  current hard_v2/hard_v3/hard_v4 main downstream boundary

0/216:
  model-transfer hard_v3/hard_v4 addendum layer

0/85:
  historical hard_v2/hard_v3 synthesis only
```

Important guardrail:

```text
The guide does not authorize tuning hard_v2, hard_v3, or hard_v4 after reading
failures. If a new experiment is needed, predeclare hard_v5 or another fresh
boundary instead.
```

## 29. README Public Reader Path

The README has been strengthened as the public entry point. This is a navigation
and hygiene change, not new evidence.

README now points readers first to:

```text
docs/reproduction_guide.md
benchmark/downstream/reports/paper_artifacts_index.md
benchmark/downstream/reports/downstream_boundary_synthesis.md
benchmark/downstream/reports/model_transfer_cross_model_synthesis.md
```

It states these aggregate roles directly:

```text
0/133:
  main hard_v2/hard_v3/hard_v4 downstream boundary

0/216:
  model-transfer hard_v3/hard_v4 addendum

0/85:
  historical hard_v2/hard_v3 synthesis only
```

The reproduction-guide audit now checks README as well:

```text
RG11_readme_names_reader_entry_points
RG12_readme_preserves_public_claim_boundary
```

Current result:

```text
total_checks: 12
passed_checks: 12
failed_checks: 0
status: pass
```

## 23. Rule for Future Work

Every new code file should be documented when created:

```text
what the file does
why it is needed
its inputs
its outputs
who should run or import it
```

This is required so the experiment remains recoverable across Codex sessions.
