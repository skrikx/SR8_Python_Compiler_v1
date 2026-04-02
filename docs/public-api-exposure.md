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

`/compile` accepts inline source text or structured payloads only. It blocks arbitrary local path ingestion, but it still executes compiler work on caller-supplied input and should not be exposed without auth, rate limiting, and operational guardrails.

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

## Final `/inspect` Policy

- `/inspect` is artifact-only.
- It accepts a trusted-local artifact path or canonical artifact identifier.
- It does not compile inline source text.
- Non-artifact input returns `422` with `inspect_target_must_be_artifact`.

## Remaining Runtime Limits

- AWS Bedrock readiness remains credential, region, and model-access dependent. Treat `ready_for_runtime=true` from `sr8 providers probe` as the source of truth before exposing assist-extract flows.
- `/settings` can return structured `422` when environment-backed model-assisted defaults are incomplete.
- Trusted-local routes should remain behind operator control even if the API is reachable over a network.
