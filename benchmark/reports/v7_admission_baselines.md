# Admission Baseline Report

This report compares simple admission baselines on the selected sample files.

| sample_file | method | correct | total | accuracy | macro_f1 | errors |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| benchmark/admission_samples/v7_blind_admission_samples.jsonl | always_discard | 10 | 50 | 0.200 | 0.067 | 40 |
| benchmark/admission_samples/v7_blind_admission_samples.jsonl | always_store_as_memory | 10 | 50 | 0.200 | 0.067 | 40 |
| benchmark/admission_samples/v7_blind_admission_samples.jsonl | always_distill_into_skill | 10 | 50 | 0.200 | 0.067 | 40 |
| benchmark/admission_samples/v7_blind_admission_samples.jsonl | always_promote_to_rule | 10 | 50 | 0.200 | 0.067 | 40 |
| benchmark/admission_samples/v7_blind_admission_samples.jsonl | always_defer | 10 | 50 | 0.200 | 0.067 | 40 |
| benchmark/admission_samples/v7_blind_admission_samples.jsonl | keyword_level_baseline | 49 | 50 | 0.980 | 0.980 | 1 |
| benchmark/admission_samples/v7_blind_admission_samples.jsonl | skilladmit.controllers.rule_based_controller_v6_frozen | 49 | 50 | 0.980 | 0.980 | 1 |

## Error Summary

### benchmark/admission_samples/v7_blind_admission_samples.jsonl / always_discard

- `sample_v7_skill_docker_healthcheck_exec`: gold=`distill_into_skill`, pred=`discard`, cluster=Docker healthcheck command repaired
- `sample_v7_skill_s3_pagination`: gold=`distill_into_skill`, pred=`discard`, cluster=S3 pagination continuation repaired
- `sample_v7_skill_sqlalchemy_rollback`: gold=`distill_into_skill`, pred=`discard`, cluster=SQLAlchemy session recovery repaired
- `sample_v7_skill_jwt_clock_skew`: gold=`distill_into_skill`, pred=`discard`, cluster=JWT leeway handling repaired
- `sample_v7_skill_nginx_forwarded_proto`: gold=`distill_into_skill`, pred=`discard`, cluster=Reverse-proxy scheme propagation repaired
- `sample_v7_skill_pandas_nullable_int`: gold=`distill_into_skill`, pred=`discard`, cluster=Nullable integer parsing repaired
- `sample_v7_skill_npm_workspace_import`: gold=`distill_into_skill`, pred=`discard`, cluster=NPM workspace package import repaired
- `sample_v7_skill_grpc_deadline_idempotent_retry`: gold=`distill_into_skill`, pred=`discard`, cluster=gRPC deadline retry bounded
- `sample_v7_skill_mime_type_upload`: gold=`distill_into_skill`, pred=`discard`, cluster=Upload MIME type repaired
- `sample_v7_skill_kafka_offset_commit_after_process`: gold=`distill_into_skill`, pred=`discard`, cluster=Kafka offset commit order repaired
- `sample_v7_memory_current_v6_frozen`: gold=`store_as_memory`, pred=`discard`, cluster=Current frozen controller path
- `sample_v7_memory_current_regression_scope`: gold=`store_as_memory`, pred=`discard`, cluster=Current regression scope
- `sample_v7_memory_current_v7_output`: gold=`store_as_memory`, pred=`discard`, cluster=Current v7 output path
- `sample_v7_memory_current_project_root`: gold=`store_as_memory`, pred=`discard`, cluster=Current project root
- `sample_v7_memory_current_docs`: gold=`store_as_memory`, pred=`discard`, cluster=Current handoff document
- `sample_v7_memory_current_python_env`: gold=`store_as_memory`, pred=`discard`, cluster=Current Python environment
- `sample_v7_memory_current_model_endpoint`: gold=`store_as_memory`, pred=`discard`, cluster=Current model endpoint setting
- `sample_v7_memory_current_v7_balance`: gold=`store_as_memory`, pred=`discard`, cluster=Current v7 label balance
- `sample_v7_memory_current_protocol`: gold=`store_as_memory`, pred=`discard`, cluster=Current blind protocol
- `sample_v7_memory_current_prediction_file`: gold=`store_as_memory`, pred=`discard`, cluster=Current v7 prediction output
- ... 20 more errors

### benchmark/admission_samples/v7_blind_admission_samples.jsonl / always_store_as_memory

