# Hard v3 Paper Tables

Generated at UTC: `2026-05-22T13:03:52.487189+00:00`

Hard v3 is boundary evidence. It should not be collapsed into a simple selected-wins table.

## Primary Strategy Table

| setting | strategy | success | neg | public_hidden | adherence | tokens | tree_rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree-aware | No experience | 29/30 | 1 | 0 | 30/30 | 70208 | 30 |
| tree-aware | SkillAdmit-selected | 29/30 | 1 | 0 | 30/30 | 69291 | 30 |
| tree-aware | Selected + tree + preconditions | 29/30 | 1 | 0 | 30/30 | 74559 | 30 |
| tree-aware | Raw memory | 30/30 | 0 | 0 | 30/30 | 68753 | 30 |
| tree-aware | All distilled skills | 30/30 | 0 | 0 | 30/30 | 75603 | 30 |
| tree-aware | Bad dependency rule | 30/30 | 0 | 0 | 4/30 | 68671 | 30 |
| tree-aware | Promoted rules | 29/30 | 1 | 1 | 30/30 | 73114 | 30 |
| tree-aware | Forced bad artifact | 0/30 | 30 | 30 | 30/30 | 0 | 30 |
| strict visible | No experience | 28/30 | 0 | 0 | 30/30 | 74153 | 0 |
| strict visible | SkillAdmit-selected | 29/30 | 1 | 0 | 30/30 | 71390 | 0 |
| strict visible | Selected + preconditions only | 30/30 | 0 | 0 | 30/30 | 82615 | 0 |
| strict visible | Raw memory | 30/30 | 0 | 0 | 30/30 | 73789 | 0 |
| strict visible | All distilled skills | 29/30 | 1 | 1 | 26/30 | 83366 | 0 |
| strict visible | Bad dependency rule | 30/30 | 0 | 0 | 11/30 | 75920 | 0 |
| strict visible | Promoted rules | 29/30 | 1 | 0 | 30/30 | 80112 | 0 |
| strict visible | Forced bad artifact | 0/30 | 30 | 30 | 30/30 | 0 | 0 |

## Selected Comparisons

| comparison | value |
| --- | --- |
| strict_precondition_only_success_delta_vs_selected | 1 |
| strict_precondition_only_token_delta_vs_selected | 11225 |
| strict_raw_memory_success_delta_vs_no_experience | 2 |
| strict_raw_memory_token_delta_vs_no_experience | -364 |
| strict_selected_success_delta_vs_no_experience | 1 |
| strict_selected_token_delta_vs_no_experience | -2763 |
| tree_precondition_context_success_delta_vs_selected | 0 |
| tree_precondition_context_token_delta_vs_selected | 5268 |
| tree_raw_memory_success_delta_vs_no_experience | 1 |
| tree_raw_memory_token_delta_vs_no_experience | -1455 |
| tree_selected_success_delta_vs_no_experience | 0 |
| tree_selected_token_delta_vs_no_experience | -917 |

## Artifact Adherence

| setting | strategy | success | adherence | adherence_rate | public_hidden |
| --- | --- | --- | --- | --- | --- |
| tree-aware | Bad dependency rule | 30/30 | 4/30 | 0.133 | 0 |
| tree-aware | All distilled skills | 30/30 | 30/30 | 1.000 | 0 |
| tree-aware | Forced bad artifact | 0/30 | 30/30 | 1.000 | 30 |
| tree-aware | Promoted rules | 29/30 | 30/30 | 1.000 | 1 |
| tree-aware | Raw memory | 30/30 | 30/30 | 1.000 | 0 |
| tree-aware | SkillAdmit-selected | 29/30 | 30/30 | 1.000 | 0 |
| tree-aware | Selected + tree + preconditions | 29/30 | 30/30 | 1.000 | 0 |
| strict visible | Bad dependency rule | 30/30 | 11/30 | 0.367 | 0 |
| strict visible | All distilled skills | 29/30 | 26/30 | 0.867 | 1 |
| strict visible | Forced bad artifact | 0/30 | 30/30 | 1.000 | 30 |
| strict visible | Promoted rules | 29/30 | 30/30 | 1.000 | 0 |
| strict visible | Raw memory | 30/30 | 30/30 | 1.000 | 0 |
| strict visible | SkillAdmit-selected | 29/30 | 30/30 | 1.000 | 0 |
| strict visible | Selected + preconditions only | 30/30 | 30/30 | 1.000 | 0 |

