# SR8 Feature Matrix

| Surface | Status | Notes |
| --- | --- | --- |
| CLI compile | Available | `sr8 compile` with profile selection and output path support |
| Chat frontdoor compile | Available | `compile:` and intake-resume flows terminate in canonical artifacts |
| CLI validate | Available | `sr8 validate` for artifact validation |
| CLI inspect | Available | Supports artifact paths and source inputs |
| CLI transform | Available | Transform targets enforced by profile compatibility |
| CLI diff | Available | Semantic field diff with impact levels |
| CLI lint | Available | Rule-based lint report (`L001` to `L010`) |
| Workspace storage | Available | `.sr8` local persistence, catalog, receipts |
| Python compile API | Available | `sr8.compiler.compile_intent` |
| FastAPI endpoints | Available | `/health`, `/compile`, `/validate`, `/transform` |
| XML package outputs | Available | promptunit_package, `sr8_prompt`, and safe alternative package renderers |
| Breadth registries | Available | entry modes, artifact families, and delivery targets are code-owned |
| CI quality gates | Available | lint, mypy, pytest, examples smoke, build smoke |
| Frontend compile surface | Available | local Svelte product surface validated by `npm run check` and `npm run build` |
| Release publish | Bounded | tag-driven release path exists, but public publish still depends on GitHub release creation and PyPI trusted publisher configuration |
| Code scanning | Available | CodeQL and dependency review workflows |

## Hardening Confidence Matrix

| Area | Confidence | Notes |
| --- | --- | --- |
| Compiler core truth | High | Canonical schema, weak-intent recovery, lineage, receipts, diff, lint, and readiness are test-backed |
| API route truth | High | Route contracts, exposure classes, and 4xx/5xx behavior are explicit and tested |
| Provider parity | Medium-high | Providers expose truthful readiness metadata; Bedrock remains intentionally bounded until live smoke succeeds |
| Operator console | Medium-high | Frontend now tracks real route envelopes, trust metadata, validation, and async job state |
| Replay safety | High | Idempotent compile replay and async job reuse are covered by replay tests |
| Chaos resilience | Medium-high | Malformed inputs and provider outage fallback are covered, but distributed and multi-process chaos is still out of scope |
