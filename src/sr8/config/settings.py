from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict

from sr8.models.compile_config import CompileConfig


class SR8Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SR8_", extra="ignore")

    default_profile: str = "generic"
    extraction_adapter: str = "rule_based"
    include_raw_source: bool = False
    assist_provider: str | None = None
    assist_model: str | None = None
    assist_fallback_to_rule_based: bool = True
    workspace_path: str = ".sr8"


def resolve_compile_config(
    settings: SR8Settings,
    *,
    profile: str | None = None,
    rule_only: bool = False,
    assist_provider: str | None = None,
    assist_model: str | None = None,
) -> CompileConfig:
    effective_profile = profile or settings.default_profile
    effective_provider = assist_provider or settings.assist_provider
    effective_model = assist_model or settings.assist_model
    extraction_adapter = settings.extraction_adapter

    if rule_only:
        extraction_adapter = "rule_based"
        effective_provider = None
        effective_model = None
    elif effective_provider or effective_model:
        extraction_adapter = "model_assisted"

    if extraction_adapter == "model_assisted" and (not effective_provider or not effective_model):
        msg = (
            "Model-assisted extraction requires both assist_provider and assist_model "
            "or matching SR8_ASSIST_PROVIDER and SR8_ASSIST_MODEL settings."
        )
        raise ValueError(msg)

    return CompileConfig(
        profile=effective_profile,
        include_raw_source=settings.include_raw_source,
        extraction_adapter=extraction_adapter,
        assist_provider=effective_provider,
        assist_model=effective_model,
        assist_fallback_to_rule_based=settings.assist_fallback_to_rule_based,
    )


def build_settings_payload(settings: SR8Settings) -> dict[str, object]:
    payload: dict[str, object] = {
        "default_profile": settings.default_profile,
        "extraction_adapter": settings.extraction_adapter,
        "assist_provider": settings.assist_provider,
        "assist_model": settings.assist_model,
        "assist_fallback_to_rule_based": settings.assist_fallback_to_rule_based,
        "include_raw_source": settings.include_raw_source,
        "workspace_path": settings.workspace_path,
    }
    try:
        compile_config = resolve_compile_config(settings)
    except ValueError as exc:
        return payload | {"configuration_error": str(exc)}
    return payload | {
        "default_profile": compile_config.profile,
        "extraction_adapter": compile_config.extraction_adapter,
        "assist_provider": compile_config.assist_provider,
        "assist_model": compile_config.assist_model,
        "assist_fallback_to_rule_based": compile_config.assist_fallback_to_rule_based,
        "include_raw_source": compile_config.include_raw_source,
    }
