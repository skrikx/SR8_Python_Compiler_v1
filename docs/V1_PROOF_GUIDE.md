# SR8 v1 Proof Guide

Generate a rules baseline proof packet:

```bash
sr8 proof run examples/product_prd.md --profile prd --mode rules --out proof/sr8-v1-local-proof/rules_baseline
```

The proof packet contains:

- `input/` - copied source input.
- `canonical/` - canonical artifact JSON.
- `derivative_markdown/` - native Markdown output and metadata.
- `derivative_srxml/` - native SRXML output and metadata.
- `receipts/` - compile and transform receipts.
- `validation/` - validation report.
- `lint/` - lint report.
- `diff/` - regeneration diff report.
- `benchmark/` - benchmark output or explicit blocker.
- `hashes.json` - SHA-256 hashes for packet files.
- `command_transcript.log` - command transcript.
- `proof_manifest.json` - mode, artifact, provider, model, and file manifest.

Assist proof packets use the same structure, but require configured provider credentials and model settings. Raw LLM prompt and response bodies are not stored unless `--save-llm-trace` is explicitly used by the compile path.
