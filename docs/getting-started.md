# Getting Started

This page gives a first-success path from clean install to validated artifact output.

## Requirements

- Python 3.11 or newer

## Install

```bash
python -m pip install -e .
python -m pip install -e ".[dev]"
```

## First Success Flow

```bash
sr8 init
sr8 compile examples/product_prd.md --profile prd --out ./.sr8/artifacts/canonical/
sr8 validate ./.sr8/artifacts/canonical/latest.json
sr8 transform ./.sr8/artifacts/canonical/latest.json --to markdown_prd --out ./.sr8/artifacts/derivative/
sr8 lint ./.sr8/artifacts/canonical/latest.json
sr8 list
```

## What to Inspect

- canonical artifact: `.sr8/artifacts/canonical/latest.json`
- derivative markdown: `.sr8/artifacts/derivative/latest.md`
- catalog: `.sr8/index/catalog.json`
- receipts:
  - `.sr8/receipts/compile/`
  - `.sr8/receipts/transform/`

## Next Steps

- Read [CLI Reference](cli-reference.md).
- Review [Profiles](profiles.md) and [Transforms](transforms.md).
- Run [Examples](examples.md).
