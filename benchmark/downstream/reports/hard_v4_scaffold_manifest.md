# Hard v4 Scaffold Manifest

Generated at UTC: `2026-05-22T15:03:42.737147+00:00`

Stage: `scaffold_frozen_no_llm_evidence`

This is a scaffold freeze record, not an LLM downstream result.

## Summary

| field | value |
| --- | --- |
| family | python_coding_agent_downstream_hard_v4 |
| tasks_dir | `benchmark/downstream_hard_v4/tasks` |
| task_count | 24 |
| file_count | 244 |
| size_bytes | 71750 |
| task_tree_sha256 | `cac5718008d867ea84c7c0722612989c2b76647ad07b74701063ca4a8b2c2460` |

## Template Counts

| template | tasks |
| --- | --- |
| T1_optional_telemetry_import | 4 |
| T2_src_layout_package_import | 4 |
| T3_dual_entrypoint_command | 4 |
| T4_workspace_config_resolution | 4 |
| T5_resource_template_resolution | 4 |
| T6_plugin_registry_namespace | 4 |

## Gold Skill Counts

| gold_skill | tasks |
| --- | --- |
| Remove Unused Missing Imports | 4 |
| Repair CWD-Sensitive File Paths | 8 |
| Repair Local Module Imports | 4 |
| Repair Package-Internal Bare Imports | 4 |
| Repair Relative Imports for Script Execution | 4 |

## Task Rows

| task_id | template | gold_skill | repo_files | task_files | task_tree_sha256 |
| --- | --- | --- | --- | --- | --- |
| hard_v4_agent_001 | T1_optional_telemetry_import | Remove Unused Missing Imports | 7 | 9 | `1139516ac9fb7c15` |
| hard_v4_agent_002 | T1_optional_telemetry_import | Remove Unused Missing Imports | 7 | 9 | `f970b80186362e04` |
| hard_v4_agent_003 | T1_optional_telemetry_import | Remove Unused Missing Imports | 7 | 9 | `ac9d9c0ce05cfd8c` |
| hard_v4_agent_004 | T1_optional_telemetry_import | Remove Unused Missing Imports | 7 | 9 | `c78210db1eb6273a` |
| hard_v4_agent_005 | T2_src_layout_package_import | Repair Local Module Imports | 8 | 10 | `eed25d61aac38637` |
| hard_v4_agent_006 | T2_src_layout_package_import | Repair Local Module Imports | 8 | 10 | `d62bfb66cdce3c66` |
| hard_v4_agent_007 | T2_src_layout_package_import | Repair Local Module Imports | 8 | 10 | `73b901bbb2fd2fc7` |
| hard_v4_agent_008 | T2_src_layout_package_import | Repair Local Module Imports | 8 | 10 | `d98c0bc402986d9b` |
| hard_v4_agent_009 | T3_dual_entrypoint_command | Repair Relative Imports for Script Execution | 9 | 11 | `f72e1cd04fc8c162` |
| hard_v4_agent_010 | T3_dual_entrypoint_command | Repair Relative Imports for Script Execution | 9 | 11 | `fe8bfbf8999e48f9` |
| hard_v4_agent_011 | T3_dual_entrypoint_command | Repair Relative Imports for Script Execution | 9 | 11 | `0900f2c8bc09edb1` |
| hard_v4_agent_012 | T3_dual_entrypoint_command | Repair Relative Imports for Script Execution | 9 | 11 | `a63c552f831582bc` |
| hard_v4_agent_013 | T4_workspace_config_resolution | Repair CWD-Sensitive File Paths | 8 | 10 | `c878953b88fe2f3e` |
| hard_v4_agent_014 | T4_workspace_config_resolution | Repair CWD-Sensitive File Paths | 8 | 10 | `c2cf4cf97bc5548b` |
| hard_v4_agent_015 | T4_workspace_config_resolution | Repair CWD-Sensitive File Paths | 8 | 10 | `2870b1bc395c55d2` |
| hard_v4_agent_016 | T4_workspace_config_resolution | Repair CWD-Sensitive File Paths | 8 | 10 | `68f15392c4370468` |
| hard_v4_agent_017 | T5_resource_template_resolution | Repair CWD-Sensitive File Paths | 8 | 10 | `b3f1aa847ccfeb8d` |
| hard_v4_agent_018 | T5_resource_template_resolution | Repair CWD-Sensitive File Paths | 8 | 10 | `5be2924a8c8405ec` |
| hard_v4_agent_019 | T5_resource_template_resolution | Repair CWD-Sensitive File Paths | 8 | 10 | `f4eee4b9401b0d67` |
| hard_v4_agent_020 | T5_resource_template_resolution | Repair CWD-Sensitive File Paths | 8 | 10 | `44399d710c78c8de` |
| hard_v4_agent_021 | T6_plugin_registry_namespace | Repair Package-Internal Bare Imports | 9 | 11 | `96823a3ff334f345` |
| hard_v4_agent_022 | T6_plugin_registry_namespace | Repair Package-Internal Bare Imports | 9 | 11 | `32b764bdacb5471f` |
| hard_v4_agent_023 | T6_plugin_registry_namespace | Repair Package-Internal Bare Imports | 9 | 11 | `338b1e029d44e645` |
| hard_v4_agent_024 | T6_plugin_registry_namespace | Repair Package-Internal Bare Imports | 9 | 11 | `f172ee5a92dffffe` |

## Checker Summary

| field | value |
| --- | --- |
| total | 24 |
| initial_failed | 24 |
| gold_passed | 24 |
| forced_public_passed | 24 |
| forced_verifier_failed | 24 |

## Claim Boundary

Supported:
- hard_v4 task scaffold is generated and hashable.
- hard_v4 deterministic checker can validate scaffold invariants.
- hard_v4 can be used as a future clean downstream boundary after explicit freeze.

Not supported:
- hard_v4 does not provide LLM downstream evidence yet.
- hard_v4 does not support any SkillAdmit success claim yet.
- hard_v4 should not be prompt-tuned from observed failures while kept as clean evidence.

## Source Hashes

| path | exists | sha256 |
| --- | --- | --- |
| `scripts/build_downstream_hard_v4_tasks.py` | True | `b3fa2fa29f733378` |
| `scripts/check_downstream_hard_v4_tasks.py` | True | `6b0f32972cd7d705` |
| `scripts/export_hard_v4_scaffold_manifest.py` | True | `b85339d89cd871f2` |
| `docs/llm_downstream_hard_v4.md` | True | `ed41b445ec26bd98` |
