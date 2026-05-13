# Provider Configuration

SR8 rules mode is offline and does not require provider configuration.

Assist mode requires both a provider and model. Auto mode runs rules first and uses provider assist only when configured and needed.

## Commands

```bash
sr8 providers list
sr8 providers probe
sr8 providers probe --provider azure_openai
```

Probe output shows configured, accessible, live-enabled, ready, available, missing env vars, and adapter detail. It must not print secret values.

## Environment Examples

OpenAI:

```bash
SR8_ASSIST_PROVIDER=openai
SR8_ASSIST_MODEL=gpt-4.1-mini
OPENAI_API_KEY=replace-with-your-openai-key
```

Azure OpenAI:

```bash
SR8_ASSIST_PROVIDER=azure_openai
SR8_ASSIST_MODEL=your-deployment
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=replace-with-your-azure-openai-key
AZURE_OPENAI_DEPLOYMENT=your-deployment
```

Anthropic:

```bash
SR8_ASSIST_PROVIDER=anthropic
SR8_ASSIST_MODEL=claude-sonnet-4-5
ANTHROPIC_API_KEY=replace-with-your-anthropic-key
```

Gemini:

```bash
SR8_ASSIST_PROVIDER=gemini
SR8_ASSIST_MODEL=gemini-2.5-flash
GEMINI_API_KEY=replace-with-your-gemini-key
```

Bedrock:

```bash
SR8_ASSIST_PROVIDER=aws_bedrock
SR8_ASSIST_MODEL=anthropic.claude-3-5-sonnet-20241022-v2:0
AWS_REGION=us-east-1
AWS_PROFILE=your-aws-profile
```

Ollama:

```bash
SR8_ASSIST_PROVIDER=ollama
SR8_ASSIST_MODEL=llama3.1
OLLAMA_BASE_URL=http://localhost:11434
```
