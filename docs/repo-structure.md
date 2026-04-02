# Repository Structure

SR8 keeps the source tree narrow and the release surface explicit.

## Primary Areas

- `src/sr8/` contains the compiler, adapters, storage, validation, and transform logic.
- `frontend/` contains the SvelteKit local product surface and typed API client code.
- `tests/` contains executable contracts for CLI, workflows, docs, and repo behavior.
- `docs/` contains user-facing documentation and release/process references.
- `.github/workflows/` contains CI, release, and hygiene automation.
- `scripts/cleanup/` contains repo audit and cleanup utilities.

## Generated Areas

- `.sr8/` stores local workspace artifacts, receipts, and indexes.
- `artifacts/` and `receipts/` are placeholder local output directories only and should remain empty in tracked release state.
- `benchmarks/` stores benchmark corpus inputs and result packs.
- `dist/` and `build/` are packaging outputs.

## Hygiene Rule

Generated areas are expected to be ignored, pruned, or kept as empty placeholders, while source, docs, and workflow files stay checked in and reviewed.
