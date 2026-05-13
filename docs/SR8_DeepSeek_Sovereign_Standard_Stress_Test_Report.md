# SR8 DeepSeek Sovereign Standard Stress Test Report

Generated: 2026-05-10T16:59:47Z
Model profile: DeepSeek-V4-Flash
Provider: azure_openai
Mode: live

## Repo truth summary

- Python package manager: pyproject.toml with hatchling.
- CLI entry point: sr8 = sr8.cli:app.
- Compile path: sr8.compiler.compile.compile_intent.
- Azure integration: sr8.adapters.azure_openai_adapter.AzureOpenAIAdapter.
- SRXML RC2 integration: sr8.srxml.rc2 render and validate functions.
- Validation source: SRXML artifact files on disk, not inferred flags.
- Root .env exists and was used through pydantic settings without printing keys.

## Metrics

- Test count: 100
- Attempted runs: 100
- Successful material runs: 100
- API failures: 0
- Compiler failures: 0
- Validator failures: 0
- Material file errors: 0
- Unique compiled intents: 100
- Unique source hashes: 100
- Unique artifact IDs: 100
- Overall pass rate: 0.95
- First-pass SRXML validity: 1.0
- Repair success rate: 1.0
- False completion rate: 0.0
- Blocked-state correctness: 1.0
- Artifact class coverage: 1.0

## Material outputs

- Raw outputs: stress_tests/sovereign_standard/deepseek/raw_outputs/
- Parsed JSON: stress_tests/sovereign_standard/deepseek/parsed/
- SRXML artifacts: stress_tests/sovereign_standard/deepseek/artifacts/
- File validation: stress_tests/sovereign_standard/deepseek/validation/
- Per-case receipts: stress_tests/sovereign_standard/deepseek/receipts/

## Failure patterns

- blocked_state_overtriggered: 5

## Readiness verdict

deepseek_pass_meets_stress_targets

## Remaining specific-domain gaps

- Legal, finance, healthcare, and compliance cases remain compiler-behavior tests only, not domain correctness validation.
- Live Azure service availability and deployment policy can still block model execution independently of SR8.
- External factual research was not performed by this harness.
