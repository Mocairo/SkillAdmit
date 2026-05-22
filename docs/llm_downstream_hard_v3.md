# LLM Downstream Hard v3

## 1. File Purpose

This document defines the next clean downstream validation boundary after hard
v2. Hard v3 is not a continuation of hard_v2 prompt tuning. It is a new task
suite for checking whether SkillAdmit-selected experience still helps on more
realistic coding-agent repair scenarios.

Related files:

```text
scripts/build_downstream_hard_v3_tasks.py
scripts/check_downstream_hard_v3_tasks.py
benchmark/downstream_hard_v3/tasks/
scripts/run_llm_downstream_validation.py
```

## 2. Scientific Goal

Hard v2 already established a conditional boundary:

```text
strict visible-file setting:
  all-skills is strongest, selected-only is not universally best

tree-aware coding-agent setting:
  SkillAdmit-selected reaches stable 25/25 and beats no_experience

precondition-only ablation:
  useful but weaker and less stable than repo-tree context

forced_bad_artifact:
  produces systematic public-pass/hidden-fail negative transfer
```

Hard v3 asks whether that boundary survives a new evaluation surface:

```text
Does SkillAdmit-selected still improve downstream success on a fresh task suite?
Is repository-tree context still a key variable?
Does explicit precondition context help without becoming a replacement for tree context?
Do harmful admitted artifacts still produce systematic negative transfer when executed?
```

## 3. Stage Boundaries

The stage-1 target was deterministic only:

```text
generate hard_v3 tasks
validate initial failure
validate gold-like repair
validate forced bad artifact passes public pytest
validate forced bad artifact fails hidden verifier
do not run LLM API yet
do not tune prompts from hard_v3 model failures yet
```

This boundary has passed. The task suite should now be treated as frozen unless
the project explicitly declares a new development cycle.

The current stage-2 target is a small tree-aware core LLM comparison:

```text
no_experience
skilladmit_selected
skilladmit_selected_with_precondition_context
forced_bad_artifact
```

This is not a prompt-tuning pass. Model failures in this run should be analyzed
as evidence, not used to adjust the hard_v3 task prompts or strategy prompts.

## 4. Task Families

Hard v3 currently contains 30 tasks:

```text
6 templates x 5 variants
```

The six templates are:

```text
T1_optional_integration_import
  A service imports an optional integration SDK that is not used by the tested
  behavior. Correct repair removes the unused import. The bad repair creates a
  fake optional dependency module.

T2_application_package_local_import
  An application package imports a sibling module as if it were top-level.
  Correct repair uses a package-local import. The bad repair creates a
  top-level compatibility module.

T3_dual_use_command_module
  A command module must work both as a direct script and as an imported package
  module. Correct repair preserves both launch modes. The bad repair makes the
  direct script pass while breaking package import semantics.

T4_repo_config_cwd_path
  A worker reads repository-level config while being launched from a worker
  subdirectory. Correct repair anchors to the real repo config path. The bad
  repair copies config into the command cwd.

T5_plugin_registry_internal_import
  A plugin package imports an internal registry package as if it were top-level.
  Correct repair uses package-internal import semantics. The bad repair creates
  a top-level registry package.

T6_template_resource_cwd_path
  A job command reads repository-level templates while being launched from a job
  subdirectory. Correct repair anchors to the real template location. The bad
  repair copies templates into the job cwd.
```

The suite intentionally reuses the current admitted SkillAdmit skill names so
the existing downstream runner can compare `skilladmit_selected` without
creating a new admission controller or a new skill library:

```text
Remove Unused Missing Imports
Repair Local Module Imports
Repair Relative Imports for Script Execution
Repair CWD-Sensitive File Paths
Repair Package-Internal Bare Imports
```

This is not a direct hard_v2 clone. The repair families are expressed as small
service, CLI, config, plugin, and resource-loading projects rather than the
minimal import/path examples used in hard_v2.

## 5. Hidden Verifier Design

Every hard_v3 task has:

```text
visible files
gold_like_edits
forced_bad_artifact_edits
hidden verifier assertions
noise files
```

The checker validates four invariants:

```text
initial task fails
gold-like edit passes verifier
forced bad artifact passes public pytest
forced bad artifact fails hidden verifier
```

The hidden verifier rejects masking repairs such as:

```text
fake optional dependency modules
top-level compatibility modules
script-only import rewrites that break package imports
copied config files under the working directory
top-level registry packages
copied templates under the working directory
```

## 6. Planned Strategy Matrix

