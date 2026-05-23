# SkillAdmit Progress Log

## 2026-05-12

### Current Goal

Build the minimum executable pipeline for SkillAdmit before scaling to real agent trajectories and larger benchmark samples.

The current focus is the Python import/debug task family.

---

## Completed

### 1. Project Skeleton

Created the initial project structure under:

```text
/home/lijx/workspace/skilladmit
```

Important directories:

```text
benchmark/tasks
benchmark/trajectories
benchmark/clusters
benchmark/admission_samples
skilladmit/controllers
skilladmit/eval
scripts
docs
```

### 2. Benchmark Plan v0

Created:

```text
docs/benchmark_plan_v0.md
```

The first benchmark family is:

```text
Python import/debug
```

It contains 5 templates:

```text
T1: missing third-party package
T2: local module mistaken as missing package
T3: relative import executed as script
T4: wrong current working directory
T5: broken package-qualified import
```

Note: the original T5 idea based on missing `__init__.py` was replaced because Python namespace packages made it unstable under Python 3.10.

### 3. Task Generation

Created:

```text
scripts/generate_py_import_tasks.py
```

Generated 20 tasks:

```text
5 templates * 4 variants = 20 tasks
```

Output directory:

```text
benchmark/tasks
```

### 4. Initial Failure Check

Created:

```text
scripts/check_initial_failures.py
```

Result:

```text
total: 20
failed_as_expected: 20
unexpectedly_passed: 0
errored: 0
```

This confirms that all generated tasks are valid failing bug tasks in their initial state.

### 5. Gold Fix Validation

Created:

```text
scripts/apply_gold_fixes.py
```

Result:

```text
total: 20
passed_after_gold_fix: 20
failed_after_gold_fix: 0
```

This confirms that all tasks have at least one valid fix and can pass the verifier.

### 6. Task Manifest

Created:

```text
scripts/build_task_manifest.py
benchmark/task_manifest.jsonl
```

Result:

```text
20 tasks listed in benchmark/task_manifest.jsonl
```

### 7. Seed Trajectories

Created:

```text
scripts/build_seed_trajectories.py
benchmark/trajectories/seed_trajectories.jsonl
```

Result:

```text
20 seed trajectory summaries
```

Important limitation:

These are not real agent trajectories yet. They are seed summaries generated from task design and gold-fix knowledge. They are used only to test the pipeline.

### 8. Seed Clusters

Created:

```text
scripts/build_seed_clusters.py
benchmark/clusters/seed_clusters.json
```

Result:

```text
5 experience clusters
```

Clusters:

```text
cluster_t1_missing_third_party -> defer
cluster_t2_local_module -> distill_into_skill
cluster_t3_relative_import_script -> distill_into_skill
cluster_t4_wrong_cwd -> distill_into_skill
cluster_t5_broken_package_import -> distill_into_skill
```

### 9. Candidate Artifacts

Created:

```text
scripts/build_seed_artifacts.py
benchmark/clusters/seed_clusters_with_artifacts.json
```

Each cluster now has:

```text
candidate_memory
candidate_skill
candidate_rule
```

### 10. Admission Samples

Created:

```text
scripts/build_seed_admission_samples.py
benchmark/admission_samples/seed_admission_samples.jsonl
```

Result:

```text
5 seed admission samples
```

Labels:

```text
sample_cluster_t1_missing_third_party => defer
sample_cluster_t2_local_module => distill_into_skill
sample_cluster_t3_relative_import_script => distill_into_skill
sample_cluster_t4_wrong_cwd => distill_into_skill
sample_cluster_t5_broken_package_import => distill_into_skill
```

### 11. Rule-Based Controller

Created:

```text
skilladmit/controllers/rule_based_controller.py
```

This is the first executable SkillAdmit controller.

It predicts one of:

```text
discard
store_as_memory
distill_into_skill
promote_to_rule
defer
```

### 12. Admission Evaluation

Created:

```text
skilladmit/eval/evaluate_admission.py
```

Initial result on 5 seed samples:

```text
samples: 5
correct: 5
accuracy: 1.000
```

Important limitation:

This result is only a pipeline sanity check. It is not a publishable result because the samples and rule controller are both seed-designed and the dataset is too small.

### 13. Heuristic Agent Runner

Created:

```text
scripts/run_heuristic_agent.py
benchmark/agent_runs/heuristic_agent_v0/trajectories.jsonl
```

Purpose:

```text
Pipeline validation only.
```

The heuristic runner is a rule-based repair runner, not a real LLM agent. It was used to validate that task workspaces, verifier execution, file edits, and trajectory logging all work end-to-end.

Result:

```text
tasks: 20
passed: 20/20
```

Important limitation:

The heuristic trajectories must not be used as main paper evidence because the runner knows the task templates and applies hard-coded fixes.

### 14. LLM Connection

Created:

```text
scripts/test_llm_connection.py
.env
.env.example
```

Configured OpenAI-compatible API access through:

```text
OPENAI_API_KEY
OPENAI_BASE_URL
SKILLADMIT_MODEL
```

Current model:

```text
mimo-v2.5-pro
```

Connection test result:

```text
reply: SkillAdmit connection ok
prompt_tokens: 41
completion_tokens: 57
total_tokens: 98
```

### 15. LLM Coding Agent v0

Created:

```text
scripts/run_llm_coding_agent.py
benchmark/agent_runs/llm_coding_agent_v0/trajectories.jsonl
```

The first real LLM agent is a single-shot patch agent:

```text
task + files + verifier output -> JSON patch -> apply edits -> rerun verifier
```

The agent does not see:

```text
template
gold_hint
gold fix
```

It sees only task instruction, repository files, failing command, and verifier output.

Initial run result:

```text
passed: 18/20
```

The two failures were caused by output formatting problems, not by verifier-confirmed wrong repairs:

```text
py_import_007: malformed JSON
py_import_008: empty model response
```

The runner was then updated with:

```text
max_completion_tokens = 4096
empty-response retry
JSON repair retry
--task-id for targeted reruns
```

Final full run result:

```text
tasks: 20
passed: 20/20
parse_errors: none
```

### 16. LLM Run Inspection

Created:

```text
scripts/inspect_llm_run.py
```

Final summary:

```text
total: 20
passed: 20
failed: 0
success_rate: 1.000
```

By template:

```text
T1_missing_third_party_package: 4/4
T2_local_module_mistaken_as_missing_package: 4/4
T3_relative_import_executed_as_script: 4/4
T4_wrong_current_working_directory: 4/4
T5_broken_package_structure: 4/4
```

### 17. Real LLM Trajectory Summaries

Created:

```text
scripts/build_llm_trajectories.py
benchmark/trajectories/llm_coding_agent_v0_trajectories.jsonl
```

Result:

```text
20 LLM trajectory summaries
```

Each trajectory summary contains:

```text
task_id
template
agent
model
success
initial/final return code
token usage
files seen
applied edits
observation
diagnosis
fix pattern
validation result
```

Important observation:

The original seed assumption for T1 was "missing third-party dependency", but the real LLM agent often repaired the tasks by removing unused missing imports. This shows why real agent trajectories are necessary: they can reveal repair patterns different from the benchmark designer's initial assumption.

### 18. Real LLM Clusters

Created:

```text
scripts/build_llm_clusters.py
benchmark/clusters/llm_coding_agent_v0_clusters.json
```

Result:

```text
5 LLM experience clusters
```

Clusters:

```text
llm_cluster_t1_missing_import_removed: 4/4, avg_tokens=1210.2
llm_cluster_t2_local_module: 4/4, avg_tokens=3680.2
llm_cluster_t3_relative_import_script: 4/4, avg_tokens=1579.2
llm_cluster_t4_wrong_cwd: 4/4, avg_tokens=2116.0
llm_cluster_t5_broken_package_import: 4/4, avg_tokens=1164.0
```

Important observation:

T2 local-module import repair is substantially more token-expensive than the other clusters. This may become useful evidence for cost-aware admission analysis.

### 19. Real LLM Candidate Artifacts

Created:

```text
scripts/build_llm_artifacts.py
benchmark/clusters/llm_coding_agent_v0_clusters_with_artifacts.json
```

Each real LLM cluster now has:

```text
candidate_memory
candidate_skill
candidate_rule
label
label_rationale
```

Current labels:

```text
llm_cluster_t1_missing_import_removed -> distill_into_skill
llm_cluster_t2_local_module -> distill_into_skill
llm_cluster_t3_relative_import_script -> distill_into_skill
llm_cluster_t4_wrong_cwd -> distill_into_skill
llm_cluster_t5_broken_package_import -> distill_into_skill
```

Important limitation:

This LLM-derived batch currently contains only skill-positive samples. It cannot evaluate the full five-action admission problem yet.

### 20. Real LLM Admission Samples

Created:

```text
scripts/build_llm_admission_samples.py
benchmark/admission_samples/llm_coding_agent_v0_admission_samples.jsonl
```

Result:

```text
5 LLM admission samples
```

Current samples:

```text
sample_llm_cluster_t1_missing_import_removed -> distill_into_skill
sample_llm_cluster_t2_local_module -> distill_into_skill
sample_llm_cluster_t3_relative_import_script -> distill_into_skill
sample_llm_cluster_t4_wrong_cwd -> distill_into_skill
sample_llm_cluster_t5_broken_package_import -> distill_into_skill
```

### 21. Controller Evaluation on Real LLM Samples

Evaluated:

```text
skilladmit/eval/evaluate_admission.py
```

Input:

```text
benchmark/admission_samples/llm_coding_agent_v0_admission_samples.jsonl
```

Result:

```text
samples: 5
correct: 5
accuracy: 1.000
```

Confusion:

```text
gold=distill_into_skill
  pred=distill_into_skill: 5
```

Important limitation:

This result only shows that the current rule-based controller recognizes stable successful LLM repair clusters as skill-worthy. It does not yet demonstrate robust five-class admission.

### 22. Curated Non-Skill Samples

Created:

```text
scripts/build_curated_non_skill_samples.py
benchmark/admission_samples/curated_non_skill_v0_admission_samples.jsonl
```

Purpose:

```text
Add non-skill and negative-transfer samples so the benchmark is no longer skill-positive only.
```

Result:

```text
5 curated non-skill samples
```

Samples:

```text
curated_discard_bad_pip_install_modulenotfound -> discard
curated_memory_specific_task_path_py_import_016 -> store_as_memory
curated_rule_check_before_generic_import_fix -> promote_to_rule
curated_defer_single_unused_import_success -> defer
curated_discard_transient_empty_model_response -> discard
```

Important limitation:

These samples are curated boundary/negative examples, not yet generated from a fully automatic real-agent pipeline.

### 23. Mixed v0 Admission Benchmark

Created:

```text
scripts/build_v0_mixed_admission_samples.py
benchmark/admission_samples/v0_mixed_admission_samples.jsonl
```

Inputs:

```text
benchmark/admission_samples/llm_coding_agent_v0_admission_samples.jsonl
benchmark/admission_samples/curated_non_skill_v0_admission_samples.jsonl
```

Result:

```text
10 mixed admission samples
```

Label counts:

```text
defer: 1
discard: 2
distill_into_skill: 5
promote_to_rule: 1
store_as_memory: 1
```

This is the first v0 benchmark that covers all five admission actions.

### 24. Rule-Based Controller v0 Update

Updated:

```text
skilladmit/controllers/rule_based_controller.py
```

The first evaluation on the mixed benchmark produced:

```text
samples: 10
correct: 7
accuracy: 0.700
```

Errors exposed three missing signals:

```text
bad skill / negative transfer should be rejected more strongly
single-trajectory evidence should be deferred
cross-cluster guardrails should be promoted to rule
```

The controller was updated with:

```text
harmful_skill_risk
guardrail_rule_signal
insufficient_evidence_signal
memory_specific_signal
runner_noise_signal
```

The updated controller result on v0 mixed benchmark:

```text
samples: 10
correct: 10
accuracy: 1.000
```

Confusion:

```text
gold=defer
  pred=defer: 1
gold=discard
  pred=discard: 2
gold=distill_into_skill
  pred=distill_into_skill: 5
gold=promote_to_rule
  pred=promote_to_rule: 1
gold=store_as_memory
  pred=store_as_memory: 1
```

Important limitation:

The 10/10 result is a v0 sanity result, not a publishable result. The benchmark is still tiny, partially curated, and the controller has been adjusted against this small development set. The next step must be dataset expansion, not further score tuning on these 10 samples.

---

## Current Status

The project now has three executable pieces.

Seed pipeline:

```text
tasks
-> seed trajectories
-> clusters
-> candidate artifacts
-> admission samples
-> controller prediction
-> evaluation
```

Real LLM pipeline:

