# OSS Launch

This page tracks the practical launch baseline for SR8.

## Launch Inputs

- public docs and contributor path
- CI, release, and security workflows
- changelog and release checklist
- maintainer and triage docs

## Pre-Launch Checklist

1. Complete `RELEASE_CHECKLIST.md`.
2. Confirm docs in `README.md` and `docs/` are accurate.
3. Confirm examples in `examples/outputs/` are current.
4. Confirm release workflow trusted publishing configuration is active.
5. Confirm governance and support docs are linked from README.

## Launch Execution

1. Create release PR with changelog and version bump.
2. Merge to main after CI passes.
3. Push semantic tag `vX.Y.Z`.
4. Verify release workflow completion and artifacts.
5. Publish release notes from generated GitHub release baseline.

## Post-Launch Follow-up

1. Monitor incoming issues and classify with triage labels.
2. Triage regressions first.
3. Publish hotfix release if needed.
