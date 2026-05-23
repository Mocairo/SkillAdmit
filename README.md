# SkillAdmit

SkillAdmit is an experimental repository for studying experience admission in
coding agents. The project focuses on deciding whether an observed agent
experience should be discarded, stored as memory, distilled into a reusable
skill, promoted to a rule, or deferred.

Start here:

- `docs/reproduction_guide.md` for the public reproduction path;
- `benchmark/downstream/reports/paper_artifacts_index.md` for the evidence index;
- `benchmark/downstream/reports/downstream_boundary_synthesis.md` for the main downstream boundary;
- `benchmark/downstream/reports/model_transfer_cross_model_synthesis.md` for the optional second-model addendum.

Current evidence boundary:

| layer | aggregate | role |
| --- | --- | --- |
| main downstream boundary | 0/133 forced_bad_artifact success | hard_v2/hard_v3/hard_v4 evidence |
| model-transfer addendum | 0/216 forced_bad_artifact success | hard_v3/hard_v4 second-model sensitivity |
| historical synthesis | 0/85 forced_bad_artifact success | older hard_v2/hard_v3 report retained for provenance |

Do not read these aggregates as one leaderboard. The current main claim is
conditional: SkillAdmit-selected helps on some downstream boundaries, but it is
not a universal selected-superiority or token-savings result. The most stable
signal is negative transfer from forced harmful artifacts.

The current repo contains:

- admission benchmark generation and regression scripts;
- Python import/debug downstream task suites;
- LLM downstream validation runners;
- hard_v2 downstream reports with hidden-verifier and negative-transfer checks;
- hard_v3 deterministic downstream task scaffold, LLM matrix runs, and reports;
- hard_v4 frozen scaffold, LLM matrix runs, and paper-facing evidence exports;
- hard_v2/hard_v3/hard_v4 boundary synthesis reports;
- generated downstream paper section, claim-defense matrix, and paper artifact index;
- paper-facing claim consistency audit;
- predeclared model-transfer replication protocol;
- completed mimo-v2.5 model-transfer evidence package and cross-model synthesis;
- model-transfer paper addendum for optional replication reporting;
- public reporting hygiene audit for aggregate and overclaim separation;
- public release-readiness audit for secrets, ignored artifacts, and regeneration commands;
- public reproduction guide and audit for release-facing rerun instructions;
- public release-candidate audit for the final aggregated pre-push check;
- experiment handoff and paper-facing status notes.

Unsupported public claims:

- Do not claim universal SkillAdmit-selected superiority.
- Do not claim selected token savings.
- Do not claim hard_v4 proves SkillAdmit-selected utility.
- Do not use the model-transfer addendum as a model-general selected-win result.
- Do not tune hard_v2, hard_v3, or hard_v4 from inspected failures while
  treating them as clean evidence.

Key entry points:

```bash
python scripts/run_admission_regression.py
python scripts/check_downstream_hard_v2_tasks.py
python scripts/check_downstream_hard_v3_tasks.py
python scripts/build_downstream_hard_v4_tasks.py
python scripts/check_downstream_hard_v4_tasks.py
python scripts/export_hard_v4_scaffold_manifest.py --run-checker --assert-current-hard-v4-scaffold
python scripts/summarize_hard_v4_results.py --assert-current-hard-v4
python scripts/export_hard_v4_evidence_package.py --assert-current-hard-v4
python scripts/inspect_llm_downstream_run.py --run-name llm_downstream_hard_v3_tree_core_30x2
python scripts/summarize_hard_v2_results.py --assert-current-hard-v2
python scripts/export_hard_v2_evidence_package.py --assert-current-hard-v2
python scripts/summarize_hard_v3_results.py --assert-current-hard-v3
python scripts/export_hard_v3_evidence_package.py --assert-current-hard-v3
python scripts/export_downstream_cross_version_synthesis.py --assert-current-synthesis
python scripts/export_downstream_boundary_synthesis.py --assert-current-boundary-synthesis
python scripts/export_downstream_paper_section.py --assert-current-paper-section
python scripts/export_downstream_claim_defense_matrix.py --assert-current-claim-defense
python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index
python scripts/audit_paper_claim_consistency.py --assert-current-audit
python scripts/export_model_transfer_replication_protocol.py --assert-current-protocol
python scripts/export_model_transfer_evidence_package.py --assert-current-model-transfer
python scripts/export_model_transfer_cross_model_synthesis.py --assert-current-cross-model
python scripts/export_model_transfer_paper_addendum.py --assert-current-addendum
python scripts/audit_reporting_hygiene.py --assert-current-hygiene
python scripts/audit_public_release_readiness.py --assert-current-release
python scripts/audit_reproduction_guide.py --assert-current-reproduction-guide
python scripts/audit_release_candidate.py --assert-current-release-candidate
```

Use the existing `skilladmit` conda environment for local reproduction. Runtime
secrets belong in `.env`; the real `.env` file is intentionally ignored by Git.
The release-candidate audit is not new empirical evidence; it only aggregates
the public checks above before a push or release tag.
