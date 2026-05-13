# SR8 v1 Release Scope

## Release Position

SR8 v1 is a beta, local-first compiler for turning messy human intent into governed canonical `IntentArtifact` records.

It supports rules, assist, and auto compile modes. Provider-backed behavior is optional and must report provider, model, prompt hash, response hash, repair attempts, schema validation status, confidence, and fallback state in receipts.

## Required Local Gates

```bash
python -m pip install -e ".[dev]"
sr8 version
sr8 --help
python -m sr8.cli --help
python -m pytest
python -m ruff check .
python -m mypy src
sr8 schema export --out schemas/intent_artifact.schema.json
sr8 compile examples/product_prd.md --profile prd --mode rules
sr8 proof run examples/product_prd.md --profile prd --mode rules --out proof/sr8-v1-local-proof/rules_baseline
sr8 benchmark run --suite rules_required --out proof/benchmark/rules_required
cd frontend && npm ci && npm run check && npm run build
```

## Optional Provider Gates

Provider gates are required only when credentials and model configuration are present.

```bash
sr8 providers probe
sr8 compile examples/messy_intent.md --profile prd --mode assist --provider azure_openai
sr8 proof run examples/messy_intent.md --profile prd --mode assist --provider azure_openai --out proof/sr8-v1-local-proof/llm_assisted
sr8 benchmark run --suite llm_required --provider azure_openai --out proof/benchmark/llm_required
```

When provider config is absent, the correct status is `BLOCKED_PROVIDER_CONFIG`, not pass.
