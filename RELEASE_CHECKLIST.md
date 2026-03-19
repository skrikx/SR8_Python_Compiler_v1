# Release Checklist

This checklist is the baseline for cutting and validating a public SR8 release.

## 1. Version and Changelog Prep

- [ ] Update version in `pyproject.toml` and `src/sr8/version.py`.
- [ ] Update `CHANGELOG.md` with release notes.
- [ ] Confirm docs reflect shipped behavior only.

## 2. Local Validation

- [ ] `python -m pip install -e .`
- [ ] `python -m pip install -e ".[dev]"`
- [ ] `ruff check .`
- [ ] `mypy src`
- [ ] `pytest`
- [ ] `python -m build`

## 3. Example and Docs Sanity

- [ ] Run documented example flows from `README.md` and `docs/examples.md`.
- [ ] Confirm example outputs in `examples/outputs/` are current.
- [ ] Confirm release and security docs are aligned:
  - `docs/release-automation.md`
  - `docs/security.md`

## 4. Tag and Publish

- [ ] Create semantic tag `vX.Y.Z`.
- [ ] Push tag to origin.
- [ ] Confirm `Release` workflow passes:
  - lint
  - typecheck
  - tests
  - examples smoke
  - build
  - publish to PyPI (OIDC trusted publishing)
  - GitHub Release artifacts

## 5. Post-Release Verification

- [ ] Confirm GitHub Release notes and attached artifacts.
- [ ] Confirm PyPI version availability.
- [ ] Smoke install and `sr8 version` on a clean environment.

## 6. Rollback / Hotfix Baseline

If a release has critical regression:

1. Open high-priority incident issue.
2. Reproduce and patch on a short-lived hotfix branch.
3. Run full quality gates.
4. Tag patched version (`vX.Y.Z+1` semantic increment).
5. Publish hotfix and update changelog with explicit regression note.
6. Add regression test coverage for the failure mode.
