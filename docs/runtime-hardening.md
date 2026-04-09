# Runtime Hardening

P3 extends runtime hardening from route safety into provider truth, operator visibility, replay stability, and chaos coverage.

## What P3 Seals

- Provider descriptors and probes now expose parity metadata such as runtime transport, configured model, bounded readiness state, and whether a live probe is still required.
- Model-assisted extraction records whether provider assist succeeded live or fell back to rule-based extraction, with bounded failure metadata preserved for inspection.
- The local frontend now unwraps real API envelopes, shows route-contract truth, surfaces weak-intent recovery, and keeps inspect and validation behavior aligned with trusted-local backend policy.
- Replay and async execution remain traceable through idempotency keys, job state, and stable result payload reuse.
- End-to-end, chaos, and replay tests now cover malformed compile input, provider outage fallback, compile-to-derivative flow, and replay truth.

## Trusted Runtime Boundary

- API `/compile` still accepts inline source text or structured payloads only. It never reads caller-supplied filesystem paths.
- API `/inspect`, `/validate`, `/transform`, `/diff`, `/lint`, `/artifacts`, and `/receipts` remain trusted-local routes tied to local workspace state.
- AWS Bedrock remains deliberately bounded until a live Converse smoke succeeds. `status=bounded` is intentional and truthful, not a half-ready success signal.
- Async jobs remain in-process and local-first. They are replay-safe, not distributed.

## Validation Commands

```bash
python -m pip install -e .
pytest tests/e2e/test_hardening_gauntlet.py tests/chaos/test_malformed_input_matrix.py tests/replay/test_compile_replay_matrix.py tests/test_provider_parity.py tests/test_bedrock_runtime.py tests/test_frontend_contracts.py tests/test_frontend_operator_paths.py
pytest
ruff check .
mypy src
python -m build
sr8 providers probe
sr8 compile examples/product_prd.md --rule-only
cd frontend && npm run check
cd frontend && npm run build
```
