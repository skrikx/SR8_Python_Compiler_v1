from __future__ import annotations

from collections.abc import Mapping

from sr8.eval.rubrics import get_default_rubric
from sr8.eval.types import (
    BenchmarkCase,
    BenchmarkCaseResult,
    DimensionId,
    DimensionScore,
    TransformCheck,
)
from sr8.models.extraction_trace import ExtractionTrace
from sr8.models.intent_artifact import IntentArtifact
from sr8.models.lint_report import LintReport
from sr8.models.validation import ValidationReport


def _normalize_text(value: str) -> str:
    return " ".join(value.lower().split())


def _collect_artifact_text(artifact: IntentArtifact) -> str:
    parts = [
        artifact.objective,
        artifact.authority_context,
        artifact.target_class,
        *artifact.scope,
        *artifact.exclusions,
        *artifact.constraints,
        *artifact.context_package,
        *artifact.dependencies,
        *artifact.assumptions,
        *artifact.success_criteria,
        *artifact.output_contract,
    ]
    return _normalize_text(" ".join(part for part in parts if part))


def _field_has_content(artifact: IntentArtifact, field_name: str) -> bool:
    value = getattr(artifact, field_name, None)
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(str(item).strip() for item in value)
    if isinstance(value, Mapping):
        return any(bool(item) for item in value.values())
    return value is not None


def _score_ratio(matches: int, total: int) -> float:
    if total == 0:
        return 1.0
    return round(matches / total, 3)


def _build_dimension_score(
    dimension: DimensionId,
    score: float,
    findings: list[str],
) -> DimensionScore:
    rubric = {item.dimension: item for item in get_default_rubric().dimensions}
    threshold = rubric[dimension].passing_score
    return DimensionScore(
        dimension=dimension,
        score=round(score, 3),
        passed=score >= threshold,
        findings=findings,
    )


