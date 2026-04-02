# SR8 v1.1 Closure Receipt

## Closed gaps
- GAP01: AC5 fixture floor enforced with 25-plus golden fixtures.
- GAP02: source hash preserved through normalization, lineage, and receipts.
- GAP03: artifact-to-artifact recompilation works from file path and in-memory artifact input.
- GAP04: `whitepaper_outline` and `code_task_graph` are fully wired profiles.
- GAP05: extraction adapter interface exists with registered rule-first default.
- GAP06: config defaults flow through `pydantic-settings`.
- GAP07: performance smoke gates execute with explicit thresholds.
- GAP08: one canonical artifact produces at least three downstream derivatives.
- GAP09: extraction trust is surfaced in inspect, validation, lint, and receipts.
- GAP10: field-quality warnings now cover weak or missing critical fields.

## Partially closed gaps
None.

## Intentionally deferred gaps
- Default model-assisted extraction remains deferred.
- Performance gates remain smoke-level rather than benchmark-grade.

## Files changed by domain
- Extraction: adapters, confidence, trace modules, rules, and signals.
- Compiler: compile and recompile flow, inspect surface, and receipt summaries.
- Profiles: `whitepaper_outline`, `code_task_graph`, and transform compatibility.
- Tests: acceptance proof, trust, field quality, CLI, receipt, and performance coverage.
- Docs: closure, extraction trust, recompile, schema, profile, architecture, and changelog updates.

## Validation results
See the WF11 validation command block in `AGENTS.md`.

## Net effect on PRD compliance
SR8 v1.1 is materially closer to the original PRD. The remaining deferrals are explicit rather than accidental.
