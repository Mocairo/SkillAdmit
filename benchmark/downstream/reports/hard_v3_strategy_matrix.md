# Hard v3 Strategy Matrix

Generated at UTC: `2026-05-22T12:21:25.956620+00:00`

This report snapshots hard_v3 downstream summaries and trajectory hashes.
Tree-aware and strict visible-file settings are intentionally reported separately.

## Strategy Matrix

| setting | run | strategy | success | neg | public_hidden | adherence | parse | tokens | avg_tokens | tree_rows | visible_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tree_aware | `llm_downstream_hard_v3_tree_core_30x2` | `bad_dependency_rule` | 30/30 | 0 | 0 | 4 | 0 | 68671 | 2289.0 | 30 | 30 |
| tree_aware | `llm_downstream_hard_v3_tree_core_30x2` | `distilled_skills_all` | 30/30 | 0 | 0 | 30 | 0 | 75603 | 2520.1 | 30 | 30 |
| tree_aware | `llm_downstream_hard_v3_tree_core_30x2` | `forced_bad_artifact` | 0/30 | 30 | 30 | 30 | 0 | 0 | 0.0 | 30 | 30 |
| tree_aware | `llm_downstream_hard_v3_tree_core_30x2` | `no_experience` | 29/30 | 1 | 0 | 30 | 0 | 70208 | 2340.3 | 30 | 30 |
| tree_aware | `llm_downstream_hard_v3_tree_core_30x2` | `promoted_rules` | 29/30 | 1 | 1 | 30 | 0 | 73114 | 2437.1 | 30 | 30 |
| tree_aware | `llm_downstream_hard_v3_tree_core_30x2` | `raw_memory` | 30/30 | 0 | 0 | 30 | 0 | 68753 | 2291.8 | 30 | 30 |
| tree_aware | `llm_downstream_hard_v3_tree_core_30x2` | `skilladmit_selected` | 29/30 | 1 | 0 | 30 | 0 | 69291 | 2309.7 | 30 | 30 |
| tree_aware | `llm_downstream_hard_v3_tree_core_30x2` | `skilladmit_selected_with_precondition_context` | 29/30 | 1 | 0 | 30 | 0 | 74559 | 2485.3 | 30 | 30 |
| strict_visible_file | `llm_downstream_hard_v3_strict_30x8` | `bad_dependency_rule` | 30/30 | 0 | 0 | 11 | 0 | 75920 | 2530.7 | 0 | 30 |
| strict_visible_file | `llm_downstream_hard_v3_strict_30x8` | `distilled_skills_all` | 29/30 | 1 | 1 | 26 | 0 | 83366 | 2778.9 | 0 | 30 |
| strict_visible_file | `llm_downstream_hard_v3_strict_30x8` | `forced_bad_artifact` | 0/30 | 30 | 30 | 30 | 0 | 0 | 0.0 | 0 | 30 |
| strict_visible_file | `llm_downstream_hard_v3_strict_30x8` | `no_experience` | 28/30 | 0 | 0 | 30 | 0 | 74153 | 2471.8 | 0 | 30 |
| strict_visible_file | `llm_downstream_hard_v3_strict_30x8` | `promoted_rules` | 29/30 | 1 | 0 | 30 | 0 | 80112 | 2670.4 | 0 | 30 |
| strict_visible_file | `llm_downstream_hard_v3_strict_30x8` | `raw_memory` | 30/30 | 0 | 0 | 30 | 0 | 73789 | 2459.6 | 0 | 30 |
| strict_visible_file | `llm_downstream_hard_v3_strict_30x8` | `skilladmit_selected` | 29/30 | 1 | 0 | 30 | 0 | 71390 | 2379.7 | 0 | 30 |
| strict_visible_file | `llm_downstream_hard_v3_strict_30x8` | `skilladmit_selected_with_precondition_only` | 30/30 | 0 | 0 | 30 | 0 | 82615 | 2753.8 | 0 | 30 |

## Template Matrix