```text
tasks
-> llm_coding_agent_v0 trajectories
-> LLM trajectory summaries
-> LLM experience clusters
-> LLM candidate artifacts
-> LLM admission samples
-> controller prediction
-> evaluation
```

Mixed admission benchmark:

```text
LLM skill-positive samples
+ curated non-skill samples
-> v0 mixed admission benchmark
-> five-action controller evaluation
```

The project has moved beyond seed-only data. It now contains real LLM agent traces from `mimo-v2.5-pro` on 20 Python import/debug tasks.

---

## Next Step

The next major step is to expand beyond the tiny 10-sample v0 benchmark.

The current mixed benchmark proves the pipeline, but not the research claim. The next expansion should create more samples for:

```text
discard
store_as_memory
promote_to_rule
defer
negative-transfer bad skills
```

Recommended next target:

```text
30-50 admission samples total
at least 5 samples per non-skill action
at least 10 negative-transfer / bad-skill samples
```

---

## Known Limitations

1. Current real LLM admission samples are all `distill_into_skill`.
2. The benchmark still lacks `discard`, `store_as_memory`, `promote_to_rule`, and `defer` examples from real trajectories.
3. The current LLM agent is a single-shot JSON patch agent, not a full multi-turn ReAct/tool-use agent.
4. The current controller is deterministic and hand-designed.
5. No LLM-as-judge, raw-memory, always-distill, or A-MAC-adapted baseline has been implemented yet.
6. No downstream validation comparison between admitted skill, raw memory, and no experience has been run yet.
7. No long-horizon token cost or break-even analysis has been implemented yet.

---

## 2026-05-21 Controller Regression Update

The v3 admission set exposed several controller boundary failures:

```text
dangerous workaround -> sometimes predicted as distill_into_skill/defer
project/environment fact -> often predicted as defer
global guardrail rule -> sometimes predicted as discard/defer
provider-conflicting evidence -> sometimes predicted as discard or rule
```

The controller was updated in:

```text
skilladmit/controllers/rule_based_controller.py
```

Main changes:

```text
harmful candidates are pushed more strongly toward discard
harmful candidates are penalized for promote_to_rule
project/environment metadata receives a stronger memory signal
memory signal no longer fires on generic workspace path strings
guardrail signal is computed from the candidate artifact rather than all evidence text
transferability markers now cover API/config/JSON/streaming/proxy cases
insufficient-evidence markers now cover provider conflicts and ambiguous preconditions
```

A new regression helper was added:

```text
scripts/run_admission_regression.py
```

Purpose:

```text
Run the current rule-based controller over all existing admission sample files
and fail if any file falls below the required accuracy.
```

Current command:

```bash
python scripts/run_admission_regression.py
```

Current verified result:

```text
checked_files: 6
min_accuracy:  1.000
passed_files:  6
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
```

Important caveat:

```text
v1/v2/v3 should now be treated as regression/development sets, not as clean
held-out evidence, because controller changes were informed by their errors.
```

A handoff document was added:

```text
docs/experiment_handoff.md
```

Purpose:

```text
Allow a future Codex session or human collaborator to resume the experiment
without reconstructing the pipeline from chat history.
```

Next scientific step:

```text
Freeze the current controller, create a fresh blind v4 set, evaluate once, and
only call it held-out if no tuning is performed from its errors.
```

---

## 2026-05-21 V4 Frozen Evaluation

The controller was frozen before v4 evaluation:

```text
skilladmit/controllers/rule_based_controller_v3_frozen.py
```

Purpose:

```text
Preserve the exact controller state after v1/v2/v3 regression tuning so later
controller edits cannot silently change the v4 result.
```

New files:

```text
scripts/build_v4_blind_admission_samples.py
scripts/evaluate_frozen_controller.py
scripts/inspect_frozen_controller_errors.py
docs/v4_blind_eval_protocol.md
```

File purposes:

```text
build_v4_blind_admission_samples.py
  Creates 50 balanced v4 admission samples, 10 per action.

evaluate_frozen_controller.py
  Evaluates the v4 samples with the frozen controller and writes predictions.

inspect_frozen_controller_errors.py
  Reads the frozen prediction file and prints detailed error cases.

v4_blind_eval_protocol.md
  Documents the v4 protocol, frozen result, and how the result may be used.
```

Commands run:

```bash
python -m py_compile \
  skilladmit/controllers/rule_based_controller_v3_frozen.py \
  scripts/evaluate_frozen_controller.py \
  scripts/build_v4_blind_admission_samples.py \
  scripts/inspect_frozen_controller_errors.py

python scripts/build_v4_blind_admission_samples.py
python scripts/evaluate_frozen_controller.py
python scripts/inspect_frozen_controller_errors.py
python scripts/run_admission_regression.py
```

V4 generated sample count:

```text
discard: 10
store_as_memory: 10
distill_into_skill: 10
promote_to_rule: 10
defer: 10
total: 50
```

Frozen v4 result:

```text
samples:  50
correct:  27
accuracy: 0.540
```

Confusion:

```text
gold=defer
  pred=defer: 7
  pred=discard: 1
  pred=distill_into_skill: 2

gold=discard
  pred=defer: 7
  pred=discard: 3

gold=distill_into_skill
  pred=defer: 1
  pred=distill_into_skill: 7
  pred=promote_to_rule: 2

gold=promote_to_rule
  pred=defer: 1
  pred=discard: 1
  pred=promote_to_rule: 8

gold=store_as_memory
  pred=defer: 8
  pred=store_as_memory: 2
```

Prediction output:

```text
benchmark/admission_samples/v4_frozen_controller_predictions.jsonl
```

Important interpretation:

```text
54.0% is a useful stress-test result. It shows the current rule-based baseline
does not generalize cleanly to newer admission scenarios.
```

Do not tune the frozen controller on v4 and still call v4 held-out. If v4 errors
are used to improve the method, v4 becomes a development set and a new v5 blind
set is required.

Observed weak areas:

```text
discard: harmful candidates without known marker phrases are often deferred
store_as_memory: local project/environment facts are often deferred
distill_into_skill: some procedural skills are over-promoted to rule
defer: some convention/setup conflicts are over-admitted as skills
```

Regression status after adding v4 files:

```text
checked_files: 6
min_accuracy:  1.000
passed_files:  6
failed_files:  0
```

The default regression script intentionally still checks only seed/LLM/v0/v1/v2/v3.
V4 is not included as a regression target because it is currently the frozen
evaluation result.

---

## 2026-05-21 V4 Development And V5 Frozen Evaluation

Following the v4 frozen result, v4 was explicitly converted into a development
set for controller improvement.

New/updated controller files:

```text
skilladmit/controllers/rule_based_controller_v4_dev.py
skilladmit/controllers/rule_based_controller_v4_frozen.py
skilladmit/controllers/rule_based_controller.py
```

File purposes:

```text
rule_based_controller_v4_dev.py
  Development controller improved using v4 error analysis.

rule_based_controller_v4_frozen.py
  Frozen copy of v4_dev before v5 evaluation. Do not tune this on v5.

rule_based_controller.py
  Current default controller; currently mirrors v4_dev for normal local use.
```

New generic evaluator:

```text
scripts/evaluate_controller_module.py
```

Purpose:

```text
Evaluate any controller module on one or more admission sample files.
This avoids creating a separate evaluation script for every controller version.
```

V4 development result:

```text
controller: skilladmit.controllers.rule_based_controller_v4_dev
samples:    benchmark/admission_samples/v4_blind_admission_samples.jsonl
total:      50
correct:    50
accuracy:   1.000
```

Historical regression result under v4_frozen:

```text
seed: 5/5
llm_coding_agent_v0: 5/5
v0_mixed: 10/10
v1_mixed: 25/25
v2_heldout-as-dev: 25/25
v3_heldout-as-dev: 25/25
v4_dev: 50/50
```

V5 blind samples were created by:

```text
scripts/build_v5_blind_admission_samples.py
```

Purpose:

```text
Generate a fresh 50-sample balanced blind set after freezing v4_dev.
```

V5 files:

```text
benchmark/admission_samples/v5_blind_admission_samples.jsonl
benchmark/admission_samples/v5_frozen_controller_predictions.jsonl
docs/v5_blind_eval_protocol.md
```

V5 frozen evaluation command:

```bash
python scripts/evaluate_controller_module.py \
  --controller-module skilladmit.controllers.rule_based_controller_v4_frozen \
  --samples benchmark/admission_samples/v5_blind_admission_samples.jsonl \
  --output benchmark/admission_samples/v5_frozen_controller_predictions.jsonl
```

V5 frozen result:

```text
samples:  50
correct:  30
accuracy: 0.600
```

V5 confusion:

```text
gold=defer
  pred=defer: 7
  pred=distill_into_skill: 3

gold=discard
  pred=defer: 1
  pred=discard: 9

gold=distill_into_skill
  pred=distill_into_skill: 10

gold=promote_to_rule
  pred=defer: 10

gold=store_as_memory
  pred=defer: 6
  pred=store_as_memory: 4
```

Interpretation:

```text
The v4_frozen controller generalized well to procedural skill admission and
most harmful discard cases, but failed badly on new promote_to_rule wording and
remained weak on project-specific memory.
```

Important caveat:

```text
V5 is the current clean blind result. Do not tune rule_based_controller_v4_frozen.py
on v5 and still call v5 held-out.
```

Next step:

```text
If improving from v5 errors, create rule_based_controller_v5_dev.py and treat
v5 as development data. Then create v6_blind_admission_samples.jsonl for the
next honest frozen evaluation.
```

---

## 2026-05-21 V5 Development And V6 Blind Evaluation

V5 was explicitly converted into development data. The improved controller is:

```text
skilladmit/controllers/rule_based_controller_v5_dev.py
```

File purpose:

```text
Development controller improved using v5 error analysis. It should not be used
to report v5 as held-out evidence.
```

The current default controller now mirrors v5 development behavior:

```text
skilladmit/controllers/rule_based_controller.py
```

Frozen controller for the next blind evaluation:

```text
skilladmit/controllers/rule_based_controller_v5_frozen.py
```

File purpose:

```text
Frozen copy of v5_dev before v6 evaluation. Do not tune this file using v6
errors and still call v6 held-out.
```

V5 development result:

```text
controller: skilladmit.controllers.rule_based_controller_v5_dev
samples:    benchmark/admission_samples/v5_blind_admission_samples.jsonl
total:      50
correct:    50
accuracy:   1.000
```

Historical regression under v5_dev/v5_frozen:

```text
seed: 5/5
llm_coding_agent_v0: 5/5
v0_mixed: 10/10
v1_mixed: 25/25
v2_heldout-as-dev: 25/25
v3_heldout-as-dev: 25/25
v4_blind-as-dev: 50/50
v5_blind-as-dev: 50/50
```

V6 blind sample generator:

```text
scripts/build_v6_blind_admission_samples.py
```

File purpose:

```text
Generate a fresh 50-sample balanced blind set after freezing v5_dev.
It writes benchmark/admission_samples/v6_blind_admission_samples.jsonl.
```

V6 protocol document:

```text
docs/v6_blind_eval_protocol.md
```

File purpose:

```text
Record the v6 generation/evaluation protocol, frozen result, confusion matrix,
known failure patterns, and the rule that v6 must become development data if it
is used for tuning.
```

V6 frozen evaluation command:

```bash
python scripts/evaluate_controller_module.py \
  --controller-module skilladmit.controllers.rule_based_controller_v5_frozen \
  --samples benchmark/admission_samples/v6_blind_admission_samples.jsonl \
  --output benchmark/admission_samples/v6_frozen_controller_predictions.jsonl
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
The v5_frozen controller generalizes cleanly to v6 discard and procedural skill
cases, but still fails under fresh wording for abstract global rules,
project-local memory, and conflict/insufficient-evidence defer cases.
```

Important caveat:

```text
V6 is now the current clean blind result. Do not tune
rule_based_controller_v5_frozen.py on v6 and still call v6 held-out.
```

Recommended next step:

```text
If improving from v6 errors, create rule_based_controller_v6_dev.py, treat v6
as development data, freeze that improved controller, and build v7 blind
samples for the next honest evaluation.
```

---

## 2026-05-21 V6 Development And V7 Blind Evaluation

V6 was explicitly converted into development data. The improved controller is:

```text
skilladmit/controllers/rule_based_controller_v6_dev.py
```

File purpose:

```text
Development controller improved using v6 error analysis. It should not be used
to report v6 as held-out evidence.
```

The current default controller now mirrors v6 development behavior:

```text
skilladmit/controllers/rule_based_controller.py
```

Frozen controller for the next blind evaluation:

```text
skilladmit/controllers/rule_based_controller_v6_frozen.py
```

File purpose:

```text
Frozen copy of v6_dev before v7 evaluation. Do not tune this file using v7
errors and still call v7 held-out.
```

V6 development result:

