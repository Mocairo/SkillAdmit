# Hard v4 Strategy Matrix

Generated at UTC: `2026-05-23T04:55:41.339896+00:00`

This report snapshots hard_v4 downstream summaries and trajectory hashes.
Tree-aware and strict visible-file settings are intentionally reported separately.

## Strategy Matrix

| setting | run | strategy | success | neg | public_hidden | adherence | parse | tokens | avg_tokens | tree_rows | visible_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree_aware | `llm_downstream_hard_v4_tree_24x8` | `bad_dependency_rule` | 24/24 | 0 | 0 | 7 | 0 | 51974 | 2165.6 | 24 | 24 |
| tree_aware | `llm_downstream_hard_v4_tree_24x8` | `distilled_skills_all` | 24/24 | 0 | 0 | 21 | 0 | 68776 | 2865.7 | 24 | 24 |
| tree_aware | `llm_downstream_hard_v4_tree_24x8` | `forced_bad_artifact` | 0/24 | 24 | 24 | 24 | 0 | 0 | 0.0 | 24 | 24 |
| tree_aware | `llm_downstream_hard_v4_tree_24x8` | `no_experience` | 24/24 | 0 | 0 | 24 | 0 | 46685 | 1945.2 | 24 | 24 |
| tree_aware | `llm_downstream_hard_v4_tree_24x8` | `promoted_rules` | 24/24 | 0 | 0 | 24 | 0 | 58813 | 2450.5 | 24 | 24 |
| tree_aware | `llm_downstream_hard_v4_tree_24x8` | `raw_memory` | 24/24 | 0 | 0 | 24 | 0 | 53406 | 2225.2 | 24 | 24 |
| tree_aware | `llm_downstream_hard_v4_tree_24x8` | `skilladmit_selected` | 24/24 | 0 | 0 | 24 | 0 | 48682 | 2028.4 | 24 | 24 |
| tree_aware | `llm_downstream_hard_v4_tree_24x8` | `skilladmit_selected_with_precondition_context` | 24/24 | 0 | 0 | 24 | 0 | 63586 | 2649.4 | 24 | 24 |
| strict_visible_file | `llm_downstream_hard_v4_strict_24x8` | `bad_dependency_rule` | 24/24 | 0 | 0 | 4 | 0 | 63789 | 2657.9 | 0 | 24 |
| strict_visible_file | `llm_downstream_hard_v4_strict_24x8` | `distilled_skills_all` | 24/24 | 0 | 0 | 21 | 0 | 69049 | 2877.0 | 0 | 24 |
| strict_visible_file | `llm_downstream_hard_v4_strict_24x8` | `forced_bad_artifact` | 0/24 | 24 | 24 | 24 | 0 | 0 | 0.0 | 0 | 24 |
| strict_visible_file | `llm_downstream_hard_v4_strict_24x8` | `no_experience` | 24/24 | 0 | 0 | 24 | 0 | 53055 | 2210.6 | 0 | 24 |
| strict_visible_file | `llm_downstream_hard_v4_strict_24x8` | `promoted_rules` | 23/24 | 1 | 0 | 23 | 0 | 69221 | 2884.2 | 0 | 24 |
| strict_visible_file | `llm_downstream_hard_v4_strict_24x8` | `raw_memory` | 23/24 | 1 | 0 | 24 | 0 | 65070 | 2711.2 | 0 | 24 |
| strict_visible_file | `llm_downstream_hard_v4_strict_24x8` | `skilladmit_selected` | 22/24 | 2 | 0 | 24 | 0 | 58450 | 2435.4 | 0 | 24 |
| strict_visible_file | `llm_downstream_hard_v4_strict_24x8` | `skilladmit_selected_with_precondition_only` | 23/24 | 1 | 0 | 24 | 0 | 69961 | 2915.0 | 0 | 24 |

## Template Matrix

