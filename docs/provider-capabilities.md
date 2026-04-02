# Provider Capabilities

SR8 declares provider capabilities explicitly so the CLI, API, and frontend can show honest status.

| Provider | Live Inference | Probe Support | Normalized Response | Notes |
| --- | --- | --- | --- | --- |
| `openai` | yes | yes | yes | Uses chat completions HTTP surface |
| `azure_openai` | yes | yes | yes | Uses deployment-scoped chat completions |
| `aws_bedrock` | partial | yes | yes | Response normalization exists; live inference is not enabled in this runtime because SigV4 signing is not wired |
| `anthropic` | yes | yes | yes | Uses messages HTTP surface |
| `gemini` | yes | yes | yes | Uses generateContent HTTP surface |
| `ollama` | yes | yes | yes | Targets local Ollama runtime |

## Probe Semantics

`registered=true` means the provider adapter exists in SR8.

`configured=true` means required environment variables were found.

`capable=true` means SR8 has a normalized adapter surface for that provider.

`live_enabled=true` means this runtime allows live calls for that provider class.

`ready_for_runtime=true` means SR8 can truthfully attempt a live request in the current runtime.

`available=true` mirrors runtime readiness for compatibility with existing CLI and frontend surfaces.

For `ollama`, availability stays visible even in local-only setups because the runtime is expected to be on localhost.

For `aws_bedrock`, probe coverage exists, but `live_enabled=false`, `ready_for_runtime=false`, and `available=false` until SigV4 request signing support is added.
