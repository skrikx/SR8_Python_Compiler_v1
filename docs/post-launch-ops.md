# Post-Launch Operations

This page defines baseline operations after public release.

## Weekly Baseline

1. Review new issues and pull requests.
2. Review dependency update PRs.
3. Review security scan outcomes.
4. Confirm docs and examples still match current behavior.

## Regression Handling

1. Reproduce reported regression.
2. Add failing test that captures behavior.
3. Land fix with tests.
4. Cut patch release using release checklist.
5. Link issue and release note entries.

## Security Handling

- route sensitive reports through private disclosure flow
- prioritize exploitability and user impact
- patch with clear remediation notes

## Documentation Hygiene

- treat docs drift as a bug
- update docs in same PR as behavior change when possible
- keep command examples executable
