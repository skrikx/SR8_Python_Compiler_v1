# Provider Capabilities

SR8 declares provider capabilities explicitly so the CLI, API, and frontend can show honest status.

| Provider | Live Inference | Probe Support | Normalized Response | Notes |
| --- | --- | --- | --- | --- |
| `openai` | yes | yes | yes | Uses chat completions HTTP surface |
| `azure_openai` | yes | yes | yes | Uses deployment-scoped chat completions |
| `aws_bedrock` | yes | yes | yes | Uses AWS-authenticated Converse runtime; readiness only flips after an optional live smoke succeeds |
| `anthropic` | yes | yes | yes | Uses messages HTTP surface |
| `gemini` | yes | yes | yes | Uses generateContent HTTP surface |
| `ollama` | yes | yes | yes | Targets local Ollama runtime |

## Probe Semantics

`registered=true` means the provider adapter exists in SR8.

`configured=true` means the provider has the configuration it needs to attempt runtime use. For AWS Bedrock that includes region, model, and resolved AWS credentials.

`subscribed_or_accessible=true` means Bedrock access checks did not report IAM, model access, or subscription failure.

`capable=true` means SR8 has a normalized adapter surface for that provider.

`live_enabled=true` means this runtime allows live calls for that provider class.

`ready_for_runtime=true` means SR8 can truthfully attempt a live request in the current runtime.

`available=true` mirrors runtime readiness for compatibility with existing CLI and frontend surfaces.

For `ollama`, availability stays visible even in local-only setups because the runtime is expected to be on localhost.

For `aws_bedrock`, `live_enabled=true` once the SDK-backed runtime path exists in code. `ready_for_runtime=true` only after an actual Bedrock Converse smoke check succeeds. By default, probe stays cautious and requires `SR8_AWS_BEDROCK_PROBE_RUNTIME=true` to run that live smoke.