| setting | strategy | template | success | neg | public_hidden | tokens | avg_tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree_aware | `bad_dependency_rule` | T1_optional_telemetry_import | 4/4 | 0 | 0 | 8523 | 2130.8 |
| tree_aware | `bad_dependency_rule` | T2_src_layout_package_import | 4/4 | 0 | 0 | 6244 | 1561.0 |
| tree_aware | `bad_dependency_rule` | T3_dual_entrypoint_command | 4/4 | 0 | 0 | 10101 | 2525.2 |
| tree_aware | `bad_dependency_rule` | T4_workspace_config_resolution | 4/4 | 0 | 0 | 8692 | 2173.0 |
| tree_aware | `bad_dependency_rule` | T5_resource_template_resolution | 4/4 | 0 | 0 | 10224 | 2556.0 |
| tree_aware | `bad_dependency_rule` | T6_plugin_registry_namespace | 4/4 | 0 | 0 | 8190 | 2047.5 |
| tree_aware | `distilled_skills_all` | T1_optional_telemetry_import | 4/4 | 0 | 0 | 8909 | 2227.2 |
| tree_aware | `distilled_skills_all` | T2_src_layout_package_import | 4/4 | 0 | 0 | 9100 | 2275.0 |
| tree_aware | `distilled_skills_all` | T3_dual_entrypoint_command | 4/4 | 0 | 0 | 15663 | 3915.8 |
| tree_aware | `distilled_skills_all` | T4_workspace_config_resolution | 4/4 | 0 | 0 | 10730 | 2682.5 |
| tree_aware | `distilled_skills_all` | T5_resource_template_resolution | 4/4 | 0 | 0 | 13833 | 3458.2 |
| tree_aware | `distilled_skills_all` | T6_plugin_registry_namespace | 4/4 | 0 | 0 | 10541 | 2635.2 |
| tree_aware | `forced_bad_artifact` | T1_optional_telemetry_import | 0/4 | 4 | 4 | 0 | 0.0 |
| tree_aware | `forced_bad_artifact` | T2_src_layout_package_import | 0/4 | 4 | 4 | 0 | 0.0 |
| tree_aware | `forced_bad_artifact` | T3_dual_entrypoint_command | 0/4 | 4 | 4 | 0 | 0.0 |
| tree_aware | `forced_bad_artifact` | T4_workspace_config_resolution | 0/4 | 4 | 4 | 0 | 0.0 |
| tree_aware | `forced_bad_artifact` | T5_resource_template_resolution | 0/4 | 4 | 4 | 0 | 0.0 |
| tree_aware | `forced_bad_artifact` | T6_plugin_registry_namespace | 0/4 | 4 | 4 | 0 | 0.0 |
| tree_aware | `no_experience` | T1_optional_telemetry_import | 4/4 | 0 | 0 | 7314 | 1828.5 |
| tree_aware | `no_experience` | T2_src_layout_package_import | 4/4 | 0 | 0 | 4059 | 1014.8 |
| tree_aware | `no_experience` | T3_dual_entrypoint_command | 4/4 | 0 | 0 | 10576 | 2644.0 |
| tree_aware | `no_experience` | T4_workspace_config_resolution | 4/4 | 0 | 0 | 9828 | 2457.0 |
| tree_aware | `no_experience` | T5_resource_template_resolution | 4/4 | 0 | 0 | 10375 | 2593.8 |
| tree_aware | `no_experience` | T6_plugin_registry_namespace | 4/4 | 0 | 0 | 4533 | 1133.2 |
| tree_aware | `promoted_rules` | T1_optional_telemetry_import | 4/4 | 0 | 0 | 8325 | 2081.2 |
| tree_aware | `promoted_rules` | T2_src_layout_package_import | 4/4 | 0 | 0 | 6724 | 1681.0 |
| tree_aware | `promoted_rules` | T3_dual_entrypoint_command | 4/4 | 0 | 0 | 12061 | 3015.2 |
| tree_aware | `promoted_rules` | T4_workspace_config_resolution | 4/4 | 0 | 0 | 9996 | 2499.0 |
| tree_aware | `promoted_rules` | T5_resource_template_resolution | 4/4 | 0 | 0 | 12124 | 3031.0 |
| tree_aware | `promoted_rules` | T6_plugin_registry_namespace | 4/4 | 0 | 0 | 9583 | 2395.8 |
| tree_aware | `raw_memory` | T1_optional_telemetry_import | 4/4 | 0 | 0 | 7611 | 1902.8 |
| tree_aware | `raw_memory` | T2_src_layout_package_import | 4/4 | 0 | 0 | 6797 | 1699.2 |
| tree_aware | `raw_memory` | T3_dual_entrypoint_command | 4/4 | 0 | 0 | 10825 | 2706.2 |
| tree_aware | `raw_memory` | T4_workspace_config_resolution | 4/4 | 0 | 0 | 9619 | 2404.8 |
| tree_aware | `raw_memory` | T5_resource_template_resolution | 4/4 | 0 | 0 | 10110 | 2527.5 |
| tree_aware | `raw_memory` | T6_plugin_registry_namespace | 4/4 | 0 | 0 | 8444 | 2111.0 |
| tree_aware | `skilladmit_selected` | T1_optional_telemetry_import | 4/4 | 0 | 0 | 6352 | 1588.0 |
| tree_aware | `skilladmit_selected` | T2_src_layout_package_import | 4/4 | 0 | 0 | 6130 | 1532.5 |
| tree_aware | `skilladmit_selected` | T3_dual_entrypoint_command | 4/4 | 0 | 0 | 12277 | 3069.2 |
| tree_aware | `skilladmit_selected` | T4_workspace_config_resolution | 4/4 | 0 | 0 | 9673 | 2418.2 |
| tree_aware | `skilladmit_selected` | T5_resource_template_resolution | 4/4 | 0 | 0 | 9491 | 2372.8 |
| tree_aware | `skilladmit_selected` | T6_plugin_registry_namespace | 4/4 | 0 | 0 | 4759 | 1189.8 |
| tree_aware | `skilladmit_selected_with_precondition_context` | T1_optional_telemetry_import | 4/4 | 0 | 0 | 9312 | 2328.0 |
| tree_aware | `skilladmit_selected_with_precondition_context` | T2_src_layout_package_import | 4/4 | 0 | 0 | 7340 | 1835.0 |
| tree_aware | `skilladmit_selected_with_precondition_context` | T3_dual_entrypoint_command | 4/4 | 0 | 0 | 15083 | 3770.8 |
| tree_aware | `skilladmit_selected_with_precondition_context` | T4_workspace_config_resolution | 4/4 | 0 | 0 | 11515 | 2878.8 |
| tree_aware | `skilladmit_selected_with_precondition_context` | T5_resource_template_resolution | 4/4 | 0 | 0 | 10979 | 2744.8 |
| tree_aware | `skilladmit_selected_with_precondition_context` | T6_plugin_registry_namespace | 4/4 | 0 | 0 | 9357 | 2339.2 |
| strict_visible_file | `bad_dependency_rule` | T1_optional_telemetry_import | 4/4 | 0 | 0 | 7285 | 1821.2 |
| strict_visible_file | `bad_dependency_rule` | T2_src_layout_package_import | 4/4 | 0 | 0 | 12530 | 3132.5 |
| strict_visible_file | `bad_dependency_rule` | T3_dual_entrypoint_command | 4/4 | 0 | 0 | 12370 | 3092.5 |
| strict_visible_file | `bad_dependency_rule` | T4_workspace_config_resolution | 4/4 | 0 | 0 | 9721 | 2430.2 |
| strict_visible_file | `bad_dependency_rule` | T5_resource_template_resolution | 4/4 | 0 | 0 | 10377 | 2594.2 |
| strict_visible_file | `bad_dependency_rule` | T6_plugin_registry_namespace | 4/4 | 0 | 0 | 11506 | 2876.5 |
| strict_visible_file | `distilled_skills_all` | T1_optional_telemetry_import | 4/4 | 0 | 0 | 9760 | 2440.0 |
| strict_visible_file | `distilled_skills_all` | T2_src_layout_package_import | 4/4 | 0 | 0 | 10042 | 2510.5 |
| strict_visible_file | `distilled_skills_all` | T3_dual_entrypoint_command | 4/4 | 0 | 0 | 11760 | 2940.0 |
| strict_visible_file | `distilled_skills_all` | T4_workspace_config_resolution | 4/4 | 0 | 0 | 11521 | 2880.2 |
| strict_visible_file | `distilled_skills_all` | T5_resource_template_resolution | 4/4 | 0 | 0 | 11939 | 2984.8 |
| strict_visible_file | `distilled_skills_all` | T6_plugin_registry_namespace | 4/4 | 0 | 0 | 14027 | 3506.8 |
| strict_visible_file | `forced_bad_artifact` | T1_optional_telemetry_import | 0/4 | 4 | 4 | 0 | 0.0 |
| strict_visible_file | `forced_bad_artifact` | T2_src_layout_package_import | 0/4 | 4 | 4 | 0 | 0.0 |
| strict_visible_file | `forced_bad_artifact` | T3_dual_entrypoint_command | 0/4 | 4 | 4 | 0 | 0.0 |
| strict_visible_file | `forced_bad_artifact` | T4_workspace_config_resolution | 0/4 | 4 | 4 | 0 | 0.0 |
| strict_visible_file | `forced_bad_artifact` | T5_resource_template_resolution | 0/4 | 4 | 4 | 0 | 0.0 |
| strict_visible_file | `forced_bad_artifact` | T6_plugin_registry_namespace | 0/4 | 4 | 4 | 0 | 0.0 |
| strict_visible_file | `no_experience` | T1_optional_telemetry_import | 4/4 | 0 | 0 | 5914 | 1478.5 |
| strict_visible_file | `no_experience` | T2_src_layout_package_import | 4/4 | 0 | 0 | 7330 | 1832.5 |
| strict_visible_file | `no_experience` | T3_dual_entrypoint_command | 4/4 | 0 | 0 | 10554 | 2638.5 |
| strict_visible_file | `no_experience` | T4_workspace_config_resolution | 4/4 | 0 | 0 | 9197 | 2299.2 |
| strict_visible_file | `no_experience` | T5_resource_template_resolution | 4/4 | 0 | 0 | 8902 | 2225.5 |
| strict_visible_file | `no_experience` | T6_plugin_registry_namespace | 4/4 | 0 | 0 | 11158 | 2789.5 |
| strict_visible_file | `promoted_rules` | T1_optional_telemetry_import | 4/4 | 0 | 0 | 10643 | 2660.8 |
| strict_visible_file | `promoted_rules` | T2_src_layout_package_import | 4/4 | 0 | 0 | 11449 | 2862.2 |
| strict_visible_file | `promoted_rules` | T3_dual_entrypoint_command | 4/4 | 0 | 0 | 12342 | 3085.5 |
| strict_visible_file | `promoted_rules` | T4_workspace_config_resolution | 4/4 | 0 | 0 | 10008 | 2502.0 |
| strict_visible_file | `promoted_rules` | T5_resource_template_resolution | 3/4 | 1 | 0 | 10542 | 2635.5 |
| strict_visible_file | `promoted_rules` | T6_plugin_registry_namespace | 4/4 | 0 | 0 | 14237 | 3559.2 |
| strict_visible_file | `raw_memory` | T1_optional_telemetry_import | 4/4 | 0 | 0 | 7085 | 1771.2 |
| strict_visible_file | `raw_memory` | T2_src_layout_package_import | 4/4 | 0 | 0 | 10586 | 2646.5 |
| strict_visible_file | `raw_memory` | T3_dual_entrypoint_command | 4/4 | 0 | 0 | 11312 | 2828.0 |
| strict_visible_file | `raw_memory` | T4_workspace_config_resolution | 4/4 | 0 | 0 | 10872 | 2718.0 |
| strict_visible_file | `raw_memory` | T5_resource_template_resolution | 3/4 | 1 | 0 | 13179 | 3294.8 |
| strict_visible_file | `raw_memory` | T6_plugin_registry_namespace | 4/4 | 0 | 0 | 12036 | 3009.0 |
| strict_visible_file | `skilladmit_selected` | T1_optional_telemetry_import | 4/4 | 0 | 0 | 7271 | 1817.8 |
| strict_visible_file | `skilladmit_selected` | T2_src_layout_package_import | 4/4 | 0 | 0 | 10499 | 2624.8 |
| strict_visible_file | `skilladmit_selected` | T3_dual_entrypoint_command | 4/4 | 0 | 0 | 9636 | 2409.0 |
| strict_visible_file | `skilladmit_selected` | T4_workspace_config_resolution | 4/4 | 0 | 0 | 9166 | 2291.5 |
| strict_visible_file | `skilladmit_selected` | T5_resource_template_resolution | 3/4 | 1 | 0 | 10351 | 2587.8 |
| strict_visible_file | `skilladmit_selected` | T6_plugin_registry_namespace | 3/4 | 1 | 0 | 11527 | 2881.8 |
| strict_visible_file | `skilladmit_selected_with_precondition_only` | T1_optional_telemetry_import | 4/4 | 0 | 0 | 8232 | 2058.0 |
| strict_visible_file | `skilladmit_selected_with_precondition_only` | T2_src_layout_package_import | 4/4 | 0 | 0 | 8966 | 2241.5 |
| strict_visible_file | `skilladmit_selected_with_precondition_only` | T3_dual_entrypoint_command | 4/4 | 0 | 0 | 14224 | 3556.0 |
| strict_visible_file | `skilladmit_selected_with_precondition_only` | T4_workspace_config_resolution | 4/4 | 0 | 0 | 11566 | 2891.5 |
| strict_visible_file | `skilladmit_selected_with_precondition_only` | T5_resource_template_resolution | 3/4 | 1 | 0 | 14693 | 3673.2 |
| strict_visible_file | `skilladmit_selected_with_precondition_only` | T6_plugin_registry_namespace | 4/4 | 0 | 0 | 12280 | 3070.0 |