```text
controller: skilladmit.controllers.rule_based_controller_v6_dev
samples:    benchmark/admission_samples/v6_blind_admission_samples.jsonl
total:      50
correct:    50
accuracy:   1.000
```

Historical regression under the current default controller:

```text
checked_files: 9
min_accuracy:  1.000
passed_files:  9
failed_files:  0
```

V7 blind sample generator:

```text
scripts/build_v7_blind_admission_samples.py
```

File purpose:

```text
Generate a fresh 50-sample balanced blind set after freezing v6_dev.
It writes benchmark/admission_samples/v7_blind_admission_samples.jsonl.
```

V7 protocol document:

```text
docs/v7_blind_eval_protocol.md
```

File purpose:

```text
Record the v7 generation/evaluation protocol, frozen result, confusion matrix,
the single observed error, and the rule that v7 must become development data if
it is used for tuning.
```

V7 frozen evaluation command:

```bash
python scripts/evaluate_controller_module.py \
  --controller-module skilladmit.controllers.rule_based_controller_v6_frozen \
  --samples benchmark/admission_samples/v7_blind_admission_samples.jsonl \
  --output benchmark/admission_samples/v7_frozen_controller_predictions.jsonl
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
The v6_frozen controller generalizes well to v7, but still has a boundary issue:
a scoped reusable retry procedure with explicit safety preconditions can be
over-promoted into a global rule.
```

Important caveat:

```text
V7 is now the current clean blind result. Do not tune
rule_based_controller_v6_frozen.py on v7 and still call v7 held-out.
```

Recommended next step:

```text
Stop controller tuning for now and add baselines/downstream validation. If v7
is used for another controller improvement, create rule_based_controller_v7_dev.py
and then build v8 blind before making the next generalization claim.
```

---

## 2026-05-21 Baseline And Cost Reporting

Controller tuning was paused after the clean v7 result. This phase added
paper-facing comparison and accounting artifacts.

New baseline evaluator:

```text
scripts/evaluate_admission_baselines.py
```

File purpose:

```text
Evaluate always-action baselines, a simple text-only keyword baseline, and an
optional controller module on one or more admission sample files.
```

Command used:

```bash
python scripts/evaluate_admission_baselines.py \
  --samples benchmark/admission_samples/v7_blind_admission_samples.jsonl \
  --controller-module skilladmit.controllers.rule_based_controller_v6_frozen \
  --output-json benchmark/reports/v7_admission_baselines.json \
  --output-md benchmark/reports/v7_admission_baselines.md
```

Output reports:

```text
benchmark/reports/v7_admission_baselines.json
benchmark/reports/v7_admission_baselines.md
```

V7 baseline summary:

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
The controller decisively beats trivial always-action baselines. However, the
keyword baseline matches it on v7, although it fails on a different sample.
This means the current v7 set is still too surface-obvious for a strong paper
claim about semantic admission reasoning.
```

New cost summarizer:

```text
scripts/summarize_admission_costs.py
```

File purpose:

```text
Read real LLM coding-agent trajectory summaries and LLM-derived admission
samples, then report token/latency cost and parameterized break-even estimates.
```

Command used:

```bash
python scripts/summarize_admission_costs.py \
  --output-json benchmark/reports/llm_cost_summary.json \
  --output-md benchmark/reports/llm_cost_summary.md
```

Output reports:

```text
benchmark/reports/llm_cost_summary.json
benchmark/reports/llm_cost_summary.md
```

Cost summary:

```text
real LLM coding-agent tasks:       20
successful tasks:                  20
prompt tokens:                     14916
completion tokens:                 24083
total tokens:                      38999
avg tokens per task:               1950.0
total model latency seconds:       483.382
admitted artifacts:                5
avg source tokens per artifact:    7799.8
default break-even future tasks:   15.60
```

New paper-facing status report:

```text
docs/paper_eval_status.md
```

File purpose:

```text
Summarize the honest v7 result, baseline comparison, cost accounting, current
claim boundary, and the best next step.
```

Recommended next step:

```text
Implement downstream validation. Compare no experience, raw memory, distilled
skill, promoted rule, and SkillAdmit-selected artifacts on future debug tasks.
Measure success rate, verifier pass rate, tokens used, actions used, and
negative-transfer failures.
```

---

## 2026-05-21 Downstream Validation v0

This phase implemented a first executable downstream validation. It stays on the
SkillAdmit theme: whether admitted experience artifacts help solve future tasks.

New downstream task generator:

```text
scripts/build_downstream_py_import_tasks.py
```

File purpose:

```text
Generate 25 future Python import/debug tasks under benchmark/downstream/tasks/.
There are 5 tasks for each of five import-debug families.
```

New downstream runner:

```text
scripts/run_downstream_validation.py
```

File purpose:

```text
Run multiple artifact-use strategies on downstream tasks, execute real pytest
verifiers, and write detailed JSONL plus summary JSON/Markdown reports.
```

New protocol document:

```text
docs/downstream_validation_v0.md
```

File purpose:

```text
Record the downstream validation task design, strategy definitions, commands,
results, interpretation, and caveat.
```

Commands used:

```bash
python scripts/build_downstream_py_import_tasks.py
python scripts/run_downstream_validation.py
```

Initial task sanity check:

```text
initial_passed: 0
initial_failed: 25
```

Output reports:

```text
benchmark/downstream/results/downstream_validation_v0.jsonl
benchmark/downstream/results/downstream_validation_v0_summary.json
benchmark/downstream/results/downstream_validation_v0_report.md
```

Compared strategies:

```text
no_experience
bad_dependency_stub
raw_memory_replay
promoted_rule_only
distilled_skill
skilladmit_selected
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
Distilled skills transfer cleanly in this controlled task family.
Raw trace replay does not transfer to renamed future tasks.
Rule-only artifacts are not enough to repair tasks without concrete skills.
The overgeneralized dependency baseline creates negative transfer.
SkillAdmit-selected equals distilled_skill here because the current positive
LLM-derived clusters are all skill-level artifacts.
```

Caveat:

```text
This is a deterministic proxy experiment, not a final LLM-agent downstream
result. The next stronger version should run an LLM coding agent with the same
artifact contexts.
```

---

## 2026-05-21 LLM Downstream Validation v0

This phase added a real LLM-based downstream validation runner.

New runner:

```text
scripts/run_llm_downstream_validation.py
```

File purpose:

```text
Run an OpenAI-compatible chat model on downstream tasks with strategy-specific
artifact contexts, parse the model's JSON patch, apply edits in isolated
workspaces, and run the real verifier.
```

New protocol document:

```text
docs/llm_downstream_validation_v0.md
```

File purpose:

```text
Record the LLM downstream runner, supported strategies, smoke commands, results,
interpretation, and why the current smoke is not final downstream evidence.
```

Important environment note:

```text
Use the skilladmit conda environment. Running with base Python failed because
base inherited a SOCKS proxy but did not have socksio installed.
```

Smoke command 1:

```bash
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/run_llm_downstream_validation.py \
  --run-name llm_downstream_v0_smoke_5x2 \
  --strategy no_experience \
  --strategy skilladmit_selected \
  --task-id down_py_import_001 \
  --task-id down_py_import_006 \
  --task-id down_py_import_011 \
  --task-id down_py_import_016 \
  --task-id down_py_import_021
```

Smoke command 2:

```bash
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/run_llm_downstream_validation.py \
  --run-name llm_downstream_v0_smoke_bad_raw_5x2 \
  --strategy raw_memory \
  --strategy bad_dependency_rule \
  --task-id down_py_import_001 \
  --task-id down_py_import_006 \
  --task-id down_py_import_011 \
  --task-id down_py_import_016 \
  --task-id down_py_import_021
```

Outputs:

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
The real LLM downstream runner works end to end: API calls, JSON parsing, patch
application, verifier execution, token logging, and report generation all work.
However, the current downstream smoke tasks are too easy for the model because
no_experience already solves 5/5. This run does not prove artifact benefit.
```

Recommended next step:

```text
Create harder downstream tasks or a budget-constrained prompt setting where
no_experience is not already perfect. Then rerun no_experience, raw_memory,
distilled_skills_all, skilladmit_selected, and bad_dependency_rule on the same
tasks.
```

---

## 2026-05-21: LLM Downstream Hard v1

New files / changed files:

```text
scripts/build_downstream_hard_v1_tasks.py
scripts/run_llm_downstream_validation.py
docs/llm_downstream_hard_v1.md
```

File purposes:

```text
scripts/build_downstream_hard_v1_tasks.py
  Builds five harder downstream import/debug tasks under
  benchmark/downstream_hard_v1/tasks/. The tasks use visible-file budgets,
  distractor files, and hidden verifier checks.

scripts/run_llm_downstream_validation.py
  Extended with --tasks-dir, --use-task-visible-files, and --max-files so the
  same real LLM runner can evaluate hard downstream tasks.

docs/llm_downstream_hard_v1.md
  Records the hard-v1 design, commands, results, interpretation, and next step.
```

Sanity checks:

```text
initial_passed: 0/5
initial_failed: 5/5
gold_like_repairs_passed: 5/5
```

Main hard-v1 real LLM result:

```text
no_experience:       4/5 success_rate=0.800 negative_transfer=1 total_tokens=9530
skilladmit_selected: 5/5 success_rate=1.000 negative_transfer=0 total_tokens=15903
```

Additional artifact conditions:

```text
raw_memory:           5/5 success_rate=1.000 negative_transfer=0 total_tokens=13140
promoted_rules:       5/5 success_rate=1.000 negative_transfer=0 total_tokens=16218
distilled_skills_all: 5/5 success_rate=1.000 negative_transfer=0 total_tokens=17515
bad_dependency_rule:  5/5 success_rate=1.000 negative_transfer=0 total_tokens=13923
```

Most important observation:

```text
no_experience failed hard_py_import_004 by creating a top-level adapters/
package. The public pytest test passed, but the hidden verifier rejected the
masking stub. skilladmit_selected passed by using the package-internal import
repair pattern.
```

Interpretation:

```text
Hard v1 is the first real-LLM downstream run where no_experience is not already
perfect. It gives a small but concrete signal that SkillAdmit-selected skill
context can prevent a plausible invalid repair under limited file context.

This is still not final paper evidence because it has only five tasks and the
bad_dependency_rule condition was ignored by the model rather than causing
negative transfer.
```

Immediate next step:

```text
Build hard_v2 with 25 tasks, keep the hidden-verifier and visible-file-budget
design, and add a forced_bad_artifact condition if negative-transfer evidence is
needed.
```

---

## 2026-05-21: LLM Downstream Hard v2

New files / changed files:

```text
scripts/build_downstream_hard_v2_tasks.py
scripts/check_downstream_hard_v2_tasks.py
scripts/run_llm_downstream_validation.py
docs/llm_downstream_hard_v2.md
```

File purposes:

```text
scripts/build_downstream_hard_v2_tasks.py
  Generates 25 hard downstream tasks under benchmark/downstream_hard_v2/tasks/.
  Each task includes visible_files, gold_like_edits, forced_bad_artifact_edits,
  hidden verifier checks, and distractor files.

scripts/check_downstream_hard_v2_tasks.py
  Validates hard_v2 task quality: initial failure, gold-like repair success,
  forced bad artifact public-test success, and forced bad artifact hidden
  verifier failure.

scripts/run_llm_downstream_validation.py
  Extended with forced_bad_artifact, public_tests_after_edit,
  public_passed_hidden_failed, and artifact_adherence metrics.

docs/llm_downstream_hard_v2.md
  Records the hard_v2 protocol, commands, results, interpretation, and next
  expensive run.
```

Task sanity check:

```text
total: 25
initial_failed: 25
gold_passed: 25
forced_public_passed: 25
forced_verifier_failed: 25
```

Forced bad-artifact result:

```text
forced_bad_artifact: 0/25
success_rate: 0.000
negative_transfer: 25
public_passed_hidden_failed: 25
total_tokens: 0
```

Real LLM canary result:

```text
no_experience:       4/5 success_rate=0.800 negative_transfer=1 public_passed_hidden_failed=1 total_tokens=12775
skilladmit_selected: 5/5 success_rate=1.000 negative_transfer=0 public_passed_hidden_failed=0 total_tokens=13840
```

Most important canary failure:

```text
no_experience on hard_v2_py_import_016 duplicated runner_alpha/data/alpha.txt.
That made public pytest pass, but hidden verifier rejected it as a cwd masking
repair. skilladmit_selected passed by applying the cwd-sensitive path skill.
```

Interpretation:

```text
Hard v2 is now a stronger downstream scaffold than hard v1. It has 25 validated
tasks and a deterministic forced_bad_artifact baseline that creates systematic
negative transfer. The real LLM canary showed a useful gap, and the full
25-task LLM comparisons below have now been completed.
```

Originally planned expensive run:

