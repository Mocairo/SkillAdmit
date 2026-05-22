# LLM Downstream Hard v2

## 1. File Purpose

This document records the second harder downstream validation suite.

Related files:

```text
scripts/build_downstream_hard_v2_tasks.py
scripts/check_downstream_hard_v2_tasks.py
scripts/run_llm_downstream_validation.py
benchmark/downstream_hard_v2/tasks/
benchmark/downstream/llm_runs/llm_downstream_hard_v2_forced_bad_25/
benchmark/downstream/llm_runs/llm_downstream_hard_v2_canary_5x2/
```

`scripts/build_downstream_hard_v2_tasks.py` generates 25 downstream tasks:

```text
5 templates x 5 variants
```

Each task includes:

```text
visible_files
gold_like_edits
forced_bad_artifact_edits
hidden verifier checks
distractor files
```

`scripts/check_downstream_hard_v2_tasks.py` validates that every generated task
has the intended structure:

```text
initial task fails
gold-like repair passes
forced bad artifact passes public pytest
forced bad artifact fails hidden verifier
```

`scripts/run_llm_downstream_validation.py` now supports a deterministic
`forced_bad_artifact` strategy in addition to real LLM strategies.

## 2. Why Hard v2 Was Needed

Hard v1 showed the first useful real-LLM signal:

```text
no_experience:       4/5
skilladmit_selected: 5/5
```

But hard v1 was too small and did not create a reliable bad-artifact baseline.
The previous `bad_dependency_rule` condition was not harmful because the model
mostly ignored the bad artifact.

Hard v2 fixes that by separating two ideas:

```text
bad_dependency_rule
  A normal LLM condition where the model may ignore bad advice.

forced_bad_artifact
  A deterministic negative-transfer baseline where the bad artifact is applied.
```

This lets the benchmark ask a clean question:

```text
What happens if harmful experience is admitted and executed?
```

## 3. Task Families

Hard v2 contains 25 tasks:

```text
hard_v2_py_import_001-005  T1 unused missing import
hard_v2_py_import_006-010  T2 local module import
hard_v2_py_import_011-015  T3 script relative import
hard_v2_py_import_016-020  T4 cwd-sensitive path
hard_v2_py_import_021-025  T5 package-internal import
```

The hidden verifier rejects masking repairs such as:

```text
creating dependency stubs for unused imports
creating top-level modules for local package imports
creating top-level helpers for script/package import conflicts
duplicating data files under the current working directory
creating top-level packages for package-internal imports
```

## 4. Sanity Check

Command:

```bash
python scripts/build_downstream_hard_v2_tasks.py
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/check_downstream_hard_v2_tasks.py
```

Result:

```text
total: 25
initial_failed: 25
gold_passed: 25
forced_public_passed: 25
forced_verifier_failed: 25
```

This means every task is usable:

```text
the original task is broken
the intended repair works
the bad artifact is a real negative-transfer repair, not a syntax error
the bad artifact can fool public pytest but not hidden validation
```

## 5. Forced Bad Artifact Result

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/run_llm_downstream_validation.py \
  --run-name llm_downstream_hard_v2_forced_bad_25 \
  --tasks-dir benchmark/downstream_hard_v2/tasks \
  --use-task-visible-files \
  --strategy forced_bad_artifact
```

Result:

```text
forced_bad_artifact: 0/25
success_rate: 0.000
negative_transfer: 25
public_passed_hidden_failed: 25
total_tokens: 0
```

Interpretation:

```text
If a harmful artifact is admitted and executed, it creates systematic negative
transfer. This is a stronger negative-transfer control than the previous
bad_dependency_rule prompt condition.
```

## 6. Real LLM Canary

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/run_llm_downstream_validation.py \
  --run-name llm_downstream_hard_v2_canary_5x2 \
  --tasks-dir benchmark/downstream_hard_v2/tasks \
  --use-task-visible-files \
  --strategy no_experience \
  --strategy skilladmit_selected \
  --task-id hard_v2_py_import_001 \
  --task-id hard_v2_py_import_006 \
  --task-id hard_v2_py_import_011 \
  --task-id hard_v2_py_import_016 \
  --task-id hard_v2_py_import_021
```

