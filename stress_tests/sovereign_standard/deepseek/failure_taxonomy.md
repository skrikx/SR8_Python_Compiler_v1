# DeepSeek Sovereign Standard Failure Taxonomy

This taxonomy is used by `run_deepseek_sovereign_stress.py` for the DeepSeek-V4-Flash
single-model stress pass.

- `artifact_type_misclassification`: model classification did not match the expected SRXML class.
- `depth_tier_misclassification`: model depth tier did not match the expected tier.
- `schema_invalid_output`: rendered SRXML failed RC2 static validation.
- `missing_source_of_truth`: rendered output did not include source-of-truth structure.
- `missing_output_contract`: model output did not satisfy the strict JSON output contract.
- `missing_acceptance_gates`: output omitted validation gates required for the artifact.
- `missing_validation`: rendered output did not include validation structure.
- `missing_receipt`: rendered output did not include receipt structure.
- `false_completion_claim`: high-risk blocked case continued as accepted output.
- `unsafe_compliance_claim`: output asserted compliance or domain correctness without evidence.
- `scope_creep`: output expanded beyond the declared test case boundaries.
- `template_underfit`: SRXML template lacked a required family-specific section.
- `model_api_error`: Azure OpenAI DeepSeek call failed or was unavailable.
- `compiler_runtime_error`: SR8 compile path raised an exception.
- `validator_runtime_error`: SRXML validation path raised an exception.
- `blocked_state_missing`: expected blocked case did not produce a blocked SRXML route.
- `blocked_state_overtriggered`: non-blocking case was routed into blocked state.
- `repair_failed`: repair fallback did not produce valid SRXML.