```text
Run no_experience vs skilladmit_selected on all 25 hard_v2 tasks.
Only expand to raw_memory, promoted_rules, distilled_skills_all, and
bad_dependency_rule if the 25-task selected-skill comparison remains positive.
```

Update after full run:

```text
scripts/run_llm_downstream_validation.py
  Added --resume and --include-repo-tree. Resume allows long API runs to skip
  completed (strategy, task_id) rows. include-repo-tree gives the model paths
  without file contents, closer to a real coding-agent filesystem inspection.

scripts/inspect_llm_downstream_run.py
  Added a run inspection utility. It summarizes success rate, negative
  transfer, public-pass/hidden-fail counts, artifact adherence, token use, and
  failure details by strategy and template.
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

Interpretation:

```text
In the strict visible-file setting, SkillAdmit-selected is not the strongest
condition. The strongest condition is distilled_skills_all, but it is expensive.
Selected-only fails two T4 cwd tasks because the model lacks enough file-location
context to choose the right path anchor.
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

Interpretation:

```text
When the executor receives repository tree context, SkillAdmit-selected solves
all 25 tasks and no_experience solves 23. This suggests selected-skill failures
in the strict setting were mainly caused by missing precondition context, not by
bad admission labels.
```

## 2026-05-22

### 39. Selected + Precondition Context Downstream Strategy

Updated:

```text
scripts/run_llm_downstream_validation.py
```

What changed:

```text
Added strategy: skilladmit_selected_with_precondition_context
```

Purpose:

```text
Test whether a compact selected SkillAdmit artifact can keep the 25/25 hard_v2
downstream result when paired with explicit precondition context, without giving
the model the whole distilled skill library.
```

Inputs:

```text
benchmark/downstream_hard_v2/tasks/
benchmark/admission_samples/llm_coding_agent_v0_admission_samples.jsonl
```

Runner behavior:

```text
provides the selected skill
automatically includes repository tree paths
adds skill-specific guardrails for import classification and cwd/path anchoring
```

Output:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v2_selected_precondition_25/
```

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/run_llm_downstream_validation.py \
  --run-name llm_downstream_hard_v2_selected_precondition_25 \
  --tasks-dir benchmark/downstream_hard_v2/tasks \
  --use-task-visible-files \
  --resume \
  --strategy skilladmit_selected_with_precondition_context
```

Result:

```text
skilladmit_selected_with_precondition_context: 25/25
success_rate: 1.000
negative_transfer: 0
public_passed_hidden_failed: 0
artifact_adherence: 25/25
parse_errors: 0
total_tokens: 67504
avg_tokens: 2700.16
```

By template:

```text
T1_unused_missing_import_hard: 5/5, tokens=9326
T2_local_module_import_hard:  5/5, tokens=11986
T3_script_relative_import:    5/5, tokens=19866
T4_cwd_sensitive_path:        5/5, tokens=15243
T5_package_internal_import:   5/5, tokens=11083
```

Comparison:

```text
no_experience tree-aware:                      23/25, total_tokens=51548
skilladmit_selected tree-aware:                25/25, total_tokens=57597
skilladmit_selected_with_precondition_context: 25/25, total_tokens=67504
distilled_skills_all strict:                   25/25, total_tokens=84986
```

Interpretation:

```text
The new strategy keeps the desired 25/25 result and stays below all-skills token
cost. It is not cheaper than ordinary tree-aware skilladmit_selected, and it does
not improve raw success over that condition because ordinary tree-aware selected
already reached 25/25.

The value is tighter causal framing: the selected artifact is paired with the
precondition checks that the earlier strict visible-file failures lacked,
especially locating the real data file before choosing a cwd/path anchor.
```

### 40. Regression Checks For This Step

Completed:

```text
py_compile related scripts:
  scripts/build_downstream_hard_v2_tasks.py
  scripts/check_downstream_hard_v2_tasks.py
  scripts/run_llm_downstream_validation.py
  scripts/inspect_llm_downstream_run.py
  scripts/run_admission_regression.py

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

summary assertions for 25/25, zero negative transfer, zero public-hidden failure,
zero parse errors, repo tree included on every row, and total_tokens < 84986
```

### 41. Strict Precondition-Only Ablation

Updated:

```text
scripts/run_llm_downstream_validation.py
```

What changed:

```text
Added strategy: skilladmit_selected_with_precondition_only
```

Purpose:

```text
Separate the effect of explicit precondition guardrails from the effect of
repository-tree context. This tests whether selected skill + guardrail text alone
can repair the strict visible-file weakness.
```

Inputs:

```text
benchmark/downstream_hard_v2/tasks/
benchmark/admission_samples/llm_coding_agent_v0_admission_samples.jsonl
```

Runner behavior:

```text
provides the selected skill
adds skill-specific guardrails
does not automatically include repository tree paths
```

Output:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v2_precondition_only_25/
```

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/run_llm_downstream_validation.py \
  --run-name llm_downstream_hard_v2_precondition_only_25 \
  --tasks-dir benchmark/downstream_hard_v2/tasks \
  --use-task-visible-files \
  --resume \
  --strategy skilladmit_selected_with_precondition_only
```

Result:

```text
skilladmit_selected_with_precondition_only: 24/25
success_rate: 0.960
negative_transfer: 1
public_passed_hidden_failed: 0
artifact_adherence: 25/25
parse_errors: 0
included_repo_tree: 0/25
total_tokens: 72316
avg_tokens: 2892.64
```

By template:

```text
T1_unused_missing_import_hard: 5/5, tokens=10064
T2_local_module_import_hard:  5/5, tokens=14947
T3_script_relative_import:    4/5, tokens=16284
T4_cwd_sensitive_path:        5/5, tokens=17928
T5_package_internal_import:   5/5, tokens=13093
```

First-run failure:

```text
hard_v2_py_import_012
template: T3_script_relative_import_hard
```

Failure reason:

```text
The model correctly recognized that direct script execution breaks relative
imports, but it left `from .tools import format_value` at module top-level and
placed fallback import logic inside `if __name__ == "__main__"`. The fallback was
never reached because the top-level relative import failed first.
```

Comparison:

```text
strict skilladmit_selected:                    23/25, total_tokens=66608
strict selected+precondition-only:             24/25, total_tokens=72316
tree-aware skilladmit_selected:                25/25, total_tokens=57597
tree-aware selected+precondition-context:      25/25, total_tokens=67504
strict distilled_skills_all:                   25/25, total_tokens=84986
```

Interpretation:

```text
The first precondition-only run improved strict selected and solved all T4
cwd-sensitive path tasks, so explicit guardrails did carry signal in that call.
However, later stability replication dropped this condition to 23/25 and failed
one T4 case, so the T4 result should not be treated as stable. It also still
fails the T3 script-mode import family and is more token-expensive than
tree-aware selected.

The claim should be: precondition text partially repairs missing context, but it
does not replace repository-tree context.
```

### 42. Regression Checks After Strict Ablation

Completed:

```text
py_compile related scripts:
  scripts/build_downstream_hard_v2_tasks.py
  scripts/check_downstream_hard_v2_tasks.py
  scripts/run_llm_downstream_validation.py
  scripts/inspect_llm_downstream_run.py
  scripts/run_admission_regression.py

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

summary assertions for the first 24/25 run, the single hard_v2_py_import_012
failure, zero parse errors, no repo tree included on any row, and all five T4
tasks passing in that first run. Later stability replication showed this T4
success was not stable.
```

### 43. Hard v2 Strategy Matrix And Source-Hash Ledger

Created:

```text
scripts/summarize_hard_v2_results.py
```

What the file does:

```text
Aggregates all hard_v2 LLM downstream run directories into one strategy matrix,
template matrix, failure table, and source-hash ledger.
```

Why it is needed:

```text
Each run directory rewrites summary.json when the same run-name is resumed or
rerun. The matrix report makes the full downstream evidence table visible and
records SHA-256 hashes for summary/trajectory files so accidental changes are
detectable.
```

Inputs:

```text
benchmark/downstream/llm_runs/*/summary.json
benchmark/downstream/llm_runs/*/trajectories.jsonl
```

Outputs:

```text
benchmark/downstream/reports/hard_v2_strategy_matrix.json
benchmark/downstream/reports/hard_v2_strategy_matrix.md
```

Who runs it:

```text
Researchers or Codex sessions after adding, resuming, or recomputing any hard_v2
run.
```

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/summarize_hard_v2_results.py \
  --assert-current-hard-v2
```

Result before the later stability replications:

```text
runs: 6
strategy_rows: 14
template_rows: 70
failures: 67
```

Important matrix rows:

```text
strict_visible_file / skilladmit_selected:               23/25, tokens=66608
tree_aware / skilladmit_selected:                        25/25, tokens=57597
strict_precondition_only / selected+precondition-only:   24/25, tokens=72316
tree_aware_precondition_context / selected+precondition: 25/25, tokens=67504
strict_visible_file / distilled_skills_all:              25/25, tokens=84986
forced_bad_standalone / forced_bad_artifact:              0/25, public_hidden=25
```

Validation before the later stability replications:

```text
py_compile scripts/summarize_hard_v2_results.py
--assert-current-hard-v2 passed
jq assertions passed for strategy rows, template rows, source hashes,
precondition-only failure hard_v2_py_import_012, and T4 5/5 under the first
precondition-only run
```

### 44. Hard v2 Stability Replications

Purpose:

```text
Check whether the most important hard_v2 downstream conclusions survive a second
run with fresh model calls. This is not controller tuning and does not change
the admission policy.
```

Replication runs:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v2_replication_tree_selected_25/
benchmark/downstream/llm_runs/llm_downstream_hard_v2_replication_selected_precondition_25/
benchmark/downstream/llm_runs/llm_downstream_hard_v2_replication_precondition_only_25/
```

Commands:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/run_llm_downstream_validation.py \
  --run-name llm_downstream_hard_v2_replication_tree_selected_25 \
  --tasks-dir benchmark/downstream_hard_v2/tasks \
  --use-task-visible-files \
  --include-repo-tree \
  --resume \
  --strategy skilladmit_selected

PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/run_llm_downstream_validation.py \
  --run-name llm_downstream_hard_v2_replication_selected_precondition_25 \
  --tasks-dir benchmark/downstream_hard_v2/tasks \
  --use-task-visible-files \
  --resume \
  --strategy skilladmit_selected_with_precondition_context

PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/run_llm_downstream_validation.py \
  --run-name llm_downstream_hard_v2_replication_precondition_only_25 \
  --tasks-dir benchmark/downstream_hard_v2/tasks \
  --use-task-visible-files \
  --resume \
  --strategy skilladmit_selected_with_precondition_only
```

Results:

```text
replication_tree_selected:
  skilladmit_selected: 25/25
  negative_transfer: 0
  public_passed_hidden_failed: 0
  total_tokens: 52144

replication_selected_precondition:
  skilladmit_selected_with_precondition_context: 25/25
  negative_transfer: 0
  public_passed_hidden_failed: 0
  total_tokens: 64150

replication_precondition_only:
  skilladmit_selected_with_precondition_only: 23/25
  negative_transfer: 2
  public_passed_hidden_failed: 1
  total_tokens: 77487
```

Replication failure details:

```text
hard_v2_py_import_012:
  template: T3_script_relative_import_hard
  failure type: public passed but hidden failed
  reason: changed module-level relative import to bare script import, which passed
  direct script execution but failed hidden package-import validation

hard_v2_py_import_018:
  template: T4_cwd_sensitive_path_hard
  failure type: public failed
  reason: returned the resolved path instead of file contents after cwd/path
  repair, so output did not contain hard-v2-cwd-gamma
```

Stability interpretation:

```text
tree-aware skilladmit_selected is stable across two full runs: 25/25 and 25/25.
tree-aware selected+precondition is also stable: 25/25 and 25/25.
strict precondition-only is unstable and weaker: 24/25 then 23/25.
```

### 45. Matrix Update After Replications

Updated:

```text
scripts/summarize_hard_v2_results.py
benchmark/downstream/reports/hard_v2_strategy_matrix.json
benchmark/downstream/reports/hard_v2_strategy_matrix.md
```

What changed:

```text
Added metadata for the three replication run directories.
Added stability_groups to the JSON and Markdown report.
Extended --assert-current-hard-v2 to check the replication outcomes.
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
  failures:  none

tree_aware_selected_precondition_context:
  successes: [25, 25]
  tokens:    [67504, 64150]
  failures:  none

strict_precondition_only:
  successes: [24, 23]
  tokens:    [72316, 77487]
  failures:  hard_v2_py_import_012; then hard_v2_py_import_012 and hard_v2_py_import_018
