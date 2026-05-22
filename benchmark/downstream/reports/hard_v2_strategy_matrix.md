# Hard v2 Strategy Matrix

Generated at UTC: `2026-05-22T05:14:29.817313+00:00`

This report snapshots hard_v2 downstream summaries and trajectory hashes so updated run directories are detectable.

## Strategy Matrix

| setting | run | strategy | success | neg | public_hidden | adherence | parse | tokens | avg_tokens | tree_rows | visible_rows |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| canary_visible_file | `llm_downstream_hard_v2_canary_5x2` | `no_experience` | 4/5 | 1 | 1 | 5 | 0 | 12775 | 2555.0 | 0 | 5 |
| canary_visible_file | `llm_downstream_hard_v2_canary_5x2` | `skilladmit_selected` | 5/5 | 0 | 0 | 5 | 0 | 13840 | 2768.0 | 0 | 5 |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | 0/25 | 25 | 25 | 25 | 0 | 0 | 0.0 | 0 | 25 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `bad_dependency_rule` | 22/25 | 2 | 0 | 3 | 0 | 75724 | 3029.0 | 0 | 25 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `distilled_skills_all` | 25/25 | 0 | 0 | 25 | 0 | 84986 | 3399.4 | 0 | 25 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | 0/25 | 25 | 25 | 25 | 0 | 0 | 0.0 | 0 | 25 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `no_experience` | 24/25 | 0 | 0 | 25 | 0 | 59272 | 2370.9 | 0 | 25 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `promoted_rules` | 21/25 | 4 | 1 | 25 | 0 | 77858 | 3114.3 | 0 | 25 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `raw_memory` | 22/25 | 3 | 0 | 25 | 0 | 56941 | 2277.6 | 0 | 25 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `skilladmit_selected` | 23/25 | 2 | 0 | 25 | 0 | 66608 | 2664.3 | 0 | 25 |
| tree_aware | `llm_downstream_hard_v2_tree_25x2` | `no_experience` | 23/25 | 2 | 0 | 25 | 0 | 51548 | 2061.9 | 25 | 25 |
| tree_aware | `llm_downstream_hard_v2_tree_25x2` | `skilladmit_selected` | 25/25 | 0 | 0 | 25 | 0 | 57597 | 2303.9 | 25 | 25 |
| strict_precondition_only | `llm_downstream_hard_v2_precondition_only_25` | `skilladmit_selected_with_precondition_only` | 24/25 | 1 | 0 | 25 | 0 | 72316 | 2892.6 | 0 | 25 |
| tree_aware_precondition_context | `llm_downstream_hard_v2_selected_precondition_25` | `skilladmit_selected_with_precondition_context` | 25/25 | 0 | 0 | 25 | 0 | 67504 | 2700.2 | 25 | 25 |
| replication_tree_aware | `llm_downstream_hard_v2_replication_tree_selected_25` | `skilladmit_selected` | 25/25 | 0 | 0 | 25 | 0 | 52144 | 2085.8 | 25 | 25 |
| replication_tree_aware_precondition_context | `llm_downstream_hard_v2_replication_selected_precondition_25` | `skilladmit_selected_with_precondition_context` | 25/25 | 0 | 0 | 25 | 0 | 64150 | 2566.0 | 25 | 25 |
| replication_strict_precondition_only | `llm_downstream_hard_v2_replication_precondition_only_25` | `skilladmit_selected_with_precondition_only` | 23/25 | 2 | 1 | 25 | 0 | 77487 | 3099.5 | 0 | 25 |

## Template Matrix

