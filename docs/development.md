# Development

## Setup

```bash
python -m pip install -e .
python -m pip install -e ".[dev]"
```

## Quality Gates

```bash
ruff check .
mypy src
pytest
python -m build
```

## Useful Local Checks

```bash
sr8 --help
sr8 version
sr8 init
sr8 inspect tests/fixtures/ambiguous_request.txt
```

## Project Structure

- `src/sr8/compiler/` compile orchestration
- `src/sr8/ingest/` source loading and type detection
- `src/sr8/normalize/` source cleanup
- `src/sr8/extract/` dimension extraction
- `src/sr8/profiles/` profile rules and registry
- `src/sr8/validate/` validation engine
- `src/sr8/transform/` derivative renderers and registry
- `src/sr8/storage/` workspace persistence and catalog
- `src/sr8/diff/` semantic diff engine
- `src/sr8/lint/` artifact lint rules
- `src/sr8/api/` FastAPI app and routes

## Workflow Expectations

- keep changes scoped and test-backed
- update docs with behavior changes
- avoid hidden network dependencies for core compiler flow
- maintain local-first behavior and deterministic outputs
