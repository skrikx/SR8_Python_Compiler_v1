# Benchmark Rollback Procedure

Objective: Document an incident rollback procedure for failed benchmark releases.

Scope:
- Step 1. Detect benchmark release breakage
- Step 2. Roll back result packs to the prior passing version
- Step 3. Notify the release owner and archive the failed pack

Exclusions:
- Schema redesign

Constraints:
- If fail on source hash mismatch, trigger rollback within 15 minutes
- Escalate to the release owner before publishing a replacement pack

Context Package:
- Release checklist
- Receipt persistence docs

Authority Context:
- product manager

Dependencies:
- Workspace receipts
- Versioned benchmark results

Assumptions:
- Fallback path uses the previous passing results bundle

Success Criteria:
- Owner approval is captured before rerun
- Escalation path is explicit for on-call review

Output Contract:
- Markdown procedure
