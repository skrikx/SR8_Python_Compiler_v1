# SR8

[![CI](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/ci.yml)
[![Docs Check](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/docs-check.yml/badge.svg?branch=main)](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/docs-check.yml)
[![Frontend CI](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/frontend-ci.yml/badge.svg?branch=main)](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/frontend-ci.yml)
[![Hygiene](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/hygiene.yml/badge.svg?branch=main)](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/hygiene.yml)
[![Release](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/release.yml/badge.svg?tag=v1.2.4)](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/release.yml)
[![CodeQL](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/codeql.yml)
[![GitHub Release](https://img.shields.io/github/v/release/skrikx/SR8_Python_Compiler_v1)](https://github.com/skrikx/SR8_Python_Compiler_v1/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)

SR8 is a local-first intent compiler for turning weakly structured requests into canonical, inspectable artifacts and derivative outputs.

Automation map: [assets/badges/README_BADGES.md](assets/badges/README_BADGES.md)

## What SR8 Is

SR8 compiles intent into a typed canonical artifact with:

- deterministic ingest, normalization, extraction, and assembly
- profile overlays and validation
- transform outputs (for example markdown PRD and plan formats)
- local storage, receipts, and catalog indexing
- diff and lint quality gates

## Why SR8 Exists

Teams often need a repeatable way to convert intent into structured artifacts without relying on external services.
SR8 provides that path with a local-first workflow that is easy to test, automate, and audit.

## Install

SR8 requires Python 3.11 or newer.

```bash
python -m pip install -e .
python -m pip install -e ".[dev]"
```

SR8 also supports repo-root `.env` and `.env.local` files for local settings and provider secrets.
Start from `.env.example` and keep real secrets out of git.

For full local product verification:

```bash
cd frontend
npm ci
```

Install guide: [docs/install.md](docs/install.md)

## Quickstart

First success path:

```bash
sr8 init
sr8 compile examples/product_prd.md --profile prd --out ./.sr8/artifacts/canonical/
sr8 transform ./.sr8/artifacts/canonical/latest.json --to markdown_prd --out ./.sr8/artifacts/derivative/
sr8 lint ./.sr8/artifacts/canonical/latest.json
sr8 diff tests/fixtures/diff/base_artifact.json tests/fixtures/diff/changed_artifact.json
sr8 list
```

## Core Concepts

- Canonical artifact: source of truth for compiled intent.
- Profile overlay: applies profile constraints and validation semantics.
- Derivative artifact: rendered output from canonical input.
- Receipt: machine-readable record of compile or transform persistence.
- Catalog: local index for artifact lookup and listing.

More detail: [docs/index.md](docs/index.md)

## CLI Overview

```bash
sr8 --help
sr8 version
sr8 init
sr8 compile <source> [--profile <profile>] [--source-type text|markdown|json|yaml]
sr8 validate <artifact-path> [--profile <profile>]
sr8 inspect <artifact-or-source>
sr8 transform <artifact-path> --to <target> [--out <dir>]
sr8 diff <left-artifact-or-id> <right-artifact-or-id>
sr8 lint <artifact-or-id>
sr8 list [--kind canonical|derivative] [--profile <profile>] [--path <workspace>]
sr8 show <record-or-artifact-id> [--path <workspace>]
```

Full reference: [docs/cli-reference.md](docs/cli-reference.md)

## Python API Overview

Minimal compile usage:

```python
from sr8.compiler import CompileConfig, compile_intent

result = compile_intent(
    source="examples/founder_ask.md",
    config=CompileConfig(profile="generic"),
)

artifact = result.artifact
print(artifact.artifact_id, artifact.validation.readiness_status)
```

FastAPI app entrypoint:

```python
from sr8.api import app
```

More detail: [docs/python-api.md](docs/python-api.md)
API exposure guidance: [docs/public-api-exposure.md](docs/public-api-exposure.md)

## Profiles

Built-in profiles:

- `generic`
- `prd`
- `repo_audit`
- `plan`
- `research_brief`
- `procedure`
- `media_spec`
- `prompt_pack`
- `whitepaper_outline`
- `code_task_graph`

Reference: [docs/profiles.md](docs/profiles.md)

## Transforms

Built-in transform targets:

- `markdown_prd`
- `markdown_plan`
- `markdown_research_brief`
- `markdown_procedure`
- `markdown_prompt_pack`

Reference: [docs/transforms.md](docs/transforms.md)

## Storage and Receipts

Default workspace layout:

- `.sr8/artifacts/canonical/`
- `.sr8/artifacts/derivative/`
- `.sr8/receipts/compile/`
- `.sr8/receipts/transform/`
- `.sr8/index/catalog.json`

Reference: [docs/storage-and-receipts.md](docs/storage-and-receipts.md)

## Diff and Lint

- `sr8 diff` compares semantic fields and classifies impact.
- `sr8 lint` runs explicit lint rules and returns a structured report.

Reference: [docs/diff-and-lint.md](docs/diff-and-lint.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, quality gates, extension authoring, and PR expectations.

## Security

See [SECURITY.md](SECURITY.md) and [docs/security.md](docs/security.md).

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## Project Status

SR8 is a hardened local-first compiler release with extraction trust, provider portability, local product surfaces, and OSS-grade automation rails.

## Release Notes

See [CHANGELOG.md](CHANGELOG.md) and [docs/release-automation.md](docs/release-automation.md).
