from __future__ import annotations

from pydantic import BaseModel


class CompileRequest(BaseModel):
    source: str
    profile: str = "generic"
    source_type: str | None = None


class ValidateRequest(BaseModel):
    artifact_path: str
    profile: str | None = None


class TransformRequest(BaseModel):
    artifact_path: str
    target: str