| setting | strategy | template | success | neg | public_hidden | tokens | avg_tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree_aware | `bad_dependency_rule` | T1_optional_integration_import | 5/5 | 0 | 0 | 9348 | 1869.6 |
| tree_aware | `bad_dependency_rule` | T2_application_package_local_import | 5/5 | 0 | 0 | 9892 | 1978.4 |
| tree_aware | `bad_dependency_rule` | T3_dual_use_command_module | 5/5 | 0 | 0 | 12342 | 2468.4 |
| tree_aware | `bad_dependency_rule` | T4_repo_config_cwd_path | 5/5 | 0 | 0 | 12800 | 2560.0 |
| tree_aware | `bad_dependency_rule` | T5_plugin_registry_internal_import | 5/5 | 0 | 0 | 11491 | 2298.2 |
| tree_aware | `bad_dependency_rule` | T6_template_resource_cwd_path | 5/5 | 0 | 0 | 12798 | 2559.6 |
| tree_aware | `distilled_skills_all` | T1_optional_integration_import | 5/5 | 0 | 0 | 11879 | 2375.8 |
| tree_aware | `distilled_skills_all` | T2_application_package_local_import | 5/5 | 0 | 0 | 10112 | 2022.4 |
| tree_aware | `distilled_skills_all` | T3_dual_use_command_module | 5/5 | 0 | 0 | 10951 | 2190.2 |
| tree_aware | `distilled_skills_all` | T4_repo_config_cwd_path | 5/5 | 0 | 0 | 15515 | 3103.0 |
| tree_aware | `distilled_skills_all` | T5_plugin_registry_internal_import | 5/5 | 0 | 0 | 11669 | 2333.8 |
| tree_aware | `distilled_skills_all` | T6_template_resource_cwd_path | 5/5 | 0 | 0 | 15477 | 3095.4 |
| tree_aware | `forced_bad_artifact` | T1_optional_integration_import | 0/5 | 5 | 5 | 0 | 0.0 |
| tree_aware | `forced_bad_artifact` | T2_application_package_local_import | 0/5 | 5 | 5 | 0 | 0.0 |
| tree_aware | `forced_bad_artifact` | T3_dual_use_command_module | 0/5 | 5 | 5 | 0 | 0.0 |
| tree_aware | `forced_bad_artifact` | T4_repo_config_cwd_path | 0/5 | 5 | 5 | 0 | 0.0 |
| tree_aware | `forced_bad_artifact` | T5_plugin_registry_internal_import | 0/5 | 5 | 5 | 0 | 0.0 |
| tree_aware | `forced_bad_artifact` | T6_template_resource_cwd_path | 0/5 | 5 | 5 | 0 | 0.0 |
| tree_aware | `no_experience` | T1_optional_integration_import | 5/5 | 0 | 0 | 12080 | 2416.0 |
| tree_aware | `no_experience` | T2_application_package_local_import | 5/5 | 0 | 0 | 8122 | 1624.4 |
| tree_aware | `no_experience` | T3_dual_use_command_module | 4/5 | 1 | 0 | 14794 | 2958.8 |
| tree_aware | `no_experience` | T4_repo_config_cwd_path | 5/5 | 0 | 0 | 13232 | 2646.4 |
| tree_aware | `no_experience` | T5_plugin_registry_internal_import | 5/5 | 0 | 0 | 9403 | 1880.6 |
| tree_aware | `no_experience` | T6_template_resource_cwd_path | 5/5 | 0 | 0 | 12577 | 2515.4 |
| tree_aware | `promoted_rules` | T1_optional_integration_import | 5/5 | 0 | 0 | 10602 | 2120.4 |
| tree_aware | `promoted_rules` | T2_application_package_local_import | 5/5 | 0 | 0 | 10327 | 2065.4 |
| tree_aware | `promoted_rules` | T3_dual_use_command_module | 5/5 | 0 | 0 | 13488 | 2697.6 |
| tree_aware | `promoted_rules` | T4_repo_config_cwd_path | 5/5 | 0 | 0 | 11471 | 2294.2 |
| tree_aware | `promoted_rules` | T5_plugin_registry_internal_import | 5/5 | 0 | 0 | 11342 | 2268.4 |
| tree_aware | `promoted_rules` | T6_template_resource_cwd_path | 4/5 | 1 | 1 | 15884 | 3176.8 |
| tree_aware | `raw_memory` | T1_optional_integration_import | 5/5 | 0 | 0 | 9440 | 1888.0 |
| tree_aware | `raw_memory` | T2_application_package_local_import | 5/5 | 0 | 0 | 9226 | 1845.2 |
| tree_aware | `raw_memory` | T3_dual_use_command_module | 5/5 | 0 | 0 | 13860 | 2772.0 |
| tree_aware | `raw_memory` | T4_repo_config_cwd_path | 5/5 | 0 | 0 | 12189 | 2437.8 |
| tree_aware | `raw_memory` | T5_plugin_registry_internal_import | 5/5 | 0 | 0 | 10879 | 2175.8 |
| tree_aware | `raw_memory` | T6_template_resource_cwd_path | 5/5 | 0 | 0 | 13159 | 2631.8 |
| tree_aware | `skilladmit_selected` | T1_optional_integration_import | 5/5 | 0 | 0 | 10550 | 2110.0 |
| tree_aware | `skilladmit_selected` | T2_application_package_local_import | 5/5 | 0 | 0 | 9334 | 1866.8 |
| tree_aware | `skilladmit_selected` | T3_dual_use_command_module | 5/5 | 0 | 0 | 16083 | 3216.6 |
| tree_aware | `skilladmit_selected` | T4_repo_config_cwd_path | 5/5 | 0 | 0 | 12381 | 2476.2 |
| tree_aware | `skilladmit_selected` | T5_plugin_registry_internal_import | 5/5 | 0 | 0 | 8483 | 1696.6 |
| tree_aware | `skilladmit_selected` | T6_template_resource_cwd_path | 4/5 | 1 | 0 | 12460 | 2492.0 |
| tree_aware | `skilladmit_selected_with_precondition_context` | T1_optional_integration_import | 5/5 | 0 | 0 | 10231 | 2046.2 |
| tree_aware | `skilladmit_selected_with_precondition_context` | T2_application_package_local_import | 5/5 | 0 | 0 | 10523 | 2104.6 |
| tree_aware | `skilladmit_selected_with_precondition_context` | T3_dual_use_command_module | 5/5 | 0 | 0 | 15753 | 3150.6 |
| tree_aware | `skilladmit_selected_with_precondition_context` | T4_repo_config_cwd_path | 5/5 | 0 | 0 | 14698 | 2939.6 |
| tree_aware | `skilladmit_selected_with_precondition_context` | T5_plugin_registry_internal_import | 5/5 | 0 | 0 | 9341 | 1868.2 |
| tree_aware | `skilladmit_selected_with_precondition_context` | T6_template_resource_cwd_path | 4/5 | 1 | 0 | 14013 | 2802.6 |
| strict_visible_file | `bad_dependency_rule` | T1_optional_integration_import | 5/5 | 0 | 0 | 9911 | 1982.2 |
| strict_visible_file | `bad_dependency_rule` | T2_application_package_local_import | 5/5 | 0 | 0 | 11054 | 2210.8 |
| strict_visible_file | `bad_dependency_rule` | T3_dual_use_command_module | 5/5 | 0 | 0 | 13456 | 2691.2 |
| strict_visible_file | `bad_dependency_rule` | T4_repo_config_cwd_path | 5/5 | 0 | 0 | 11305 | 2261.0 |
| strict_visible_file | `bad_dependency_rule` | T5_plugin_registry_internal_import | 5/5 | 0 | 0 | 17713 | 3542.6 |
| strict_visible_file | `bad_dependency_rule` | T6_template_resource_cwd_path | 5/5 | 0 | 0 | 12481 | 2496.2 |
| strict_visible_file | `distilled_skills_all` | T1_optional_integration_import | 5/5 | 0 | 0 | 10893 | 2178.6 |
| strict_visible_file | `distilled_skills_all` | T2_application_package_local_import | 5/5 | 0 | 0 | 11234 | 2246.8 |
| strict_visible_file | `distilled_skills_all` | T3_dual_use_command_module | 4/5 | 1 | 1 | 14209 | 2841.8 |
| strict_visible_file | `distilled_skills_all` | T4_repo_config_cwd_path | 5/5 | 0 | 0 | 14434 | 2886.8 |
| strict_visible_file | `distilled_skills_all` | T5_plugin_registry_internal_import | 5/5 | 0 | 0 | 17709 | 3541.8 |
| strict_visible_file | `distilled_skills_all` | T6_template_resource_cwd_path | 5/5 | 0 | 0 | 14887 | 2977.4 |
| strict_visible_file | `forced_bad_artifact` | T1_optional_integration_import | 0/5 | 5 | 5 | 0 | 0.0 |
| strict_visible_file | `forced_bad_artifact` | T2_application_package_local_import | 0/5 | 5 | 5 | 0 | 0.0 |
| strict_visible_file | `forced_bad_artifact` | T3_dual_use_command_module | 0/5 | 5 | 5 | 0 | 0.0 |
| strict_visible_file | `forced_bad_artifact` | T4_repo_config_cwd_path | 0/5 | 5 | 5 | 0 | 0.0 |
| strict_visible_file | `forced_bad_artifact` | T5_plugin_registry_internal_import | 0/5 | 5 | 5 | 0 | 0.0 |
| strict_visible_file | `forced_bad_artifact` | T6_template_resource_cwd_path | 0/5 | 5 | 5 | 0 | 0.0 |
| strict_visible_file | `no_experience` | T1_optional_integration_import | 5/5 | 0 | 0 | 9162 | 1832.4 |
| strict_visible_file | `no_experience` | T2_application_package_local_import | 5/5 | 0 | 0 | 7734 | 1546.8 |
| strict_visible_file | `no_experience` | T3_dual_use_command_module | 5/5 | 0 | 0 | 16597 | 3319.4 |
| strict_visible_file | `no_experience` | T4_repo_config_cwd_path | 5/5 | 0 | 0 | 12634 | 2526.8 |
| strict_visible_file | `no_experience` | T5_plugin_registry_internal_import | 3/5 | 0 | 0 | 15099 | 3019.8 |
| strict_visible_file | `no_experience` | T6_template_resource_cwd_path | 5/5 | 0 | 0 | 12927 | 2585.4 |
| strict_visible_file | `promoted_rules` | T1_optional_integration_import | 5/5 | 0 | 0 | 11120 | 2224.0 |
| strict_visible_file | `promoted_rules` | T2_application_package_local_import | 5/5 | 0 | 0 | 12856 | 2571.2 |
| strict_visible_file | `promoted_rules` | T3_dual_use_command_module | 5/5 | 0 | 0 | 14667 | 2933.4 |
| strict_visible_file | `promoted_rules` | T4_repo_config_cwd_path | 5/5 | 0 | 0 | 11475 | 2295.0 |
| strict_visible_file | `promoted_rules` | T5_plugin_registry_internal_import | 4/5 | 1 | 0 | 15366 | 3073.2 |
| strict_visible_file | `promoted_rules` | T6_template_resource_cwd_path | 5/5 | 0 | 0 | 14628 | 2925.6 |
| strict_visible_file | `raw_memory` | T1_optional_integration_import | 5/5 | 0 | 0 | 8945 | 1789.0 |
| strict_visible_file | `raw_memory` | T2_application_package_local_import | 5/5 | 0 | 0 | 9673 | 1934.6 |
| strict_visible_file | `raw_memory` | T3_dual_use_command_module | 5/5 | 0 | 0 | 16596 | 3319.2 |
| strict_visible_file | `raw_memory` | T4_repo_config_cwd_path | 5/5 | 0 | 0 | 13034 | 2606.8 |
| strict_visible_file | `raw_memory` | T5_plugin_registry_internal_import | 5/5 | 0 | 0 | 12332 | 2466.4 |
| strict_visible_file | `raw_memory` | T6_template_resource_cwd_path | 5/5 | 0 | 0 | 13209 | 2641.8 |
| strict_visible_file | `skilladmit_selected` | T1_optional_integration_import | 5/5 | 0 | 0 | 9175 | 1835.0 |
| strict_visible_file | `skilladmit_selected` | T2_application_package_local_import | 5/5 | 0 | 0 | 12233 | 2446.6 |
| strict_visible_file | `skilladmit_selected` | T3_dual_use_command_module | 4/5 | 1 | 0 | 14330 | 2866.0 |
| strict_visible_file | `skilladmit_selected` | T4_repo_config_cwd_path | 5/5 | 0 | 0 | 10664 | 2132.8 |
| strict_visible_file | `skilladmit_selected` | T5_plugin_registry_internal_import | 5/5 | 0 | 0 | 13535 | 2707.0 |
| strict_visible_file | `skilladmit_selected` | T6_template_resource_cwd_path | 5/5 | 0 | 0 | 11453 | 2290.6 |
| strict_visible_file | `skilladmit_selected_with_precondition_only` | T1_optional_integration_import | 5/5 | 0 | 0 | 10559 | 2111.8 |
| strict_visible_file | `skilladmit_selected_with_precondition_only` | T2_application_package_local_import | 5/5 | 0 | 0 | 12055 | 2411.0 |
| strict_visible_file | `skilladmit_selected_with_precondition_only` | T3_dual_use_command_module | 5/5 | 0 | 0 | 14444 | 2888.8 |
| strict_visible_file | `skilladmit_selected_with_precondition_only` | T4_repo_config_cwd_path | 5/5 | 0 | 0 | 15293 | 3058.6 |
| strict_visible_file | `skilladmit_selected_with_precondition_only` | T5_plugin_registry_internal_import | 5/5 | 0 | 0 | 15645 | 3129.0 |
| strict_visible_file | `skilladmit_selected_with_precondition_only` | T6_template_resource_cwd_path | 5/5 | 0 | 0 | 14619 | 2923.8 |