Result:

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | total_tokens | avg_tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_experience | 4 | 5 | 0.800 | 1 | 1 | 12775 | 2555.0 |
| skilladmit_selected | 5 | 5 | 1.000 | 0 | 0 | 13840 | 2768.0 |

## 7. Important Failure Case

The no-experience failure was:

```text
task: hard_v2_py_import_016
template: T4_cwd_sensitive_path_hard
```

The model saw:

```text
tests/test_loader.py
runner_alpha/loader.py
runner_alpha/main.py
```

It created:

```text
runner_alpha/data/alpha.txt
```

That made public pytest pass, but hidden validation rejected the repair:

```text
AssertionError: duplicating data under cwd masks the path bug
```

With `skilladmit_selected`, the model used the cwd-sensitive path repair skill
and passed the hidden verifier.

## 8. Interpretation

Hard v2 is a useful improvement over hard v1:

```text
25 validated downstream tasks instead of 5
explicit gold-like edits
explicit forced bad-artifact edits
all forced bad artifacts create public-pass/hidden-fail negative transfer
real LLM canary still shows no_experience < skilladmit_selected
```

The honest claim is:

```text
Hard v2 provides a validated downstream task suite and a canary real-LLM result
showing that SkillAdmit-selected skill context can prevent at least one masking
repair under limited file context.
```

The current result should not yet be claimed as:

```text
full 25-task real LLM downstream superiority
token savings
general superiority over raw memory or promoted rules
```

## 9. Full Visible-File Run

The full run without repository tree context was completed:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v2_full_25x6/
```

Command pattern:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/run_llm_downstream_validation.py \
  --run-name llm_downstream_hard_v2_full_25x6 \
  --tasks-dir benchmark/downstream_hard_v2/tasks \
  --use-task-visible-files \
  --resume \
  --strategy <strategy>
```

Result:

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | total_tokens | avg_tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| distilled_skills_all | 25 | 25 | 1.000 | 0 | 0 | 84986 | 3399.4 |
| no_experience | 24 | 25 | 0.960 | 0 | 0 | 59272 | 2370.9 |
| skilladmit_selected | 23 | 25 | 0.920 | 2 | 0 | 66608 | 2664.3 |
| raw_memory | 22 | 25 | 0.880 | 3 | 0 | 56941 | 2277.6 |
| bad_dependency_rule | 22 | 25 | 0.880 | 2 | 0 | 75724 | 3029.0 |
| promoted_rules | 21 | 25 | 0.840 | 4 | 1 | 77858 | 3114.3 |
| forced_bad_artifact | 0 | 25 | 0.000 | 25 | 25 | 0 | 0.0 |

Important interpretation:

```text
In the strict visible-file setting, SkillAdmit-selected is not the best
condition. The strongest condition is distilled_skills_all, which gives the
model the whole skill library. This reaches 25/25 but costs the most tokens.

SkillAdmit-selected fails two T4 cwd-sensitive path tasks. The selected CWD
skill says to locate the target file, but the strict visible-file prompt hides
the repository tree, so the model sometimes anchors the path to the script
directory instead of the repository root.
```

This is a useful negative result:

```text
Selecting one skill is not enough if the executor lacks the context needed to
check that skill's preconditions.
```

## 10. Tree-Aware Full Run

A more realistic agent prompt was then tested by adding repository tree context:

```text
--include-repo-tree
```

Output:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v2_tree_25x2/
```

Result:

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | total_tokens | avg_tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_experience | 23 | 25 | 0.920 | 2 | 0 | 51548 | 2061.9 |
| skilladmit_selected | 25 | 25 | 1.000 | 0 | 0 | 57597 | 2303.9 |

Important interpretation:

```text
When the model receives a repository tree, SkillAdmit-selected reaches 25/25
and no_experience reaches 23/25. This suggests that the earlier selected-skill
failures were caused by insufficient file-location context, not by the admitted
skill being intrinsically bad.
```

The tree-aware no-experience failures were:

```text
hard_v2_py_import_011  T3 script relative import
hard_v2_py_import_016  T4 cwd-sensitive path
```

SkillAdmit-selected solved both.

## 11. Selected + Precondition Context Run

The next strategy was implemented in:

```text
scripts/run_llm_downstream_validation.py
```

New strategy:

```text
skilladmit_selected_with_precondition_context
```

This strategy provides:

```text
selected SkillAdmit skill
repository tree, automatically included for this strategy
skill-specific precondition and guardrail context
```

The guardrail context is intentionally compact. It tells the executor to classify
the failure before editing, use the repository tree before creating stubs or data
files, and apply skill-specific checks such as:

```text
cwd/path tasks:
  locate the real target data file before choosing a path anchor
  do not anchor merely to the script directory
  do not duplicate data under the current working directory

