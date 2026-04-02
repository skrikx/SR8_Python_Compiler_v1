# LLM Adapters

SR8 keeps rule-first local compilation as the default path.
Provider adapters are optional and additive.

## Registered Providers

- `openai`
- `azure_openai`
- `aws_bedrock`
- `anthropic`
- `gemini`
- `ollama`

Each provider is exposed through the shared contract in `src/sr8/adapters/`.
The contract normalizes:

- request shape
- response shape
- capability descriptors
- probe results
- provider-specific error mapping

## CLI Surface

List registered providers:

```bash
sr8 providers list
```

Probe readiness from environment-backed settings:

```bash
sr8 providers probe
sr8 providers probe --provider openai
```

## Environment Settings

Provider credentials and defaults are resolved from environment variables only.
SR8 does not persist secrets in repo state.

Examples:

```bash
SR8_OPENAI_API_KEY=...
SR8_OPENAI_MODEL=gpt-4.1-mini

SR8_ANTHROPIC_API_KEY=...
SR8_ANTHROPIC_MODEL=claude-3-5-sonnet-latest

SR8_GEMINI_API_KEY=...
SR8_GEMINI_MODEL=gemini-1.5-pro

SR8_OLLAMA_MODEL=llama3.1
```

## Runtime Contract

- Rule-only compile remains available with zero provider configuration.
- Provider probing is safe to run without invoking remote inference.
- Model-assisted extraction must be requested explicitly.
- Provider output is normalized back into SR8-native extraction shapes.
- Provider failures can fall back to rule-based extraction when configured.
