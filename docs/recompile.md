# Recompile

Use `sr8 recompile <artifact.json>` to rebuild a canonical artifact while preserving source hash and appending lineage.

Python API:

```python
from sr8.compiler import compile_intent, recompile_artifact

rebuilt = recompile_artifact(existing_artifact, profile="whitepaper_outline")
roundtrip = compile_intent(existing_artifact)
```

Examples:

```bash
sr8 recompile tests/fixtures/recompile/base_artifact.json
sr8 recompile tests/fixtures/recompile/base_artifact.json --profile code_task_graph
sr8 recompile tests/fixtures/recompile/base_artifact.json --profile whitepaper_outline --out ./artifacts/
```

Lineage guarantees:

- original `source_hash` is preserved
- parent artifact ID is appended to lineage
- a distinct `recompile` step is recorded