- `sample_v7_skill_docker_healthcheck_exec`: gold=`distill_into_skill`, pred=`store_as_memory`, cluster=Docker healthcheck command repaired
- `sample_v7_skill_s3_pagination`: gold=`distill_into_skill`, pred=`store_as_memory`, cluster=S3 pagination continuation repaired
- `sample_v7_skill_sqlalchemy_rollback`: gold=`distill_into_skill`, pred=`store_as_memory`, cluster=SQLAlchemy session recovery repaired
- `sample_v7_skill_jwt_clock_skew`: gold=`distill_into_skill`, pred=`store_as_memory`, cluster=JWT leeway handling repaired
- `sample_v7_skill_nginx_forwarded_proto`: gold=`distill_into_skill`, pred=`store_as_memory`, cluster=Reverse-proxy scheme propagation repaired
- `sample_v7_skill_pandas_nullable_int`: gold=`distill_into_skill`, pred=`store_as_memory`, cluster=Nullable integer parsing repaired
- `sample_v7_skill_npm_workspace_import`: gold=`distill_into_skill`, pred=`store_as_memory`, cluster=NPM workspace package import repaired
- `sample_v7_skill_grpc_deadline_idempotent_retry`: gold=`distill_into_skill`, pred=`store_as_memory`, cluster=gRPC deadline retry bounded
- `sample_v7_skill_mime_type_upload`: gold=`distill_into_skill`, pred=`store_as_memory`, cluster=Upload MIME type repaired
- `sample_v7_skill_kafka_offset_commit_after_process`: gold=`distill_into_skill`, pred=`store_as_memory`, cluster=Kafka offset commit order repaired
- `sample_v7_discard_disable_csrf`: gold=`discard`, pred=`store_as_memory`, cluster=Disable CSRF protection globally
- `sample_v7_discard_log_bearer_tokens`: gold=`discard`, pred=`store_as_memory`, cluster=Log bearer tokens for debugging
- `sample_v7_discard_drop_constraints`: gold=`discard`, pred=`store_as_memory`, cluster=Drop database constraints to import data
- `sample_v7_discard_mark_migrations_applied`: gold=`discard`, pred=`store_as_memory`, cluster=Mark migrations applied without running them
- `sample_v7_discard_force_latest_lockfile`: gold=`discard`, pred=`store_as_memory`, cluster=Delete lockfile and upgrade everything
- `sample_v7_discard_swallow_kafka_commit_errors`: gold=`discard`, pred=`store_as_memory`, cluster=Ignore Kafka commit failures
- `sample_v7_discard_commit_base64_secrets`: gold=`discard`, pred=`store_as_memory`, cluster=Commit base64 encoded secrets
- `sample_v7_discard_cors_credentials_wildcard`: gold=`discard`, pred=`store_as_memory`, cluster=Use wildcard CORS with credentials
- `sample_v7_discard_truncate_data_to_fit_schema`: gold=`discard`, pred=`store_as_memory`, cluster=Truncate data to fit schema
- `sample_v7_discard_disable_rate_limits`: gold=`discard`, pred=`store_as_memory`, cluster=Disable rate limits globally
- ... 20 more errors

### benchmark/admission_samples/v7_blind_admission_samples.jsonl / always_distill_into_skill

