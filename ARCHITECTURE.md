# SR8 Architecture

## Compiler Boundary

SR8 compiles source intent into canonical artifacts.
Core boundary responsibilities:

1. ingest input (`src/sr8/ingest/`)
2. normalize content (`src/sr8/normalize/`)
3. extract dimensions (`src/sr8/extract/`)
4. assemble canonical model (`src/sr8/compiler/`)
5. apply profile overlay and validation (`src/sr8/profiles/`, `src/sr8/validate/`)
6. optional transform (`src/sr8/transform/`)
7. local persistence and indexing (`src/sr8/storage/`)
8. quality analysis via diff and lint (`src/sr8/diff/`, `src/sr8/lint/`)

Out of boundary:

- remote orchestration services
- non-local persistent infrastructure

## Canonical Artifact Model

Primary model: `IntentArtifact` in `src/sr8/models/intent_artifact.py`.
It includes:

- identity and version fields
- source metadata
- semantic fields (objective, scope, constraints, and related dimensions)
- governance flags
- validation report
- lineage
- freeform metadata

Canonical artifacts are the source of truth for validation, transforms, diff, lint, and storage records.

## Profile Overlay Model

Profiles are defined by `ProfileDefinition` in `src/sr8/profiles/base.py`.
Each profile declares:

- required and warning rules
- target class behavior
- supported transform targets

`apply_profile_overlay` updates profile-target context before validation.
Profiles do not fork the artifact schema.

## Transform Model

Transform targets are registered in `src/sr8/transform/registry.py` with `TransformTargetSpec`.
A transform operation:

1. verifies target exists
2. verifies profile compatibility
3. renders content via target renderer
4. emits `DerivativeArtifact` with parent lineage

Derivative outputs are always traceable to canonical source and compile lineage.

## Storage, Index, and Receipt Model

Workspace root defaults to `.sr8` and contains:

- `artifacts/canonical/`
- `artifacts/derivative/`
- `receipts/compile/`
- `receipts/transform/`
- `index/catalog.json`

`SR8Workspace` initializes deterministic local structure.
Save operations append artifacts and receipts while maintaining a catalog for list/show lookups.

## Diff and Lint Model

Diff:

- semantic field-level comparison over a fixed field set
- change classes: `added`, `removed`, `modified`, `unchanged`
- impact levels: `low`, `medium`, `high`

Lint:

- explicit rules (`L001` to `L010`)
- structured findings with severity and suggested fix
- read-only analysis that does not mutate artifacts

## Workflow Lineage (WF01 to WF08)

- WF01-WF04: compiler foundation, profile and transform rails
- WF05-WF07: persistence, receipts, packaging, release readiness
- WF08: CI, reusable workflows, release automation, code scanning, dependency review

This architecture document reflects the implemented v1.0.0 state.
