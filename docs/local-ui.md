# Local UI

The SR8 local UI is a product surface, not a second compiler.

## Backend Truth Surfaces

The UI reads these backend areas directly:

- compile and inspect
- artifacts and artifact detail
- transforms
- semantic diff
- lint reports
- compile and transform receipts
- benchmark suites and benchmark runs
- provider descriptors and probe results
- workspace settings

## Rule-Only Usability

Rule-only mode remains fully usable from the UI.
Provider selection is optional and visible as an additive control on the compile route.

## Visible Weakness

The UI keeps weak states visible:

- validation warnings
- extraction trust
- low-confidence fields
- lineage
- receipt summaries
- provider readiness
- route exposure and path policy
- async compile job state and replay keys when used

## Operator Paths

The artifact detail route now acts as the inspect surface for local operators. It loads the indexed artifact, shows lineage and receipt metadata, and re-runs validation for canonical artifacts so readiness remains visible without guessing.

The compile route exposes backend-owned trust state directly:

- route contract
- request identity mode
- assist-extract status
- weak-intent recovery guidance
- async job identifiers when compile is queued

## Frontend CI

Frontend build and type checks run through `.github/workflows/frontend-ci.yml`.
That workflow is part of the main CI path.
