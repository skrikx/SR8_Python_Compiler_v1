from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from sr8.models.base import SR8Model, utc_now
from sr8.models.extraction_confidence import FieldStatus
from sr8.models.source_intent import SourceType

BenchmarkSuite = Literal[
    "founder",
    "research",
    "repo",
    "procedure",
    "weak_inputs",
    "self_hosting",
]
CaseSourceKind = Literal["text", "artifact"]
ReadinessStatus = Literal["pass", "warn", "fail"]
DimensionId = Literal[
    "faithfulness",
    "completeness",
    "constraint_integrity",
    "readiness",
    "trust_surface",
    "transform_utility",
]


class BenchmarkExpectation(SR8Model):
    source_terms: list[str] = Field(default_factory=list)
    required_fields: list[str] = Field(default_factory=list)
    constraint_terms: list[str] = Field(default_factory=list)
    required_transform_targets: list[str] = Field(default_factory=list)
    trust_field_statuses: dict[str, FieldStatus] = Field(default_factory=dict)
    expect_human_review: bool | None = None
    minimum_readiness: ReadinessStatus = "warn"


class BenchmarkCase(SR8Model):
    case_id: str
    suite: BenchmarkSuite
    name: str
    description: str
    source_path: str
    source_kind: CaseSourceKind = "text"
    profile: str = "generic"
    source_type: SourceType | None = None
    transform_targets: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    expectations: BenchmarkExpectation = Field(default_factory=BenchmarkExpectation)


class RubricDimension(SR8Model):
    dimension: DimensionId
    question: str
    passing_score: float = 0.65
    weight: float = 1.0


class RubricDefinition(SR8Model):
    rubric_id: str
    name: str
    dimensions: list[RubricDimension]
    notes: list[str] = Field(default_factory=list)


class TransformCheck(SR8Model):
    target: str
    success: bool
    detail: str
    derivative_id: str | None = None


class DimensionScore(SR8Model):
    dimension: DimensionId
    score: float
    passed: bool
    findings: list[str] = Field(default_factory=list)


class BenchmarkCaseResult(SR8Model):
    case_id: str
    suite: BenchmarkSuite
    profile: str
    artifact_id: str
    readiness_status: ReadinessStatus
    lint_status: ReadinessStatus
    dimension_scores: list[DimensionScore]
    aggregate_score: float
    passed: bool
    findings: list[str] = Field(default_factory=list)
    failure_clusters: list[str] = Field(default_factory=list)
    transform_checks: list[TransformCheck] = Field(default_factory=list)
    output_path: str | None = None
    source_hash: str


class BenchmarkSummary(SR8Model):
    suite: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    average_score: float
    average_dimension_scores: dict[DimensionId, float]
    failure_clusters: dict[str, int] = Field(default_factory=dict)


class BenchmarkRunReport(SR8Model):
    run_id: str
    suite: str
    compiler_version: str
    rubric_id: str
    generated_at: datetime = Field(default_factory=utc_now)
    results: list[BenchmarkCaseResult]
    summary: BenchmarkSummary


class RegressionDimensionDelta(SR8Model):
    dimension: DimensionId
    baseline_score: float
    candidate_score: float
    delta: float


class RegressionReport(SR8Model):
    baseline_run_id: str
    candidate_run_id: str
    baseline_version: str
    candidate_version: str
    summary_delta: float
    case_delta: int
    dimension_deltas: list[RegressionDimensionDelta]
    regressions: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
