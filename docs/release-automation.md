# Release Automation

SR8 release automation is GitHub-native and built from reusable workflows.
CI validates quality gates on pull requests and protected branches.
Tagged releases rerun gates, build distributions, publish to PyPI through OIDC trusted publishing, and create a GitHub Release.

## Workflow Map

- `.github/workflows/reusable-test.yml`
  - Shared `workflow_call` module for setup, dependency install, lint, typecheck, pytest, and examples smoke.
- `.github/workflows/reusable-build.yml`
  - Shared `workflow_call` module for `python -m build` and optional artifact upload.
- `.github/workflows/ci.yml`
  - Runs on `pull_request`, `push` to `main` and `release/**`, plus manual `workflow_dispatch`.
- Jobs: lint, typecheck, tests (Python 3.11, 3.12, and 3.13), examples smoke, package build smoke.
- `.github/workflows/release.yml`
  - Runs on semantic tag push (`v*.*.*`) and optional `workflow_dispatch`.
  - Reruns release gates, builds sdist and wheel, publishes to PyPI with OIDC, creates GitHub Release.
- `.github/workflows/dependency-review.yml`
  - Runs on pull requests and fails on high-severity dependency risk.
- `.github/workflows/codeql.yml`
  - Runs on push to `main`, pull requests targeting `main`, weekly schedule, and manual `workflow_dispatch`.
- `.github/workflows/docs-check.yml`
  - Verifies docs and workflow contract tests that guard the release surface.
- `.github/workflows/hygiene.yml`
  - Verifies repo layout and cleanup audits.
- `.github/workflows/frontend-ci.yml`
  - Runs the frontend install, `npm run check`, and `npm run build` gates.

## README Badge Surface

`README.md` exposes badges for:

1. `CI`
2. `Docs Check`
3. `Frontend CI`
4. `Hygiene`
5. `Release`
6. `CodeQL`
7. GitHub release version
8. License
9. Python support

Dependency Review remains active but is not badged because it is pull-request scoped rather than a stable default-branch status surface.

## CI Validation Scope

`ci.yml` validates:

1. `ruff check .`
2. `mypy src`
3. `pytest`
4. Example CLI smoke:
   - `sr8 init --path .sr8_ci`
   - `sr8 compile examples/product_prd.md --profile prd --out .sr8_ci/artifacts/canonical`
   - `sr8 transform .sr8_ci/artifacts/canonical/latest.json --to markdown_prd --out .sr8_ci/artifacts/derivative`
   - `sr8 lint .sr8_ci/artifacts/canonical/latest.json`
5. Package build smoke: `python -m build`
6. Docs and hygiene checks:
   - `pytest tests/test_docs_commands.py tests/test_repo_structure.py tests/test_release_workflow_contracts.py`
   - `python scripts/cleanup/check_repo_layout.py`
   - `python scripts/cleanup/repo_audit.py --check`

## Trusted Publishing Configuration

`release.yml` uses `pypa/gh-action-pypi-publish@release/v1` with `id-token: write`.
No long-lived PyPI API token is required.

Maintainer setup checklist:

1. In PyPI project settings, add a Trusted Publisher entry that points to this repository and `.github/workflows/release.yml`.
2. In GitHub repository settings, create the `pypi` environment used by the publish job.
3. Apply any desired environment protections (for example required reviewers).
4. Verify project name alignment (`sr8`) before first publish.

## Release Procedure

1. Update version and changelog in-repo.
2. Run local release gates:
   - `python -m pip install -e .`
   - `python -m build`
   - `pytest`
   - `ruff check .`
   - `mypy src`
3. Create and push a semantic tag:
   - `git tag vX.Y.Z`
   - `git push origin vX.Y.Z`
4. Confirm the `Release` workflow completed:
   - lint, typecheck, tests, examples smoke, build
   - publish to PyPI via OIDC
   - GitHub Release artifact attachment

`workflow_dispatch` can be used for a controlled rerun by providing an existing semantic tag.
