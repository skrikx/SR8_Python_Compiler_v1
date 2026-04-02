# SR8 Architecture

## Compiler Boundary

SR8 compiles local source intent into canonical artifacts and derivative outputs.
Core boundary responsibilities:

1. ingest source and compute deterministic source hash
2. normalize content without mutating the ingest hash
3. extract typed dimensions through a swappable adapter interface
4. assemble canonical models and lineage
5. apply profile overlays plus validation and lint
6. recompile canonical artifacts while preserving lineage
7. transform canonical artifacts into derivative outputs
8. persist artifacts, receipts, and catalog records locally

Out of boundary:

- remote orchestration services
- non-local persistent infrastructure
- default LLM-backed extraction

## Canonical Artifact Model

Primary model: `IntentArtifact` in `src/sr8/models/intent_artifact.py`.
The canonical model includes:

- identity and version fields
- source metadata with stable `source_hash`
- semantic dimensions including `context_package`
- governance flags
- validation report
- lineage
- freeform metadata including extraction trust

Canonical artifacts remain the source of truth for validation, transforms, diff, lint, and storage records.

## Extraction and Trust Model

Extraction is adapter-based. The default adapter is rule-first and local.
Each extraction run can emit:

- `ExtractedDimensions`
- `ExtractionTrace`
- field-level confidence signals with explicit, inferred, weak, empty, or contradictory status

Trust output is surfaced in:

- `metadata.extraction_trace`
- CLI inspect output
- validation warnings
- lint findings
- persisted compilation receipts

## Profile Overlay Model

Profiles are defined by `ProfileDefinition` in `src/sr8/profiles/base.py`.
Each profile declares:

- required and warning rules
- target class behavior
- supported transform targets

WF11 adds:

- `whitepaper_outline`
- `code_task_graph`

Profiles do not fork the canonical schema.

## Recompile and Transform Model

Recompile paths live in `src/sr8/compiler/recompile.py`.
They support:

- `recompile_artifact(artifact, profile=None, config=None)`
- recompilation from artifact objects or artifact paths via `compile_intent`

Transform targets are registered in `src/sr8/transform/registry.py`.
A transform operation verifies both target compatibility and profile compatibility before emitting a `DerivativeArtifact` with parent lineage.

## Storage, Index, and Receipt Model

Workspace root defaults to `.sr8` and contains:

- `artifacts/canonical/`
- `artifacts/derivative/`
- `receipts/compile/`
- `receipts/transform/`
- `index/catalog.json`

Compilation receipts now persist:

- source hash
- validation summary
- extraction trust summary
- lineage summary

## Diff and Lint Model

Diff provides semantic field-level comparison over a fixed field set.
Lint provides explicit rule findings plus extraction-trust findings for weak, empty, or contradictory fields.

## Workflow Lineage

- WF01-WF07: compiler, persistence, and release foundation
- WF08-WF10: OSS launch and release rails
- WF11: PRD closure, extraction trust, recompile hardening, profile completion, and acceptance proof