## Derived Comparisons

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

## Failures

| setting | strategy | task | template | public_hidden | neg | used_artifact | short diagnosis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_001 | T1_optional_telemetry_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_002 | T1_optional_telemetry_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_003 | T1_optional_telemetry_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_004 | T1_optional_telemetry_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_005 | T2_src_layout_package_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_006 | T2_src_layout_package_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_007 | T2_src_layout_package_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_008 | T2_src_layout_package_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_009 | T3_dual_entrypoint_command | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_010 | T3_dual_entrypoint_command | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_011 | T3_dual_entrypoint_command | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_012 | T3_dual_entrypoint_command | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_013 | T4_workspace_config_resolution | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_014 | T4_workspace_config_resolution | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_015 | T4_workspace_config_resolution | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_016 | T4_workspace_config_resolution | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_017 | T5_resource_template_resolution | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_018 | T5_resource_template_resolution | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_019 | T5_resource_template_resolution | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_020 | T5_resource_template_resolution | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_021 | T6_plugin_registry_namespace | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_022 | T6_plugin_registry_namespace | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_023 | T6_plugin_registry_namespace | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v4_agent_024 | T6_plugin_registry_namespace | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_001 | T1_optional_telemetry_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_002 | T1_optional_telemetry_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_003 | T1_optional_telemetry_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_004 | T1_optional_telemetry_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_005 | T2_src_layout_package_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_006 | T2_src_layout_package_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_007 | T2_src_layout_package_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_008 | T2_src_layout_package_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_009 | T3_dual_entrypoint_command | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_010 | T3_dual_entrypoint_command | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_011 | T3_dual_entrypoint_command | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_012 | T3_dual_entrypoint_command | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_013 | T4_workspace_config_resolution | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_014 | T4_workspace_config_resolution | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_015 | T4_workspace_config_resolution | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_016 | T4_workspace_config_resolution | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_017 | T5_resource_template_resolution | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_018 | T5_resource_template_resolution | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_019 | T5_resource_template_resolution | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_020 | T5_resource_template_resolution | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_021 | T6_plugin_registry_namespace | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_022 | T6_plugin_registry_namespace | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_023 | T6_plugin_registry_namespace | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v4_agent_024 | T6_plugin_registry_namespace | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `promoted_rules` | hard_v4_agent_020 | T5_resource_template_resolution | 0 | 1 | promoted_rules | render.py uses a relative path for the template file which resolves against the cwd (notice_delta/), not the module's location. Fix by ma... |
| strict_visible_file | `raw_memory` | hard_v4_agent_018 | T5_resource_template_resolution | 0 | 1 | raw_memory | render.py uses a relative path 'resources/templates/notice_beta.txt' which fails when the working directory is notice_beta/. Need to reso... |
| strict_visible_file | `skilladmit_selected` | hard_v4_agent_018 | T5_resource_template_resolution | 0 | 1 | skilladmit_selected | render.py uses a relative path that depends on cwd. When the test runs with cwd='notice_beta', the path 'resources/templates/notice_beta.... |
| strict_visible_file | `skilladmit_selected` | hard_v4_agent_022 | T6_plugin_registry_namespace | 0 | 1 | skilladmit_selected | The import in platform_beta/main.py incorrectly attempts to load from a non-existent top-level 'catalog' module. Converting it to a relat... |
| strict_visible_file | `skilladmit_selected_with_precondition_only` | hard_v4_agent_019 | T5_resource_template_resolution | 0 | 1 | skilladmit_selected_with_precondition_only | Template path is CWD-dependent; need to anchor to script location |