import tasks:
  distinguish local modules, package-internal modules, script-mode import
  failures, unused imports, and true external dependencies before editing
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

Output:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v2_selected_precondition_25/
```

Result:

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| skilladmit_selected_with_precondition_context | 25 | 25 | 1.000 | 0 | 0 | 25 | 0 | 67504 | 2700.2 |

By template:

| template | successes | tasks | total_tokens | avg_tokens |
| --- | ---: | ---: | ---: | ---: |
| T1_unused_missing_import_hard | 5 | 5 | 9326 | 1865.2 |
| T2_local_module_import_hard | 5 | 5 | 11986 | 2397.2 |
| T3_script_relative_import_hard | 5 | 5 | 19866 | 3973.2 |
| T4_cwd_sensitive_path_hard | 5 | 5 | 15243 | 3048.6 |
| T5_package_internal_import_hard | 5 | 5 | 11083 | 2216.6 |

Comparison:

```text
no_experience tree-aware:                      23/25, total_tokens=51548
skilladmit_selected tree-aware:                25/25, total_tokens=57597
skilladmit_selected_with_precondition_context: 25/25, total_tokens=67504
distilled_skills_all strict:                   25/25, total_tokens=84986
```

Interpretation:

```text
The selected+precondition strategy keeps the full 25/25 success result and stays
well below the all-skills token cost: 67504 vs 84986.

It does not improve raw success over ordinary tree-aware skilladmit_selected,
because ordinary tree-aware selected was already 25/25. It also costs more:
67504 vs 57597 tokens.

The evidence is therefore not "precondition context is cheaper than selected."
The sharper interpretation is: explicit precondition context preserves the 25/25
result while making the failure-prevention logic auditable, especially for T4
cwd-sensitive path anchoring. It buys prompt-level robustness and explanation at
additional token cost, while still being cheaper than giving all distilled skills.
```

## 12. Strict Precondition-Only Ablation

A stricter ablation was then added to separate the value of explicit
precondition text from the value of repository-tree context.

New strategy:

```text
skilladmit_selected_with_precondition_only
```

This strategy provides:

```text
selected SkillAdmit skill
skill-specific precondition and guardrail context
no automatic repository tree
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

Output:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v2_precondition_only_25/
```

Result:

| strategy | successes | tasks | success_rate | negative_transfer | public_passed_hidden_failed | artifact_adherence | parse_errors | total_tokens | avg_tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| skilladmit_selected_with_precondition_only | 24 | 25 | 0.960 | 1 | 0 | 25 | 0 | 72316 | 2892.6 |

By template:

| template | successes | tasks | total_tokens | avg_tokens |
| --- | ---: | ---: | ---: | ---: |
| T1_unused_missing_import_hard | 5 | 5 | 10064 | 2012.8 |
| T2_local_module_import_hard | 5 | 5 | 14947 | 2989.4 |
| T3_script_relative_import_hard | 4 | 5 | 16284 | 3256.8 |
| T4_cwd_sensitive_path_hard | 5 | 5 | 17928 | 3585.6 |
| T5_package_internal_import_hard | 5 | 5 | 13093 | 2618.6 |

Failure:

```text
hard_v2_py_import_012
template: T3_script_relative_import_hard
```

The model correctly diagnosed script-mode execution but left the module-level
relative import at the top of the file:

```text
from .tools import format_value
```

It then added fallback import logic inside `if __name__ == "__main__"`, but that
block is never reached because the module-level relative import fails first.

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
The first precondition-only run improved the strict visible-file setting from
23/25 to 24/25 and solved all five T4 cwd-sensitive path tasks without seeing a
repository tree. That is a first-run observation, not a stable conclusion: the
replication dropped to 23/25 and failed one T4 cwd-sensitive path task
(`hard_v2_py_import_018`) in addition to the recurring T3 import failure.

Therefore explicit guardrails alone are not a clean substitute for
repository-tree context. The ablation does not reach 25/25, costs more than
ordinary strict selected, costs more than tree-aware selected, and is less
stable across repeated calls.

The useful mechanism claim is narrower: precondition text can partially repair
the missing-context problem, especially for cwd/path anchoring, but the best
current compact condition remains tree-aware skilladmit_selected.
```

