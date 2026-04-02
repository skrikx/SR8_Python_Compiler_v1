# AGENTS.md - SR8 Repository Law

## Project Purpose and Boundary

SR8 is a local-first intent compiler in final ship phase.
Compiler, frontend, workflow, and runtime hardening surfaces are real in this repository state.
Do not claim broader API exposure, final release seal, or validation beyond the documented ship ladder and route policy.

## Directory Map

- `src/sr8/` - SR8 package root
- `src/sr8/models/` - Pydantic domain models
- `src/sr8/ingest/` - ingest lane
- `src/sr8/normalize/` - normalization lane
- `src/sr8/extract/` - extraction lane
- `src/sr8/profiles/` - profile system lane
- `src/sr8/validate/` - validation lane
- `src/sr8/transform/` - transformation lane
- `src/sr8/storage/` - persistence lane
- `tests/` - automated tests
- `tests/fixtures/` - test fixture inputs
- `artifacts/` - generated artifacts
- `receipts/` - compilation receipts
- `docs/` - repository documentation

## Run Commands

Install:

```bash
python -m pip install -e .
python -m pip install -e ".[dev]"
```

CLI:

```bash
sr8 --help
sr8 version
sr8 init
sr8 inspect
```

Validation:

```bash
pytest
ruff check .
mypy src
```

## Engineering Conventions

- Use datamodel-first design with Pydantic v2.
- Keep modules small and explicit.
- Type annotate public functions.
- Keep CLI output stable and user-oriented.
- Favor minimal diffs over broad refactors.
- Add or update tests for any behavior change.

## Rules for Changing Code

- Implement real structure immediately where possible.
- Avoid dead abstractions.
- Keep architecture local-first and modular.
- Maintain separation across ingest, normalize, extract, validate, transform, and storage lanes.

## Do-Not Rules

- Do not fabricate completion claims.
- Do not merge code that fails lint, type check, or tests without explicit rationale.
- Do not add hidden network dependencies for core compiler flow.
- Do not leave TODO placeholders unless explicitly requested.

## Workflow Execution Discipline

- Scope each workflow to its objective.
- Verify with executable commands, not assumptions.
- Report exact command outcomes.
- Leave repository in a passing state.
- For WF11-class closure work, use read-heavy parallel analysis first and integrate write-heavy changes sequentially.
- Do not claim a gap is closed unless code and tests both exist for that gap.

## Final Ship Law

- `/compile` in the API must never read arbitrary user-supplied local filesystem paths.
- `/inspect` in the API is trusted-local artifact inspection only. Do not let it compile inline source.
- Route exposure claims must match `docs/public-api-exposure.md`.
- `pytest`, `ruff check .`, `mypy src`, `python -m build`, `cd frontend && npm ci`, `cd frontend && npm run check`, and `cd frontend && npm run build` are final ship blockers.
- Public release state must stay archive-clean. Do not ship `node_modules`, `.svelte-kit`, `dist`, build caches, `.sr8`, benchmark result outputs, transient example outputs, or ad hoc audit bundles.
- Do not issue a final ship receipt unless the W17 ladder passes in a normal environment.

## Definition of Done by Workflow

For each workflow, done means:

- Target files and modules exist and are wired.
- Commands required by that workflow run successfully or are explicitly scoped with rationale.
- Documentation and tests reflect current behavior.
- No claims exceed implemented capability.

## WF11 Gap Closure Rules

- Treat ingest `source_hash` as deterministic and stable through normalization, storage, receipts, inspect, and recompile.
- Extraction trust must be tied to real extraction behavior. Decorative confidence output does not count.
- New profiles or target classes must include transform compatibility, fixtures, and tests.
- Recompile flows must preserve lineage clarity by recording parent artifact IDs and a distinct `recompile` step.
- Performance gates may be smoke-level, but they must execute and use explicit thresholds.

## WF11 Validation Commands

```bash
python -m pip install -e .
pytest tests/test_ac5_fixture_count.py tests/test_ac7_multi_derivative.py tests/test_recompile_flow.py tests/test_source_hash_lineage.py tests/test_extraction_confidence.py tests/test_extraction_adapter_registry.py tests/test_whitepaper_outline_profile.py tests/test_code_task_graph_profile.py tests/test_performance_gate.py tests/test_field_population_quality.py
pytest
ruff check .
mypy src
sr8 recompile tests/fixtures/recompile/base_artifact.json --profile whitepaper_outline
sr8 inspect tests/fixtures/recompile/base_artifact.json
sr8 compile tests/fixtures/weak_inputs/minimal_directive.txt
sr8 transform tests/fixtures/golden/canonical_prd.json --to markdown_prd
sr8 transform tests/fixtures/golden/canonical_prd.json --to markdown_plan
sr8 transform tests/fixtures/golden/canonical_prd.json --to markdown_prompt_pack
```

## WF17 Validation Commands

```bash
python -m pip install -e .
pytest
ruff check .
mypy src
python -m build
sr8 providers probe
sr8 compile examples/product_prd.md --rule-only
cd frontend && npm ci
cd frontend && npm run check
cd frontend && npm run build
pytest tests/test_release_archive_cleanliness.py
```
