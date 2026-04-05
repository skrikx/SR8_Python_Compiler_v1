# WF11 Gap Closure

Use this skill for SR8 PRD-to-ship closure passes that must leave the repository in a test-backed v1.1 hardened state.

## Gap Matrix

- AC5 fixture floor: enforce 25 or more golden fixtures.
- Source hash and lineage: preserve deterministic ingest hash through normalization, receipts, inspect, storage, and recompile.
- UC7 recompilation: support artifact-path and artifact-object recompilation without ambiguous lineage.
- Missing target classes: keep `whitepaper_outline` and `code_task_graph` wired through profiles, transforms, fixtures, and tests.
- Extraction trust: expose explicit, inferred, weak, empty, and contradictory field states from real extraction output.
- Config spine: route useful defaults through `pydantic-settings`.
- Performance: run smoke-level compile and validation timing gates.

## Subagent Assignment Template

- Auditor: map requested PRD gaps to current files, tests, and docs.
- Extraction: inspect field population quality, trust signals, and adapter boundaries.
- Profiles: verify new profiles, target classes, and transform compatibility.
- Recompile: verify API, CLI, and lineage preservation.
- Fixtures and tests: expand corpus, proof tests, and contradiction cases.
- Docs and release truth: update changelog, architecture, schema docs, and closure notes.

Keep read-heavy analysis parallel. Integrate file writes sequentially.

## Validation Commands

```bash
python -m pip install -e .
pytest tests/test_ac5_fixture_count.py tests/test_ac7_multi_derivative.py tests/test_recompile_flow.py tests/test_source_hash_lineage.py tests/test_extraction_confidence.py tests/test_extraction_adapter_registry.py tests/test_whitepaper_outline_profile.py tests/test_code_task_graph_profile.py tests/test_performance_gate.py tests/test_field_population_quality.py
pytest
ruff check .
mypy src
sr8 recompile tests/fixtures/recompile/base_artifact.json --profile whitepaper_outline
sr8 inspect tests/fixtures/recompile/base_artifact.json
sr8 compile tests/fixtures/weak_inputs/minimal_directive.txt
sr8 transform tests/fixtures/golden/canonical_prd.json --to markdown_prd
sr8 transform tests/fixtures/golden/canonical_prd.json --to markdown_plan
sr8 transform tests/fixtures/golden/canonical_prd.json --to markdown_prompt_pack
```

## Receipt Format

- Outcome: what closed and what remains.
- Files changed: paths only.
- Commands run: exact commands with pass or fail.
- Tests added or updated.
- Assumptions: only if used.
- Next action: one highest-value follow-up.
