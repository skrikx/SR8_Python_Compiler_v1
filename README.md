# SR8

SR8 is a domain-agnostic intent compiler scaffold.
It converts weakly structured intent into structured intermediate artifacts that can be inspected, validated, transformed, governed, stored, and executed by downstream systems.

## Current Status

Workflow W01 foundation is implemented.
This repository is installable, includes a CLI shell, typed model skeletons, and baseline quality gates.
Full compiler logic is intentionally out of scope for this workflow.

## Requirements

- Python 3.12+

## Install

```bash
python -m pip install -e .
python -m pip install -e ".[dev]"
```

## CLI Quickstart

```bash
sr8 --help
sr8 version
sr8 init
sr8 inspect
```

## Quality Gates

```bash
pytest
ruff check .
mypy src
```

## Workflow Roadmap Note

W01 establishes repository and tooling rails for later workflows (W02-W07) where ingest, normalization, extraction, profiles, validation logic, transformation, and persistence are implemented.
