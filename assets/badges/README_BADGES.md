# README Badge Plan

This file defines a truthful badge plan without hardcoding repository-specific URLs.

## Recommended Badges

1. CI status (`.github/workflows/ci.yml`)
2. Release workflow status (`.github/workflows/release.yml`)
3. CodeQL status (`.github/workflows/codeql.yml`)
4. PyPI version (after first publish)
5. License (`LICENSE`)
6. Python version support (`>=3.12`)

## Activation Guidance

Before adding badge markdown to `README.md`:

1. Confirm the repository remote slug.
2. Confirm workflow filenames and default branch.
3. Confirm PyPI project page exists.
4. Verify badge links resolve publicly.

Avoid placeholder badge links in the public README.
