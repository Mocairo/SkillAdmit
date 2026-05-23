# SkillAdmit Reproduction Guide

This guide is the public entry point for reproducing the current SkillAdmit
evidence package. This guide is not new empirical evidence. It explains which generated
artifacts should be trusted for which claim, which commands rebuild the public
reports, and which experiments should not be tuned after inspection.

## Scope

The current public evidence is organized into three layers:

| layer | role | primary artifact |
| --- | --- | --- |
| current main boundary | hard_v2, hard_v3, and hard_v4 downstream validation | `benchmark/downstream/reports/downstream_boundary_synthesis.json` |
| model-transfer addendum | second-model sensitivity over frozen hard_v3 and hard_v4 | `benchmark/downstream/reports/model_transfer_cross_model_synthesis.json` |
| historical two-boundary synthesis | older hard_v2 and hard_v3 synthesis retained for provenance | `benchmark/downstream/reports/downstream_cross_version_synthesis.json` |

Use the current main boundary for the paper's main downstream claim. Use the
model-transfer addendum only as a sensitivity or appendix layer. Treat the
historical hard_v2/hard_v3 synthesis as historical context, not as the current
top-level result.

## Environment

Use the repository root as the working directory:

```bash
cd SkillAdmit
```

Use an environment with the repository's Python dependencies installed. Then
run scripts from the repository root with `python`, for example:

```bash
python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index
```

Runtime secrets belong in `.env`; do not commit `.env`. The report-regeneration
commands below read existing tracked evidence files and do not require a new LLM
API run.

## Fast Public Check

Run these commands before using or publishing the repository:

```bash
python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index
python scripts/audit_paper_claim_consistency.py --assert-current-audit
python scripts/audit_reporting_hygiene.py --assert-current-hygiene
python scripts/audit_public_release_readiness.py --assert-current-release
python scripts/audit_reproduction_guide.py --assert-current-reproduction-guide
```

These checks verify that the evidence index is current, paper-facing claims are
consistent, aggregate roles remain separated, local secrets and workspaces stay
out of Git, and this guide has not drifted away from the generated reports.

## Full Report Regeneration

Use this sequence to rebuild the deterministic reports from the tracked task
scaffolds and completed run artifacts:

```bash
python scripts/check_downstream_hard_v2_tasks.py
python scripts/check_downstream_hard_v3_tasks.py
python scripts/build_downstream_hard_v4_tasks.py
python scripts/check_downstream_hard_v4_tasks.py
python scripts/run_admission_regression.py
python scripts/summarize_hard_v2_results.py --assert-current-hard-v2
python scripts/export_hard_v2_evidence_package.py --assert-current-hard-v2
python scripts/summarize_hard_v3_results.py --assert-current-hard-v3
python scripts/export_hard_v3_evidence_package.py --assert-current-hard-v3
python scripts/export_hard_v4_scaffold_manifest.py --run-checker --assert-current-hard-v4-scaffold
python scripts/summarize_hard_v4_results.py --assert-current-hard-v4
python scripts/export_hard_v4_evidence_package.py --assert-current-hard-v4
python scripts/export_downstream_cross_version_synthesis.py --assert-current-synthesis
python scripts/export_downstream_boundary_synthesis.py --assert-current-boundary-synthesis
python scripts/export_downstream_paper_section.py --assert-current-paper-section
python scripts/export_downstream_claim_defense_matrix.py --assert-current-claim-defense
python scripts/export_model_transfer_replication_protocol.py --assert-current-protocol
python scripts/export_model_transfer_evidence_package.py --assert-current-model-transfer
python scripts/export_model_transfer_cross_model_synthesis.py --assert-current-cross-model
python scripts/export_model_transfer_paper_addendum.py --assert-current-addendum
python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index
python scripts/audit_paper_claim_consistency.py --assert-current-audit
python scripts/audit_reporting_hygiene.py --assert-current-hygiene
python scripts/audit_public_release_readiness.py --assert-current-release
python scripts/audit_reproduction_guide.py --assert-current-reproduction-guide
```

## Evidence Boundaries

The current main downstream boundary is:

```text
hard_v2 + hard_v3 + hard_v4 forced_bad_artifact: 0/133 success
public-pass/hidden-fail cases: 133
```

The optional model-transfer addendum is:

```text
hard_v3 + hard_v4 across baseline and mimo-v2.5 transfer model:
forced_bad_artifact: 0/216 success
public-pass/hidden-fail cases: 216
```

The older hard_v2/hard_v3 synthesis remains tracked as:

```text
historical forced_bad_artifact aggregate: 0/85
```

Do not merge these numbers into one leaderboard. They answer different
questions and have different reporting roles.

## Supported Claims

The current artifacts support these claims:

- hard_v2 provides the clearest positive downstream evidence for tree-aware
  SkillAdmit-selected context on its suite.
- hard_v3 and hard_v4 bound the stronger claim that SkillAdmit-selected
  universally dominates no_experience.
- forced_bad_artifact is the strongest negative-transfer control: harmful
  admitted artifacts reliably produce public-pass/hidden-fail failures when
  forced into the executor.
- model-transfer evidence replicates the forced-bad negative-transfer pattern,
  while selected-vs-no_experience deltas remain model-sensitive.

## Unsupported Claims

Do not claim universal SkillAdmit-selected superiority.
Do not claim selected token savings.
Do not claim hard_v4 proves SkillAdmit-selected utility.
Do not claim raw memory or bad_dependency_rule is a safe admission policy just
because some downstream rows succeed.
Do not claim that the model-transfer addendum upgrades the main result into
model-general selected superiority.

## No-Retuning Rule

Do not tune hard_v2, hard_v3, or hard_v4 prompts, strategies, artifacts, or task
definitions from observed failures while treating those suites as clean
evidence. If a new experiment is needed, predeclare a hard_v5 boundary instead
of patching the current frozen boundaries.

## Files Not To Commit

Do not commit:

```text
.env
benchmark/downstream/llm_runs/*/workspaces/
benchmark/agent_runs/
__pycache__/
.pytest_cache/
```

The public release-readiness audit checks these paths before release.
