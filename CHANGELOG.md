# Changelog

## [1.2.4] - 2026-04-02

### Added
- Chat frontdoor integration with compile and resume intake flows, plus governance-aware package emission.
- XML package renderers for promptunit_package, sr8_prompt, and safe alternative outputs.
- Breadth registries for entry modes, artifact families, and delivery targets.
- OSS chat compiler assets absorbed into specs, intake, rules, and examples.
- WF19 acceptance tests and documentation for the frontdoor bridge.

### Changed
- CLI and API compile routes now detect chat frontdoor invocations and emit package outputs.
- Transform engine now writes XML derivatives with .xml extensions.

## [1.2.3] - 2026-04-02

### Added
- AWS Bedrock live runtime support through an SDK-backed Converse path.
- Bedrock request-normalization, runtime smoke, non-live fallback, and readiness-state regression coverage.
- Bedrock setup documentation for AWS credentials, region, model access, and live probe enablement.

### Changed
- Bedrock probe now distinguishes configuration, access, live enablement, and actual runtime readiness.
- CLI Bedrock probe output now surfaces accessibility, live enablement, and ready state separately.

## [1.2.2] - 2026-04-02

### Added
- Final public API exposure guidance covering deliberate exposure, trusted-local routes, and the sealed `/inspect` policy.
- Release archive cleanliness contract test and repo skill for rerunning the final ship seal.

### Changed
- API compile and settings configuration failures now resolve to structured `422` responses instead of leaking as `500`.
- API `/inspect` is now artifact-only and no longer compiles inline source.
- Repo ship law, release checklist, and ignore policy now defend archive-clean release state.

## [1.2.1] - 2026-04-02

### Added
- Runtime hardening docs for API input security and storage integrity behavior.
- Regression coverage for API path-ingestion blocking, artifact error mapping, settings parity, catalog concurrency, derivative record semantics, and Bedrock readiness truth.

### Changed
- API `/compile` now accepts inline source text or structured payloads only and rejects arbitrary local filesystem paths.
- API error responses now use a stable structured envelope for expected client-caused failures.
- CLI and API compile paths now share one settings-to-`CompileConfig` resolution flow.
- Storage catalog writes now use a lock plus atomic replace to prevent corruption under concurrent saves.
- Derivative catalog records now preserve derivative semantics instead of overloading `target_class`.
- Bedrock probe output now distinguishes registration and configuration from actual runtime readiness.

## [1.2.0] - 2026-03-19

### Added
- Local benchmark corpus spanning founder, research, repo, procedure, weak-input, and self-hosting tracks.
- Typed eval harness, rubric-backed scoring, JSON/Markdown report writers, and regression comparison reports.
- `sr8 benchmark run` and `sr8 benchmark compare` CLI commands.
- Self-hosting proof cases covering workflow compilation, three-derivative transforms, artifact recompilation, and artifact-eval flows.

### Changed
- SR8 now records reproducible benchmark result packs under `benchmarks/results/`.
- Benchmark scoring explicitly measures faithfulness, completeness, constraint integrity, readiness, trust surface, and transform utility.
- Release documentation now includes benchmark methodology, rubric interpretation, and self-hosting proof limits.

## [1.1.0] - 2026-03-19

### Added
- Extraction adapter registry with deterministic trust tracing and field-level confidence signals.
- Artifact-object and artifact-path recompilation with lineage-safe `recompile` steps.
- `whitepaper_outline` and `code_task_graph` profiles with transform compatibility and tests.
- AC5, AC7, field-quality, trust, and performance smoke tests for the v1.1 hardening pass.
- Repo-local WF11 Codex skill and config for repeatable gap-closure runs.

### Changed
- Source hash preservation now holds from ingest through normalization, receipts, inspect, and recompile.
- CLI inspect output now surfaces source hash and extraction trust summaries.
- Compilation receipts now include trust and lineage summaries.
- Packaging metadata now reflects Python 3.11 support.

## [1.0.0] - 2026-03-19

### Added
- Workflow-complete SR8 release surface with compile, validate, inspect, transform, diff, lint, persistence, receipts, and index.
- Release docs, example corpus, and optional thin FastAPI wrapper.