- `sample_v7_discard_disable_csrf`: gold=`discard`, pred=`distill_into_skill`, cluster=Disable CSRF protection globally
- `sample_v7_discard_log_bearer_tokens`: gold=`discard`, pred=`distill_into_skill`, cluster=Log bearer tokens for debugging
- `sample_v7_discard_drop_constraints`: gold=`discard`, pred=`distill_into_skill`, cluster=Drop database constraints to import data
- `sample_v7_discard_mark_migrations_applied`: gold=`discard`, pred=`distill_into_skill`, cluster=Mark migrations applied without running them
- `sample_v7_discard_force_latest_lockfile`: gold=`discard`, pred=`distill_into_skill`, cluster=Delete lockfile and upgrade everything
- `sample_v7_discard_swallow_kafka_commit_errors`: gold=`discard`, pred=`distill_into_skill`, cluster=Ignore Kafka commit failures
- `sample_v7_discard_commit_base64_secrets`: gold=`discard`, pred=`distill_into_skill`, cluster=Commit base64 encoded secrets
- `sample_v7_discard_cors_credentials_wildcard`: gold=`discard`, pred=`distill_into_skill`, cluster=Use wildcard CORS with credentials
- `sample_v7_discard_truncate_data_to_fit_schema`: gold=`discard`, pred=`distill_into_skill`, cluster=Truncate data to fit schema
- `sample_v7_discard_disable_rate_limits`: gold=`discard`, pred=`distill_into_skill`, cluster=Disable rate limits globally
- `sample_v7_memory_current_v6_frozen`: gold=`store_as_memory`, pred=`distill_into_skill`, cluster=Current frozen controller path
- `sample_v7_memory_current_regression_scope`: gold=`store_as_memory`, pred=`distill_into_skill`, cluster=Current regression scope
- `sample_v7_memory_current_v7_output`: gold=`store_as_memory`, pred=`distill_into_skill`, cluster=Current v7 output path
- `sample_v7_memory_current_project_root`: gold=`store_as_memory`, pred=`distill_into_skill`, cluster=Current project root
- `sample_v7_memory_current_docs`: gold=`store_as_memory`, pred=`distill_into_skill`, cluster=Current handoff document
- `sample_v7_memory_current_python_env`: gold=`store_as_memory`, pred=`distill_into_skill`, cluster=Current Python environment
- `sample_v7_memory_current_model_endpoint`: gold=`store_as_memory`, pred=`distill_into_skill`, cluster=Current model endpoint setting
- `sample_v7_memory_current_v7_balance`: gold=`store_as_memory`, pred=`distill_into_skill`, cluster=Current v7 label balance
- `sample_v7_memory_current_protocol`: gold=`store_as_memory`, pred=`distill_into_skill`, cluster=Current blind protocol
- `sample_v7_memory_current_prediction_file`: gold=`store_as_memory`, pred=`distill_into_skill`, cluster=Current v7 prediction output
- ... 20 more errors

### benchmark/admission_samples/v7_blind_admission_samples.jsonl / always_promote_to_rule

- `sample_v7_skill_docker_healthcheck_exec`: gold=`distill_into_skill`, pred=`promote_to_rule`, cluster=Docker healthcheck command repaired
- `sample_v7_skill_s3_pagination`: gold=`distill_into_skill`, pred=`promote_to_rule`, cluster=S3 pagination continuation repaired
- `sample_v7_skill_sqlalchemy_rollback`: gold=`distill_into_skill`, pred=`promote_to_rule`, cluster=SQLAlchemy session recovery repaired
- `sample_v7_skill_jwt_clock_skew`: gold=`distill_into_skill`, pred=`promote_to_rule`, cluster=JWT leeway handling repaired
- `sample_v7_skill_nginx_forwarded_proto`: gold=`distill_into_skill`, pred=`promote_to_rule`, cluster=Reverse-proxy scheme propagation repaired
- `sample_v7_skill_pandas_nullable_int`: gold=`distill_into_skill`, pred=`promote_to_rule`, cluster=Nullable integer parsing repaired
- `sample_v7_skill_npm_workspace_import`: gold=`distill_into_skill`, pred=`promote_to_rule`, cluster=NPM workspace package import repaired
- `sample_v7_skill_grpc_deadline_idempotent_retry`: gold=`distill_into_skill`, pred=`promote_to_rule`, cluster=gRPC deadline retry bounded
- `sample_v7_skill_mime_type_upload`: gold=`distill_into_skill`, pred=`promote_to_rule`, cluster=Upload MIME type repaired
- `sample_v7_skill_kafka_offset_commit_after_process`: gold=`distill_into_skill`, pred=`promote_to_rule`, cluster=Kafka offset commit order repaired
- `sample_v7_discard_disable_csrf`: gold=`discard`, pred=`promote_to_rule`, cluster=Disable CSRF protection globally
- `sample_v7_discard_log_bearer_tokens`: gold=`discard`, pred=`promote_to_rule`, cluster=Log bearer tokens for debugging
- `sample_v7_discard_drop_constraints`: gold=`discard`, pred=`promote_to_rule`, cluster=Drop database constraints to import data
- `sample_v7_discard_mark_migrations_applied`: gold=`discard`, pred=`promote_to_rule`, cluster=Mark migrations applied without running them
- `sample_v7_discard_force_latest_lockfile`: gold=`discard`, pred=`promote_to_rule`, cluster=Delete lockfile and upgrade everything
- `sample_v7_discard_swallow_kafka_commit_errors`: gold=`discard`, pred=`promote_to_rule`, cluster=Ignore Kafka commit failures
- `sample_v7_discard_commit_base64_secrets`: gold=`discard`, pred=`promote_to_rule`, cluster=Commit base64 encoded secrets
- `sample_v7_discard_cors_credentials_wildcard`: gold=`discard`, pred=`promote_to_rule`, cluster=Use wildcard CORS with credentials
- `sample_v7_discard_truncate_data_to_fit_schema`: gold=`discard`, pred=`promote_to_rule`, cluster=Truncate data to fit schema
- `sample_v7_discard_disable_rate_limits`: gold=`discard`, pred=`promote_to_rule`, cluster=Disable rate limits globally
- ... 20 more errors

