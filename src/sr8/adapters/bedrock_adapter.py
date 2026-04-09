from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from sr8.adapters.base import ProviderAdapter, extract_text_content
from sr8.adapters.errors import (
    ProviderError,
    ProviderExecutionError,
    ProviderNormalizationError,
    ProviderNotConfiguredError,
)
from sr8.adapters.types import (
    ProviderProbeResult,
    ProviderProbeStatus,
    ProviderRequest,
    ProviderResponse,
)
from sr8.config.provider_settings import AWSBedrockProviderSettings


class BedrockAdapter(ProviderAdapter[AWSBedrockProviderSettings]):
    name = "aws_bedrock"
    label = "AWS Bedrock"
    required_env_vars = ("SR8_AWS_BEDROCK_REGION", "SR8_AWS_BEDROCK_MODEL")
    default_model_env_var = "SR8_AWS_BEDROCK_MODEL"
    runtime_transport = "sdk"
    supports_live_inference = True

    def __init__(self, settings: AWSBedrockProviderSettings) -> None:
        super().__init__(settings)
        self.settings = settings

    def probe(self) -> ProviderProbeResult:
        missing = self._missing_config_requirements()
        if missing:
            return ProviderProbeResult(
                provider=self.name,
                status="missing_config",
                configured=False,
                subscribed_or_accessible=None,
                capable=True,
                live_enabled=True,
                ready_for_runtime=False,
                available=False,
                supports_live_inference=self.supports_live_inference,
                configured_model=self.settings.model,
                requires_live_probe=False,
                missing_env_vars=missing,
                detail="Missing required Bedrock region or model configuration.",
                capabilities=list(self.capabilities),
            )

        try:
            session = self._create_session()
        except ProviderNotConfiguredError as exc:
            return ProviderProbeResult(
                provider=self.name,
                status="missing_config",
                configured=False,
                subscribed_or_accessible=None,
                capable=True,
                live_enabled=True,
                ready_for_runtime=False,
                available=False,
                supports_live_inference=self.supports_live_inference,
                configured_model=self.settings.model,
                requires_live_probe=False,
                missing_env_vars=[],
                detail=str(exc),
                capabilities=list(self.capabilities),
            )
        except ProviderExecutionError as exc:
            return ProviderProbeResult(
                provider=self.name,
                status="degraded",
                configured=False,
                subscribed_or_accessible=None,
                capable=True,
                live_enabled=False,
                ready_for_runtime=False,
                available=False,
                supports_live_inference=self.supports_live_inference,
                configured_model=self.settings.model,
                requires_live_probe=False,
                missing_env_vars=[],
                detail=str(exc),
                capabilities=list(self.capabilities),
            )

        configured = self._credentials_available(session)
        if not configured:
            return ProviderProbeResult(
                provider=self.name,
                status="missing_config",
                configured=False,
                subscribed_or_accessible=None,
                capable=True,
                live_enabled=True,
                ready_for_runtime=False,
                available=False,
                supports_live_inference=self.supports_live_inference,
                configured_model=self.settings.model,
                requires_live_probe=False,
                missing_env_vars=[],
                detail=(
                    "AWS credentials could not be resolved. Use the standard boto3 credential "
                    "chain, an AWS profile, or explicit SR8_AWS_BEDROCK_* credentials."
                ),
                capabilities=list(self.capabilities),
            )

        try:
            control_client = self._create_client(session, "bedrock", self.settings.timeout_seconds)
            control_client.get_foundation_model(modelIdentifier=str(self.settings.model))
        except Exception as exc:
            subscribed_or_accessible, detail, status = self._probe_detail_from_exception(exc)
            return ProviderProbeResult(
                provider=self.name,
                status=status,
                configured=True,
                subscribed_or_accessible=subscribed_or_accessible,
                capable=True,
                live_enabled=True,
                ready_for_runtime=False,
                available=False,
                supports_live_inference=self.supports_live_inference,
                configured_model=self.settings.model,
                requires_live_probe=False,
                missing_env_vars=[],
                detail=detail,
                capabilities=list(self.capabilities),
            )

        if not self.settings.probe_runtime:
            return ProviderProbeResult(
                provider=self.name,
                status="bounded",
                configured=True,
                subscribed_or_accessible=True,
                capable=True,
                live_enabled=True,
                ready_for_runtime=False,
                available=False,
                supports_live_inference=self.supports_live_inference,
                configured_model=self.settings.model,
                requires_live_probe=True,
                missing_env_vars=[],
                detail=(
                    "Configured and model access appears available. Set "
                    "SR8_AWS_BEDROCK_PROBE_RUNTIME=true to run a live Converse smoke check."
                ),
                capabilities=list(self.capabilities),
            )

        try:
            runtime_client = self._create_client(
                session,
                "bedrock-runtime",
                self.settings.timeout_seconds,
            )
            response = runtime_client.converse(**self._build_probe_payload())
        except Exception as exc:
            subscribed_or_accessible, detail, status = self._probe_detail_from_exception(exc)
            return ProviderProbeResult(
                provider=self.name,
                status=status,
                configured=True,
                subscribed_or_accessible=subscribed_or_accessible,
                capable=True,
                live_enabled=True,
                ready_for_runtime=False,
                available=False,
                supports_live_inference=self.supports_live_inference,
                configured_model=self.settings.model,
                requires_live_probe=True,
                missing_env_vars=[],
                detail=detail,
                capabilities=list(self.capabilities),
            )

        normalized = self.normalize_response(cast(Mapping[str, object], response))
        return ProviderProbeResult(
            provider=self.name,
            status="ready",
            configured=True,
            subscribed_or_accessible=True,
            capable=True,
            live_enabled=True,
            ready_for_runtime=True,
            available=True,
            supports_live_inference=self.supports_live_inference,
            configured_model=self.settings.model,
            requires_live_probe=False,
            missing_env_vars=[],
            detail=f"Live runtime smoke succeeded with model '{normalized.model}'.",
            capabilities=list(self.capabilities),
        )

    def complete(self, request: ProviderRequest) -> ProviderResponse:
        missing = self._missing_config_requirements(request.model)
        if missing:
            raise ProviderNotConfiguredError(
                self.name,
                (
                    "AWS Bedrock requires SR8_AWS_BEDROCK_REGION and a Bedrock model from "
                    "either the request or SR8_AWS_BEDROCK_MODEL."
                ),
            )

        session = self._create_session()
        if not self._credentials_available(session):
            raise ProviderNotConfiguredError(
                self.name,
                (
                    "AWS credentials could not be resolved. Use the standard boto3 credential "
                    "chain, an AWS profile, or explicit SR8_AWS_BEDROCK_* credentials."
                ),
            )

        runtime_client = self._create_client(session, "bedrock-runtime", request.timeout_seconds)
        try:
            response = runtime_client.converse(**self._build_converse_payload(request))
        except Exception as exc:
            raise self._execution_error_from_exception(exc) from exc
        return self.normalize_response(cast(Mapping[str, object], response))

    def prepare_http_request(
        self,
        request: ProviderRequest,
    ) -> tuple[str, dict[str, str], dict[str, object]]:
        raise ProviderNormalizationError(
            self.name,
            (
                "AWS Bedrock uses an SDK-backed Converse runtime path. "
                "prepare_http_request is not used for live invocation."
            ),
        )

    def normalize_response(self, payload: Mapping[str, object]) -> ProviderResponse:
        content = payload.get("outputText")
        if not isinstance(content, str):
            output = payload.get("output")
            if isinstance(output, Mapping):
                message = output.get("message")
                if isinstance(message, Mapping):
                    content = extract_text_content(message.get("content"))
        if not isinstance(content, str) or not content.strip():
            content = extract_text_content(payload.get("content"))
        if not isinstance(content, str) or not content.strip():
            raise ProviderNormalizationError(self.name, "Bedrock response missing text content.")

        usage_payload = payload.get("usage")
        usage: dict[str, int] = {}
        if isinstance(usage_payload, Mapping):
            for source_name, target_name in (
                ("inputTokens", "input_tokens"),
                ("outputTokens", "output_tokens"),
                ("totalTokens", "total_tokens"),
            ):
                value = usage_payload.get(source_name)
                if isinstance(value, int):
                    usage[target_name] = value

        model_name = payload.get("modelId", self.settings.model or "")
        return ProviderResponse(
            provider=self.name,
            model=str(model_name),
            content=content,
            finish_reason=str(payload.get("stopReason", "stop")),
            usage=usage,
            raw_payload=dict(payload),
        )

    def _missing_config_requirements(self, model: str | None = None) -> list[str]:
        missing: list[str] = []
        if not self.settings.region:
            missing.append("SR8_AWS_BEDROCK_REGION")
        if not (model or self.settings.model):
            missing.append("SR8_AWS_BEDROCK_MODEL")
        return missing

    def _create_session(self) -> Any:
        try:
            import boto3
        except ImportError as exc:
            raise ProviderExecutionError(
                self.name,
                "boto3 is required for AWS Bedrock live runtime support.",
            ) from exc

        session_kwargs: dict[str, object] = {}
        if self.settings.profile:
            session_kwargs["profile_name"] = self.settings.profile
        if self.settings.access_key_id:
            session_kwargs["aws_access_key_id"] = self.settings.access_key_id
        if self.settings.secret_access_key:
            session_kwargs["aws_secret_access_key"] = self.settings.secret_access_key
        if self.settings.session_token:
            session_kwargs["aws_session_token"] = self.settings.session_token

        try:
            return boto3.session.Session(**session_kwargs)
        except Exception as exc:
            raise ProviderNotConfiguredError(
                self.name,
                f"Unable to create an AWS session for Bedrock: {exc}",
            ) from exc

    def _credentials_available(self, session: Any) -> bool:
        try:
            credentials = session.get_credentials()
        except Exception:
            return False
        if credentials is None:
            return False
        try:
            frozen = credentials.get_frozen_credentials()
        except Exception:
            return False
        access_key = getattr(frozen, "access_key", None)
        secret_key = getattr(frozen, "secret_key", None)
        return (
            isinstance(access_key, str)
            and bool(access_key)
            and isinstance(secret_key, str)
            and bool(secret_key)
        )

    def _create_client(self, session: Any, service_name: str, timeout_seconds: float) -> Any:
        try:
            from botocore.config import Config
        except ImportError as exc:
            raise ProviderExecutionError(
                self.name,
                "botocore is required for AWS Bedrock live runtime support.",
            ) from exc

        return session.client(
            service_name,
            region_name=self.settings.region,
            endpoint_url=self.settings.endpoint_url,
            config=Config(
                connect_timeout=min(float(timeout_seconds), 10.0),
                read_timeout=float(timeout_seconds),
                retries={"max_attempts": 1},
            ),
        )

    def _build_converse_payload(self, request: ProviderRequest) -> dict[str, object]:
        payload: dict[str, object] = {
            "modelId": request.model,
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": request.prompt}],
                }
            ],
            "inferenceConfig": {
                "temperature": request.temperature,
                "maxTokens": request.max_tokens,
            },
        }
        if request.system_prompt.strip():
            payload["system"] = [{"text": request.system_prompt}]
        return payload

    def _build_probe_payload(self) -> dict[str, object]:
        return self._build_converse_payload(
            ProviderRequest(
                provider=self.name,
                model=str(self.settings.model),
                prompt=self.settings.probe_prompt,
                system_prompt="Return only the requested text.",
                response_format="text",
                max_tokens=16,
                timeout_seconds=self.settings.timeout_seconds,
            )
        )

    def _probe_detail_from_exception(
        self,
        exc: Exception,
    ) -> tuple[bool | None, str, ProviderProbeStatus]:
        code = self._error_code(exc)
        if code in {"AccessDeniedException", "NotAuthorized"}:
            return (
                False,
                (
                    "AWS credentials resolved, but Bedrock model access was denied. Check IAM "
                    "permissions, model access, and any Marketplace prerequisites."
                ),
                "degraded",
            )
        if code in {"ValidationException", "ResourceNotFoundException"}:
            return (
                False,
                (
                    "Bedrock rejected the configured model or runtime shape. Verify the model ID "
                    "and that the target supports Converse."
                ),
                "degraded",
            )
        if code in {"ThrottlingException", "ModelNotReadyException"}:
            return (
                None,
                f"Bedrock runtime is reachable but not yet ready: {self._error_message(exc)}",
                "bounded",
            )
        return (None, f"Bedrock probe failed: {self._error_message(exc)}", "degraded")

    def _execution_error_from_exception(self, exc: Exception) -> ProviderError:
        code = self._error_code(exc)
        if code in {"AccessDeniedException", "NotAuthorized"}:
            return ProviderExecutionError(
                self.name,
                (
                    "Bedrock runtime denied access. Check IAM permissions, model access, and any "
                    "Marketplace prerequisites."
                ),
            )
        if code in {"ValidationException", "ResourceNotFoundException"}:
            return ProviderExecutionError(
                self.name,
                (
                    "Bedrock rejected the request. Verify the configured model ID and that the "
                    "target model supports Converse."
                ),
            )
        if code in {"UnrecognizedClientException", "ExpiredTokenException"}:
            return ProviderNotConfiguredError(
                self.name,
                "AWS credentials are invalid or expired.",
            )
        return ProviderExecutionError(
            self.name,
            f"Bedrock runtime failed: {self._error_message(exc)}",
        )

    def _error_code(self, exc: Exception) -> str | None:
        response = getattr(exc, "response", None)
        if not isinstance(response, Mapping):
            return None
        error_payload = response.get("Error")
        if not isinstance(error_payload, Mapping):
            return None
        code = error_payload.get("Code")
        return code if isinstance(code, str) else None

    def _error_message(self, exc: Exception) -> str:
        response = getattr(exc, "response", None)
        if isinstance(response, Mapping):
            error_payload = response.get("Error")
            if isinstance(error_payload, Mapping):
                message = error_payload.get("Message")
                if isinstance(message, str) and message:
                    return message
        return str(exc)
