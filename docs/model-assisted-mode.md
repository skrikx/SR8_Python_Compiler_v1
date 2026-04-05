# Model-Assisted Mode

Model-assisted extraction is opt-in.
Rule-first local extraction remains the default.

## Rule-Only

Force deterministic local extraction:

```bash
sr8 compile examples/product_prd.md --rule-only
```

## Model-Assisted Extraction

Provide both a provider and model:

```bash
sr8 compile examples/product_prd.md --assist-provider openai --assist-model gpt-4.1-mini
```

Equivalent environment-backed configuration:

```bash
SR8_ASSIST_PROVIDER=openai
SR8_ASSIST_MODEL=gpt-4.1-mini
```

## Behavior

- SR8 sends the normalized source to the selected provider.
- The provider must return strict JSON matching SR8 extraction fields.
- SR8 validates that payload into native `ExtractedDimensions`.
- Extraction trace metadata records the provider and model.
- If fallback is enabled and the provider fails, SR8 falls back to `rule_based` extraction and marks that fallback in trace metadata.

## Visible Trust Surface

Model-assisted mode does not hide weakness.
Validation warnings, extraction trust, and governance flags remain visible in the artifact metadata and downstream lint/validation reports.
