# Release

## Release Checklist

1. `python -m pip install -e .`
2. `python -m pip install -e ".[dev]"`
3. `python -m build`
4. Run core CLI smoke flows:
   - compile
   - validate
   - inspect
   - transform
   - diff
   - lint
   - list
   - show
5. Run targeted release tests.
6. Update `CHANGELOG.md`.
7. Tag release version.
8. Verify `Release` workflow completion.

See also:

- `RELEASE_CHECKLIST.md`
- `docs/release-automation.md`
- `docs/release-notes-policy.md`

## Versioning

Version is defined in:
- `pyproject.toml` project version
- `src/sr8/version.py`
