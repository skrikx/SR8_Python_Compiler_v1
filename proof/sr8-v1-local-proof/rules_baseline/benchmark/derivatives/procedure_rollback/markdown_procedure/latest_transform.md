# Procedure - art_986f27ce44fa4d3e8b93
## Purpose
Document an incident rollback procedure for failed benchmark releases.
## Authority Context
product manager
## Steps
- Step 1. Detect benchmark release breakage
- Step 2. Roll back result packs to the prior passing version
- Step 3. Notify the release owner and archive the failed pack

## Fallbacks
- If fail on source hash mismatch, trigger rollback within 15 minutes

## Escalation
- Escalate to the release owner before publishing a replacement pack
- Owner approval is captured before rerun
- Escalation path is explicit for on-call review