### benchmark/admission_samples/v7_blind_admission_samples.jsonl / always_defer

- `sample_v7_skill_docker_healthcheck_exec`: gold=`distill_into_skill`, pred=`defer`, cluster=Docker healthcheck command repaired
- `sample_v7_skill_s3_pagination`: gold=`distill_into_skill`, pred=`defer`, cluster=S3 pagination continuation repaired
- `sample_v7_skill_sqlalchemy_rollback`: gold=`distill_into_skill`, pred=`defer`, cluster=SQLAlchemy session recovery repaired
- `sample_v7_skill_jwt_clock_skew`: gold=`distill_into_skill`, pred=`defer`, cluster=JWT leeway handling repaired
- `sample_v7_skill_nginx_forwarded_proto`: gold=`distill_into_skill`, pred=`defer`, cluster=Reverse-proxy scheme propagation repaired
- `sample_v7_skill_pandas_nullable_int`: gold=`distill_into_skill`, pred=`defer`, cluster=Nullable integer parsing repaired
- `sample_v7_skill_npm_workspace_import`: gold=`distill_into_skill`, pred=`defer`, cluster=NPM workspace package import repaired
- `sample_v7_skill_grpc_deadline_idempotent_retry`: gold=`distill_into_skill`, pred=`defer`, cluster=gRPC deadline retry bounded
- `sample_v7_skill_mime_type_upload`: gold=`distill_into_skill`, pred=`defer`, cluster=Upload MIME type repaired
- `sample_v7_skill_kafka_offset_commit_after_process`: gold=`distill_into_skill`, pred=`defer`, cluster=Kafka offset commit order repaired
- `sample_v7_discard_disable_csrf`: gold=`discard`, pred=`defer`, cluster=Disable CSRF protection globally
- `sample_v7_discard_log_bearer_tokens`: gold=`discard`, pred=`defer`, cluster=Log bearer tokens for debugging
- `sample_v7_discard_drop_constraints`: gold=`discard`, pred=`defer`, cluster=Drop database constraints to import data
- `sample_v7_discard_mark_migrations_applied`: gold=`discard`, pred=`defer`, cluster=Mark migrations applied without running them
- `sample_v7_discard_force_latest_lockfile`: gold=`discard`, pred=`defer`, cluster=Delete lockfile and upgrade everything
- `sample_v7_discard_swallow_kafka_commit_errors`: gold=`discard`, pred=`defer`, cluster=Ignore Kafka commit failures
- `sample_v7_discard_commit_base64_secrets`: gold=`discard`, pred=`defer`, cluster=Commit base64 encoded secrets
- `sample_v7_discard_cors_credentials_wildcard`: gold=`discard`, pred=`defer`, cluster=Use wildcard CORS with credentials
- `sample_v7_discard_truncate_data_to_fit_schema`: gold=`discard`, pred=`defer`, cluster=Truncate data to fit schema
- `sample_v7_discard_disable_rate_limits`: gold=`discard`, pred=`defer`, cluster=Disable rate limits globally
- ... 20 more errors

### benchmark/admission_samples/v7_blind_admission_samples.jsonl / keyword_level_baseline

- `sample_v7_skill_mime_type_upload`: gold=`distill_into_skill`, pred=`discard`, cluster=Upload MIME type repaired

### benchmark/admission_samples/v7_blind_admission_samples.jsonl / skilladmit.controllers.rule_based_controller_v6_frozen

- `sample_v7_skill_grpc_deadline_idempotent_retry`: gold=`distill_into_skill`, pred=`promote_to_rule`, cluster=gRPC deadline retry bounded
