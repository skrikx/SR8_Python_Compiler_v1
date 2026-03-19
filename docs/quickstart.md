# Quickstart

Use [getting-started.md](getting-started.md) for the primary first-success flow.

Fast path:

```bash
python -m pip install -e .
python -m pip install -e ".[dev]"
sr8 init
sr8 compile examples/product_prd.md --profile prd --out ./.sr8/artifacts/canonical/
sr8 transform ./.sr8/artifacts/canonical/latest.json --to markdown_prd --out ./.sr8/artifacts/derivative/
sr8 lint ./.sr8/artifacts/canonical/latest.json
```
