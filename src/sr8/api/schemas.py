from __future__ import annotations

from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class CompileRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    source_text: str | None = Field(
        default=None,
        validation_alias=AliasChoices("source_text", "source"),
    )
    source_payload: dict[str, object] | None = None
    profile: str | None = None
    source_type: Literal["text", "markdown", "json", "yaml"] | None = None
    rule_only: bool = False
    assist_provider: str | None = None
    assist_model: str | None = None

    @model_validator(mode="after")
    def validate_single_source(self) -> CompileRequest:
        source_count = int(self.source_text is not None) + int(self.source_payload is not None)
        if source_count != 1:
            msg = "Provide exactly one of source_text/source or source_payload."
            raise ValueError(msg)
        return self


class ValidateRequest(BaseModel):
    artifact_path: str
    profile: str | None = None


class TransformRequest(BaseModel):
    artifact_path: str
    target: str


class DiffRequest(BaseModel):
    left: str
    right: str
    workspace_path: str = ".sr8"


class LintRequest(BaseModel):
    artifact_ref: str
    workspace_path: str = ".sr8"


class InspectRequest(BaseModel):
    target: str
    workspace_path: str = ".sr8"


class BenchmarkRunRequest(BaseModel):
    suite: str | None = None
    out_dir: str = "benchmarks/results"
