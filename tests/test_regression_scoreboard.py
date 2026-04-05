from sr8.eval.regression import compare_benchmark_reports
from sr8.eval.types import (
    BenchmarkCaseResult,
    BenchmarkRunReport,
    BenchmarkSummary,
    DimensionScore,
    TransformCheck,
)


def _case_result(case_id: str, aggregate_score: float) -> BenchmarkCaseResult:
    return BenchmarkCaseResult(
        case_id=case_id,
        suite="founder",
        profile="prd",
        artifact_id=f"art_{case_id}",
        readiness_status="pass",
        lint_status="pass",
        dimension_scores=[
            DimensionScore(dimension="faithfulness", score=aggregate_score, passed=True),
            DimensionScore(dimension="completeness", score=aggregate_score, passed=True),
            DimensionScore(dimension="constraint_integrity", score=aggregate_score, passed=True),
            DimensionScore(dimension="readiness", score=aggregate_score, passed=True),
            DimensionScore(dimension="trust_surface", score=aggregate_score, passed=True),
            DimensionScore(dimension="transform_utility", score=aggregate_score, passed=True),
        ],
        aggregate_score=aggregate_score,
        passed=True,
        transform_checks=[TransformCheck(target="markdown_prd", success=True, detail="ok")],
        source_hash=f"hash_{case_id}",
    )


def test_compare_benchmark_reports_detects_improvement() -> None:
    baseline = BenchmarkRunReport(
        run_id="base",
        suite="founder",
        compiler_version="1.1.0",
        rubric_id="wf12.default",
        results=[_case_result("founder_launch", 0.7)],
        summary=BenchmarkSummary(
            suite="founder",
            total_cases=1,
            passed_cases=1,
            failed_cases=0,
            average_score=0.7,
            average_dimension_scores={
                "faithfulness": 0.7,
                "completeness": 0.7,
                "constraint_integrity": 0.7,
                "readiness": 0.7,
                "trust_surface": 0.7,
                "transform_utility": 0.7,
            },
        ),
    )
    candidate = baseline.model_copy(
        update={
            "run_id": "candidate",
            "compiler_version": "1.2.0",
            "results": [_case_result("founder_launch", 0.9)],
            "summary": BenchmarkSummary(
                suite="founder",
                total_cases=1,
                passed_cases=1,
                failed_cases=0,
                average_score=0.9,
                average_dimension_scores={
                    "faithfulness": 0.9,
                    "completeness": 0.9,
                    "constraint_integrity": 0.9,
                    "readiness": 0.9,
                    "trust_surface": 0.9,
                    "transform_utility": 0.9,
                },
            ),
        }
    )

    report = compare_benchmark_reports(baseline, candidate)

    assert report.summary_delta == 0.2
    assert report.case_delta == 0
    assert report.improvements == ["founder_launch: +0.2"]
    assert report.regressions == []