| setting | run | strategy | template | success | neg | public_hidden | tokens | avg_tokens |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| canary_visible_file | `llm_downstream_hard_v2_canary_5x2` | `no_experience` | T1_unused_missing_import_hard | 1/1 | 0 | 0 | 1979 | 1979.0 |
| canary_visible_file | `llm_downstream_hard_v2_canary_5x2` | `no_experience` | T2_local_module_import_hard | 1/1 | 0 | 0 | 2398 | 2398.0 |
| canary_visible_file | `llm_downstream_hard_v2_canary_5x2` | `no_experience` | T3_script_relative_import_hard | 1/1 | 0 | 0 | 2690 | 2690.0 |
| canary_visible_file | `llm_downstream_hard_v2_canary_5x2` | `no_experience` | T4_cwd_sensitive_path_hard | 0/1 | 1 | 1 | 3260 | 3260.0 |
| canary_visible_file | `llm_downstream_hard_v2_canary_5x2` | `no_experience` | T5_package_internal_import_hard | 1/1 | 0 | 0 | 2448 | 2448.0 |
| canary_visible_file | `llm_downstream_hard_v2_canary_5x2` | `skilladmit_selected` | T1_unused_missing_import_hard | 1/1 | 0 | 0 | 1258 | 1258.0 |
| canary_visible_file | `llm_downstream_hard_v2_canary_5x2` | `skilladmit_selected` | T2_local_module_import_hard | 1/1 | 0 | 0 | 2824 | 2824.0 |
| canary_visible_file | `llm_downstream_hard_v2_canary_5x2` | `skilladmit_selected` | T3_script_relative_import_hard | 1/1 | 0 | 0 | 3734 | 3734.0 |
| canary_visible_file | `llm_downstream_hard_v2_canary_5x2` | `skilladmit_selected` | T4_cwd_sensitive_path_hard | 1/1 | 0 | 0 | 3455 | 3455.0 |
| canary_visible_file | `llm_downstream_hard_v2_canary_5x2` | `skilladmit_selected` | T5_package_internal_import_hard | 1/1 | 0 | 0 | 2569 | 2569.0 |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | T1_unused_missing_import_hard | 0/5 | 5 | 5 | 0 | 0.0 |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | T2_local_module_import_hard | 0/5 | 5 | 5 | 0 | 0.0 |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | T3_script_relative_import_hard | 0/5 | 5 | 5 | 0 | 0.0 |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | T4_cwd_sensitive_path_hard | 0/5 | 5 | 5 | 0 | 0.0 |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | T5_package_internal_import_hard | 0/5 | 5 | 5 | 0 | 0.0 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `bad_dependency_rule` | T1_unused_missing_import_hard | 5/5 | 0 | 0 | 7781 | 1556.2 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `bad_dependency_rule` | T2_local_module_import_hard | 4/5 | 0 | 0 | 16024 | 3204.8 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `bad_dependency_rule` | T3_script_relative_import_hard | 4/5 | 1 | 0 | 17713 | 3542.6 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `bad_dependency_rule` | T4_cwd_sensitive_path_hard | 4/5 | 1 | 0 | 15463 | 3092.6 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `bad_dependency_rule` | T5_package_internal_import_hard | 5/5 | 0 | 0 | 18743 | 3748.6 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `distilled_skills_all` | T1_unused_missing_import_hard | 5/5 | 0 | 0 | 9318 | 1863.6 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `distilled_skills_all` | T2_local_module_import_hard | 5/5 | 0 | 0 | 18119 | 3623.8 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `distilled_skills_all` | T3_script_relative_import_hard | 5/5 | 0 | 0 | 19235 | 3847.0 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `distilled_skills_all` | T4_cwd_sensitive_path_hard | 5/5 | 0 | 0 | 18203 | 3640.6 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `distilled_skills_all` | T5_package_internal_import_hard | 5/5 | 0 | 0 | 20111 | 4022.2 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | T1_unused_missing_import_hard | 0/5 | 5 | 5 | 0 | 0.0 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | T2_local_module_import_hard | 0/5 | 5 | 5 | 0 | 0.0 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | T3_script_relative_import_hard | 0/5 | 5 | 5 | 0 | 0.0 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | T4_cwd_sensitive_path_hard | 0/5 | 5 | 5 | 0 | 0.0 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | T5_package_internal_import_hard | 0/5 | 5 | 5 | 0 | 0.0 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `no_experience` | T1_unused_missing_import_hard | 5/5 | 0 | 0 | 7571 | 1514.2 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `no_experience` | T2_local_module_import_hard | 4/5 | 0 | 0 | 12928 | 2585.6 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `no_experience` | T3_script_relative_import_hard | 5/5 | 0 | 0 | 13093 | 2618.6 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `no_experience` | T4_cwd_sensitive_path_hard | 5/5 | 0 | 0 | 14033 | 2806.6 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `no_experience` | T5_package_internal_import_hard | 5/5 | 0 | 0 | 11647 | 2329.4 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `promoted_rules` | T1_unused_missing_import_hard | 5/5 | 0 | 0 | 7848 | 1569.6 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `promoted_rules` | T2_local_module_import_hard | 4/5 | 1 | 0 | 19735 | 3947.0 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `promoted_rules` | T3_script_relative_import_hard | 5/5 | 0 | 0 | 17015 | 3403.0 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `promoted_rules` | T4_cwd_sensitive_path_hard | 3/5 | 2 | 0 | 17527 | 3505.4 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `promoted_rules` | T5_package_internal_import_hard | 4/5 | 1 | 1 | 15733 | 3146.6 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `raw_memory` | T1_unused_missing_import_hard | 5/5 | 0 | 0 | 9171 | 1834.2 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `raw_memory` | T2_local_module_import_hard | 5/5 | 0 | 0 | 9646 | 1929.2 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `raw_memory` | T3_script_relative_import_hard | 5/5 | 0 | 0 | 14054 | 2810.8 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `raw_memory` | T4_cwd_sensitive_path_hard | 2/5 | 3 | 0 | 14017 | 2803.4 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `raw_memory` | T5_package_internal_import_hard | 5/5 | 0 | 0 | 10053 | 2010.6 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `skilladmit_selected` | T1_unused_missing_import_hard | 5/5 | 0 | 0 | 6917 | 1383.4 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `skilladmit_selected` | T2_local_module_import_hard | 5/5 | 0 | 0 | 14204 | 2840.8 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `skilladmit_selected` | T3_script_relative_import_hard | 5/5 | 0 | 0 | 15722 | 3144.4 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `skilladmit_selected` | T4_cwd_sensitive_path_hard | 3/5 | 2 | 0 | 15118 | 3023.6 |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `skilladmit_selected` | T5_package_internal_import_hard | 5/5 | 0 | 0 | 14647 | 2929.4 |
| tree_aware | `llm_downstream_hard_v2_tree_25x2` | `no_experience` | T1_unused_missing_import_hard | 5/5 | 0 | 0 | 8125 | 1625.0 |
| tree_aware | `llm_downstream_hard_v2_tree_25x2` | `no_experience` | T2_local_module_import_hard | 5/5 | 0 | 0 | 7850 | 1570.0 |
| tree_aware | `llm_downstream_hard_v2_tree_25x2` | `no_experience` | T3_script_relative_import_hard | 4/5 | 1 | 0 | 14384 | 2876.8 |
| tree_aware | `llm_downstream_hard_v2_tree_25x2` | `no_experience` | T4_cwd_sensitive_path_hard | 4/5 | 1 | 0 | 11977 | 2395.4 |
| tree_aware | `llm_downstream_hard_v2_tree_25x2` | `no_experience` | T5_package_internal_import_hard | 5/5 | 0 | 0 | 9212 | 1842.4 |
| tree_aware | `llm_downstream_hard_v2_tree_25x2` | `skilladmit_selected` | T1_unused_missing_import_hard | 5/5 | 0 | 0 | 6605 | 1321.0 |
| tree_aware | `llm_downstream_hard_v2_tree_25x2` | `skilladmit_selected` | T2_local_module_import_hard | 5/5 | 0 | 0 | 10765 | 2153.0 |
| tree_aware | `llm_downstream_hard_v2_tree_25x2` | `skilladmit_selected` | T3_script_relative_import_hard | 5/5 | 0 | 0 | 18147 | 3629.4 |
| tree_aware | `llm_downstream_hard_v2_tree_25x2` | `skilladmit_selected` | T4_cwd_sensitive_path_hard | 5/5 | 0 | 0 | 13850 | 2770.0 |
| tree_aware | `llm_downstream_hard_v2_tree_25x2` | `skilladmit_selected` | T5_package_internal_import_hard | 5/5 | 0 | 0 | 8230 | 1646.0 |
| strict_precondition_only | `llm_downstream_hard_v2_precondition_only_25` | `skilladmit_selected_with_precondition_only` | T1_unused_missing_import_hard | 5/5 | 0 | 0 | 10064 | 2012.8 |
| strict_precondition_only | `llm_downstream_hard_v2_precondition_only_25` | `skilladmit_selected_with_precondition_only` | T2_local_module_import_hard | 5/5 | 0 | 0 | 14947 | 2989.4 |
| strict_precondition_only | `llm_downstream_hard_v2_precondition_only_25` | `skilladmit_selected_with_precondition_only` | T3_script_relative_import_hard | 4/5 | 1 | 0 | 16284 | 3256.8 |
| strict_precondition_only | `llm_downstream_hard_v2_precondition_only_25` | `skilladmit_selected_with_precondition_only` | T4_cwd_sensitive_path_hard | 5/5 | 0 | 0 | 17928 | 3585.6 |
| strict_precondition_only | `llm_downstream_hard_v2_precondition_only_25` | `skilladmit_selected_with_precondition_only` | T5_package_internal_import_hard | 5/5 | 0 | 0 | 13093 | 2618.6 |
| tree_aware_precondition_context | `llm_downstream_hard_v2_selected_precondition_25` | `skilladmit_selected_with_precondition_context` | T1_unused_missing_import_hard | 5/5 | 0 | 0 | 9326 | 1865.2 |
| tree_aware_precondition_context | `llm_downstream_hard_v2_selected_precondition_25` | `skilladmit_selected_with_precondition_context` | T2_local_module_import_hard | 5/5 | 0 | 0 | 11986 | 2397.2 |
| tree_aware_precondition_context | `llm_downstream_hard_v2_selected_precondition_25` | `skilladmit_selected_with_precondition_context` | T3_script_relative_import_hard | 5/5 | 0 | 0 | 19866 | 3973.2 |
| tree_aware_precondition_context | `llm_downstream_hard_v2_selected_precondition_25` | `skilladmit_selected_with_precondition_context` | T4_cwd_sensitive_path_hard | 5/5 | 0 | 0 | 15243 | 3048.6 |
| tree_aware_precondition_context | `llm_downstream_hard_v2_selected_precondition_25` | `skilladmit_selected_with_precondition_context` | T5_package_internal_import_hard | 5/5 | 0 | 0 | 11083 | 2216.6 |
| replication_tree_aware | `llm_downstream_hard_v2_replication_tree_selected_25` | `skilladmit_selected` | T1_unused_missing_import_hard | 5/5 | 0 | 0 | 7342 | 1468.4 |
| replication_tree_aware | `llm_downstream_hard_v2_replication_tree_selected_25` | `skilladmit_selected` | T2_local_module_import_hard | 5/5 | 0 | 0 | 9974 | 1994.8 |
| replication_tree_aware | `llm_downstream_hard_v2_replication_tree_selected_25` | `skilladmit_selected` | T3_script_relative_import_hard | 5/5 | 0 | 0 | 15653 | 3130.6 |
| replication_tree_aware | `llm_downstream_hard_v2_replication_tree_selected_25` | `skilladmit_selected` | T4_cwd_sensitive_path_hard | 5/5 | 0 | 0 | 12689 | 2537.8 |
| replication_tree_aware | `llm_downstream_hard_v2_replication_tree_selected_25` | `skilladmit_selected` | T5_package_internal_import_hard | 5/5 | 0 | 0 | 6486 | 1297.2 |
| replication_tree_aware_precondition_context | `llm_downstream_hard_v2_replication_selected_precondition_25` | `skilladmit_selected_with_precondition_context` | T1_unused_missing_import_hard | 5/5 | 0 | 0 | 10157 | 2031.4 |
| replication_tree_aware_precondition_context | `llm_downstream_hard_v2_replication_selected_precondition_25` | `skilladmit_selected_with_precondition_context` | T2_local_module_import_hard | 5/5 | 0 | 0 | 11410 | 2282.0 |
| replication_tree_aware_precondition_context | `llm_downstream_hard_v2_replication_selected_precondition_25` | `skilladmit_selected_with_precondition_context` | T3_script_relative_import_hard | 5/5 | 0 | 0 | 18715 | 3743.0 |
| replication_tree_aware_precondition_context | `llm_downstream_hard_v2_replication_selected_precondition_25` | `skilladmit_selected_with_precondition_context` | T4_cwd_sensitive_path_hard | 5/5 | 0 | 0 | 14043 | 2808.6 |
| replication_tree_aware_precondition_context | `llm_downstream_hard_v2_replication_selected_precondition_25` | `skilladmit_selected_with_precondition_context` | T5_package_internal_import_hard | 5/5 | 0 | 0 | 9825 | 1965.0 |
| replication_strict_precondition_only | `llm_downstream_hard_v2_replication_precondition_only_25` | `skilladmit_selected_with_precondition_only` | T1_unused_missing_import_hard | 5/5 | 0 | 0 | 10326 | 2065.2 |
| replication_strict_precondition_only | `llm_downstream_hard_v2_replication_precondition_only_25` | `skilladmit_selected_with_precondition_only` | T2_local_module_import_hard | 5/5 | 0 | 0 | 14713 | 2942.6 |
| replication_strict_precondition_only | `llm_downstream_hard_v2_replication_precondition_only_25` | `skilladmit_selected_with_precondition_only` | T3_script_relative_import_hard | 4/5 | 1 | 1 | 17025 | 3405.0 |
| replication_strict_precondition_only | `llm_downstream_hard_v2_replication_precondition_only_25` | `skilladmit_selected_with_precondition_only` | T4_cwd_sensitive_path_hard | 4/5 | 1 | 0 | 18554 | 3710.8 |
| replication_strict_precondition_only | `llm_downstream_hard_v2_replication_precondition_only_25` | `skilladmit_selected_with_precondition_only` | T5_package_internal_import_hard | 5/5 | 0 | 0 | 16869 | 3373.8 |

