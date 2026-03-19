# Profiles

Profiles are overlays applied to canonical artifacts.
They enforce profile intent through validation rules and transform compatibility.

## Available Profiles

- `generic`
- `prd`
- `repo_audit`
- `plan`
- `research_brief`
- `procedure`
- `media_spec`
- `prompt_pack`

## How Profiles Work

Profile behavior is implemented with `ProfileDefinition` in `src/sr8/profiles/base.py`.
Each profile defines:

- `target_class`
- `required_rules`
- optional `warning_rules`
- `supported_transform_targets`
- optional section ordering hints

`apply_profile_overlay` updates profile and target class before validation.

## Usage

```bash
sr8 compile examples/product_prd.md --profile prd --out ./.sr8/artifacts/canonical/
```

## Transform Compatibility

Transform compatibility is enforced by both:

1. transform target compatibility list
2. profile `supported_transform_targets`

If either gate fails, transform raises an explicit `ValueError`.

## Extension

See [profile-authoring.md](profile-authoring.md) for adding new profiles.
