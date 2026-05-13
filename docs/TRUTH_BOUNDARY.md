# SR8 v1 Truth Boundary

SR8 v1 is a local-first, LLM-assisted intent-to-canonical compiler.

The LLM proposes structure. SR8 compiles, validates, records, transforms, and proves it.

## In Scope

- Ingest text, Markdown, JSON, YAML, files, and structured payloads through `src/sr8/ingest/`.
- Compile input into the canonical `IntentArtifact` model in `src/sr8/models/intent_artifact.py`.
- Run deterministic rules mode without provider calls.
- Run assist mode through provider adapters in `src/sr8/adapters/` and strict extraction parsing in `src/sr8/compiler/model_assist.py`.
- Run auto mode as rules first, with LLM assist only when configured and needed.
- Validate artifacts through `src/sr8/validate/engine.py`.
- Record receipts through `src/sr8/models/receipts.py` and `src/sr8/storage/receipts.py`.
- Transform canonical artifacts into native Markdown and SRXML files through `src/sr8/transform/`.
- Generate proof packets with `sr8 proof run`.

## Out Of Scope

- SR8 v1 is not a general app, site, repo, or code generator.
- SR8 v1 is not the full SROS runtime.
- SR8 v1 does not execute SRXML.
- SR8 v1 does not trust raw LLM output without typed parsing and validation.
- SR8 v1 does not require a provider for rules baseline operation.

## Claim Mapping

| Claim | Source or command |
| --- | --- |
| Canonical schema | `src/sr8/models/intent_artifact.py`, `sr8 schema export` |
| Compile modes | `src/sr8/models/compile_config.py`, `src/sr8/compiler/compile.py` |
| LLM assist provenance | `src/sr8/compiler/model_assist.py`, `src/sr8/models/receipts.py` |
| Provider diagnostics | `src/sr8/adapters/`, `sr8 providers probe` |
| API compile path safety | `src/sr8/api/dependencies.py`, `tests/test_api_compile_security.py` |
| Native transforms | `src/sr8/transform/`, `src/sr8/storage/save.py` |
| Proof packet | `src/sr8/cli.py`, `sr8 proof run` |