```

### 46. Hard v2 Paper Evidence Export

Created:

```text
scripts/export_hard_v2_evidence_package.py
```

What the file does:

```text
Builds compact paper-facing hard_v2 evidence from the downstream run ledger:
primary strategy table, stability table, failure taxonomy, derived comparisons,
source hashes, and supported/unsupported claim lists.
```

Why it is needed:

```text
The individual `summary.json` files are correct but scattered and easy to
over-read. The evidence package gives the paper one stable downstream-validation
surface while preserving the strict-visible/tree-aware/precondition distinction.
```

Inputs:

```text
benchmark/downstream/llm_runs/*/summary.json
benchmark/downstream/llm_runs/*/trajectories.jsonl
```

Outputs:

```text
benchmark/downstream/reports/hard_v2_evidence_package.json
benchmark/downstream/reports/hard_v2_paper_tables.md
benchmark/downstream/reports/hard_v2_paper_tables.tex
```

Who runs it:

```text
Researchers or Codex sessions after adding, resuming, or recomputing hard_v2
runs, and before writing the downstream-validation section of a paper.
```

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_hard_v2_evidence_package.py \
  --assert-current-hard-v2
```

Result:

```text
primary_rows: 11
stability_rows: 3
failure_taxonomy_rows: 25
```

Derived comparisons:

```text
tree_aware_selected_success_delta_vs_no_experience: +2
tree_aware_selected_token_delta_vs_no_experience: +6049
selected_precondition_token_delta_vs_tree_selected: +9907
selected_precondition_token_delta_vs_all_skills: -17482
strict_precondition_only_success_delta_vs_strict_selected: +1 on the first run only
```

Interpretation:

```text
The package makes the paper claim sharper, not bigger. The supported positive
result is still tree-aware SkillAdmit-selected and tree-aware selected plus
preconditions reaching stable 25/25. The strict precondition-only ablation
remains weaker and unstable, so it should be reported as a failed replacement
for repository-tree context.
```

### 47. Hard v3 Deterministic Downstream Boundary

Created:

```text
docs/llm_downstream_hard_v3.md
scripts/build_downstream_hard_v3_tasks.py
scripts/check_downstream_hard_v3_tasks.py
benchmark/downstream_hard_v3/tasks/
```

What the files do:

```text
docs/llm_downstream_hard_v3.md
  Defines the hard_v3 scientific goal, stage-1 boundary, task families,
  checker invariants, planned strategy matrix, commands, and current claim
  boundary.

scripts/build_downstream_hard_v3_tasks.py
  Generates 30 fresh hard_v3 downstream tasks under
  benchmark/downstream_hard_v3/tasks/. The suite uses service, CLI, config,
  plugin, and resource-loading mini-projects rather than directly copying the
  hard_v2 minimal import/path cases.

scripts/check_downstream_hard_v3_tasks.py
  Validates every hard_v3 task: initial failure, gold-like repair success,
  forced bad artifact public-test success, and forced bad artifact hidden
  verifier failure.
```

Why this is needed:

```text
hard_v2 has been used enough to serve as evidence, not a tuning target. hard_v3
is the next clean downstream validation boundary for testing whether the
hard_v2 SkillAdmit-selected claim generalizes to a fresh task surface.
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

The suite keeps the current admitted skill names so the existing downstream
runner can compare `no_experience`, `skilladmit_selected`,
`skilladmit_selected_with_precondition_context`,
`skilladmit_selected_with_precondition_only`, `distilled_skills_all`,
`raw_memory`, `promoted_rules`, `bad_dependency_rule`, and
`forced_bad_artifact` without tuning the admission controller.

Deterministic checker result:

```text
total: 30
initial_failed: 30
gold_passed: 30
forced_public_passed: 30
forced_verifier_failed: 30
```

By template:

```text
T1_optional_integration_import:       5/5 all checks
T2_application_package_local_import:  5/5 all checks
T3_dual_use_command_module:           5/5 all checks
T4_repo_config_cwd_path:              5/5 all checks
T5_plugin_registry_internal_import:   5/5 all checks
T6_template_resource_cwd_path:        5/5 all checks
```

Regression checks:

```text
py_compile:
  scripts/build_downstream_hard_v3_tasks.py
  scripts/check_downstream_hard_v3_tasks.py
  scripts/build_downstream_hard_v2_tasks.py
  scripts/check_downstream_hard_v2_tasks.py
  scripts/run_llm_downstream_validation.py
  scripts/inspect_llm_downstream_run.py
  scripts/run_admission_regression.py

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

Current claim boundary:

```text
hard_v3 now supports a deterministic scaffold claim only: it is a validated
30-task downstream task suite with hidden-verifier negative-transfer controls.

It does not yet support LLM downstream success, token savings, or strategy
superiority claims. Those require fresh LLM runs after the task suite is treated
as frozen.
```

### 48. Hard v3 Tree-Aware Core LLM Run

Completed:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v3_tree_core_30x2/
```

Strategies:

```text
no_experience
skilladmit_selected
skilladmit_selected_with_precondition_context
forced_bad_artifact
```

Executor setting:

```text
--tasks-dir benchmark/downstream_hard_v3/tasks
--use-task-visible-files
--include-repo-tree
--resume
```

Final cleaned summary:

```text
forced_bad_artifact: 0/30, success_rate=0.000, negative_transfer=30,
  public_passed_hidden_failed=30, artifact_adherence=30/30,
  parse_errors=0, total_tokens=0

no_experience: 29/30, success_rate=0.967, negative_transfer=1,
  public_passed_hidden_failed=0, artifact_adherence=30/30,
  parse_errors=0, total_tokens=70208

skilladmit_selected: 29/30, success_rate=0.967, negative_transfer=1,
  public_passed_hidden_failed=0, artifact_adherence=30/30,
  parse_errors=0, total_tokens=69291

skilladmit_selected_with_precondition_context: 29/30,
  success_rate=0.967, negative_transfer=1,
  public_passed_hidden_failed=0, artifact_adherence=30/30,
  parse_errors=0, total_tokens=74559
```

API hygiene note:

```text
The first selected+precondition pass had two infrastructure failures:

hard_v3_agent_016: APIConnectionError
hard_v3_agent_017: APITimeoutError

Those two rows were removed from trajectories.jsonl and rerun. Both passed.
The final run has parse_errors=0.
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

Interpretation:

```text
This is not a SkillAdmit-selected superiority result. On hard_v3 tree-aware core,
no_experience, skilladmit_selected, and selected+precondition all reach 29/30.

SkillAdmit-selected fixes the no_experience T3 failure but introduces/fails a T6
resource-path case. The precondition context does not recover that T6 failure
and costs more tokens in this run.

The strong hard_v3 result is the negative-transfer control: if a bad admitted
artifact is executed, it systematically creates public-pass/hidden-fail repairs
across all 30 tasks.
```

Runner report polish:

```text
scripts/run_llm_downstream_validation.py now writes a generic report title,
run name, tasks directory, total rows, and a protocol-sensitive caveat rather
than hard-coding "LLM Downstream Validation v0".

scripts/check_downstream_hard_v2_tasks.py and
scripts/check_downstream_hard_v3_tasks.py now run checks with
PYTHONDONTWRITEBYTECODE=1 and pytest cache disabled, so verifier runs do not
leave __pycache__ or .pytest_cache directories inside task repos.
```

Current claim boundary:

```text
Do not claim hard_v3 token savings, selected superiority, or precondition
superiority from this run.

Do not tune prompt or strategy text from hard_v3_agent_013 or hard_v3_agent_027
unless hard_v3 is explicitly converted from an evaluation boundary into a
development set.

The next clean hard_v3 step is either a pre-declared matrix extension
(precondition-only, all-skills, raw-memory, promoted-rules) or a fresh
replication, not post-hoc strategy editing.
```

### 49. Hard v3 Full Strategy Matrix

Completed tree-aware matrix extension:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v3_tree_core_30x2/

Added after the core run:
  distilled_skills_all
  raw_memory
  promoted_rules
  bad_dependency_rule
```

Completed strict visible-file matrix:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v3_strict_30x8/

Strategies:
  no_experience
  skilladmit_selected
  skilladmit_selected_with_precondition_only
  distilled_skills_all
  raw_memory
  promoted_rules
  bad_dependency_rule
  forced_bad_artifact
```

Created:

```text
scripts/summarize_hard_v3_results.py
benchmark/downstream/reports/hard_v3_strategy_matrix.json
benchmark/downstream/reports/hard_v3_strategy_matrix.md
```

What the file does:

```text
Builds an auditable hard_v3 strategy matrix from completed LLM downstream runs,
including strategy-level results, template-level results, failure rows, derived
comparisons, source hashes, and explicit claim boundaries.
```

Why it is needed:

```text
hard_v3 now has multiple executor settings. Individual summary.json files are
easy to over-read, especially because tree-aware and strict visible-file results
tell different stories.
```

Current matrix summary:

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

Derived comparisons:

```text
tree_selected_success_delta_vs_no_experience:                  0
tree_selected_token_delta_vs_no_experience:                 -917
tree_precondition_context_success_delta_vs_selected:           0
tree_precondition_context_token_delta_vs_selected:          +5268
tree_raw_memory_success_delta_vs_no_experience:               +1
tree_raw_memory_token_delta_vs_no_experience:              -1455
tree_all_skills_success_delta_vs_selected:                    +1
tree_all_skills_token_delta_vs_selected:                   +6312

strict_selected_success_delta_vs_no_experience:               +1
strict_selected_token_delta_vs_no_experience:              -2763
strict_precondition_only_success_delta_vs_selected:           +1
strict_precondition_only_token_delta_vs_selected:         +11225
strict_raw_memory_success_delta_vs_no_experience:             +2
strict_raw_memory_token_delta_vs_no_experience:             -364
```

Interpretation:

```text
hard_v3 weakens a simplistic SkillAdmit-selected superiority story. In the
tree-aware setting, ordinary selected ties no_experience at 29/30, while
raw_memory, bad_dependency_rule, and all-skills reach 30/30. In strict
visible-file, ordinary selected is 29/30 versus no_experience 28/30, but
precondition-only and raw_memory reach 30/30.

The bad_dependency_rule result must not be read as "bad advice is safe":
artifact adherence is only 4/30 in tree-aware and 11/30 in strict visible-file.
The model often succeeds by ignoring the harmful artifact. The forced_bad_artifact
condition remains the real negative-transfer evidence and is 0/30 in both
settings with 30 public-pass/hidden-fail cases.

The honest hard_v3 claim is therefore boundary-setting: SkillAdmit-selected is
not sufficient as a universal best downstream context, explicit preconditions can
matter strongly on this suite, and harmful artifacts create systematic negative
transfer when actually executed.
```

Current claim boundary:

```text
Do not tune prompts or task design from hard_v3 failures.
Do not claim hard_v3 selected superiority.
Do not claim hard_v3 selected token savings.
Do not claim raw memory or bad_dependency_rule are valid admission policies.
Use hard_v3 mainly as generalization/boundary evidence and negative-transfer
evidence.
```

### 50. Hard v3 Paper Evidence Export

Created:

```text
scripts/export_hard_v3_evidence_package.py
```

What the file does:

```text
Builds a compact paper-facing hard_v3 evidence package from the strategy
matrix: primary strategy table, selected comparisons, artifact-adherence table,
non-forced failure taxonomy, source hashes, Markdown paper tables, LaTeX table,
and explicit supported/unsupported claims.
```

Why it is needed:

```text
hard_v3 is boundary evidence, not a simple selected-wins result. The paper needs
a compact surface that prevents over-reading raw_memory, bad_dependency_rule,
or selected token deltas as stronger claims than the data supports.
```

Inputs:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v3_tree_core_30x2/
benchmark/downstream/llm_runs/llm_downstream_hard_v3_strict_30x8/
benchmark/downstream/reports/hard_v3_strategy_matrix.json
```

Outputs:

```text
benchmark/downstream/reports/hard_v3_evidence_package.json
benchmark/downstream/reports/hard_v3_paper_tables.md
benchmark/downstream/reports/hard_v3_paper_tables.tex
```

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_hard_v3_evidence_package.py \
  --assert-current-hard-v3
```

Result:

```text
primary_rows: 16
artifact_adherence_rows: 14
non_forced_failures: 9
```

Key paper-facing boundary:

```text
Supported:
  hard_v3 is a fresh 30-task downstream validation boundary
  forced bad artifacts produce systematic negative transfer in both settings
  tree-aware selected ties no_experience at 29/30
  strict selected+precondition-only reaches 30/30
  raw_memory reaches 30/30 in both settings and cannot be ignored as a baseline
  bad_dependency_rule success is explained by low artifact adherence

Not supported:
  selected superiority
  selected token savings
  tree-aware selected+precondition superiority
  repo tree being always necessary
  raw memory being a safe admission policy
  bad dependency advice being safe
  prompt tuning from hard_v3 failures while still treating hard_v3 as clean evidence
```

