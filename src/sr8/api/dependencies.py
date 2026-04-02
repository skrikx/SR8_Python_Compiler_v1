from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path

import yaml
from pydantic import ValidationError

from sr8.adapters import list_provider_names
from sr8.api.errors import (
    ArtifactNotFoundError,
    InvalidArtifactPayloadError,
    InvalidArtifactReferenceError,
    InvalidConfigurationError,
    InvalidInspectTargetError,
    InvalidProviderError,
    PathInputDisallowedError,
    UnsupportedArtifactContentError,
)
from sr8.api.schemas import CompileRequest
from sr8.config.settings import SR8Settings, build_settings_payload, resolve_compile_config
from sr8.io.exporters import load_artifact
from sr8.models.compile_config import CompileConfig
from sr8.models.derivative_artifact import DerivativeArtifact
from sr8.models.intent_artifact import IntentArtifact
from sr8.models.source_intent import SourceType
from sr8.storage.load import load_by_id
from sr8.storage.workspace import SR8Workspace, init_workspace
from sr8.utils.paths import resolve_trusted_local_path

WINDOWS_DRIVE_PATH_RE = re.compile(r"^[a-zA-Z]:[\\/]")
ARTIFACT_SUFFIXES = {".json", ".yaml", ".yml"}
ARTIFACT_ID_RE = re.compile(r"^(art|drv)_[A-Za-z0-9]+$")


def get_settings() -> SR8Settings:
    return SR8Settings()


def get_settings_payload(settings: SR8Settings | None = None) -> dict[str, object]:
    return build_settings_payload(settings or get_settings())


def get_effective_settings_payload(settings: SR8Settings | None = None) -> dict[str, object]:
    payload = get_settings_payload(settings)
    configuration_error = payload.get("configuration_error")
    if isinstance(configuration_error, str):
        raise InvalidConfigurationError(configuration_error)
    return payload


def resolve_workspace(path: str | None = None) -> SR8Workspace:
    settings = get_settings()
    return init_workspace(path or settings.workspace_path)


def validate_provider_name(provider: str | None) -> None:
    if provider is None:
        return
    if provider not in list_provider_names():
        raise InvalidProviderError(provider)


def resolve_compile_config_for_request(
    payload: CompileRequest,
    settings: SR8Settings | None = None,
) -> CompileConfig:
    active_settings = settings or get_settings()
    try:
        resolved = resolve_compile_config(
            active_settings,
            profile=payload.profile,
            rule_only=payload.rule_only,
            assist_provider=payload.assist_provider,
            assist_model=payload.assist_model,
        )
    except ValueError as exc:
        raise InvalidConfigurationError(str(exc)) from exc
    validate_provider_name(resolved.assist_provider)
    return resolved


def resolve_compile_source(
    payload: CompileRequest,
) -> tuple[str | Mapping[str, object], SourceType | None]:
    source_type = payload.source_type
    if payload.source_payload is not None:
        return payload.source_payload, source_type
    source_text = payload.source_text or ""
    if looks_like_disallowed_api_path(source_text):
        raise PathInputDisallowedError(source_text)
    return source_text, source_type


def load_artifact_for_api(path: str | Path) -> IntentArtifact:
    try:
        artifact_path = resolve_trusted_local_path(path, must_exist=True)
    except FileNotFoundError as exc:
        raise ArtifactNotFoundError(str(path)) from exc
    except ValueError as exc:
        raise InvalidArtifactReferenceError(str(path), str(exc)) from exc
    try:
        return load_artifact(artifact_path)
    except UnicodeDecodeError as exc:
        raise UnsupportedArtifactContentError(str(artifact_path), "binary_or_non_utf8") from exc
    except json.JSONDecodeError as exc:
        raise InvalidArtifactPayloadError(str(artifact_path), "invalid_json") from exc
    except yaml.YAMLError as exc:
        raise InvalidArtifactPayloadError(str(artifact_path), "invalid_yaml") from exc
    except ValidationError as exc:
        raise InvalidArtifactPayloadError(str(artifact_path), "schema_validation_failed") from exc
    except ValueError as exc:
        reason = "unsupported_extension"
        if "object/map" in str(exc):
            reason = "artifact_payload_not_object"
        raise InvalidArtifactPayloadError(str(artifact_path), reason) from exc


def resolve_canonical_artifact_for_api(
    value: str,
    workspace_path: str,
) -> tuple[IntentArtifact, str]:
    try:
        candidate = resolve_trusted_local_path(value, must_exist=True, extra_roots=[workspace_path])
    except FileNotFoundError:
        candidate = None
    except ValueError as exc:
        raise InvalidArtifactReferenceError(value, str(exc)) from exc
    if candidate is not None:
        artifact = load_artifact_for_api(candidate)
        return artifact, str(candidate)
    if looks_like_artifact_reference(value):
        raise ArtifactNotFoundError(value)

    try:
        loaded = load_by_id(resolve_workspace(workspace_path), value)
    except ValueError as exc:
        raise ArtifactNotFoundError(value) from exc
    if isinstance(loaded, DerivativeArtifact):
        msg = f"Identifier '{value}' resolves to a derivative artifact, not canonical."
        raise InvalidArtifactReferenceError(value, msg)
    return loaded, value


def resolve_inspect_artifact_for_api(
    value: str,
    workspace_path: str,
) -> tuple[IntentArtifact, str]:
    stripped = value.strip()
    try:
        candidate = resolve_trusted_local_path(
            stripped,
            must_exist=True,
            extra_roots=[workspace_path],
        )
    except FileNotFoundError:
        candidate = None
    except ValueError as exc:
        raise InvalidInspectTargetError(f"{stripped}: {exc}") from exc
    if candidate is not None and candidate.suffix.lower() in ARTIFACT_SUFFIXES:
        artifact = load_artifact_for_api(candidate)
        return artifact, str(candidate)
    if ARTIFACT_ID_RE.match(stripped):
        return resolve_canonical_artifact_for_api(stripped, workspace_path)
    raise InvalidInspectTargetError(stripped)


def looks_like_disallowed_api_path(value: str) -> bool:
    stripped = value.strip()
    if not stripped or "\n" in stripped or "\r" in stripped:
        return False
    if WINDOWS_DRIVE_PATH_RE.match(stripped):
        return True
    if (
        stripped.startswith("\\\\")
        or stripped.startswith("/")
        or stripped.startswith("~/")
        or stripped.startswith("~\\")
    ):
        return True
    try:
        resolve_trusted_local_path(stripped, must_exist=True)
        return True
    except (OSError, ValueError, FileNotFoundError):
        return False


def looks_like_artifact_reference(value: str) -> bool:
    stripped = value.strip()
    if not stripped or "\n" in stripped or "\r" in stripped:
        return False
    suffix = Path(stripped).suffix.lower()
    return suffix in ARTIFACT_SUFFIXES or looks_like_disallowed_api_path(stripped)
