# Artifact Schema

This page documents the primary model fields used in SR8 v1.0.0.

## Canonical Artifact (`IntentArtifact`)

### Identity

- `artifact_id`
- `artifact_version`
- `compiler_version`
- `profile`
- `created_at`

### Source

- `source.source_id`
- `source.source_type` (`text`, `markdown`, `json`, `yaml`)
- `source.source_hash`
- `source.origin`

### Semantic Dimensions

- `objective`
- `scope`
- `exclusions`
- `constraints`
- `target_class`
- `authority_context`
- `dependencies`
- `assumptions`
- `success_criteria`
- `output_contract`

### Governance and Quality

- `governance_flags.ambiguous`
- `governance_flags.incomplete`
- `governance_flags.requires_human_review`
- `validation.report_id`
- `validation.readiness_status`
- `validation.summary`
- `validation.errors[]`
- `validation.warnings[]`

### Lineage and Metadata

- `lineage.compile_run_id`
- `lineage.pipeline_version`
- `lineage.source_hash`
- `lineage.steps[]`
- `metadata` (freeform map)

## Derivative Artifact (`DerivativeArtifact`)

- `derivative_id`
- `parent_artifact_id`
- `parent_artifact_version`
- `transform_target`
- `profile`
- `created_at`
- `content`
- `lineage.parent_source_hash`
- `lineage.parent_compile_run_id`
- `lineage.parent_lineage_steps[]`
- `metadata`

## Diff and Lint Report Models

Diff report (`DiffReport`) contains:

- `report_id`
- `left_ref`
- `right_ref`
- `summary`
- `changes[]` with `field`, `change_class`, `impact`, `left`, `right`

Lint report (`LintReport`) contains:

- `report_id`
- `artifact_ref`
- `status` (`pass`, `warn`, `fail`)
- `summary`
- `findings[]`
