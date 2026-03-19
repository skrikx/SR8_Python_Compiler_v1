# AGENTS.md - SR8 Repository Law

## Project Purpose and Boundary

SR8 is an intent compiler scaffold in this phase.
W01 builds an installable package, CLI shell, typed model placeholders, and quality rails.
Do not claim extraction, validation, transformation, or profile execution as complete until those workflows are implemented.

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

## Definition of Done by Workflow

For each workflow, done means:

- Target files and modules exist and are wired.
- Commands required by that workflow run successfully or are explicitly scoped with rationale.
- Documentation and tests reflect current behavior.
- No claims exceed implemented capability.
