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
- experiment handoff and paper-facing status notes.

Key entry points:

```bash
python scripts/run_admission_regression.py
python scripts/check_downstream_hard_v2_tasks.py
python scripts/summarize_hard_v2_results.py --assert-current-hard-v2
python scripts/export_hard_v2_evidence_package.py --assert-current-hard-v2
```

Use the existing `skilladmit` conda environment for local reproduction. Runtime
secrets belong in `.env`; the real `.env` file is intentionally ignored by Git.
