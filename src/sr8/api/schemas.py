from __future__ import annotations

from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

RouteExposureClass = Literal["safe", "deliberate-exposure", "trusted-local"]
AuthMode = Literal["trusted-local", "bearer-token"]


class RouteContract(BaseModel):
    route_id: str
    exposure_class: RouteExposureClass
    path_policy: str
    summary: str


class RequestIdentity(BaseModel):
    actor_id: str
    auth_mode: AuthMode
    idempotency_key: str | None = None
    remote_host: str = "local"


class CompileRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    source_text: str | None = Field(
        default=None,
        validation_alias=AliasChoices("source_text", "source"),
    )
    source_payload: dict[str, object] | None = None
    profile: str | None = None
    target: str | None = None
    validate_target: bool = Field(
        default=False,
        validation_alias=AliasChoices("validate_target", "validate"),
    )
    source_type: Literal["text", "markdown", "json", "yaml"] | None = None
    mode: Literal["rules", "assist", "auto"] = "auto"
    rule_only: bool = False
    assist_extract: bool = False
    assist_provider: str | None = None
    assist_model: str | None = None
    save_llm_trace: bool = False
    persist: bool = False
    async_mode: bool = False
    idempotency_key: str | None = None
    workspace_path: str | None = None

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
    workspace_path: str | None = None


class LintRequest(BaseModel):
    artifact_ref: str
    workspace_path: str | None = None


class InspectRequest(BaseModel):
    target: str
    workspace_path: str | None = None


class BenchmarkRunRequest(BaseModel):
    suite: str | None = None
    out_dir: str = "benchmarks/results"


class HealthResponse(BaseModel):
    route_contract: RouteContract
    status: str


class StatusResponse(BaseModel):
    route_contract: RouteContract
    status: str
    workspace_path: str
    default_profile: object
    extraction_adapter: object
    providers: list[dict[str, object]]
    benchmark_suites: list[str]


class ProvidersResponse(BaseModel):
    route_contract: RouteContract
    providers: list[dict[str, object]]


class ProvidersProbeResponse(BaseModel):
    route_contract: RouteContract
    result: dict[str, object] | None = None
    results: list[dict[str, object]] = Field(default_factory=list)


class SettingsResponse(BaseModel):
    route_contract: RouteContract
    settings: dict[str, object]


class ArtifactsResponse(BaseModel):
    route_contract: RouteContract
    records: list[dict[str, object]]


class ArtifactDetailResponse(BaseModel):
    route_contract: RouteContract
    record: dict[str, object]
    payload: dict[str, object]


class ReceiptsResponse(BaseModel):
    route_contract: RouteContract
    receipts: list[dict[str, object]]


class CompileResponse(BaseModel):
    route_contract: RouteContract
    frontdoor: dict[str, object] | None = None
    artifact: dict[str, object] | None = None
    receipt: dict[str, object] | None = None
    normalized_source: dict[str, object] | None = None
    extracted_dimensions: dict[str, object] | None = None
    target_validation: dict[str, object] | None = None
    persistence: dict[str, object] | None = None
    job: dict[str, object] | None = None
    request_identity: RequestIdentity
    replayed: bool = False


class InspectResponse(BaseModel):
    route_contract: RouteContract
    artifact: dict[str, object]
    artifact_ref: str
    mode: str


class ReportEnvelope(BaseModel):
    route_contract: RouteContract
    request_identity: RequestIdentity
    payload: dict[str, object]


class BenchmarkSuitesResponse(BaseModel):
    route_contract: RouteContract
    suites: list[str]


class BenchmarkRunResponse(BaseModel):
    route_contract: RouteContract
    payload: dict[str, object]


class JobResponse(BaseModel):
    route_contract: RouteContract
    job: dict[str, object]
    request_identity: RequestIdentity
