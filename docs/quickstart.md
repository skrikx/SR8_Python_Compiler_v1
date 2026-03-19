# Quickstart

```bash
python -m pip install -e .
sr8 init
sr8 compile examples/founder_ask.md --profile generic --out ./.sr8/artifacts/canonical/
sr8 inspect ./.sr8/artifacts/canonical/latest.json
sr8 transform ./.sr8/artifacts/canonical/latest.json --to markdown_plan --out ./.sr8/artifacts/derivative/
sr8 lint ./.sr8/artifacts/canonical/latest.json
```
