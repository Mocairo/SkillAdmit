# SkillAdmit

SkillAdmit is an experimental repository for studying experience admission in
coding agents. The project focuses on deciding whether an observed agent
experience should be discarded, stored as memory, distilled into a reusable
skill, promoted to a rule, or deferred.

The current repo contains:

- admission benchmark generation and regression scripts;
- Python import/debug downstream task suites;
- LLM downstream validation runners;
- hard_v2 downstream reports with hidden-verifier and negative-transfer checks;
- hard_v3 deterministic downstream task scaffold, LLM matrix runs, and reports;
- hard_v4 frozen scaffold, LLM matrix runs, and paper-facing evidence exports;
- experiment handoff and paper-facing status notes.

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
python scripts/export_downstream_paper_section.py --assert-current-paper-section
python scripts/export_downstream_claim_defense_matrix.py --assert-current-claim-defense
python scripts/export_paper_artifacts_index.py --assert-current-artifacts-index
```

Use the existing `skilladmit` conda environment for local reproduction. Runtime
secrets belong in `.env`; the real `.env` file is intentionally ignored by Git.
