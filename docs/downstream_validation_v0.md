# Downstream Validation v0

Last updated: 2026-05-21

## 1. Purpose

This document records the first executable downstream validation for SkillAdmit.

The goal is to test whether admitted artifacts help solve future tasks, not just
whether the admission controller matches labels.

This is a controlled proxy experiment:

```text
real generated Python import/debug tasks
real pytest verifiers
deterministic strategy runners
no LLM calls
```

It is useful as an engineering check, but it is not the final paper-grade
downstream experiment.

## 2. New Code Files

Task generator:

```text
scripts/build_downstream_py_import_tasks.py
```

Purpose:

```text
Generate 25 future Python import/debug tasks under benchmark/downstream/tasks/.
There are 5 tasks for each template family.
```

Strategy runner:

```text
scripts/run_downstream_validation.py
```

Purpose:

```text
Run multiple artifact-use strategies on the downstream tasks, execute verifiers,
and write detailed and summarized results.
```

## 3. Generated Tasks

Output directory:

```text
benchmark/downstream/tasks/
```

Task count:

```text
25 tasks
5 T1_unused_missing_import
5 T2_local_module_import
5 T3_script_relative_import
5 T4_cwd_sensitive_path
5 T5_package_internal_import
```

Initial sanity check:

```text
initial_passed: 0
initial_failed: 25
```

All downstream tasks fail before artifact use, as intended.

## 4. Compared Strategies

The runner compares:

```text
no_experience
bad_dependency_stub
raw_memory_replay
promoted_rule_only
distilled_skill
skilladmit_selected
```

Strategy meanings:

```text
no_experience
  Runs verifier without applying an experience artifact.

bad_dependency_stub
  Negative-transfer baseline for the bad rule "treat missing module as
  dependency"; it creates a top-level stub for missing module names.

raw_memory_replay
  Replays exact old edits from previous trajectories without abstraction.

promoted_rule_only
  Provides only constraints/guardrails and no concrete repair procedure.

distilled_skill
  Applies generalized template-level repair procedures.

skilladmit_selected
  Selects the admitted distilled skill for the task family and applies it.
```

## 5. Commands

Generate downstream tasks:

```bash
python scripts/build_downstream_py_import_tasks.py
```

Run validation:

```bash
python scripts/run_downstream_validation.py
```

Outputs:

```text
benchmark/downstream/results/downstream_validation_v0.jsonl
benchmark/downstream/results/downstream_validation_v0_summary.json
benchmark/downstream/results/downstream_validation_v0_report.md
```

## 6. Result

Summary:

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
Raw trace replay does not transfer to renamed future tasks.
Rule-only artifacts are useful constraints but not complete repair procedures.
The overgeneralized dependency baseline transfers badly and creates failures.
Distilled skills transfer cleanly in this controlled task family.
SkillAdmit-selected artifacts match the distilled-skill result because all
current positive LLM clusters are skill-level artifacts.
```

## 7. Caveat

This is a deterministic proxy, not a final downstream LLM-agent result.

It proves that the benchmark can execute artifact-use comparisons end to end,
but a paper should eventually run an LLM coding agent with artifact context and
measure:

```text
verifier success
tokens used
actions used
negative-transfer failures
time or latency
```

The next stronger experiment should compare the same strategies with a real LLM
runner rather than deterministic patch functions.
