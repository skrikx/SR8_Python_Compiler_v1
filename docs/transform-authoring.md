# Transform Authoring

This guide explains how to add a new transform target.

## Transform Contract

Each target is a `TransformTargetSpec` with:

- `target`
- `description`
- `renderer` (`Callable[[IntentArtifact], str]`)
- `compatible_profiles`

## Step-by-Step

1. Create a renderer in `src/sr8/transform/renderers/`.
2. Return deterministic markdown text from `IntentArtifact`.
3. Register target in `src/sr8/transform/registry.py`.
4. Add compatibility to relevant profile definitions.
5. Add tests for:
   - successful rendering
   - profile incompatibility error
6. Update docs:
   - `docs/transforms.md`
   - `README.md` target list if public-facing

## Minimal Renderer Pattern

```python
from sr8.models.intent_artifact import IntentArtifact

def render_markdown_example(artifact: IntentArtifact) -> str:
    return f"# Example - {artifact.artifact_id}\n"
```

Registry entry pattern:

```python
from sr8.transform.types import TransformTargetSpec

TRANSFORM_REGISTRY["markdown_example"] = TransformTargetSpec(
    target="markdown_example",
    description="Render example markdown output.",
    renderer=render_markdown_example,
    compatible_profiles=("generic",),
)
```

## Quality Checklist

- target name is unique
- renderer is deterministic
- newline behavior is consistent
- compatible profile list is correct
- tests cover both acceptance and rejection paths