## Claim Boundary

Supported:
- Hard v4 is a fresh 24-task downstream validation boundary with hidden verifiers.
- The completed hard_v4 runs contain no parse errors.
- Tree-aware hard_v4 is saturated: every non-forced strategy reaches 24/24.
- Strict visible-file hard_v4 rejects selected superiority: SkillAdmit-selected reaches 22/24, while no_experience reaches 24/24.
- Strict precondition-only improves over ordinary selected by one task but still trails no_experience and all-skills.
- Forced bad artifacts produce systematic negative transfer across hard_v4: 0/48 success with 48 public-pass/hidden-fail cases.
- The ordinary bad_dependency_rule condition succeeds only with low artifact adherence (7/24 tree-aware and 4/24 strict), so its success mainly shows that the model can ignore harmful advice.

Not supported:
- Hard v4 does not support a SkillAdmit-selected downstream-success claim.
- Hard v4 does not support a SkillAdmit-selected token-savings claim.
- Hard v4 does not show that precondition-only can replace repo tree.
- Hard v4 does not prove that bad dependency advice is safe.
- Do not tune prompts, strategy text, or task design from observed hard_v4 failures.

## Source Hashes

| run | summary_sha256 | trajectories_sha256 |
| --- | --- | --- |
| `llm_downstream_hard_v4_tree_24x8` | `cdfe857cf1e1f53f` | `55337d0ca869e4e7` |
| `llm_downstream_hard_v4_strict_24x8` | `191fb75b4369b4d0` | `016a1f71fcafa9a0` |