## 13. Hard v2 Strategy Matrix

A persistent hard_v2 matrix report was added so the current evidence is not
confused with whichever `summary.json` happens to be open in the editor.

Script:

```text
scripts/summarize_hard_v2_results.py
```

What the file does:

```text
Reads hard_v2 run directories, aggregates strategy/template/failure rows, records
source-file SHA-256 hashes for each summary and trajectory file, and writes a
paper-facing matrix report.
```

Why it is needed:

```text
Individual run directories rewrite summary.json whenever the same run-name is
resumed or rerun. The matrix report makes the complete hard_v2 evidence table
explicit and records source hashes so accidental changes are detectable.
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
Researchers or Codex sessions after any hard_v2 run is added, resumed, or
recomputed.
```

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/summarize_hard_v2_results.py \
  --assert-current-hard-v2
```

Current matrix size after stability replications:

```text
runs: 9
strategy_rows: 17
template_rows: 85
failures: 69
```

Important current matrix rows:

```text
strict_visible_file / skilladmit_selected:               23/25, tokens=66608
tree_aware / skilladmit_selected:                        25/25, tokens=57597
strict_precondition_only / selected+precondition-only:   24/25, tokens=72316
tree_aware_precondition_context / selected+precondition: 25/25, tokens=67504
strict_visible_file / distilled_skills_all:              25/25, tokens=84986
forced_bad_standalone / forced_bad_artifact:              0/25, public_hidden=25
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

The report is a ledger, not a new model run. It should be regenerated after
future hard_v2 experiments.

## 14. Current Claim Boundary

Reasonable claims:

```text
Hard v2 is now a 25-task downstream suite with validated hidden-verifier
negative-transfer controls.

Forced harmful artifacts create systematic public-pass/hidden-fail negative
transfer: 0/25 success, 25/25 negative transfer.

In a tree-aware setting closer to a real coding agent, SkillAdmit-selected
outperforms no_experience on hard_v2: 25/25 vs 23/25.

The selected+precondition variant also reaches 25/25 and makes the path/import
preconditions explicit while using fewer tokens than the all-skills condition.

The strict precondition-only ablation is weaker and less stable than tree-aware
selected: observed runs were 24/25 and 23/25, with failures in T3 script-mode
relative import and sometimes T4 cwd-sensitive path handling.

In the strict visible-file setting, giving all distilled skills reaches 25/25
but costs more tokens than no_experience or SkillAdmit-selected.
```

Claims that should not be made:

```text
SkillAdmit-selected dominates all baselines in every prompt setting.
SkillAdmit-selected reduces token cost in hard_v2.
Precondition context is empirically more accurate than ordinary tree-aware
selected; both are 25/25 on this run.
Precondition-only is enough to replace repository-tree context.
Rules-only context is enough.
Raw memory is reliably better than no experience.
```

## 15. Next Step

The next scientific step is not more admission-controller tuning. The downstream
story should now be reported as four executor settings:

```text
strict visible-file setting
strict visible-file + precondition-only ablation
tree-aware coding-agent setting
tree-aware selected skill with explicit precondition context
```

For a paper, report all four:

```text
strict setting:
  distilled_skills_all is strongest but expensive
  selected-only can fail when precondition context is hidden

precondition-only strict setting:
  sometimes improves selected-only, but replication drops to 23/25 and shows it
  does not replace file-tree context

tree-aware setting:
  skilladmit_selected beats no_experience, 25/25 vs 23/25

selected+precondition setting:
  matches 25/25, costs less than all-skills, but costs more than ordinary
  tree-aware selected
```

Remaining useful follow-up:

```text
repeat the selected+precondition run with another model or seed if variance
evidence is needed; do not tune the admission controller from these downstream
outcomes
```
