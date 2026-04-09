# Public API Exposure

SR8 is local-first by design. Its API is safe enough for deliberate exposure only when operators keep the runtime behind normal web controls such as authentication, rate limits, and resource isolation.

## Route Classes

### Safe for broader exposure

- `GET /health`
- `GET /providers`
- `GET /providers/probe`

These routes do not read user-supplied local paths and do not expose workspace artifact contents.

### Deliberate exposure only

- `POST /compile`
- `GET /jobs/{job_id}`

`/compile` accepts inline source text or structured payloads only. It blocks arbitrary local path ingestion, enforces compile budget limits, supports optional idempotency keys, and can run in async job mode. It should not be exposed without auth, rate limiting, and operational guardrails.

`/jobs/{job_id}` only exposes async compile job state created by `/compile`. It does not open new local path access, but it does disclose compile result state and therefore shares the same deliberate-exposure posture.

### Trusted-local only

- `GET /status`
- `GET /settings`
- `GET /artifacts`
- `GET /artifacts/{identifier}`
- `GET /receipts`
- `POST /inspect`
- `POST /validate`
- `POST /transform`
- `POST /diff`
- `POST /lint`
- `GET /benchmarks/suites`
- `POST /benchmarks/run`

These routes reveal local workspace state, read trusted-local artifact paths or identifiers, or run operations intended for operator-controlled local use.

## Route Contract Metadata

Every route now advertises a route contract in OpenAPI under `x-sr8-route-contract` and mirrors that contract in JSON responses under `route_contract`.
The contract exposes:

- `route_id`
- `exposure_class`
- `path_policy`
- `summary`

This metadata is part of the API truth surface and should stay aligned with actual route behavior.

## Final `/inspect` Policy

- `/inspect` is artifact-only.
- It accepts a trusted-local artifact path or canonical artifact identifier.
- It does not compile inline source text.
- Non-artifact input returns `422` with `inspect_target_must_be_artifact`.

## Remaining Runtime Limits

- AWS Bedrock readiness remains credential, region, and model-access dependent. Treat `ready_for_runtime=true` from `sr8 providers probe` as the source of truth before exposing assist-extract flows.
- `/settings` can return structured `422` when environment-backed model-assisted defaults are incomplete.
- Trusted-local routes should remain behind operator control even if the API is reachable over a network.
- Workspace override is denied by default. Multi-workspace access is not a supported exposed-API tenancy model in this repository state.
- Async jobs are in-process and bounded. They are replay-safe through idempotency keys but are not a distributed job platform.
