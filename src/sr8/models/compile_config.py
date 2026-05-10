from __future__ import annotations

from sr8.models.base import SR8Model
from sr8.models.schema_version import SchemaVersion
from sr8.version import __version__


class CompileConfig(SR8Model):
    artifact_version: str = SchemaVersion().canonical_schema
    compiler_version: str = __version__
    profile: str = "generic"
    target: str | None = None
    validate_target: bool = False
    include_raw_source: bool = False
    extraction_adapter: str = "rule_based"
    assist_provider: str | None = None
    assist_model: str | None = None
    assist_fallback_to_rule_based: bool = True
