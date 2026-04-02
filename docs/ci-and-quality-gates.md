# CI and Quality Gates

SR8 uses small, explicit workflows so release and hygiene checks stay readable.

## Active Gates

- `ci.yml` runs lint, typecheck, tests, example smoke, docs checks, hygiene, frontend CI, and package build smoke.
- `docs-check.yml` verifies the docs and workflow contract tests that protect the release surface.
- `hygiene.yml` verifies repository layout and runs the cleanup audit scripts.
- `release.yml` reruns gates on semantic tags, builds distributions, publishes via trusted publishing, and creates the GitHub Release.
- `codeql.yml` runs scheduled and branch-based Python code scanning.
- `dependency-review.yml` blocks pull requests with high-severity dependency risk.

## Deferred Gates

- `frontend-ci.yml` is present and wired, but it intentionally degrades to a no-op until `frontend/package.json` exists.

## Local Commands

- `python -m pip install -e ".[dev]"`
- `pytest tests/test_docs_commands.py tests/test_repo_structure.py tests/test_release_workflow_contracts.py`
- `python scripts/cleanup/check_repo_layout.py`
- `python scripts/cleanup/repo_audit.py --check`

