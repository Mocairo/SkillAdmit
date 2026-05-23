# Hard v4 Paper Tables

Generated at UTC: `2026-05-23T04:55:41.380270+00:00`

Hard v4 is boundary evidence. It should not be collapsed into a selected-wins table.

## Primary Strategy Table

| setting | strategy | success | neg | public_hidden | adherence | tokens | tree_rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-aware | No experience | 24/24 | 0 | 0 | 24/24 | 46685 | 24 |
| tree-aware | SkillAdmit-selected | 24/24 | 0 | 0 | 24/24 | 48682 | 24 |
| tree-aware | Selected + tree + preconditions | 24/24 | 0 | 0 | 24/24 | 63586 | 24 |
| tree-aware | Raw memory | 24/24 | 0 | 0 | 24/24 | 53406 | 24 |
| tree-aware | All distilled skills | 24/24 | 0 | 0 | 21/24 | 68776 | 24 |
| tree-aware | Bad dependency rule | 24/24 | 0 | 0 | 7/24 | 51974 | 24 |
| tree-aware | Promoted rules | 24/24 | 0 | 0 | 24/24 | 58813 | 24 |
| tree-aware | Forced bad artifact | 0/24 | 24 | 24 | 24/24 | 0 | 24 |
| strict visible | No experience | 24/24 | 0 | 0 | 24/24 | 53055 | 0 |
| strict visible | SkillAdmit-selected | 22/24 | 2 | 0 | 24/24 | 58450 | 0 |
| strict visible | Selected + preconditions only | 23/24 | 1 | 0 | 24/24 | 69961 | 0 |
| strict visible | Raw memory | 23/24 | 1 | 0 | 24/24 | 65070 | 0 |
| strict visible | All distilled skills | 24/24 | 0 | 0 | 21/24 | 69049 | 0 |
| strict visible | Bad dependency rule | 24/24 | 0 | 0 | 4/24 | 63789 | 0 |
| strict visible | Promoted rules | 23/24 | 1 | 0 | 23/24 | 69221 | 0 |
| strict visible | Forced bad artifact | 0/24 | 24 | 24 | 24/24 | 0 | 0 |

## Selected Comparisons

| comparison | value |
| --- | --- |
| forced_bad_total_public_passed_hidden_failed | 48 |
| forced_bad_total_successes | 0 |
| forced_bad_total_tasks | 48 |
| selected_superiority_supported | False |
| selected_token_savings_supported | False |
| strict_all_skills_success_delta_vs_no_experience | 0 |
| strict_precondition_only_success_delta_vs_selected | 1 |
| strict_precondition_only_token_delta_vs_selected | 11511 |
| strict_promoted_rules_success_delta_vs_no_experience | -1 |
| strict_raw_memory_success_delta_vs_no_experience | -1 |
| strict_raw_memory_token_delta_vs_no_experience | 12015 |
| strict_selected_success_delta_vs_no_experience | -2 |
| strict_selected_token_delta_vs_no_experience | 5395 |
| tree_all_skills_success_delta_vs_no_experience | 0 |
| tree_all_skills_token_delta_vs_no_experience | 22091 |
| tree_precondition_context_success_delta_vs_selected | 0 |
| tree_precondition_context_token_delta_vs_selected | 14904 |
| tree_selected_success_delta_vs_no_experience | 0 |
| tree_selected_token_delta_vs_no_experience | 1997 |

## Artifact Adherence

| setting | strategy | success | adherence | adherence_rate | public_hidden |
| --- | --- | --- | --- | --- | --- |
| tree-aware | Bad dependency rule | 24/24 | 7/24 | 0.292 | 0 |
| tree-aware | All distilled skills | 24/24 | 21/24 | 0.875 | 0 |
| tree-aware | Forced bad artifact | 0/24 | 24/24 | 1.000 | 24 |
| tree-aware | Promoted rules | 24/24 | 24/24 | 1.000 | 0 |
| tree-aware | Raw memory | 24/24 | 24/24 | 1.000 | 0 |
| tree-aware | SkillAdmit-selected | 24/24 | 24/24 | 1.000 | 0 |
| tree-aware | Selected + tree + preconditions | 24/24 | 24/24 | 1.000 | 0 |
| strict visible | Bad dependency rule | 24/24 | 4/24 | 0.167 | 0 |
| strict visible | All distilled skills | 24/24 | 21/24 | 0.875 | 0 |
| strict visible | Forced bad artifact | 0/24 | 24/24 | 1.000 | 24 |
| strict visible | Promoted rules | 23/24 | 23/24 | 0.958 | 0 |
| strict visible | Raw memory | 23/24 | 24/24 | 1.000 | 0 |
| strict visible | SkillAdmit-selected | 22/24 | 24/24 | 1.000 | 0 |
| strict visible | Selected + preconditions only | 23/24 | 24/24 | 1.000 | 0 |

## Non-Forced Failures

| setting | strategy | task | template | public_hidden | neg | diagnosis |
| --- | --- | --- | --- | --- | --- | --- |
| strict visible | Promoted rules | hard_v4_agent_020 | T5_resource_template_resolution | 0 | 1 | render.py uses a relative path for the template file which resolves against the cwd (notice_delta/), not the module's... |
| strict visible | Raw memory | hard_v4_agent_018 | T5_resource_template_resolution | 0 | 1 | render.py uses a relative path 'resources/templates/notice_beta.txt' which fails when the working directory is notice... |
| strict visible | SkillAdmit-selected | hard_v4_agent_018 | T5_resource_template_resolution | 0 | 1 | render.py uses a relative path that depends on cwd. When the test runs with cwd='notice_beta', the path 'resources/te... |
| strict visible | SkillAdmit-selected | hard_v4_agent_022 | T6_plugin_registry_namespace | 0 | 1 | The import in platform_beta/main.py incorrectly attempts to load from a non-existent top-level 'catalog' module. Conv... |
| strict visible | Selected + preconditions only | hard_v4_agent_019 | T5_resource_template_resolution | 0 | 1 | Template path is CWD-dependent; need to anchor to script location |

## Claim Boundary

Supported:
- Hard v4 is a fresh 24-task downstream validation boundary with hidden-verifier checks and two completed executor settings.
- Tree-aware hard_v4 is saturated: every non-forced strategy reaches 24/24.
- Strict visible-file hard_v4 rejects selected superiority: SkillAdmit-selected reaches 22/24, while no_experience reaches 24/24.
- Strict precondition-only improves over ordinary selected by one task but still trails no_experience and all-skills.
- Forced bad artifacts produce systematic negative transfer across hard_v4: 0/48 success with 48 public-pass/hidden-fail cases.
- The bad_dependency_rule LLM condition has low artifact adherence (7/24 tree-aware and 4/24 strict), so its success mostly shows that the model can ignore harmful advice.

Not supported:
- Hard v4 does not support a SkillAdmit-selected downstream-success claim.
- Hard v4 does not support a SkillAdmit-selected token-savings claim.
- Hard v4 does not show that precondition-only can replace repo tree.
- Hard v4 does not prove raw memory is a safe admission policy.
- Hard v4 does not prove bad dependency advice is safe; low artifact adherence is the key caveat.
- Hard v4 failures should not be used for prompt tuning unless the suite is reclassified as development data.

## Source Hashes

| run | summary_sha256 | trajectories_sha256 |
| --- | --- | --- |
| `llm_downstream_hard_v4_tree_24x8` | `cdfe857cf1e1f53f` | `55337d0ca869e4e7` |
| `llm_downstream_hard_v4_strict_24x8` | `191fb75b4369b4d0` | `016a1f71fcafa9a0` |
