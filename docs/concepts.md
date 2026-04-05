# Concepts

SR8 keeps product truth, category truth, and system horizon separate:

- Product truth: SR8 is an intent compiler for AI systems.
- Category truth: SR8 proves governed artifact infrastructure through canonical artifacts, validation, lineage, and package outputs.
- Horizon truth: SROS v2 is the larger governed execution direction beyond the shipped runtime in this repository.

## Canonical Artifact

Canonical artifact (`IntentArtifact`) is the primary structured representation of intent.
It is the source of truth for validation, transforms, diff, lint, and storage records.

## Profile Overlay

A profile overlay updates artifact context (`profile`, `target_class`) and applies profile-specific validation rules.
Profiles do not change the base artifact schema.

## Derivative Artifact

A derivative artifact is rendered output from a canonical artifact for a specific transform target.
Each derivative includes lineage back to the parent compile flow.

## Receipt

Receipts are structured records written when compile or transform outputs are persisted in a `.sr8` workspace.
They provide machine-readable traceability for writes.

## Catalog

Catalog is a local JSON index at `.sr8/index/catalog.json`.
It tracks canonical and derivative records for listing and lookup by ID.

## Local-First Principle

SR8 is designed so core compile behavior works locally without network dependencies.
CI and release automation validate this local-first surface rather than replacing it.

## Chat Frontdoor

The chat frontdoor is an intake surface, not a parallel runtime.
Chat-originated requests must terminate in the canonical SR8 artifact path before validation, governance marking, or package emission.

## Governed Package Outputs

SR8 can emit governed package outputs such as XML promptunit packages and child `sr8_prompt` artifacts.
These are derivative delivery targets from canonical artifacts, not shadow sources of truth.