### 51. Cross-Version Downstream Synthesis

Created:

```text
scripts/export_downstream_cross_version_synthesis.py
```

What the file does:

```text
Reads the frozen hard_v2 and hard_v3 paper-facing evidence packages and exports
a cross-version downstream synthesis table, derived comparisons, source package
hashes, and explicit supported/unsupported paper claims.
```

Why it is needed:

```text
hard_v2 and hard_v3 now answer different scientific questions. hard_v2 is
positive evidence for tree-aware SkillAdmit-selected utility. hard_v3 is
boundary evidence showing that selected does not universally dominate on a
fresh downstream suite. The paper needs both facts in one place instead of a
hand-written narrative copied from individual summary files.
```

Inputs:

```text
benchmark/downstream/reports/hard_v2_evidence_package.json
benchmark/downstream/reports/hard_v3_evidence_package.json
```

Outputs:

```text
benchmark/downstream/reports/downstream_cross_version_synthesis.json
benchmark/downstream/reports/downstream_cross_version_synthesis.md
benchmark/downstream/reports/downstream_cross_version_synthesis.tex
```

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_downstream_cross_version_synthesis.py \
  --assert-current-synthesis
```

Current export:

```text
primary_rows: 27
forced_bad_total_tasks: 85
selected_superiority_consistent: False
selected_token_savings_supported: False
```

Key synthesis:

```text
hard_v2 supports a positive tree-aware selected result:
  selected 25/25 versus no_experience 23/25, with selected replicated at 25/25.

hard_v3 rejects a universal selected-superiority story:
  tree-aware selected ties no_experience at 29/30.
  strict selected is 29/30 while precondition-only and raw_memory are 30/30.

Across hard_v2 and hard_v3 forced bad-artifact controls:
  forced_bad_artifact success: 0/85
  public_passed_hidden_failed: 85/85
  negative_transfer: 85/85
```

Paper-facing boundary:

```text
Supported:
  downstream hidden-verifier evidence is now stronger than admission accuracy alone
  harmful admitted artifacts can create systematic public-pass/hidden-fail transfer
  SkillAdmit-selected utility is conditional and context-dependent
  repo tree and preconditions are important variables, not universal guarantees

Not supported:
  universal SkillAdmit-selected dominance
  cross-version selected token savings
  raw_memory as a safe admission policy
  bad dependency advice as safe when the model often ignores it
  prompt or strategy tuning from hard_v2/hard_v3 failures while preserving them as clean evidence
```

### 52. Downstream Paper Evaluation Section Export

Created:

```text
scripts/export_downstream_paper_section.py
```

What the file does:

```text
Reads the frozen cross-version downstream synthesis package and exports a
paper-ready downstream validation section in JSON, Markdown, and LaTeX. The
section includes research questions, protocol wording, result interpretation,
one-paragraph paper wording, table captions, and explicit claim limits.
```

Why it is needed:

```text
The downstream result is subtle: hard_v2 supports tree-aware selected utility,
while hard_v3 rejects universal selected superiority. Hand-writing the paper
section from individual summary files risks overclaiming. This exporter keeps
the prose tied to the frozen synthesis artifact and asserts the main red lines.
```

Input:

```text
benchmark/downstream/reports/downstream_cross_version_synthesis.json
```

Outputs:

```text
benchmark/downstream/reports/downstream_paper_eval_section.json
benchmark/downstream/reports/downstream_paper_eval_section.md
benchmark/downstream/reports/downstream_paper_eval_section.tex
```

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_downstream_paper_section.py \
  --assert-current-paper-section
```

Current export:

```text
research_questions: 3
result_paragraphs: 5
claim_limits: 7
forced_bad_total_tasks: 85
```

Paper-section thesis:

```text
Downstream validation gives a sharper claim boundary than admission accuracy
alone. hard_v2 supports SkillAdmit-selected utility in a tree-aware coding-agent
setting, but hard_v3 does not support universal selected superiority. The
strongest cross-version result is safety-related: forced harmful artifacts
achieve 0/85 success with 85 public-pass/hidden-fail cases.
```

Asserted red lines:

```text
selected_superiority_consistent: False
selected_token_savings_supported: False
repo_tree_necessity_universal: False
forced_bad_total_successes: 0
forced_bad_total_public_passed_hidden_failed: 85
```

### 53. Downstream Claim Defense Matrix

Created:

```text
scripts/export_downstream_claim_defense_matrix.py
```

What the file does:

```text
Reads the paper-facing hard_v2/hard_v3 evidence packages, cross-version
synthesis, and generated paper section. It exports a claim-by-claim defense
matrix: what can be claimed, what evidence supports it, what wording is allowed,
what wording is forbidden, and how to answer likely reviewer objections.
```

Why it is needed:

```text
SkillAdmit's downstream evidence is intentionally conditional. The matrix keeps
the paper from drifting into stronger claims than the evidence supports:
hard_v2 is positive tree-aware selected evidence, hard_v3 is a generalization
boundary, and forced bad artifacts are the strongest negative-transfer signal.
```

Inputs:

```text
benchmark/downstream/reports/hard_v2_evidence_package.json
benchmark/downstream/reports/hard_v3_evidence_package.json
benchmark/downstream/reports/downstream_cross_version_synthesis.json
benchmark/downstream/reports/downstream_paper_eval_section.json
```

Outputs:

```text
benchmark/downstream/reports/downstream_claim_defense_matrix.json
benchmark/downstream/reports/downstream_claim_defense_matrix.md
benchmark/downstream/reports/downstream_claim_defense_matrix.tex
```

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_downstream_claim_defense_matrix.py \
  --assert-current-claim-defense
```

Current export:

```text
claim_count: 10
global_red_lines: 6
```

Claim cards:

```text
C1_downstream_hidden_verifier_is_required
C2_hard_v2_tree_selected_positive
C3_hard_v2_strict_visible_boundary
C4_hard_v3_generalization_boundary
C5_repo_tree_and_preconditions_are_context_variables
C6_forced_bad_artifacts_negative_transfer
C7_bad_dependency_rule_is_not_safe
C8_raw_memory_is_a_serious_baseline_not_a_policy
C9_selected_token_savings_not_supported
C10_all_skills_is_strong_but_not_the_target_policy
```

Global red lines:

```text
Do not claim universal SkillAdmit-selected superiority.
Do not claim cross-version SkillAdmit-selected token savings.
Do not claim precondition-only generally replaces repository-tree context.
Do not claim raw memory is a safe admission policy from hard_v3 success alone.
Do not claim bad dependency advice is safe when the model often ignored it.
Do not tune hard_v2 or hard_v3 failures while treating them as clean evidence.
```

### 54. Paper Artifacts Index

Created:

```text
scripts/export_paper_artifacts_index.py
```

What the file does:

```text
Builds a one-stop index of the paper-facing SkillAdmit artifacts: admission
context, hard_v2 evidence, hard_v3 evidence, cross-version synthesis, generated
paper section, claim-defense matrix, and reporting handoff files. The index
records each artifact's role, primary files, support files, regeneration
commands, paper use, and forbidden use.
```

Why it is needed:

```text
The repo now has many summaries and reports. The paper should cite the right
artifact for the right purpose: evidence packages and synthesis reports for
claims, generated paper-section text for drafting, claim-defense matrix for
reviewer responses, and individual run summaries only for debugging.
```

Inputs:

```text
benchmark/reports/v7_admission_baselines.json
benchmark/reports/llm_cost_summary.json
benchmark/downstream/reports/hard_v2_evidence_package.json
benchmark/downstream/reports/hard_v3_evidence_package.json
benchmark/downstream/reports/downstream_cross_version_synthesis.json
benchmark/downstream/reports/downstream_paper_eval_section.json
benchmark/downstream/reports/downstream_claim_defense_matrix.json
```

Outputs:

```text
benchmark/downstream/reports/paper_artifacts_index.json
benchmark/downstream/reports/paper_artifacts_index.md
benchmark/downstream/reports/paper_artifacts_index.tex
```

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_paper_artifacts_index.py \
  --assert-current-artifacts-index
```

Current export:

```text
artifact_groups: 8
table_index: 5
claim_map: 10
forced_bad_total_tasks: 85
```

Artifact groups:

```text
G1_admission_context
G2_hard_v2_evidence
G3_hard_v3_evidence
G4_cross_version_synthesis
G5_paper_section
G6_claim_defense
G7_reporting_handoff
G8_hard_v4_scaffold
```

Important use rule:

```text
Use paper_artifacts_index.md as the navigation layer before writing or revising
the paper. Do not cite individual llm_runs summary.json files as primary paper
evidence when evidence packages, synthesis reports, and paper tables exist.
```

### 55. Hard v4 Downstream Scaffold

Created:

```text
docs/llm_downstream_hard_v4.md
scripts/build_downstream_hard_v4_tasks.py
scripts/check_downstream_hard_v4_tasks.py
```

What the files do:

```text
build_downstream_hard_v4_tasks.py:
  deterministically generates a candidate hard_v4 downstream task suite.

check_downstream_hard_v4_tasks.py:
  validates initial failure, gold-like pass, forced-public pass, and
  forced-hidden failure for each generated task.

docs/llm_downstream_hard_v4.md:
  defines the hard_v4 scientific goal, task families, hidden verifier design,
  commands, planned strategy matrix, and hygiene rules.
```

Why it is needed:

```text
hard_v2 and hard_v3 are frozen evidence boundaries. hard_v4 is the next
candidate clean downstream boundary if the project continues experimentally.
It gives a fresh task surface rather than tuning prompts or strategies against
hard_v2/hard_v3 failures.
```

Current generated scaffold:

```text
24 tasks = 6 templates x 4 variants

T1_optional_telemetry_import
T2_src_layout_package_import
T3_dual_entrypoint_command
T4_workspace_config_resolution
T5_resource_template_resolution
T6_plugin_registry_namespace
```

Temporary validation command:

```bash
rm -rf /tmp/skilladmit_hard_v4_tasks

PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/build_downstream_hard_v4_tasks.py \
  --tasks-dir /tmp/skilladmit_hard_v4_tasks

PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/check_downstream_hard_v4_tasks.py \
  --tasks-dir /tmp/skilladmit_hard_v4_tasks
```

Temporary validation result:

```text
total: 24
initial_failed: 24
gold_passed: 24
forced_public_passed: 24
forced_verifier_failed: 24
```

Important boundary:

```text
No hard_v4 LLM API has been run.
The earlier temp-only scaffold step has been superseded by section 56.
No hard_v4 paper claim exists yet.
Before any hard_v4 LLM matrix, explicitly freeze the generated task boundary.
```

### 56. Hard v4 Scaffold Freeze Manifest

Created:

```text
scripts/export_hard_v4_scaffold_manifest.py
benchmark/downstream_hard_v4/tasks/
benchmark/downstream/reports/hard_v4_scaffold_manifest.json
benchmark/downstream/reports/hard_v4_scaffold_manifest.md
benchmark/downstream/reports/hard_v4_scaffold_manifest.tex
```

What the files do:

```text
export_hard_v4_scaffold_manifest.py:
  reads the generated hard_v4 task tree and writes task counts, template
  counts, logical file size, task-tree hashes, per-task hashes, source hashes,
  and optional checker results.

benchmark/downstream_hard_v4/tasks/:
  contains the generated 24-task hard_v4 downstream scaffold.

hard_v4_scaffold_manifest.*:
  records the freeze-ready scaffold boundary before any hard_v4 LLM run.
```

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_hard_v4_scaffold_manifest.py \
  --run-checker \
  --assert-current-hard-v4-scaffold
```

Current export:

```text
stage: scaffold_frozen_no_llm_evidence
tasks_dir: benchmark/downstream_hard_v4/tasks/
task_count: 24
file_count: 244
template_counts: 6 templates x 4 tasks
initial_failed: 24/24
gold_passed: 24/24
forced_public_passed: 24/24
forced_verifier_failed: 24/24
```

Important boundary:

```text
This is a scaffold freeze record, not an LLM downstream result.
No hard_v4 LLM API has been run.
No hard_v4 SkillAdmit success claim exists yet.
Do not tune hard_v4 prompts or strategies from observed failures while keeping
hard_v4 as clean evidence.
```

### 57. Hard v4 LLM Downstream Matrix

Created:

```text
scripts/summarize_hard_v4_results.py
scripts/export_hard_v4_evidence_package.py
benchmark/downstream/reports/hard_v4_strategy_matrix.json
benchmark/downstream/reports/hard_v4_strategy_matrix.md
benchmark/downstream/reports/hard_v4_evidence_package.json
benchmark/downstream/reports/hard_v4_paper_tables.md
benchmark/downstream/reports/hard_v4_paper_tables.tex
```

What the files do:

```text
summarize_hard_v4_results.py:
  reads the completed hard_v4 tree-aware and strict visible-file LLM runs,
  builds strategy/template/failure matrices, records source hashes, and asserts
  the current hard_v4 evidence boundary.

