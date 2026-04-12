# Python API

SR8 exposes compile functionality as importable Python modules and includes a FastAPI app surface.

## Core Compile API

```python
from sr8.compiler import CompileConfig, compile_intent

result = compile_intent(
    source="examples/founder_ask.md",
    config=CompileConfig(profile="generic"),
)

artifact = result.artifact
receipt = result.receipt
print(
    artifact.artifact_id,
    receipt.compile_kind,
    receipt.compile_truth_summary,
)
```

`CompileConfig` fields:

- `artifact_version`
- `compiler_version`
- `profile`
- `include_raw_source`

`CompilationResult` fields:

- `artifact`
- `receipt`
- `normalized_source`
- `extracted_dimensions`

Truthful compile metadata is exposed on `artifact.metadata` and `receipt`, including:

- `compile_kind`
- `semantic_transform_applied`
- `source_supplied_fields`
- `compiler_derived_fields`
- `unresolved_fields`
- `compile_truth_summary`

## Transform API

```python
from sr8.io.exporters import load_artifact
from sr8.transform.engine import transform_artifact

artifact = load_artifact("examples/outputs/canonical_prd.json")
result = transform_artifact(artifact, "markdown_prd")
print(result.derivative.derivative_id)
```

## Validation API

```python
from sr8.io.exporters import load_artifact
from sr8.validate.engine import validate_artifact

artifact = load_artifact("examples/outputs/canonical_prd.json")
report = validate_artifact(artifact, profile_name=artifact.profile)
print(report.readiness_status)
```

## FastAPI Surface

App entrypoint:

```python
from sr8.api import app
```

Routes:

- `GET /health`
- `POST /compile`
- `POST /validate`
- `POST /transform`

Run locally:

```bash
uvicorn sr8.api.app:app --reload
```