## Non-Forced Failures

| setting | strategy | task | template | public_hidden | neg | diagnosis |
| --- | --- | --- | --- | --- | --- | --- |
| tree-aware | No experience | hard_v3_agent_013 | T3_dual_use_command_module | 0 | 1 | The script uses a relative import which fails when run directly as a file. We need to make the import work both as a ... |
| tree-aware | Promoted rules | hard_v3_agent_029 | T6_template_resource_cwd_path | 1 | 1 | The renderer uses a relative path that is incorrect when the script is run from the job_delta directory. The template... |
| tree-aware | SkillAdmit-selected | hard_v3_agent_027 | T6_template_resource_cwd_path | 0 | 1 | The renderer uses a relative path for the template, which fails when the current working directory is not the reposit... |
| tree-aware | Selected + tree + preconditions | hard_v3_agent_027 | T6_template_resource_cwd_path | 0 | 1 | FileNotFoundError due to relative path used when script runs from job_beta subdirectory. Need to anchor path to repos... |
| strict visible | All distilled skills | hard_v3_agent_014 | T3_dual_use_command_module | 1 | 1 | The script uses a relative import (from .payload) which fails when executed directly. Need to change import strategy ... |
| strict visible | No experience | hard_v3_agent_022 | T5_plugin_registry_internal_import | 0 | 0 | The import path in plugins_beta/main.py references a non-existent top-level catalog module. Since we cannot create a ... |
| strict visible | No experience | hard_v3_agent_025 | T5_plugin_registry_internal_import | 0 | 0 | The import `from adapters.loader import load_plugin` fails because there is no top-level `adapters` module. Since we ... |
| strict visible | Promoted rules | hard_v3_agent_024 | T5_plugin_registry_internal_import | 0 | 1 | The import 'from extensions.loader import load_plugin' fails because 'extensions' is not a top-level module. It's lik... |
| strict visible | SkillAdmit-selected | hard_v3_agent_015 | T3_dual_use_command_module | 0 | 1 | The script fails with ImportError due to relative import when executed directly; modified import to handle both scrip... |

## Claim Boundary

Supported:
- Hard v3 is a fresh 30-task downstream validation boundary with hidden-verifier checks and two completed executor settings.
- Forced bad artifacts produce systematic negative transfer in both hard_v3 settings: 0/30 success with 30 public-pass/hidden-fail cases.
- In tree-aware hard_v3, SkillAdmit-selected ties no_experience at 29/30 rather than beating it.
- In strict visible-file hard_v3, selected + preconditions only reaches 30/30, while ordinary selected reaches 29/30 and no_experience reaches 28/30.
- Raw memory reaches 30/30 in both hard_v3 settings, making it an important comparison condition rather than a disposable baseline.
- The bad_dependency_rule LLM condition has low artifact adherence (4/30 tree-aware and 11/30 strict), so its success mostly shows that the model can ignore harmful advice.

Not supported:
- Hard v3 does not support a SkillAdmit-selected superiority claim.
- Hard v3 does not support a SkillAdmit-selected token-savings claim.
- Hard v3 does not show that selected + precondition context beats ordinary tree-aware selected.
- Hard v3 does not show that repo tree is always necessary; strict precondition-only reaches 30/30.
- Hard v3 does not prove raw memory is a safe admission policy.
- Hard v3 does not prove bad dependency advice is safe; low artifact adherence is the key caveat.
- Hard v3 failures should not be used for prompt tuning unless the suite is reclassified as development data.

## Source Hashes

| run | summary_sha256 | trajectories_sha256 |
| --- | --- | --- |
| `llm_downstream_hard_v3_tree_core_30x2` | `f9544d04ff7e601b` | `acef5a38d78b1533` |
| `llm_downstream_hard_v3_strict_30x8` | `fe155aed1450bc04` | `501171e60b54bac8` |
