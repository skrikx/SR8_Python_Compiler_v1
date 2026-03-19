Objective:
- Audit repository quality and risk posture for release readiness.

Scope:
- Evaluate lint, typecheck, and test posture.
- Evaluate release and security automation baseline.
- Identify high-impact maintainability and reliability risks.
- Provide prioritized remediation sequence.

Exclusions:
- No architecture rewrite.
- No framework migration.

Constraints:
- Deterministic local checks only.
- Recommendations must map to existing repository boundaries.

Assumptions:
- CI workflow definitions in `.github/workflows/` are source of truth.

Success Criteria:
- Findings include prioritized remediation with severity tiers.
- Audit output is actionable for maintainers within one release cycle.

Output Contract:
- Audit report and remediation checklist suitable for planning.
