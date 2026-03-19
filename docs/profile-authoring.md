# Profile Authoring

This guide explains how to add a new profile in SR8.

## Profile Contract

Profiles are defined with `ProfileDefinition`:

- `name`
- `target_class`
- `required_rules`
- optional `warning_rules`
- `supported_transform_targets`
- optional `section_order_hints`

## Step-by-Step

1. Add a new module in `src/sr8/profiles/`, for example `my_profile.py`.
2. Implement rules as predicate functions that receive `IntentArtifact`.
3. Build `ProfileRule` entries and a `ProfileDefinition`.
4. Register the profile in `src/sr8/profiles/registry.py`.
5. Add tests for:
   - profile availability via `list_profiles()`
   - validation error/warning behavior
   - transform compatibility expectations
6. Update docs:
   - `docs/profiles.md`
   - `README.md` profile list if public-facing

## Minimal Example Pattern

```python
from sr8.models.intent_artifact import IntentArtifact
from sr8.profiles.base import ProfileDefinition, ProfileRule

def _has_objective(artifact: IntentArtifact) -> bool:
    return artifact.objective.strip() != ""

MY_PROFILE = ProfileDefinition(
    name="my_profile",
    target_class="my_target",
    required_rules=(
        ProfileRule(
            code="VAL-PRO-MY-001",
            message="my_profile requires objective",
            path="objective",
            severity="error",
            check=_has_objective,
        ),
    ),
    supported_transform_targets=("markdown_plan",),
)
```

## Quality Checklist

- profile name is unique
- rule codes are unique
- rule messages are actionable
- supported transform targets are real registry targets
- tests cover pass and fail paths