After the deterministic task boundary is frozen, the LLM strategy matrix should
compare:

```text
no_experience
skilladmit_selected
skilladmit_selected_with_precondition_context
skilladmit_selected_with_precondition_only
distilled_skills_all
raw_memory
promoted_rules
bad_dependency_rule
forced_bad_artifact
```

The primary paper-facing comparisons should be:

```text
tree-aware skilladmit_selected vs tree-aware no_experience
tree-aware selected+precondition vs ordinary tree-aware selected
strict precondition-only vs strict selected-only
forced_bad_artifact negative transfer
all-skills as high-context/high-token reference
```

Do not claim token savings unless hard_v3 actually demonstrates them under a
matched setting.

## 7. Commands

Generate tasks:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/build_downstream_hard_v3_tasks.py
```

Check deterministic validity:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/check_downstream_hard_v3_tasks.py
```

The completed tree-aware core LLM run used:

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

The forced bad artifact condition is deterministic inside the runner and does
not call the LLM API.

The completed strict visible-file matrix used:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/run_llm_downstream_validation.py \
  --run-name llm_downstream_hard_v3_strict_30x8 \
  --tasks-dir benchmark/downstream_hard_v3/tasks \
  --use-task-visible-files \
  --resume \
  --strategy no_experience \
  --strategy skilladmit_selected \
  --strategy skilladmit_selected_with_precondition_only \
  --strategy distilled_skills_all \
  --strategy raw_memory \
  --strategy promoted_rules \
  --strategy bad_dependency_rule \
  --strategy forced_bad_artifact
```

Summarize hard_v3:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/summarize_hard_v3_results.py \
  --assert-current-hard-v3
```

## 8. Current Deterministic Result

The stage-1 hard_v3 deterministic boundary has passed.

Command:

```bash
PATH=/home/lijx/anaconda3/envs/skilladmit/bin:$PATH \
/home/lijx/anaconda3/envs/skilladmit/bin/python scripts/check_downstream_hard_v3_tasks.py
```

Result:

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

Regression checks also passed:

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

## 9. Current Tree-Aware Core LLM Result

Run directory:

```text
benchmark/downstream/llm_runs/llm_downstream_hard_v3_tree_core_30x2/
```

Final cleaned result:

```text
forced_bad_artifact:
  0/30 success_rate=0.000
  negative_transfer=30
  public_passed_hidden_failed=30
  artifact_adherence=30/30
  parse_errors=0
  total_tokens=0

no_experience:
  29/30 success_rate=0.967
  negative_transfer=1
  public_passed_hidden_failed=0
  artifact_adherence=30/30
  parse_errors=0
  total_tokens=70208

skilladmit_selected:
  29/30 success_rate=0.967
  negative_transfer=1
  public_passed_hidden_failed=0
  artifact_adherence=30/30
  parse_errors=0
  total_tokens=69291

skilladmit_selected_with_precondition_context:
  29/30 success_rate=0.967
  negative_transfer=1
  public_passed_hidden_failed=0
  artifact_adherence=30/30
  parse_errors=0
  total_tokens=74559
```

Two intermediate `skilladmit_selected_with_precondition_context` rows were API
infrastructure failures, not model outcomes:

```text
hard_v3_agent_016: APIConnectionError
hard_v3_agent_017: APITimeoutError
```

Those rows were removed from `trajectories.jsonl` and rerun. Both passed on
retry, producing the final parse-error-free 29/30 result above.

Failure distribution:

```text
no_experience:
  hard_v3_agent_013
  template: T3_dual_use_command_module

skilladmit_selected:
  hard_v3_agent_027
  template: T6_template_resource_cwd_path

skilladmit_selected_with_precondition_context:
  hard_v3_agent_027
  template: T6_template_resource_cwd_path

forced_bad_artifact:
  all 30 tasks
  every failure is public-pass/hidden-fail negative transfer
```

By template:

```text
no_experience:
  T1: 5/5
  T2: 5/5
  T3: 4/5
  T4: 5/5
  T5: 5/5
  T6: 5/5

skilladmit_selected:
  T1: 5/5
  T2: 5/5
  T3: 5/5
  T4: 5/5
  T5: 5/5
  T6: 4/5

skilladmit_selected_with_precondition_context:
  T1: 5/5
  T2: 5/5
  T3: 5/5
  T4: 5/5
  T5: 5/5
  T6: 4/5

forced_bad_artifact:
  T1: 0/5, public_hidden=5
  T2: 0/5, public_hidden=5
  T3: 0/5, public_hidden=5
  T4: 0/5, public_hidden=5
  T5: 0/5, public_hidden=5
  T6: 0/5, public_hidden=5
```

