# Install Snippets

## Editable Install

```bash
python -m pip install -e .
```

## Development Install

```bash
python -m pip install -e ".[dev]"
```

## First Success Commands

```bash
sr8 init
sr8 compile examples/product_prd.md --profile prd --out ./.sr8/artifacts/canonical/
sr8 transform ./.sr8/artifacts/canonical/latest.json --to markdown_prd --out ./.sr8/artifacts/derivative/
sr8 lint ./.sr8/artifacts/canonical/latest.json
```