## Failures

| setting | run | strategy | task | template | public_hidden | used_artifact | short diagnosis |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| canary_visible_file | `llm_downstream_hard_v2_canary_5x2` | `no_experience` | hard_v2_py_import_016 | T4_cwd_sensitive_path_hard | 1 | none | Missing data file 'runner_alpha/data/alpha.txt' causing FileNotFoundError when loader.py attempts to read it. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_001 | T1_unused_missing_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_002 | T1_unused_missing_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_003 | T1_unused_missing_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_004 | T1_unused_missing_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_005 | T1_unused_missing_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_006 | T2_local_module_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_007 | T2_local_module_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_008 | T2_local_module_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_009 | T2_local_module_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_010 | T2_local_module_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_011 | T3_script_relative_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_012 | T3_script_relative_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_013 | T3_script_relative_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_014 | T3_script_relative_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_015 | T3_script_relative_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_016 | T4_cwd_sensitive_path_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_017 | T4_cwd_sensitive_path_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_018 | T4_cwd_sensitive_path_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_019 | T4_cwd_sensitive_path_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_020 | T4_cwd_sensitive_path_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_021 | T5_package_internal_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_022 | T5_package_internal_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_023 | T5_package_internal_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_024 | T5_package_internal_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| forced_bad_standalone | `llm_downstream_hard_v2_forced_bad_25` | `forced_bad_artifact` | hard_v2_py_import_025 | T5_package_internal_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `bad_dependency_rule` | hard_v2_py_import_009 | T2_local_module_import_hard | 0 | none | The code imports a missing 'parser' module. Since we cannot create top-level stubs, we need to provide the missing functionality within the project structure... |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `bad_dependency_rule` | hard_v2_py_import_015 | T3_script_relative_import_hard | 0 | none | Relative import fails when script is run directly; changed to conditional import based on __name__ to preserve both script and package behavior. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `bad_dependency_rule` | hard_v2_py_import_018 | T4_cwd_sensitive_path_hard | 0 | none | The test runs main.py from the runner_gamma directory, but load_value() uses a relative path 'data/gamma.txt' which doesn't exist there. Need to adjust path ... |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_001 | T1_unused_missing_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_002 | T1_unused_missing_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_003 | T1_unused_missing_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_004 | T1_unused_missing_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_005 | T1_unused_missing_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_006 | T2_local_module_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_007 | T2_local_module_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_008 | T2_local_module_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_009 | T2_local_module_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_010 | T2_local_module_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_011 | T3_script_relative_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_012 | T3_script_relative_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_013 | T3_script_relative_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_014 | T3_script_relative_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_015 | T3_script_relative_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_016 | T4_cwd_sensitive_path_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_017 | T4_cwd_sensitive_path_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_018 | T4_cwd_sensitive_path_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_019 | T4_cwd_sensitive_path_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_020 | T4_cwd_sensitive_path_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_021 | T5_package_internal_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_022 | T5_package_internal_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_023 | T5_package_internal_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_024 | T5_package_internal_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `forced_bad_artifact` | hard_v2_py_import_025 | T5_package_internal_import_hard | 1 | forced_bad_artifact | Deterministically applying the task-provided bad artifact to measure negative transfer. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `no_experience` | hard_v2_py_import_008 | T2_local_module_import_hard | 0 | none | The 'service' module is imported but doesn't exist in the repository. This is causing the ModuleNotFoundError when the test tries to import gamma_app.main. T... |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `promoted_rules` | hard_v2_py_import_008 | T2_local_module_import_hard | 0 | promoted_rules | The import 'from service import run_service' in gamma_app/main.py uses an absolute import, but the module 'service' is not found in the Python path. Based on... |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `promoted_rules` | hard_v2_py_import_018 | T4_cwd_sensitive_path_hard | 0 | promoted_rules | The test runs main.py from runner_gamma directory, but data/gamma.txt doesn't exist relative to that directory. The data file likely exists at a different lo... |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `promoted_rules` | hard_v2_py_import_019 | T4_cwd_sensitive_path_hard | 0 | promoted_rules | Path('data/delta.txt') is relative to cwd, which is runner_delta when the test runs. The data file likely exists at a different location (repo root data/). F... |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `promoted_rules` | hard_v2_py_import_022 | T5_package_internal_import_hard | 1 | promoted_rules | The 'engine' module is missing, causing import failure. Creating a local 'engine' package with 'worker' module to satisfy the import. |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `raw_memory` | hard_v2_py_import_016 | T4_cwd_sensitive_path_hard | 0 | raw_memory | The loader.py uses a relative path that only works when run from the repository root. When the test sets cwd to 'runner_alpha', the path becomes invalid beca... |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `raw_memory` | hard_v2_py_import_018 | T4_cwd_sensitive_path_hard | 0 | raw_memory | Path('data/gamma.txt') is relative to CWD, so when main.py is run from runner_gamma/ it looks for runner_gamma/data/gamma.txt. Fix by resolving path relative... |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `raw_memory` | hard_v2_py_import_020 | T4_cwd_sensitive_path_hard | 0 | raw_memory | The path 'data/omega.txt' in loader.py is relative to the current working directory. When main.py is executed from runner_omega/, the file cannot be found. N... |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `skilladmit_selected` | hard_v2_py_import_019 | T4_cwd_sensitive_path_hard | 0 | skilladmit_selected | The test runs main.py from the 'runner_delta' subdirectory, causing a relative path 'data/delta.txt' to fail. The fix anchors the path to the script's locati... |
| strict_visible_file | `llm_downstream_hard_v2_full_25x6` | `skilladmit_selected` | hard_v2_py_import_020 | T4_cwd_sensitive_path_hard | 0 | skilladmit_selected | loader.py uses a relative path that fails when main.py is executed from a different directory. Need to anchor the path using __file__ to resolve relative to ... |
| tree_aware | `llm_downstream_hard_v2_tree_25x2` | `no_experience` | hard_v2_py_import_011 | T3_script_relative_import_hard | 0 | none | The script uses relative import which fails when run directly as __main__. Need to adjust import for direct execution while preserving package behavior. |
| tree_aware | `llm_downstream_hard_v2_tree_25x2` | `no_experience` | hard_v2_py_import_016 | T4_cwd_sensitive_path_hard | 0 | none | The script fails because it's looking for data/alpha.txt relative to the runner_alpha directory, but the data directory is at the project root. Fix by using ... |
| strict_precondition_only | `llm_downstream_hard_v2_precondition_only_25` | `skilladmit_selected_with_precondition_only` | hard_v2_py_import_012 | T3_script_relative_import_hard | 0 | skilladmit_selected_with_precondition_only | The script is executed directly via `python clipkg_beta/main.py`, but uses a relative import (`from .tools import format_value`) which fails because Python d... |
| replication_strict_precondition_only | `llm_downstream_hard_v2_replication_precondition_only_25` | `skilladmit_selected_with_precondition_only` | hard_v2_py_import_012 | T3_script_relative_import_hard | 1 | skilladmit_selected_with_precondition_only | The script clipkg_beta/main.py uses a relative import (from .tools) but is executed directly via python path/to/file.py rather than as a module. This causes ... |
| replication_strict_precondition_only | `llm_downstream_hard_v2_replication_precondition_only_25` | `skilladmit_selected_with_precondition_only` | hard_v2_py_import_018 | T4_cwd_sensitive_path_hard | 0 | skilladmit_selected_with_precondition_only | The code uses a relative path that assumes current working directory is the repo root, but the subprocess runs from runner_gamma subdirectory |

