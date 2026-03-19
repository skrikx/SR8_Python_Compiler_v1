# Release Notes Policy

Release notes must map to shipped behavior and test-backed changes.

## Required Sections

1. Summary
2. Added
3. Changed
4. Fixed
5. Security
6. Upgrade Notes (if any)

## Rules

- no claims for features not present in repository
- include affected commands/modules where relevant
- include known limitations when unresolved
- include breaking changes explicitly

## Source of Truth

- merged PRs and commits in release range
- `CHANGELOG.md`
- generated GitHub release notes baseline
- release artifacts from CI

## Patch Release Guidance

Patch releases should focus on:

- regressions
- correctness fixes
- security fixes

Large feature additions should use minor version increments.