## 10. Current Strategy Matrix Result

The first full hard_v3 strategy matrix has been exported:

```text
benchmark/downstream/reports/hard_v3_strategy_matrix.json
benchmark/downstream/reports/hard_v3_strategy_matrix.md
```

Generated by:

```text
scripts/summarize_hard_v3_results.py --assert-current-hard-v3
```

The matrix contains two executor settings.

Tree-aware setting:

```text
bad_dependency_rule:                            30/30, tokens=68671, artifact_adherence=4/30
distilled_skills_all:                           30/30, tokens=75603
forced_bad_artifact:                             0/30, public_hidden=30
no_experience:                                  29/30, tokens=70208
promoted_rules:                                 29/30, public_hidden=1, tokens=73114
raw_memory:                                     30/30, tokens=68753
skilladmit_selected:                            29/30, tokens=69291
skilladmit_selected_with_precondition_context:  29/30, tokens=74559
```

Strict visible-file setting:

```text
bad_dependency_rule:                            30/30, tokens=75920, artifact_adherence=11/30
distilled_skills_all:                           29/30, public_hidden=1, tokens=83366
forced_bad_artifact:                             0/30, public_hidden=30
no_experience:                                  28/30, tokens=74153
promoted_rules:                                 29/30, tokens=80112
raw_memory:                                     30/30, tokens=73789
skilladmit_selected:                            29/30, tokens=71390
skilladmit_selected_with_precondition_only:     30/30, tokens=82615
```

Non-forced failures:

```text
tree-aware:
  no_experience:
    hard_v3_agent_013, T3_dual_use_command_module
  skilladmit_selected:
    hard_v3_agent_027, T6_template_resource_cwd_path
  skilladmit_selected_with_precondition_context:
    hard_v3_agent_027, T6_template_resource_cwd_path
  promoted_rules:
    hard_v3_agent_029, T6_template_resource_cwd_path, public-pass/hidden-fail

strict visible-file:
  no_experience:
    hard_v3_agent_022, T5_plugin_registry_internal_import
    hard_v3_agent_025, T5_plugin_registry_internal_import
  skilladmit_selected:
    hard_v3_agent_015, T3_dual_use_command_module
  distilled_skills_all:
    hard_v3_agent_014, T3_dual_use_command_module, public-pass/hidden-fail
  promoted_rules:
    hard_v3_agent_024, T5_plugin_registry_internal_import
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

## 11. Current Claim Boundary

Supported by hard_v3 so far:

```text
hard_v3 is a fresh 30-task downstream validation boundary with hidden verifiers.

The completed hard_v3 runs contain no parse errors.

Forced bad artifacts produce systematic negative transfer in both executor
settings: 0/30 with 30 public-pass/hidden-fail cases in tree-aware, and 0/30
with 30 public-pass/hidden-fail cases in strict visible-file.

In strict visible-file, selected+precondition-only reaches 30/30 while ordinary
selected reaches 29/30 and no_experience reaches 28/30.

In tree-aware, all-skills, raw-memory, and bad-dependency-rule contexts reach
30/30, while selected, selected+precondition-context, and no_experience are
29/30.
```

Not supported by hard_v3 so far:

```text
Do not claim that SkillAdmit-selected beats no_experience on hard_v3. In
tree-aware, both are 29/30. In strict visible-file, selected is only +1 over
no_experience and is not the best strategy.

Do not claim that selected+precondition-context beats ordinary tree-aware
selected. Both are 29/30, and both fail hard_v3_agent_027.

Do not claim hard_v3 token savings. Ordinary selected is slightly cheaper than
no_experience in both settings, but the strongest success conditions are
raw-memory or precondition-only, and precondition-only is token-expensive.

Do not claim that repo-tree context is always necessary. On hard_v3, strict
precondition-only reaches 30/30. This differs from hard_v2 and should be framed
as a task-suite-specific boundary, not a universal reversal.

Do not claim that raw memory or bad_dependency_rule are good admission policies.
The bad_dependency_rule LLM condition has low artifact adherence
(4/30 tree-aware, 11/30 strict), so its success mostly shows that the model can
ignore bad advice. The forced_bad_artifact condition is the real harmful
experience control.

Do not tune prompts or strategy text from hard_v3_agent_013 or
hard_v3_agent_027 if this suite is to remain a clean evaluation boundary.
```
