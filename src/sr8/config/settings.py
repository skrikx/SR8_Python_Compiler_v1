from __future__ import annotations

import os

from pydantic_settings import BaseSettings

from sr8.config.env import settings_config
from sr8.models.compile_config import CompileConfig, CompileMode

PROVIDER_ALIASES = {
    "azure": "azure_openai",
    "azure-openai": "azure_openai",
    "bedrock": "aws_bedrock",
    "aws-bedrock": "aws_bedrock",
}


class SR8Settings(BaseSettings):
    model_config = settings_config(env_prefix="SR8_")

    default_profile: str = "generic"
    compile_mode: CompileMode = "auto"
    extraction_adapter: str = "rule_based"
    include_raw_source: bool = False
    assist_provider: str | None = None
    assist_model: str | None = None
    assist_fallback_to_rule_based: bool = True
    save_llm_trace: bool = False
    workspace_path: str = ".sr8"
    api_auth_token: str | None = None
    api_rate_limit_requests: int = 0
    api_rate_limit_window_seconds: int = 60
    api_allow_workspace_override: bool = False
    api_allow_multi_tenant: bool = False
    api_max_source_chars: int = 200_000
    api_max_payload_nodes: int = 1_024
    api_max_concurrent_operations: int = 4
    api_async_jobs_enabled: bool = True


def resolve_compile_config(
    settings: SR8Settings,
    *,
    profile: str | None = None,
    target: str | None = None,
    validate_target: bool = False,
    mode: CompileMode | None = None,
    rule_only: bool = False,
    assist_extract: bool = False,
    assist_provider: str | None = None,
    assist_model: str | None = None,
    save_llm_trace: bool | None = None,
) -> CompileConfig:
    effective_profile = profile or settings.default_profile
    env_provider_set = "SR8_ASSIST_PROVIDER" in os.environ
    env_model_set = "SR8_ASSIST_MODEL" in os.environ
    compile_mode: CompileMode = mode or settings.compile_mode
    if rule_only:
        compile_mode = "rules"
    elif assist_extract:
        compile_mode = "assist"
    effective_provider: str | None
    effective_model: str | None
    if assist_provider is not None and assist_model is None:
        effective_provider = assist_provider
        effective_model = settings.assist_model if compile_mode == "assist" else None
    elif env_provider_set and not env_model_set and assist_model is None:
        effective_provider = settings.assist_provider
        effective_model = None
    else:
        effective_provider = assist_provider or settings.assist_provider
        effective_model = assist_model or settings.assist_model
    if effective_provider is not None:
        provider_key = effective_provider.strip().lower()
        effective_provider = PROVIDER_ALIASES.get(provider_key, provider_key)
    extraction_adapter = settings.extraction_adapter

    if target is not None and not validate_target:
        msg = "--validate is required when --target is provided."
        raise ValueError(msg)
    if target is not None and target.strip().lower() != "xml_srxml_rc2":
        msg = "Unsupported compile target. Expected xml_srxml_rc2."
        raise ValueError(msg)

    if compile_mode == "rules":
        extraction_adapter = "rule_based"
        effective_provider = None
        effective_model = None
    elif compile_mode == "assist":
        extraction_adapter = "model_assisted"
    elif effective_provider or effective_model:
        extraction_adapter = "model_assisted"

    explicit_pair_missing = (assist_provider is not None) != (assist_model is not None)
    assist_provider_uses_config_model = (
        compile_mode == "assist" and assist_provider is not None and effective_model is not None
    )
    if explicit_pair_missing and not assist_provider_uses_config_model:
        msg = "Explicit assist configuration requires both provider and model."
        raise ValueError(msg)
    if extraction_adapter == "model_assisted" and (not effective_provider or not effective_model):
        msg = (
            "Model-assisted extraction requires both assist_provider and assist_model "
            "or matching SR8_ASSIST_PROVIDER and SR8_ASSIST_MODEL settings."
        )
        raise ValueError(msg)
    if compile_mode == "auto" and bool(effective_provider) != bool(effective_model):
        msg = "Auto mode assist fallback requires both provider and model when either is supplied."
        raise ValueError(msg)

    return CompileConfig(
        profile=effective_profile,
        compile_mode=compile_mode,
        target=target,
        validate_target=validate_target,
        include_raw_source=settings.include_raw_source,
        extraction_adapter=extraction_adapter,
        assist_provider=effective_provider,
        assist_model=effective_model,
        assist_fallback_to_rule_based=(
            False
            if compile_mode == "assist"
            else True
            if compile_mode == "auto"
            else settings.assist_fallback_to_rule_based
        ),
        save_llm_trace=settings.save_llm_trace if save_llm_trace is None else save_llm_trace,
    )


def build_settings_payload(settings: SR8Settings) -> dict[str, object]:
    payload: dict[str, object] = {
        "default_profile": settings.default_profile,
        "compile_mode": settings.compile_mode,
        "extraction_adapter": settings.extraction_adapter,
        "assist_provider": settings.assist_provider,
        "assist_model": settings.assist_model,
        "assist_fallback_to_rule_based": settings.assist_fallback_to_rule_based,
        "save_llm_trace": settings.save_llm_trace,
        "include_raw_source": settings.include_raw_source,
        "workspace_path": settings.workspace_path,
        "api_auth_token_configured": settings.api_auth_token is not None,
        "api_rate_limit_requests": settings.api_rate_limit_requests,
        "api_rate_limit_window_seconds": settings.api_rate_limit_window_seconds,
        "api_allow_workspace_override": settings.api_allow_workspace_override,
        "api_allow_multi_tenant": settings.api_allow_multi_tenant,
        "api_max_source_chars": settings.api_max_source_chars,
        "api_max_payload_nodes": settings.api_max_payload_nodes,
        "api_max_concurrent_operations": settings.api_max_concurrent_operations,
        "api_async_jobs_enabled": settings.api_async_jobs_enabled,
    }
    try:
        compile_config = resolve_compile_config(settings)
    except ValueError as exc:
        return payload | {"configuration_error": str(exc)}
    return payload | {
        "default_profile": compile_config.profile,
        "compile_mode": compile_config.compile_mode,
        "extraction_adapter": compile_config.extraction_adapter,
        "assist_provider": compile_config.assist_provider,
        "assist_model": compile_config.assist_model,
        "assist_fallback_to_rule_based": compile_config.assist_fallback_to_rule_based,
        "save_llm_trace": compile_config.save_llm_trace,
        "include_raw_source": compile_config.include_raw_source,
    }