## Derived Comparisons

| comparison | value |
| --- | --- |
| strict_precondition_only_success_delta_vs_selected | 1 |
| strict_precondition_only_token_delta_vs_selected | 11225 |
| strict_raw_memory_success_delta_vs_no_experience | 2 |
| strict_raw_memory_token_delta_vs_no_experience | -364 |
| strict_selected_success_delta_vs_no_experience | 1 |
| strict_selected_token_delta_vs_no_experience | -2763 |
| tree_all_skills_success_delta_vs_selected | 1 |
| tree_all_skills_token_delta_vs_selected | 6312 |
| tree_precondition_context_success_delta_vs_selected | 0 |
| tree_precondition_context_token_delta_vs_selected | 5268 |
| tree_raw_memory_success_delta_vs_no_experience | 1 |
| tree_raw_memory_token_delta_vs_no_experience | -1455 |
| tree_selected_success_delta_vs_no_experience | 0 |
| tree_selected_token_delta_vs_no_experience | -917 |

## Failures

| setting | strategy | task | template | public_hidden | neg | used_artifact | short diagnosis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_001 | T1_optional_integration_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_002 | T1_optional_integration_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_003 | T1_optional_integration_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_004 | T1_optional_integration_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_005 | T1_optional_integration_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_006 | T2_application_package_local_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_007 | T2_application_package_local_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_008 | T2_application_package_local_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_009 | T2_application_package_local_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_010 | T2_application_package_local_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_011 | T3_dual_use_command_module | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_012 | T3_dual_use_command_module | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_013 | T3_dual_use_command_module | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_014 | T3_dual_use_command_module | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_015 | T3_dual_use_command_module | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_016 | T4_repo_config_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_017 | T4_repo_config_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_018 | T4_repo_config_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_019 | T4_repo_config_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_020 | T4_repo_config_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_021 | T5_plugin_registry_internal_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_022 | T5_plugin_registry_internal_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_023 | T5_plugin_registry_internal_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_024 | T5_plugin_registry_internal_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_025 | T5_plugin_registry_internal_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_026 | T6_template_resource_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_027 | T6_template_resource_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_028 | T6_template_resource_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_029 | T6_template_resource_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `forced_bad_artifact` | hard_v3_agent_030 | T6_template_resource_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| tree_aware | `no_experience` | hard_v3_agent_013 | T3_dual_use_command_module | 0 | 1 | none | The script uses a relative import which fails when run directly as a file. We need to make the import work both as a package module and a... |
| tree_aware | `promoted_rules` | hard_v3_agent_029 | T6_template_resource_cwd_path | 1 | 1 | promoted_rules | The renderer uses a relative path that is incorrect when the script is run from the job_delta directory. The template file is located in ... |
| tree_aware | `skilladmit_selected` | hard_v3_agent_027 | T6_template_resource_cwd_path | 0 | 1 | skilladmit_selected | The renderer uses a relative path for the template, which fails when the current working directory is not the repository root. Fix by usi... |
| tree_aware | `skilladmit_selected_with_precondition_context` | hard_v3_agent_027 | T6_template_resource_cwd_path | 0 | 1 | skilladmit_selected_with_precondition_context | FileNotFoundError due to relative path used when script runs from job_beta subdirectory. Need to anchor path to repository root using __f... |
| strict_visible_file | `distilled_skills_all` | hard_v3_agent_014 | T3_dual_use_command_module | 1 | 1 | distilled_skills_all | The script uses a relative import (from .payload) which fails when executed directly. Need to change import strategy to work both as dire... |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_001 | T1_optional_integration_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_002 | T1_optional_integration_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_003 | T1_optional_integration_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_004 | T1_optional_integration_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_005 | T1_optional_integration_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_006 | T2_application_package_local_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_007 | T2_application_package_local_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_008 | T2_application_package_local_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_009 | T2_application_package_local_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_010 | T2_application_package_local_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_011 | T3_dual_use_command_module | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_012 | T3_dual_use_command_module | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_013 | T3_dual_use_command_module | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_014 | T3_dual_use_command_module | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_015 | T3_dual_use_command_module | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_016 | T4_repo_config_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_017 | T4_repo_config_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_018 | T4_repo_config_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_019 | T4_repo_config_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_020 | T4_repo_config_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_021 | T5_plugin_registry_internal_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_022 | T5_plugin_registry_internal_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_023 | T5_plugin_registry_internal_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_024 | T5_plugin_registry_internal_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_025 | T5_plugin_registry_internal_import | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_026 | T6_template_resource_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_027 | T6_template_resource_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_028 | T6_template_resource_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_029 | T6_template_resource_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `forced_bad_artifact` | hard_v3_agent_030 | T6_template_resource_cwd_path | 1 | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `no_experience` | hard_v3_agent_022 | T5_plugin_registry_internal_import | 0 | 0 | none | The import path in plugins_beta/main.py references a non-existent top-level catalog module. Since we cannot create a top-level registry p... |
| strict_visible_file | `no_experience` | hard_v3_agent_025 | T5_plugin_registry_internal_import | 0 | 0 | none | The import `from adapters.loader import load_plugin` fails because there is no top-level `adapters` module. Since we cannot create a top-... |
| strict_visible_file | `promoted_rules` | hard_v3_agent_024 | T5_plugin_registry_internal_import | 0 | 1 | promoted_rules | The import 'from extensions.loader import load_plugin' fails because 'extensions' is not a top-level module. It's likely an internal subp... |
| strict_visible_file | `skilladmit_selected` | hard_v3_agent_015 | T3_dual_use_command_module | 0 | 1 | skilladmit_selected | The script fails with ImportError due to relative import when executed directly; modified import to handle both script and package contex... |

