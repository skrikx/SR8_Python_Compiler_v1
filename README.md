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

SR8 is an intent compiler for AI systems.

It turns weakly structured requests into typed, validated, receipted, lineage-bearing artifacts that can be transformed, audited, and used safely downstream.

Public packaging stays simple: SR8 is a local-first intent compiler. Deeper in the repo, SR8 is the working proof layer for what this project calls governed artifact infrastructure.

Automation map: [assets/badges/README_BADGES.md](assets/badges/README_BADGES.md)

## What SR8 Is

SR8 is a real installable Python package with:

- deterministic ingest, normalization, extraction, and canonical assembly
- profile overlays with readiness-aware validation
- receipts, lineage, catalog persistence, semantic diff, and lint
- transform outputs for markdown and XML package surfaces
- local CLI, Python API, FastAPI, and local frontend surfaces
- provider descriptors and readiness reporting across supported adapters
- benchmark, self-hosting, and release-automation rails
- chat-frontdoor and intake-resume flows that still terminate in canonical artifacts

## What SR8 Is Not

SR8 is not:

- just a prompt formatter or markdown utility
- a hosted multi-tenant orchestration platform
- the full SROS runtime or a universal execution kernel
- a claim that every downstream runtime path is already universally sealed

SR8 is the proof layer. It compiles intent into governed artifacts that can feed larger systems safely.

## Why SR8 Exists

Most teams do not fail because they lack prompts. They fail because weak requests enter downstream systems without typed structure, visible trust surfaces, or clear readiness boundaries.

SR8 exists to make that handoff legible. It gives operators a local-first path from messy intent to inspectable artifacts before those artifacts are transformed, reviewed, or handed into downstream execution.

## What This Repository Proves Now

This repository proves that SR8 can:

- compile weakly structured input into typed canonical artifacts
- apply profile-specific validation and readiness states
- preserve receipts, lineage, and catalog records locally
- generate derivative outputs for product, plan, research, procedure, prompt-pack, and XML package targets
- expose the same core compiler through CLI, Python API, FastAPI, and a local frontend
- surface provider truth honestly, including bounded AWS Bedrock readiness
- support chat-native intake and resume flows without bypassing compiler-core truth
- benchmark and self-host parts of its own workflow surface

## Bounded Claims and Runtime Truth

SR8 is local-first and honest about its limits.

- Trusted-local API routes should stay behind operator control.
- Model-assisted paths are additive, not the baseline truth path.
- AWS Bedrock support is real, but runtime readiness remains credential, region, model-access, and live-smoke dependent.
- This repository proves execution-prep and downstream handoff surfaces. Stronger claims about live governed runtime execution should be tied to runtime receipts outside this repo.

## Use Cases

SR8 is already suited to:

- prompt and specification compilation
- product PRD generation
- research brief generation
- repository audit and code task graph flows
- operational procedure and governed request flows
- chat-frontdoor intake, refine, and resume flows
- XML package emission for downstream delivery targets
- execution-prep artifacts that feed larger governed stacks

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

Chat-frontdoor success path:

```text
compile: Objective: Draft a launch plan
Scope:
- Phase one
Success Criteria:
- Ready to ship
```

If the request is underspecified, SR8 returns an intake XML form. Submit the completed form again with `resume:`.

## Core Concepts

- Canonical artifact: typed source of truth for compiled intent.
- Profile overlay: validation and readiness behavior without forking schema.
- Derivative artifact: rendered output from canonical input.
- Receipt: machine-readable record of persistence and transform events.
- Catalog: local index for artifact lookup and listing.
- Breadth registries: code-owned maps for entry modes, artifact families, and delivery targets.

More detail: [docs/index.md](docs/index.md)

## Product Surfaces

- CLI: [docs/cli-reference.md](docs/cli-reference.md)
- Python API: [docs/python-api.md](docs/python-api.md)
- Public API boundary: [docs/public-api-exposure.md](docs/public-api-exposure.md)
- Frontend: [docs/frontend.md](docs/frontend.md)
- Chat front door: [docs/chat-frontdoor.md](docs/chat-frontdoor.md)
- XML package contract: [docs/xml-package-contract.md](docs/xml-package-contract.md)
- Breadth registries: [docs/breadth-registries.md](docs/breadth-registries.md)
- Benchmarking: [docs/benchmarking.md](docs/benchmarking.md)

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

Built-in transform targets include:

- `markdown_prd`
- `markdown_plan`
- `markdown_research_brief`
- `markdown_procedure`
- `markdown_prompt_pack`
- `xml_promptunit_package`
- `xml_sr8_prompt`
- `xml_safe_alternative_package`

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
- `sr8 lint` runs explicit lint rules and trust-surface checks.

Reference: [docs/diff-and-lint.md](docs/diff-and-lint.md)

## Architecture and Positioning

- System boundary: [ARCHITECTURE.md](ARCHITECTURE.md)
- Overview: [docs/overview.md](docs/overview.md)
- Claims matrix: [assets/release/claims-matrix.md](assets/release/claims-matrix.md)
- Release summary: [assets/release/release-summary.md](assets/release/release-summary.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, quality gates, extension authoring, and PR expectations.

## Security

See [SECURITY.md](SECURITY.md) and [docs/security.md](docs/security.md).

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## Project Status

SR8 is a hardened local-first compiler release with real package surfaces across CLI, API, frontend, frontdoor, XML packaging, registries, benchmarking, and release automation.

## Release Notes

See [CHANGELOG.md](CHANGELOG.md), [docs/release-automation.md](docs/release-automation.md), [assets/social/github-release-card.md](assets/social/github-release-card.md), and [assets/release/release-polish-receipt.md](assets/release/release-polish-receipt.md).
