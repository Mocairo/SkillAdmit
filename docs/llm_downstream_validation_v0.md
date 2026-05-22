# LLM Downstream Validation v0

Last updated: 2026-05-21

## 1. Purpose

This document records the first real LLM-based downstream validation runner for
SkillAdmit.

The goal is to move beyond deterministic patch functions and test whether a
coding LLM can use different experience artifact contexts while solving future
debug tasks.

This is still a smoke experiment, not the final downstream result.

## 2. Runner

Script:

```text
scripts/run_llm_downstream_validation.py
```

Purpose:

```text
Run an OpenAI-compatible chat model on downstream Python import/debug tasks,
inject strategy-specific artifact context, ask the model for a JSON patch,
apply the patch in an isolated workspace, and run the real verifier.
```

Inputs:

```text
benchmark/downstream/tasks/
benchmark/admission_samples/llm_coding_agent_v0_admission_samples.jsonl
.env
```

Outputs:

```text
benchmark/downstream/llm_runs/<run-name>/trajectories.jsonl
benchmark/downstream/llm_runs/<run-name>/summary.json
benchmark/downstream/llm_runs/<run-name>/report.md
```

Use the `skilladmit` conda environment when running this script:

```bash
conda activate skilladmit
cd /home/lijx/workspace/skilladmit
```

In this session, using base Python failed because the base environment inherited
a SOCKS proxy but did not have `socksio` installed. The `skilladmit` environment
worked.

## 3. Strategies Supported

```text
no_experience
raw_memory
promoted_rules
distilled_skills_all
skilladmit_selected
bad_dependency_rule
```

Strategy meanings:

```text
no_experience
  No prior artifact context.

raw_memory
  Raw retrieved experience cluster for the task's skill family.

promoted_rules
  Rule-style constraints derived from admitted artifacts.

distilled_skills_all
  All admitted distilled skills are provided; the model must choose.

skilladmit_selected
  Only the task-relevant SkillAdmit-selected skill is provided.

bad_dependency_rule
  Intentionally bad artifact: treat ModuleNotFoundError as a missing dependency.
```

## 4. Smoke Runs

The smoke runs used one downstream task from each template family:

```text
down_py_import_001  T1_unused_missing_import
down_py_import_006  T2_local_module_import
down_py_import_011  T3_script_relative_import
down_py_import_016  T4_cwd_sensitive_path
down_py_import_021  T5_package_internal_import
```

### Run 1

Command:

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

Output:

```text
benchmark/downstream/llm_runs/llm_downstream_v0_smoke_5x2/
```

Result:

```text
no_experience:       5/5 success_rate=1.000 negative_transfer=0 total_tokens=7789
skilladmit_selected: 5/5 success_rate=1.000 negative_transfer=0 total_tokens=8112
```

### Run 2

Command:

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

Output:

```text
benchmark/downstream/llm_runs/llm_downstream_v0_smoke_bad_raw_5x2/
```

Result:

```text
raw_memory:          5/5 success_rate=1.000 negative_transfer=0 total_tokens=8927
bad_dependency_rule: 5/5 success_rate=1.000 negative_transfer=0 total_tokens=11044
```

## 5. Interpretation

The runner works:

```text
real LLM calls succeeded
JSON patches parsed
patches were applied
verifiers ran
trajectory and summary files were written
```

But the smoke tasks are too easy for the current model:

```text
no_experience already solves 5/5
skilladmit_selected also solves 5/5 but uses slightly more tokens in this smoke
raw_memory solves 5/5
bad_dependency_rule solves 5/5 because the model ignores the bad rule on most
non-T1 tasks and applies a stub only where it happens to pass
```

Therefore, this smoke run does not show a success-rate gain from SkillAdmit
context. It shows that the LLM downstream runner is operational and that the
next downstream benchmark must be harder or more budget-constrained.

## 6. What This Does And Does Not Prove

It proves:

```text
The project can run real LLM downstream validation with artifact contexts.
The logging format captures model usage, latency, edits, parse errors, and
verifier outcomes.
```

It does not prove:

```text
SkillAdmit improves strong-model success rate on these easy tasks.
SkillAdmit reduces tokens in this smoke run.
Bad artifacts always cause negative transfer for strong models.
```

## 7. Recommended Next Step

Create a harder downstream suite where no-experience does not already solve all
tasks. Good options:

```text
larger repositories with distractor files
ambiguous errors requiring retrieval of the right prior artifact
tasks where the obvious local patch passes one test but fails hidden validation
token-budgeted prompts where artifact context replaces repository exploration
multi-step repairs where raw memory is too verbose but distilled skill is compact
```

Then run:

```text
no_experience
raw_memory
distilled_skills_all
skilladmit_selected
bad_dependency_rule
```

on the same tasks and compare:

```text
verifier success
token usage
latency
negative-transfer failures
parse errors
number of edited files
```

## 8. Follow-up Completed

The harder follow-up has been started:

```text
docs/llm_downstream_hard_v1.md
scripts/build_downstream_hard_v1_tasks.py
benchmark/downstream_hard_v1/tasks/
```

Hard v1 result:

```text
no_experience:       4/5 success_rate=0.800 negative_transfer=1
skilladmit_selected: 5/5 success_rate=1.000 negative_transfer=0
```

This is the first real LLM downstream run where no_experience is not already
perfect. It should be scaled to hard_v2 before being used as a central paper
claim.