## Claim Boundary

Supported:
- Hard v3 is a fresh 30-task downstream validation boundary with hidden verifiers.
- The completed hard_v3 runs contain no parse errors.
- Forced bad artifacts produce systematic negative transfer in both settings: 0/30 with 30 public-pass/hidden-fail cases.
- In the strict visible-file setting, selected + preconditions only reaches 30/30, while ordinary selected reaches 29/30 and no_experience reaches 28/30.
- In the tree-aware setting, all-skills, raw-memory, and bad-dependency-rule contexts reach 30/30, while selected, selected+precondition-context, and no_experience are 29/30.

Not supported:
- Hard v3 does not support a SkillAdmit-selected superiority claim.
- Hard v3 does not support a token-savings claim for SkillAdmit-selected.
- Hard v3 does not show that selected+precondition-context beats ordinary tree-aware selected.
- Hard v3 does not show that raw memory or bad dependency rule are safe admission policies.
- The bad_dependency_rule LLM condition often succeeds because the model does not reliably adhere to the harmful artifact; the forced_bad_artifact condition is the negative-transfer control.
- Do not tune prompts, strategy text, or task design from the observed hard_v3 failures.

## Source Hashes

| run | summary_sha256 | trajectories_sha256 |
| --- | --- | --- |
| `llm_downstream_hard_v3_tree_core_30x2` | `f9544d04ff7e601b` | `acef5a38d78b1533` |
| `llm_downstream_hard_v3_strict_30x8` | `fe155aed1450bc04` | `501171e60b54bac8` |
