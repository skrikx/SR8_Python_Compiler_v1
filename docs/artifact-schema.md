# Artifact Schema

Canonical `IntentArtifact` fields include:
- identity: `artifact_id`, `artifact_version`, `compiler_version`, `profile`, `created_at`
- source: `source_id`, `source_type`, `source_hash`, `origin`
- semantic dimensions: `objective`, `scope`, `exclusions`, `constraints`, `dependencies`, `assumptions`, `success_criteria`, `output_contract`
- controls: `governance_flags`, `validation`, `lineage`, `metadata`

Derivative `DerivativeArtifact` fields include:
- `derivative_id`, `parent_artifact_id`, `parent_artifact_version`, `transform_target`, `profile`
- `content`, `lineage`, `metadata`