## Stability Groups

| group | success values | token values | failure tasks |
| --- | --- | --- | --- |
| tree_aware_skilladmit_selected | [25, 25] | [57597, 52144] | llm_downstream_hard_v2_tree_25x2: none; llm_downstream_hard_v2_replication_tree_selected_25: none |
| tree_aware_selected_precondition_context | [25, 25] | [67504, 64150] | llm_downstream_hard_v2_selected_precondition_25: none; llm_downstream_hard_v2_replication_selected_precondition_25: none |
| strict_precondition_only | [24, 23] | [72316, 77487] | llm_downstream_hard_v2_precondition_only_25: hard_v2_py_import_012; llm_downstream_hard_v2_replication_precondition_only_25: hard_v2_py_import_012,hard_v2_py_import_018 |

## Source Hashes

| run | summary_sha256 | trajectories_sha256 |
| --- | --- | --- |
| `llm_downstream_hard_v2_canary_5x2` | `f3871b2c22f6b891` | `7aea6cfaced47cf0` |
| `llm_downstream_hard_v2_forced_bad_25` | `00c948a714722de7` | `7d72e9580606855c` |
| `llm_downstream_hard_v2_full_25x6` | `aaa4ddda178e546d` | `b5cecc5b1d882d29` |
| `llm_downstream_hard_v2_tree_25x2` | `8f9a451282744323` | `21cac9fc80ca97b1` |
| `llm_downstream_hard_v2_precondition_only_25` | `634f318fc2d8b643` | `0c5bbf2d04e0d809` |
| `llm_downstream_hard_v2_selected_precondition_25` | `ef9c0292db345bb0` | `514921d44c7e22df` |
| `llm_downstream_hard_v2_replication_tree_selected_25` | `8c680c4a238b4239` | `0288786a19aa8904` |
| `llm_downstream_hard_v2_replication_selected_precondition_25` | `6c068c371bb735cf` | `0e0588553fbfb8e4` |
| `llm_downstream_hard_v2_replication_precondition_only_25` | `3b58624eb5101a32` | `12569afc718a8153` |