def score_case(
    case: BenchmarkCase,
    artifact: IntentArtifact,
    validation: ValidationReport,
    lint: LintReport,
    trace: ExtractionTrace | None,
    transform_checks: list[TransformCheck],
) -> tuple[list[DimensionScore], float]:
    artifact_text = _collect_artifact_text(artifact)
    trace_map = {
        signal.field_name: signal
        for signal in (trace.confidence if trace is not None else [])
    }

    faithfulness_hits = [
        term for term in case.expectations.source_terms if _normalize_text(term) in artifact_text
    ]
    faithfulness_findings = [
        f"Missing source term: {term}"
        for term in case.expectations.source_terms
        if term not in faithfulness_hits
    ]
    faithfulness = _build_dimension_score(
        "faithfulness",
        _score_ratio(len(faithfulness_hits), len(case.expectations.source_terms)),
        faithfulness_findings,
    )

    completeness_hits = [
        field_name
        for field_name in case.expectations.required_fields
        if _field_has_content(artifact, field_name)
    ]
    completeness_findings = [
        f"Required field empty: {field_name}"
        for field_name in case.expectations.required_fields
        if field_name not in completeness_hits
    ]
    completeness = _build_dimension_score(
        "completeness",
        _score_ratio(len(completeness_hits), len(case.expectations.required_fields)),
        completeness_findings,
    )

    constraint_surface = _normalize_text(
        " ".join(
            [
                artifact.authority_context,
                *artifact.constraints,
                *artifact.exclusions,
                *artifact.success_criteria,
                *artifact.output_contract,
            ]
        )
    )
    constraint_hits = [
        term
        for term in case.expectations.constraint_terms
        if _normalize_text(term) in constraint_surface
    ]
    constraint_findings = [
        f"Missing constraint term: {term}"
        for term in case.expectations.constraint_terms
        if term not in constraint_hits
    ]
    constraint_integrity = _build_dimension_score(
        "constraint_integrity",
        _score_ratio(len(constraint_hits), len(case.expectations.constraint_terms)),
        constraint_findings,
    )

    readiness_map = {"pass": 1.0, "warn": 0.7, "fail": 0.2}
    lint_map = {"pass": 1.0, "warn": 0.8, "fail": 0.3}
    readiness_rank = {"fail": 0, "warn": 1, "pass": 2}
    readiness_findings = [
        *(issue.message for issue in validation.errors),
        *(issue.message for issue in validation.warnings),
        *(finding.message for finding in lint.findings[:3]),
    ]
    readiness_score = round(
        (readiness_map[validation.readiness_status] + lint_map[lint.status]) / 2,
        3,
    )
    if (
        readiness_rank[validation.readiness_status]
        < readiness_rank[case.expectations.minimum_readiness]
    ):
        readiness_score = round(max(readiness_score - 0.2, 0.0), 3)
        readiness_findings.append(
            "Readiness below expected minimum: "
            f"{validation.readiness_status} < {case.expectations.minimum_readiness}"
        )
    readiness = _build_dimension_score("readiness", readiness_score, readiness_findings)

    trust_findings: list[str] = []
    trust_hits = 0
    trust_total = 0
    for field_name, status in case.expectations.trust_field_statuses.items():
        trust_total += 1
        actual = trace_map.get(field_name)
        if actual is not None and actual.status == status:
            trust_hits += 1
        else:
            actual_status = actual.status if actual is not None else "missing"
            trust_findings.append(
                f"Trust status mismatch for {field_name}: expected {status}, got {actual_status}"
            )
    if case.expectations.expect_human_review is not None:
        trust_total += 1
        actual_review = artifact.governance_flags.requires_human_review
        if actual_review == case.expectations.expect_human_review:
            trust_hits += 1
        else:
            trust_findings.append(
                "Human-review expectation mismatch: "
                f"expected {case.expectations.expect_human_review}, got {actual_review}"
            )
    if trust_total == 0:
        trust_total = 1
        trust_hits = 1 if trace is not None else 0
        if trace is None:
            trust_findings.append("No extraction trace available.")
    trust_surface = _build_dimension_score(
        "trust_surface",
        _score_ratio(trust_hits, trust_total),
        trust_findings,
    )

    required_targets = case.expectations.required_transform_targets or case.transform_targets
    transform_hits = [
        check.target
        for check in transform_checks
        if check.success and check.target in required_targets
    ]
    transform_findings = [
        check.detail for check in transform_checks if not check.success
    ]
    for target in required_targets:
        if target not in transform_hits:
            transform_findings.append(f"Required transform missing: {target}")
    transform_utility = _build_dimension_score(
        "transform_utility",
        _score_ratio(len(transform_hits), len(required_targets)),
        transform_findings,
    )

    scores = [
        faithfulness,
        completeness,
        constraint_integrity,
        readiness,
        trust_surface,
        transform_utility,
    ]
    aggregate = round(sum(item.score for item in scores) / len(scores), 3)
    return scores, aggregate


def build_case_result(
    case: BenchmarkCase,
    artifact: IntentArtifact,
    validation: ValidationReport,
    lint: LintReport,
    trace: ExtractionTrace | None,
    transform_checks: list[TransformCheck],
    output_path: str | None = None,
) -> BenchmarkCaseResult:
    dimension_scores, aggregate = score_case(
        case,
        artifact,
        validation,
        lint,
        trace,
        transform_checks,
    )
    findings = [finding for score in dimension_scores for finding in score.findings]
    failure_clusters = sorted(
        {
            score.dimension
            for score in dimension_scores
            if not score.passed
        }
    )
    return BenchmarkCaseResult(
        case_id=case.case_id,
        suite=case.suite,
        profile=artifact.profile,
        artifact_id=artifact.artifact_id,
        readiness_status=validation.readiness_status,
        lint_status=lint.status,
        dimension_scores=dimension_scores,
        aggregate_score=aggregate,
        passed=all(score.passed for score in dimension_scores),
        findings=findings,
        failure_clusters=[str(cluster) for cluster in failure_clusters],
        transform_checks=transform_checks,
        output_path=output_path,
        source_hash=artifact.source.source_hash,
    )
