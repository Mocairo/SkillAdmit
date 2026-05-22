# LLM Downstream Hard v1

## 1. File Purpose

This document records the first harder real-LLM downstream validation run.

Related files:

```text
scripts/build_downstream_hard_v1_tasks.py
scripts/run_llm_downstream_validation.py
benchmark/downstream_hard_v1/tasks/
benchmark/downstream/llm_runs/llm_downstream_hard_v1_smoke_5x2/
benchmark/downstream/llm_runs/llm_downstream_hard_v1_extra_5x4/
```

`scripts/build_downstream_hard_v1_tasks.py` creates five harder future
Python import/debug tasks. Its input is the fixed task design in the script.
Its output is `benchmark/downstream_hard_v1/tasks/`.

`scripts/run_llm_downstream_validation.py` runs a real OpenAI-compatible model
on downstream tasks. For hard v1, it now supports:

```text
--tasks-dir
--use-task-visible-files
--max-files
```

These options make it possible to evaluate a different task directory and show
the model only the files declared by each task.

## 2. Why Hard v1 Was Needed

The earlier LLM downstream smoke test was too easy:

```text
no_experience:       5/5
skilladmit_selected: 5/5
raw_memory:          5/5
bad_dependency_rule: 5/5
```

That result proved the runner worked, but it did not prove that SkillAdmit
artifacts improve future task performance.

Hard v1 makes the downstream setting sharper by using:

```text
budgeted visible files
hidden verifier checks
distractor files
tasks where an obvious patch can pass public tests but fail hidden validation
```

## 3. Task Design

Hard v1 contains five tasks:

```text
hard_py_import_001  T2 local module import
hard_py_import_002  T3 script relative import
hard_py_import_003  T4 cwd-sensitive path
hard_py_import_004  T5 package-internal import
hard_py_import_005  T1 unused missing import
```

Sanity check:

```text
initial_passed: 0/5
initial_failed: 5/5
gold_like_repairs_passed: 5/5
```

This means the generated tasks fail before repair and can pass with the intended
repair.

## 4. Commands

Generate tasks:

```bash
python scripts/build_downstream_hard_v1_tasks.py
```

Run the main comparison:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/run_llm_downstream_validation.py \
  --run-name llm_downstream_hard_v1_smoke_5x2 \
  --tasks-dir benchmark/downstream_hard_v1/tasks \
  --use-task-visible-files \
  --strategy no_experience \
  --strategy skilladmit_selected \
  --task-id hard_py_import_001 \
  --task-id hard_py_import_002 \
  --task-id hard_py_import_003 \
  --task-id hard_py_import_004 \
  --task-id hard_py_import_005
```

Run the additional artifact conditions:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/run_llm_downstream_validation.py \
  --run-name llm_downstream_hard_v1_extra_5x4 \
  --tasks-dir benchmark/downstream_hard_v1/tasks \
  --use-task-visible-files \
  --strategy raw_memory \
  --strategy promoted_rules \
  --strategy distilled_skills_all \
  --strategy bad_dependency_rule \
  --task-id hard_py_import_001 \
  --task-id hard_py_import_002 \
  --task-id hard_py_import_003 \
  --task-id hard_py_import_004 \
  --task-id hard_py_import_005
```

## 5. Results

| strategy | successes | tasks | success_rate | negative_transfer | total_tokens | avg_tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| no_experience | 4 | 5 | 0.800 | 1 | 9530 | 1906.0 |
| skilladmit_selected | 5 | 5 | 1.000 | 0 | 15903 | 3180.6 |
| raw_memory | 5 | 5 | 1.000 | 0 | 13140 | 2628.0 |
| promoted_rules | 5 | 5 | 1.000 | 0 | 16218 | 3243.6 |
| distilled_skills_all | 5 | 5 | 1.000 | 0 | 17515 | 3503.0 |
| bad_dependency_rule | 5 | 5 | 1.000 | 0 | 13923 | 2784.6 |

## 6. Important Failure Case

The meaningful failure is:

```text
strategy: no_experience
task: hard_py_import_004
template: T5_package_internal_import_hard
```

The model only saw:

```text
tests/test_main.py
omega_pkg/main.py
```

Without prior experience, it created a top-level `adapters/` package. This made
the public pytest test pass, but the hidden verifier rejected it:

```text
AssertionError: top-level package masks the package-internal import bug
```

With `skilladmit_selected`, the model used the package-internal import skill and
changed `omega_pkg/main.py` to use a relative import:

```text
from .adapters.worker import work
```

This passed the hidden verifier.

## 7. Interpretation

Hard v1 is stronger than the earlier downstream smoke:

```text
no_experience is no longer perfect
skilladmit_selected fixes the case where the bare model makes a masking stub
the runner can evaluate hidden-verifier behavior under limited file context
```

But this is still not paper-grade final evidence:

```text
only five hard tasks
only one no-experience failure
raw_memory, promoted_rules, and all-skills are also 5/5
bad_dependency_rule is not harmful here because the model ignored it
```

Therefore the honest claim is:

```text
Hard v1 provides the first real-LLM downstream signal that selected admitted
skills can prevent a plausible but invalid repair under limited context.
```

It should not be claimed as:

```text
SkillAdmit broadly beats all baselines.
SkillAdmit reliably reduces token cost.
The bad dependency artifact causes negative transfer in this LLM setting.
```

## 8. Next Step

The next useful step is to scale hard downstream validation, not to tune the
admission controller.

Recommended next version:

```text
hard_v2 with 25 tasks
5 templates x 5 variants
same hidden-verifier idea
same visible-file budget
at least 2-3 cases where no_experience tends to create masking stubs
an artifact-following bad baseline that is forced to apply the bad artifact
```

After hard_v2, run:

```text
no_experience
skilladmit_selected
raw_memory
promoted_rules
distilled_skills_all
forced_bad_artifact
```

Only after hard_v2 should smaller or weaker models be used as a sensitivity
analysis.
