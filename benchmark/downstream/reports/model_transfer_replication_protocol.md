# Model-Transfer Replication Protocol

Generated at UTC: `2026-05-23T08:33:58.683890+00:00`

Protocol ID: `model_transfer_replication_v0`

Predeclare the next clean downstream validation boundary: replicate the frozen hard_v3/hard_v4 matrices with a second model, without tuning prompts, strategies, task files, or hidden verifiers from observed failures.

## Frozen Current Boundary

| fact | value |
| --- | --- |
| forced_bad_total_success | 0/133 |
| forced_bad_total_tasks | 133 |
| forced_bad_total_public_passed_hidden_failed | 133 |
| selected_superiority_consistent | False |
| selected_token_savings_consistent | False |
| hard_v4_strict_selected_delta_vs_no_experience | -2 |

## Transfer Model

| field | value |
| --- | --- |
| environment_variable | SKILLADMIT_TRANSFER_MODEL |
| model_expression | $SKILLADMIT_TRANSFER_MODEL |
| model_slug | mimo_v2_5 |
| must_differ_from_baseline | True |
| baseline_model_label | mimo-v2.5-pro |

## Prerequisites

- Run paper claim consistency audit and require 12/12 checks passing.
- Choose one transfer model before starting; record its exact provider model id.
- Set SKILLADMIT_TRANSFER_MODEL or pass --model explicitly; do not overwrite baseline evidence.
- Run hard_v3 and hard_v4 deterministic checkers before any model calls.
- Do not inspect failures to change prompts, artifacts, strategies, or tasks.

## Run Matrix

Expected total rows: `864`

| run | suite | setting | rows | run_name | command |
| --- | --- | --- | --- | --- | --- |
| MT1_hard_v3_tree | hard_v3 | tree-aware | 240 | `llm_downstream_hard_v3_transfer_mimo_v2_5_tree_30x8` | `python scripts/run_llm_downstream_validation.py --model "$SKILLADMIT_TRANSFER_MODEL" --run-name llm_downstream_hard_v3_transfer_mimo_v2_5_tree_30x8 --tasks-dir benchmark/downstream_hard_v3/tasks --strategy no_experience --strategy skilladmit_selected --strategy skilladmit_selected_with_precondition_context --strategy raw_memory --strategy distilled_skills_all --strategy promoted_rules --strategy bad_dependency_rule --strategy forced_bad_artifact --use-task-visible-files --include-repo-tree --resume` |
| MT2_hard_v3_strict | hard_v3 | strict visible-file | 240 | `llm_downstream_hard_v3_transfer_mimo_v2_5_strict_30x8` | `python scripts/run_llm_downstream_validation.py --model "$SKILLADMIT_TRANSFER_MODEL" --run-name llm_downstream_hard_v3_transfer_mimo_v2_5_strict_30x8 --tasks-dir benchmark/downstream_hard_v3/tasks --strategy no_experience --strategy skilladmit_selected --strategy skilladmit_selected_with_precondition_only --strategy raw_memory --strategy distilled_skills_all --strategy promoted_rules --strategy bad_dependency_rule --strategy forced_bad_artifact --use-task-visible-files --resume` |
| MT3_hard_v4_tree | hard_v4 | tree-aware | 192 | `llm_downstream_hard_v4_transfer_mimo_v2_5_tree_24x8` | `python scripts/run_llm_downstream_validation.py --model "$SKILLADMIT_TRANSFER_MODEL" --run-name llm_downstream_hard_v4_transfer_mimo_v2_5_tree_24x8 --tasks-dir benchmark/downstream_hard_v4/tasks --strategy no_experience --strategy skilladmit_selected --strategy skilladmit_selected_with_precondition_context --strategy raw_memory --strategy distilled_skills_all --strategy promoted_rules --strategy bad_dependency_rule --strategy forced_bad_artifact --use-task-visible-files --include-repo-tree --resume` |
| MT4_hard_v4_strict | hard_v4 | strict visible-file | 192 | `llm_downstream_hard_v4_transfer_mimo_v2_5_strict_24x8` | `python scripts/run_llm_downstream_validation.py --model "$SKILLADMIT_TRANSFER_MODEL" --run-name llm_downstream_hard_v4_transfer_mimo_v2_5_strict_24x8 --tasks-dir benchmark/downstream_hard_v4/tasks --strategy no_experience --strategy skilladmit_selected --strategy skilladmit_selected_with_precondition_only --strategy raw_memory --strategy distilled_skills_all --strategy promoted_rules --strategy bad_dependency_rule --strategy forced_bad_artifact --use-task-visible-files --resume` |

## Stop Rules

- Use --resume only to recover interrupted rows; do not selectively rerun failed rows.
- If API outage or parser failure affects many rows, pause and document infrastructure status before rerunning.
- After the first full transfer run, freeze it as evidence. Any prompt or strategy adjustment must create a new protocol id.
- Do not add or remove tasks after seeing transfer-model outcomes.

## Primary Comparisons

- selected vs no_experience in hard_v3 tree-aware and strict settings
- selected vs no_experience in hard_v4 tree-aware and strict settings
- selected + precondition context vs selected in tree-aware settings
- precondition-only vs selected and no_experience in strict settings
- forced_bad_artifact aggregate across hard_v3 and hard_v4
- bad_dependency_rule artifact adherence vs forced_bad_artifact negative transfer

## Allowed Claims After Run

- The hard_v3/hard_v4 boundary pattern replicated, weakened, or reversed under a second model.
- Forced harmful artifacts did or did not remain systematic negative-transfer controls under the transfer model.
- Repo tree and precondition context remained, weakened, or changed as context variables under the transfer model.

## Forbidden Claims After Run

- Do not claim model-general SkillAdmit-selected superiority from one transfer model.
- Do not claim selected token savings unless a separate cost-controlled protocol is run.
- Do not compare transfer results to baseline after changing prompts, task visibility, or hidden verifiers.
- Do not treat forced_bad_artifact as a normal LLM-choice strategy; it is a deterministic negative-transfer control.

## Post-Run Required Exports

- Inspect raw run summaries for completeness only, not for prompt tuning.
- Create a model-transfer evidence package before adding paper claims.
- Rerun paper claim consistency audit after adding any transfer-facing report.

## Source Files

| name | path | sha256 | generated_at_utc |
| --- | --- | --- | --- |
| downstream_boundary_synthesis | `benchmark/downstream/reports/downstream_boundary_synthesis.json` | `b5e58a54217563fb` | `2026-05-23T05:33:33.739619+00:00` |
| paper_claim_consistency_audit | `benchmark/downstream/reports/paper_claim_consistency_audit.json` | `8cb50a50ad78752b` | `2026-05-23T06:49:54.964692+00:00` |
