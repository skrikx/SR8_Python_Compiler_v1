# Release

## Release Checklist

1. `python -m pip install -e .`
2. `python -m build`
3. Run core CLI smoke flows:
   - compile
   - validate
   - inspect
   - transform
   - diff
   - lint
   - list
   - show
4. Run targeted release tests.
5. Update `CHANGELOG.md`.
6. Tag release version.

## Versioning

Version is defined in:
- `pyproject.toml` project version
- `src/sr8/version.py`
