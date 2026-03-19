# Contributing to SR8

Thanks for contributing to SR8.
This guide covers clean-machine setup, development workflow, extension authoring, and pull request expectations.

## Prerequisites

- Python 3.12 or newer
- Git

## Local Setup

1. Fork and clone the repository.
2. Create and activate a virtual environment.
3. Install SR8 in editable mode with dev dependencies.

```bash
python -m pip install -e .
python -m pip install -e ".[dev]"
```

## Development Commands

Run before opening a pull request:

```bash
ruff check .
mypy src
pytest
python -m build
```

## Run Example Flows

```bash
sr8 init
sr8 compile examples/founder_ask.md --profile generic --out ./.sr8/artifacts/canonical/
sr8 compile examples/product_prd.md --profile prd --out ./.sr8/artifacts/canonical/
sr8 compile examples/repo_audit.md --profile repo_audit --out ./.sr8/artifacts/canonical/
sr8 transform ./.sr8/artifacts/canonical/latest.json --to markdown_plan --out ./.sr8/artifacts/derivative/
sr8 lint ./.sr8/artifacts/canonical/latest.json
```

## Adding a New Profile

1. Create a new profile module in `src/sr8/profiles/`.
2. Define `ProfileDefinition` with:
   - `name`
   - `target_class`
   - `required_rules`
   - optional `warning_rules`
   - `supported_transform_targets`
3. Register the profile in `src/sr8/profiles/registry.py`.
4. Add tests in `tests/` for:
   - profile registry listing
   - profile validation behavior
   - transform compatibility (if relevant)
5. Update docs:
   - `docs/profiles.md`
   - `docs/profile-authoring.md`
   - `README.md` profile list if user-facing.

## Adding a New Transform Target

1. Implement a renderer in `src/sr8/transform/renderers/`.
2. Add a `TransformTargetSpec` entry in `src/sr8/transform/registry.py`.
3. Ensure profile compatibility lists are accurate.
4. Add tests in `tests/` for:
   - successful render
   - incompatible profile rejection
5. Update docs:
   - `docs/transforms.md`
   - `docs/transform-authoring.md`
   - `README.md` transform list if user-facing.

## PR Expectations

- Keep diffs focused on one objective.
- Include tests or doc updates for behavior changes.
- Keep CLI output stable unless the PR explicitly changes it.
- Follow the pull request template:
  - what changed
  - why it changed
  - how it was validated
  - docs/example impact

## Commit and Review Guidance

- Use clear commit messages tied to functional changes.
- Address review comments with follow-up commits.
- Do not force push over unresolved review context unless coordinated.

## Release Etiquette

- Do not publish releases from feature branches.
- Release tags must be semantic and aligned with `pyproject.toml` and `src/sr8/version.py`.
- Follow `docs/release-automation.md` and `RELEASE_CHECKLIST.md` before pushing a release tag.

## Security Reports

For vulnerabilities, do not open a public issue with exploit detail.
Follow [SECURITY.md](SECURITY.md).