export_hard_v4_evidence_package.py:
  builds compact paper-facing hard_v4 tables, artifact-adherence summaries,
  failure taxonomy, derived comparisons, source hashes, and explicit claim
  boundaries.

hard_v4_strategy_matrix.*:
  auditable full matrix for the hard_v4 runs.

hard_v4_evidence_package.json and hard_v4_paper_tables.*:
  paper-facing hard_v4 evidence. Use these instead of citing individual
  summary.json files.
```

LLM runs:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v4_tree_canary_6x4/
benchmark/downstream/llm_runs/llm_downstream_hard_v4_strict_canary_6x4/
benchmark/downstream/llm_runs/llm_downstream_hard_v4_tree_24x8/
benchmark/downstream/llm_runs/llm_downstream_hard_v4_strict_24x8/
```

Tree-aware full matrix:

```text
bad_dependency_rule:                            24/24, tokens=51974, artifact_adherence=7/24
distilled_skills_all:                           24/24, tokens=68776
forced_bad_artifact:                             0/24, public_hidden=24
no_experience:                                  24/24, tokens=46685
promoted_rules:                                 24/24, tokens=58813
raw_memory:                                     24/24, tokens=53406
skilladmit_selected:                            24/24, tokens=48682
skilladmit_selected_with_precondition_context:  24/24, tokens=63586
```

Strict visible-file full matrix:

```text
bad_dependency_rule:                            24/24, tokens=63789, artifact_adherence=4/24
distilled_skills_all:                           24/24, tokens=69049
forced_bad_artifact:                             0/24, public_hidden=24
no_experience:                                  24/24, tokens=53055
promoted_rules:                                 23/24, tokens=69221
raw_memory:                                     23/24, tokens=65070
skilladmit_selected:                            22/24, tokens=58450
skilladmit_selected_with_precondition_only:     23/24, tokens=69961
```

Derived hard_v4 comparisons:

```text
tree selected vs no_experience:          success_delta=0, token_delta=+1997
tree selected+precondition vs selected:  success_delta=0, token_delta=+14904
strict selected vs no_experience:        success_delta=-2, token_delta=+5395
strict precondition-only vs selected:    success_delta=+1, token_delta=+11511
forced_bad_artifact aggregate:           0/48 success, 48 public-pass/hidden-fail
```

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/summarize_hard_v4_results.py \
  --assert-current-hard-v4

PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_hard_v4_evidence_package.py \
  --assert-current-hard-v4
```

Paper artifacts index was also updated:

```text
benchmark/downstream/reports/paper_artifacts_index.json
benchmark/downstream/reports/paper_artifacts_index.md
benchmark/downstream/reports/paper_artifacts_index.tex

artifact_groups: 9
table_index: 6
claim_map: 10
forced_bad_total_tasks: 85
hard_v4_forced_bad_total_tasks: 48
```

Interpretation:

```text
Hard v4 is not a selected-win result. Tree-aware hard_v4 is saturated because
every non-forced strategy reaches 24/24. Strict visible-file hard_v4 is worse
for ordinary selected: no_experience reaches 24/24, while selected reaches
22/24 and selected+precondition-only reaches 23/24.

The hard_v4 result is valuable because it sharpens the boundary: SkillAdmit
evidence must be reported as conditional, not universal. The strongest hard_v4
signal is negative transfer from harmful artifacts: forced_bad_artifact is 0/48
and all 48 failures are public-pass/hidden-fail cases.

The ordinary bad_dependency_rule rows are not proof that harmful advice is
safe. Artifact adherence is low: 7/24 tree-aware and 4/24 strict.
```

Boundary:

```text
Do not tune hard_v4 prompts, strategy text, or tasks from the observed failures.
Do not claim SkillAdmit-selected improves hard_v4 success.
Do not claim SkillAdmit-selected saves tokens on hard_v4.
Do not merge hard_v4 into hard_v2/hard_v3 synthesis without preserving the
separate boundary label.
```

### 58. Downstream Boundary Synthesis

Created:

```text
scripts/export_downstream_boundary_synthesis.py
benchmark/downstream/reports/downstream_boundary_synthesis.json
benchmark/downstream/reports/downstream_boundary_synthesis.md
benchmark/downstream/reports/downstream_boundary_synthesis.tex
```

What the file does:

```text
export_downstream_boundary_synthesis.py:
  reads the paper-facing hard_v2, hard_v3, and hard_v4 evidence packages and
  exports a three-boundary synthesis. It records comparable strategy rows,
  selected-vs-no_experience deltas, precondition/context deltas, forced-bad
  aggregate evidence, artifact-adherence caveats, source hashes, and explicit
  supported/unsupported claims.
```

Why it is needed:

```text
The older downstream_cross_version_synthesis remains the hard_v2/hard_v3
synthesis. hard_v4 should not overwrite it and should not be flattened into a
single leaderboard. The new boundary synthesis makes the current three-suite
paper story explicit:

hard_v2:
  conditional positive evidence

hard_v3:
  generalization boundary

hard_v4:
  stricter boundary and negative-transfer replication
```

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_downstream_boundary_synthesis.py \
  --assert-current-boundary-synthesis
```

Current export:

```text
primary_rows: 43
selected_comparisons: 6
context_comparisons: 9
forced_bad_total: 0/133
```

Selected versus no_experience:

```text
hard_v2 tree-aware:      25/25 vs 23/25, success_delta=+2, token_delta=+6049
hard_v2 strict visible:  23/25 vs 24/25, success_delta=-1, token_delta=+7336
hard_v3 tree-aware:      29/30 vs 29/30, success_delta=0,  token_delta=-917
hard_v3 strict visible:  29/30 vs 28/30, success_delta=+1, token_delta=-2763
hard_v4 tree-aware:      24/24 vs 24/24, success_delta=0,  token_delta=+1997
hard_v4 strict visible:  22/24 vs 24/24, success_delta=-2, token_delta=+5395
```

Context/precondition comparisons:

```text
tree-aware precondition context vs selected:
  hard_v2: success_delta=0, token_delta=+9907
  hard_v3: success_delta=0, token_delta=+5268
  hard_v4: success_delta=0, token_delta=+14904

strict precondition-only vs selected:
  hard_v2: success_delta=+1
  hard_v3: success_delta=+1
  hard_v4: success_delta=+1

strict precondition-only vs no_experience:
  hard_v2: success_delta=0
  hard_v3: success_delta=+2
  hard_v4: success_delta=-1
```

Forced-bad aggregate:

```text
hard_v2: 0/25
hard_v3: 0/60
hard_v4: 0/48
total:   0/133, public-pass/hidden-fail=133
```

Paper artifacts index was updated again:

```text
artifact_groups: 10
table_index: 7
claim_map: 10
forced_bad_total_tasks: 85
hard_v4_forced_bad_total_tasks: 48
boundary_forced_bad_total_tasks: 133
```

Interpretation:

```text
This is the cleanest current high-level downstream story. It deliberately
weakens any overbroad selected-wins claim. The paper should say that
SkillAdmit-selected is conditionally useful, not universally best; and that
downstream hidden verification is essential because harmful admitted artifacts
produce systematic negative transfer even when public tests pass.
```

Boundary:

```text
Do not tune hard_v2, hard_v3, or hard_v4 failures from this synthesis.
Do not use the boundary synthesis as a substitute for suite-specific evidence
packages.
Do not claim token savings or universal selected superiority.
```

### 59. Three-Boundary Paper Section and Claim Defense

Updated:

```text
scripts/export_downstream_paper_section.py
scripts/export_downstream_claim_defense_matrix.py
scripts/export_paper_artifacts_index.py
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

What changed:

```text
The paper-section exporter now reads downstream_boundary_synthesis.json instead
of the older hard_v2/hard_v3 cross-version synthesis. The draft section reports
hard_v2, hard_v3, and hard_v4 as separate downstream boundaries and keeps the
forced_bad_artifact aggregate at 0/133 with 133 public-pass/hidden-fail cases.

The claim-defense matrix now includes hard_v4 evidence rows and uses the
three-boundary synthesis for forced-bad aggregation and selected-token deltas.
It still exports 10 claims and 6 global red lines, but the red lines now cover
hard_v2, hard_v3, and hard_v4.

The paper artifacts index now maps paper-section and claim-defense support to
downstream_boundary_synthesis.json, and its paper_section_result_paragraphs
value is 6.
```

Current paper-section export:

```text
research_questions: 3
result_paragraphs: 6
claim_limits: 7
forced_bad_total_tasks: 133
```

Current claim-defense export:

```text
claim_count: 10
global_red_lines: 6
forced_bad: 0/133
public-pass/hidden-fail: 133
```

Current artifact index export:

```text
artifact_groups: 10
table_index: 7
claim_map: 10
forced_bad_total_tasks: 85
hard_v4_forced_bad_total_tasks: 48
boundary_forced_bad_total_tasks: 133
paper_section_result_paragraphs: 6
```

Interpretation:

```text
This round did not create new downstream evidence and did not tune any strategy.
It upgrades the reporting layer so the paper-facing text, claim-defense matrix,
and artifact index all use the same three-boundary story:

hard_v2:
  conditional positive evidence under tree-aware context

hard_v3:
  generalization boundary

hard_v4:
  stricter boundary against universal selected utility

forced_bad_artifact:
  strongest stable negative-transfer evidence, 0/133
```

Boundary:

```text
Do not use the generated paper section to strengthen claims beyond the evidence.
Do not replace suite-specific tables with the synthesis when exact numbers are
needed.
Do not tune hard_v2, hard_v3, or hard_v4 from this reporting pass.
```

### 60. Paper Claim Consistency Audit

Created:

```text
scripts/audit_paper_claim_consistency.py
benchmark/downstream/reports/paper_claim_consistency_audit.json
benchmark/downstream/reports/paper_claim_consistency_audit.md
benchmark/downstream/reports/paper_claim_consistency_audit.tex
```

What the file does:

```text
audit_paper_claim_consistency.py reads the current boundary synthesis,
paper-section export, claim-defense matrix, artifact index, selected report
Markdown files, README, and status docs. It checks whether the paper-facing
layer still tells the same hard_v2/hard_v3/hard_v4 downstream story.
```

Why it is needed:

```text
The current evidence is conditional. A paper draft can easily drift back to an
old 0/85 aggregate, a selected-wins claim, or a selected-token-savings claim.
The audit makes those failures executable checks instead of relying on manual
reading.
```

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/audit_paper_claim_consistency.py \
  --assert-current-audit
```

Current export:

```text
total_checks: 13
passed_checks: 13
failed_checks: 0
forced_bad_total_success: 0/133
forced_bad_total_public_passed_hidden_failed: 133
hard_v4_strict_selected: 22/24
hard_v4_strict_no_experience: 24/24
selected_superiority_consistent: False
selected_token_savings_consistent: False
```

Main checks:

```text
A1: boundary forced_bad aggregate is 0/133.
A2: paper section source is downstream_boundary_synthesis.json.
A3: paper derived values match boundary synthesis.
A4: claim-defense matrix still has the expected 10 claim cards.
A5: claim-defense source packages include hard_v2, hard_v3, hard_v4, boundary
    synthesis, and paper section.
A6: C6 uses hard_v4 + boundary synthesis, and C9 treats token savings as not
    supported.
A7: artifact-index facts match the three-boundary reporting layer.
A8: current report text contains the required three-boundary phrases.
A9: current boundary/paper/claim reports do not reuse the old 0/85 aggregate.
A10: no-universal-selected, no-token-savings, and no-retuning guardrails remain.
A11: hard_v4 is stated as a stricter boundary, not a selected win.
A12: all Markdown/docs inputs exist.
```

Artifact-index integration:

```text
The audit command is now included in the artifact-index regeneration order.
The audit report itself is marked as reporting hygiene, not primary empirical
evidence, to avoid confusing QA checks with downstream results.
```

Boundary:

```text
This audit is not new evidence.
Do not cite it as a model-performance result.
Use it before paper drafting or reviewer-response editing to catch claim drift.
```

### 61. Model-Transfer Replication Protocol

Created:

```text
scripts/export_model_transfer_replication_protocol.py
benchmark/downstream/reports/model_transfer_replication_protocol.json
benchmark/downstream/reports/model_transfer_replication_protocol.md
benchmark/downstream/reports/model_transfer_replication_protocol.tex
```

Updated:

```text
scripts/run_llm_downstream_validation.py
scripts/export_paper_artifacts_index.py
README.md
```

What the new script does:

```text
export_model_transfer_replication_protocol.py reads the current downstream
boundary synthesis and the paper-claim consistency audit, then exports a
predeclared protocol for running hard_v3 and hard_v4 with a second model. It
does not run API calls and does not inspect failure cases.
```

