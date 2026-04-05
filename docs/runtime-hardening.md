# Runtime Hardening

WF16 hardens the SR8 runtime surface where the local API, storage catalog, settings resolution, and provider readiness can diverge from compiler-core truth.

## What WF16 Seals

- API `/compile` now accepts inline source text or structured payloads only.
- API file-based routes return structured `4xx` responses for expected client failures.
- Catalog writes use a lock plus atomic replace so concurrent saves do not leave partial JSON on disk.
- CLI and API compile paths share one settings-to-`CompileConfig` resolution flow.
- Derivative catalog records preserve derivative semantics instead of overloading canonical `target_class`.
- AWS Bedrock now uses an SDK-backed Converse runtime path, but only reports ready after a live smoke succeeds.

## Remaining Runtime Limits

- CLI and direct library usage still allow local filesystem paths for compile and inspect flows.
- API `/inspect`, `/validate`, `/transform`, `/diff`, `/lint`, `/artifacts`, and `/receipts` remain trusted-local routes tied to local artifact and workspace state.
- API `/inspect` no longer compiles inline source. It accepts trusted-local artifact paths or canonical artifact identifiers only.
- AWS Bedrock readiness stays false until credentials, region, model access, and a live smoke check all line up.

## Validation Commands

```bash
python -m pip install -e .
pytest tests/test_api_compile_security.py tests/test_catalog_concurrency.py tests/test_api_error_mapping.py tests/test_api_cli_settings_parity.py tests/test_derivative_record_semantics.py tests/test_bedrock_readiness_reporting.py tests/test_runtime_break_regressions.py
pytest
ruff check .
mypy src
python -m build
sr8 providers probe
sr8 compile examples/product_prd.md --rule-only
```
