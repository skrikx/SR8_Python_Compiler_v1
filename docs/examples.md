# Examples

SR8 includes runnable examples in `examples/`.

## Input Examples

- `examples/founder_ask.md` (generic intent)
- `examples/product_prd.md` (product requirement context)
- `examples/repo_audit.md` (repository audit context)

## Output Examples

- `examples/outputs/canonical_generic.json`
- `examples/outputs/canonical_prd.json`
- `examples/outputs/canonical_repo_audit.json`
- `examples/outputs/markdown_prd.md`
- `examples/outputs/markdown_plan.md`
- `examples/outputs/diff_summary.txt`
- `examples/outputs/lint_report.txt`

## Rebuild Example Outputs

```bash
sr8 compile examples/founder_ask.md --profile generic --out examples/outputs
sr8 compile examples/product_prd.md --profile prd --out examples/outputs
sr8 compile examples/repo_audit.md --profile repo_audit --out examples/outputs
sr8 transform examples/outputs/canonical_prd.json --to markdown_prd --out examples/outputs
sr8 transform examples/outputs/canonical_repo_audit.json --to markdown_plan --out examples/outputs
sr8 diff tests/fixtures/diff/base_artifact.json tests/fixtures/diff/changed_artifact.json
sr8 lint tests/fixtures/lint/weak_artifact.json
```

When generating docs assets, save the last two command outputs to:

- `examples/outputs/diff_summary.txt`
- `examples/outputs/lint_report.txt`

## Test Coverage

Examples are guarded by:

- `tests/test_readme_examples.py`
- `tests/test_examples_roundtrip.py`
- `tests/test_docs_commands.py`