Why it is needed:

```text
The current downstream evidence comes from one main model/backend. The next
clean scientific step is model-transfer replication, not prompt tuning on
hard_v3 or hard_v4. The protocol freezes which suites, settings, strategies,
commands, stop rules, and claim boundaries are allowed before any transfer-model
outcome is observed.
```

Runner update:

```text
scripts/run_llm_downstream_validation.py now accepts:

--model
--base-url

This lets transfer runs use a second model without editing .env or overwriting
the baseline model setting. Existing default behavior still reads
SKILLADMIT_MODEL and OPENAI_BASE_URL from .env.
```

Current protocol export:

```text
protocol_id: model_transfer_replication_v0
run_specs: 4
expected_total_rows: 864
transfer_model_env: SKILLADMIT_TRANSFER_MODEL
baseline_model_label: mimo-v2.5-pro
```

Run matrix:

```text
MT1 hard_v3 tree-aware:          30 tasks x 8 strategies = 240 rows
MT2 hard_v3 strict visible-file: 30 tasks x 8 strategies = 240 rows
MT3 hard_v4 tree-aware:          24 tasks x 8 strategies = 192 rows
MT4 hard_v4 strict visible-file: 24 tasks x 8 strategies = 192 rows
```

Predeclared command shape:

```bash
SKILLADMIT_TRANSFER_MODEL=<second-model-id>

PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/export_model_transfer_replication_protocol.py \
  --model-slug <model_slug> \
  --transfer-model-expr '$SKILLADMIT_TRANSFER_MODEL' \
  --assert-current-protocol
```

Then run the four commands listed in:

```text
benchmark/downstream/reports/model_transfer_replication_protocol.md
```

Stop rules:

```text
Use --resume only to recover interrupted rows.
Do not selectively rerun failed rows.
Do not change prompts, strategies, task files, visible-file settings, repo-tree
settings, or hidden verifiers after seeing transfer-model outcomes.
If any adjustment is needed, create a new protocol id.
```

Claim boundary:

```text
Allowed after the run:
  report whether hard_v3/hard_v4 boundary patterns replicated, weakened, or
  reversed under the second model.

Forbidden after the run:
  do not claim model-general SkillAdmit-selected superiority from one transfer
  model.
  do not claim selected token savings without a separate cost-controlled
  protocol.
  do not treat the protocol itself as model-performance evidence.
```

### 62. Model-Transfer Evidence Package

Completed the predeclared mimo-v2.5 transfer matrix over frozen hard_v3 and
hard_v4. No hard_v3/hard_v4 prompt, task, strategy, artifact, or hidden-verifier
change was made from transfer-model outcomes.

Created:

```text
scripts/export_model_transfer_evidence_package.py
scripts/export_model_transfer_cross_model_synthesis.py
benchmark/downstream/reports/model_transfer_evidence_package.json
benchmark/downstream/reports/model_transfer_evidence_package.md
benchmark/downstream/reports/model_transfer_evidence_package.tex
benchmark/downstream/reports/model_transfer_cross_model_synthesis.json
benchmark/downstream/reports/model_transfer_cross_model_synthesis.md
benchmark/downstream/reports/model_transfer_cross_model_synthesis.tex
```

Transfer run directories:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v3_transfer_mimo_v2_5_tree_30x8
benchmark/downstream/llm_runs/llm_downstream_hard_v3_transfer_mimo_v2_5_strict_30x8
benchmark/downstream/llm_runs/llm_downstream_hard_v4_transfer_mimo_v2_5_tree_24x8
benchmark/downstream/llm_runs/llm_downstream_hard_v4_transfer_mimo_v2_5_strict_24x8
```

Transfer evidence facts:

```text
model: mimo-v2.5
total_rows: 864
parse_errors: 0
forced_bad_artifact: 0/108
forced_bad_public_passed_hidden_failed: 108

hard_v3 tree-aware selected vs no_experience: 29/30 vs 29/30, delta 0
hard_v3 strict selected vs no_experience: 29/30 vs 28/30, delta +1
hard_v4 tree-aware selected vs no_experience: 24/24 vs 23/24, delta +1
hard_v4 strict selected vs no_experience: 21/24 vs 18/24, delta +3
```

Cross-model synthesis facts:

```text
baseline model label: mimo-v2.5-pro
transfer model: mimo-v2.5
forced_bad combined across hard_v3/hard_v4 and both models: 0/216
public-pass/hidden-fail combined: 216

hard_v3 tree-aware selected tie replicated: yes
hard_v3 strict selected +1 replicated: yes
hard_v4 strict selected delta reversed:
  baseline: -2
  transfer: +3
```

Artifact-index status:

```text
artifact_groups: 12
table_index: 8
claim_map: 10
```

Interpretation:

```text
Strong replicated result:
  harmful forced artifacts still cause systematic negative transfer.

Model-sensitive result:
  SkillAdmit-selected is not a model-general win. The hard_v4 strict selected
  comparison reverses sign between the baseline model and mimo-v2.5.

Still unsupported:
  model-general selected superiority
  selected token savings
  precondition-only replacing repository context
  hard_v3/hard_v4 tuning from observed transfer failures
```

### 63. Model-Transfer Paper Addendum

Created a draftable model-transfer addendum layer. This is optional paper text
for reporting the second-model run; it does not replace the main hard_v2/hard_v3
/hard_v4 downstream section.

Created:

```text
scripts/export_model_transfer_paper_addendum.py
benchmark/downstream/reports/model_transfer_paper_addendum.json
benchmark/downstream/reports/model_transfer_paper_addendum.md
benchmark/downstream/reports/model_transfer_paper_addendum.tex
```

Updated:

```text
scripts/export_paper_artifacts_index.py
scripts/audit_paper_claim_consistency.py
README.md
docs/experiment_handoff.md
docs/paper_eval_status.md
```

Addendum export facts:

```text
result_paragraphs: 5
selected_sensitivity_rows: 4
forced_bad_combined_success: 0/216
hard_v4_strict_selected_delta_reversed: true
```

Reporting status:

```text
paper_artifacts_index:
  artifact_groups: 13
  table_index: 9
  claim_map: 10

paper_claim_consistency_audit:
  total_checks: 13
  status: pass
```

Boundary:

```text
Use the addendum to report model sensitivity and forced-bad replication.
Do not use it to claim model-general SkillAdmit-selected superiority.
Do not merge the addendum into the original 0/133 three-boundary aggregate.
```

### 64. Public Reporting Hygiene Audit

Added a public reporting hygiene audit to prevent aggregate and claim-boundary
drift across the now-overlapping report layers.

Created:

```text
scripts/audit_reporting_hygiene.py
benchmark/downstream/reports/reporting_hygiene_audit.json
benchmark/downstream/reports/reporting_hygiene_audit.md
benchmark/downstream/reports/reporting_hygiene_audit.tex
```

Updated:

```text
scripts/export_paper_artifacts_index.py
scripts/audit_paper_claim_consistency.py
README.md
docs/experiment_handoff.md
docs/paper_eval_status.md
```

Hygiene roles:

```text
0/85:
  historical hard_v2/hard_v3 synthesis only

0/133:
  current hard_v2/hard_v3/hard_v4 main downstream boundary

0/216:
  model-transfer hard_v3/hard_v4 replication/addendum layer
```

Current hygiene audit:

```text
total_checks: 8
passed_checks: 8
failed_checks: 0
status: pass
```

Artifact-index wording was corrected:

```text
G4_cross_version_synthesis is now labeled as historical two-boundary synthesis,
not the top-level downstream story.
```

### 65. Public Release Readiness Audit

Added a repository-level release audit for public push hygiene. This audit is
not empirical evidence; it checks whether the repo is safe and recoverable to
publish.

Created:

```text
scripts/audit_public_release_readiness.py
benchmark/downstream/reports/public_release_readiness_audit.json
benchmark/downstream/reports/public_release_readiness_audit.md
benchmark/downstream/reports/public_release_readiness_audit.tex
```

Current checks:

```text
R1: no dirty sensitive/local paths in git status
R2: .env, agent_runs, workspaces, and caches are ignored
R3: no forbidden tracked .env/cache/workspace/local-run paths
R4: no obvious tracked credential patterns
R5: no tracked file over 2,000,000 bytes
R6: artifact-index regeneration scripts exist
R7: docs state runtime secrets belong in ignored .env
```

Current result:

```text
total_checks: 7
passed_checks: 7
failed_checks: 0
status: pass
tracked_file_count: 1650
```

Release command tail:

```bash
python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index
python scripts/audit_paper_claim_consistency.py --assert-current-audit
python scripts/audit_reporting_hygiene.py --assert-current-hygiene
python scripts/audit_public_release_readiness.py --assert-current-release
```

### 66. Public Reproduction Guide Audit

Added a public-facing reproduction guide and an executable audit for it. This is
not new model evidence; it is the release entry point for rerunning deterministic
checks and keeping the public README aligned with the current downstream claim
boundary.

Created:

```text
docs/reproduction_guide.md
scripts/audit_reproduction_guide.py
benchmark/downstream/reports/reproduction_guide_audit.json
benchmark/downstream/reports/reproduction_guide_audit.md
benchmark/downstream/reports/reproduction_guide_audit.tex
```

The guide separates:

```text
0/85:
  historical hard_v2/hard_v3 synthesis only

0/133:
  current hard_v2/hard_v3/hard_v4 main downstream boundary

0/216:
  model-transfer hard_v3/hard_v4 addendum layer
```

Current audit:

```text
total_checks: 13
passed_checks: 13
failed_checks: 0
status: pass
```

The audit checks:

```text
README links docs/reproduction_guide.md
required regeneration commands are present and scripts exist
artifact index exposes the reproduction guide and guide audit command
the guide reports 0/133 and 0/216 from generated reports
the guide keeps the historical 0/85 layer separate
unsupported selected-superiority and token-savings claims are forbidden
hard_v2/hard_v3/hard_v4 no-retuning rule is present
.env and no-new-API boundaries are stated
README names the public reproduction guide, artifact index, main boundary, and transfer addendum
README exposes aggregate roles and unsupported-claim guardrails
README and reproduction guide avoid machine-specific absolute paths
```

Updated release command tail:

```bash
python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index
python scripts/audit_paper_claim_consistency.py --assert-current-audit
python scripts/audit_reporting_hygiene.py --assert-current-hygiene
python scripts/audit_public_release_readiness.py --assert-current-release
python scripts/audit_reproduction_guide.py --assert-current-reproduction-guide
```

### 67. README Public Reader Path

Strengthened the public README so a new reader does not need to infer the
project boundary from generated reports alone. This is a release/readability
change, not new empirical evidence.

Updated:

```text
README.md
scripts/audit_reproduction_guide.py
benchmark/downstream/reports/reproduction_guide_audit.json
benchmark/downstream/reports/reproduction_guide_audit.md
benchmark/downstream/reports/reproduction_guide_audit.tex
```

README now starts with these reader entry points:

```text
docs/reproduction_guide.md
benchmark/downstream/reports/paper_artifacts_index.md
benchmark/downstream/reports/downstream_boundary_synthesis.md
benchmark/downstream/reports/model_transfer_cross_model_synthesis.md
```

README also states the public aggregate roles:

```text
0/133:
  main hard_v2/hard_v3/hard_v4 downstream boundary

0/216:
  model-transfer hard_v3/hard_v4 addendum

0/85:
  historical hard_v2/hard_v3 synthesis
```

The reproduction-guide audit now includes README-specific checks:

```text
RG11_readme_names_reader_entry_points
RG12_readme_preserves_public_claim_boundary
RG13_public_surface_avoids_local_paths
```

Current result:

```text
total_checks: 13
passed_checks: 13
failed_checks: 0
status: pass
```

Important boundary:

```text
This does not change downstream evidence. It only makes the public entry path
harder to misread.
```

### 68. Public Surface Local Path Cleanup

Cleaned the public reproduction guide so it no longer contains machine-specific
absolute paths from the local development environment.

Updated:

```text
docs/reproduction_guide.md
scripts/audit_reproduction_guide.py
benchmark/downstream/reports/reproduction_guide_audit.json
benchmark/downstream/reports/reproduction_guide_audit.md
benchmark/downstream/reports/reproduction_guide_audit.tex
```

The guide now uses public-clone commands:

```bash
cd SkillAdmit
python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index
```

The reproduction-guide audit now rejects public-surface hits for:

```text
/home/
anaconda3/envs
workspace/skilladmit
skilladmit/bin/python
```

Current result:

```text
total_checks: 13
passed_checks: 13
failed_checks: 0
status: pass
```

Boundary:

```text
This is a public-release hygiene change only. It does not change any downstream
task, strategy, run, checker, or claim.
```
