# SR8 Release Proof Pack

Objective: Compile a PRD for the SR8 self-hosting release proof pack used by users and reviewers.

Scope:
- User-facing benchmark summary for release reviewers
- Markdown proof pack for OSS release notes
- Regression comparison checklist

Exclusions:
- Hosted telemetry dashboard

Constraints:
- Keep outputs local-first
- Preserve source hash lineage in every receipt

Context Package:
- v1.1 gap closure docs
- release automation notes
- benchmark rubric descriptions

Authority Context:
- founder sponsor

Dependencies:
- Benchmark harness
- Receipt persistence

Assumptions:
- Reviewers read markdown artifacts first

Success Criteria:
- Reviewers can inspect benchmark deltas without opening raw JSON
- Release notes stay aligned with the canonical artifact

Output Contract:
- Canonical PRD artifact
- Markdown PRD
- Markdown plan
- Markdown prompt pack
