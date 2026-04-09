# Bedrock Setup

SR8 uses the AWS SDK path for Bedrock so credentials are resolved and SigV4 signing is handled by the client rather than by custom HTTP code.

## Required SR8 Settings

- `SR8_AWS_BEDROCK_REGION`
- `SR8_AWS_BEDROCK_MODEL`

## Optional SR8 Settings

- `SR8_AWS_BEDROCK_PROFILE`
- `SR8_AWS_BEDROCK_ACCESS_KEY_ID`
- `SR8_AWS_BEDROCK_SECRET_ACCESS_KEY`
- `SR8_AWS_BEDROCK_SESSION_TOKEN`
- `SR8_AWS_BEDROCK_ENDPOINT_URL`
- `SR8_AWS_BEDROCK_PROBE_RUNTIME=true`
- `SR8_AWS_BEDROCK_PROBE_PROMPT`

## Credential Resolution

SR8 follows the standard boto3 credential chain. That means explicit session parameters, environment variables, AWS profiles, shared credential files, container credentials, and instance metadata can all satisfy credential resolution.

## AWS-Side Prerequisites

1. Choose a commercial Bedrock region that offers the model you want.
2. Ensure your IAM principal can use Bedrock control-plane and runtime APIs.
3. Ensure the target model is accessible in your account.
4. For applicable third-party models, complete any AWS Marketplace or first-use access prerequisites before expecting the first invocation to succeed.

## Probe Semantics

- `configured=true` means SR8 has region, model, and AWS credentials resolved.
- `subscribed_or_accessible=true` means the Bedrock access check did not report model-access failure.
- `live_enabled=true` means SR8 has a real Converse runtime path available in code.
- `ready_for_runtime=true` means a live Bedrock smoke call succeeded.
- `status=bounded` means SR8 can see Bedrock configuration and control-plane access, but has not yet sealed runtime truth with a live smoke.
- `status=degraded` means Bedrock returned a real access, model, or runtime failure that blocks trustworthy live use.
- `requires_live_probe=true` means Bedrock is intentionally not marked ready until a real runtime smoke is allowed.

By default, `sr8 providers probe` does not spend money or make a live Bedrock inference call. Set `SR8_AWS_BEDROCK_PROBE_RUNTIME=true` when you want the probe to verify runtime readiness with a real signed Converse request.

## Minimal Local Flow

```bash
set SR8_AWS_BEDROCK_REGION=us-east-1
set SR8_AWS_BEDROCK_MODEL=anthropic.claude-3-haiku-20240307-v1:0
set SR8_AWS_BEDROCK_PROFILE=default
set SR8_AWS_BEDROCK_PROBE_RUNTIME=true

sr8 providers probe
sr8 compile examples/product_prd.md --assist-extract --provider aws_bedrock --model anthropic.claude-3-haiku-20240307-v1:0
```
