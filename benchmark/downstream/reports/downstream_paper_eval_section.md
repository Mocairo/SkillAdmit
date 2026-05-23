# Downstream Validation Paper Section

Generated at UTC: `2026-05-23T06:09:05.254849+00:00`

This is a draftable paper section generated from the frozen three-boundary downstream synthesis. It should be edited for style, not for stronger claims.

## Research Questions

- Does admitted experience improve downstream coding-agent success under hidden-verifier evaluation?
- Are repository-tree context and explicit preconditions critical variables for transferring admitted experience?
- Does executing harmful admitted experience create systematic negative transfer even when public tests pass?

## Protocol

We evaluate SkillAdmit downstream rather than relying only on admission-label accuracy. hard_v2 contains 25 import/debug tasks and hard_v3 contains 30 more agent-like repository repair tasks. hard_v4 adds 24 stricter multi-signal repository repair tasks. All three suites use hidden verifiers, so public-test success is insufficient for success.

The comparison includes no_experience, SkillAdmit-selected context, selected context with explicit preconditions, precondition-only ablations where available, raw memory, all distilled skills, promoted rules, bad dependency rules, and forced bad artifacts. hard_v2, hard_v3, and hard_v4 are reported as distinct evaluation boundaries rather than collapsed into one leaderboard.

## Results

On hard_v2, the tree-aware setting gives the clearest positive downstream result for SkillAdmit-selected experience: SkillAdmit-selected solves 25/25 tasks, compared with 23/25 for no_experience. The selected + precondition context condition also solves 25/25. In contrast, strict visible-file hard_v2 does not support a selected-win story: selected solves 23/25, while no_experience solves 24/25 and all distilled skills solve 25/25.

hard_v3 is a fresh generalization boundary and is deliberately less favorable to a simple selected-superiority claim. In the tree-aware hard_v3 setting, SkillAdmit-selected and no_experience both solve 29/30; selected + preconditions also solves 29/30. Raw memory and all distilled skills solve 30/30 and 30/30, respectively.

In strict visible-file hard_v3, SkillAdmit-selected improves over no_experience by one task (29/30 versus 28/30), but it is not the best condition: precondition-only and raw memory both solve 30/30. This separates the claim that selected experience can help from the stronger and unsupported claim that selected experience is universally optimal.

hard_v4 is a stricter downstream boundary rather than a hard_v3 retune. In the tree-aware setting, no_experience, SkillAdmit-selected, selected + preconditions, raw memory, and all distilled skills all solve 24/24, so hard_v4 tree-aware is saturated and cannot support a selected superiority claim. In strict visible-file hard_v4, selected solves 22/24, while no_experience and all distilled skills solve 24/24. Precondition-only reaches 23/24. This is the clearest current boundary against universal selected utility.

The strongest stable safety result is the forced harmful-artifact control. Across hard_v2, hard_v3, and hard_v4, forced bad artifacts solve 0/133 tasks and produce 133 public-pass/hidden-fail cases. This is direct evidence that admitting the wrong experience can systematically damage downstream behavior in ways public tests do not catch.

The ordinary bad_dependency_rule rows should not be interpreted as proving that bad advice is safe. In hard_v3, artifact adherence for that condition is only 4/30 in the tree-aware run and 11/30 in the strict visible-file run, and in hard_v4 it is 7/24 and 4/24. Success often reflects the executor ignoring harmful advice. The forced bad-artifact condition is the cleaner negative-transfer control.

## Interpretation

These results support a conditional downstream-utility claim: SkillAdmit-selected experience can improve downstream repair success under a coding-agent setting, as shown by hard_v2 tree-aware validation, but the effect does not generalize into universal dominance on hard_v3 or hard_v4.

The repository tree and explicit preconditions are best treated as context variables rather than as a single universally dominant representation. hard_v2 shows that precondition text alone is less reliable than tree-aware context, while hard_v3 shows that precondition-only context can be sufficient for a different task family, and hard_v4 shows that precondition-only can still trail no_experience under a stricter task family.

Token savings are not a supported paper claim. The current evidence is about success, hidden-verifier safety, and negative transfer; any token-efficiency claim would require a separate controlled cost study.

## One-Paragraph Paper Wording

Overall, downstream validation gives a sharper claim boundary than admission accuracy alone. hard_v2 supports SkillAdmit-selected utility in a tree-aware coding-agent setting (25/25 versus 23/25), but hard_v3 and hard_v4 do not support universal selected superiority: hard_v3 tree-aware selected ties no_experience at 29/30, and hard_v4 strict selected trails no_experience at 22/24 versus 24/24. The strongest three-boundary result is safety-related: forced harmful artifacts achieve 0/133 success with 133 public-pass/hidden-fail cases, demonstrating systematic negative transfer when harmful experience is executed.

## Table Captions

- `tab:downstream-cross-version`: Three-boundary downstream validation. hard_v2 provides positive evidence for tree-aware SkillAdmit-selected utility, hard_v3 is a generalization boundary, and hard_v4 is a stricter boundary showing that selected context does not universally dominate. Public-hidden counts indicate cases that pass public tests but fail hidden verification.
- `tab:negative-transfer`: Forced harmful-artifact control. Across hard_v2, hard_v3, and hard_v4, forced bad artifacts solve 0/133 tasks and create 133 public-pass/hidden-fail failures.

## Claims This Section Must Not Make

- Do not claim SkillAdmit-selected universally dominates no_experience.
- Do not claim SkillAdmit-selected is the universal best downstream context.
- Do not claim cross-version selected token savings.
- Do not claim precondition-only generally replaces repository-tree context.
- Do not claim raw memory is a safe admission policy from hard_v3 success alone.
- Do not claim bad dependency advice is safe when the model often ignored it.
- Do not tune hard_v2, hard_v3, or hard_v4 failures while still calling them clean evidence.

## Source

- synthesis: `benchmark/downstream/reports/downstream_boundary_synthesis.json`
- synthesis_sha256: `b5e58a54217563fbe2a24e3b4d63090b66d5d0ded6d9872ccb5e57e6bd1237aa`
- synthesis_generated_at_utc: `2026-05-23T05:33:33.739619+00:00`

