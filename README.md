# SR8

SR8 is a local-first intent compiler that turns weakly structured intent into canonical, inspectable artifacts and derivative outputs.

## Why SR8 Exists

Teams need a deterministic way to convert intent into structured artifacts that can be validated, transformed, persisted, diffed, and linted without requiring network services.

## Install

```bash
python -m pip install -e .
```

## Quickstart

```bash
sr8 init
sr8 compile examples/product_prd.md --profile prd --out ./.sr8/artifacts/canonical/
sr8 transform ./.sr8/artifacts/canonical/latest.json --to markdown_prd --out ./.sr8/artifacts/derivative/
sr8 lint ./.sr8/artifacts/canonical/latest.json
sr8 diff tests/fixtures/diff/base_artifact.json tests/fixtures/diff/changed_artifact.json
sr8 list
```

## Core Concepts

- Canonical artifacts are the source of truth.
- Profiles are overlays that shape validation and transform compatibility.
- Derivatives are render outputs with parent lineage.
- Workspace persistence stores artifacts, receipts, and index records under `.sr8`.

## CLI Commands

```bash
sr8 --help
sr8 version
sr8 init
sr8 compile <source>
sr8 validate <artifact>
sr8 inspect <artifact-or-source>
sr8 transform <artifact> --to <target>
sr8 diff <left> <right>
sr8 lint <artifact>
sr8 list
sr8 show <record-or-artifact-id>
```

## Profiles

Built-in profiles include `generic`, `prd`, `repo_audit`, `plan`, `research_brief`, `procedure`, `media_spec`, and `prompt_pack`.

## Transforms

Supported derivative targets:
- `markdown_prd`
- `markdown_plan`
- `markdown_research_brief`
- `markdown_procedure`
- `markdown_prompt_pack`

## Storage and Receipts

Workspace layout:
- `.sr8/artifacts/canonical/`
- `.sr8/artifacts/derivative/`
- `.sr8/receipts/compile/`
- `.sr8/receipts/transform/`
- `.sr8/index/catalog.json`

## Diff and Lint

- `sr8 diff` performs semantic field-level comparison with impact levels.
- `sr8 lint` runs explicit artifact quality rules and returns structured findings.

## Project Status

SR8 is sealed as production-grade v1 for local compiler workflows.

## Release Notes

See [CHANGELOG.md](CHANGELOG.md).
