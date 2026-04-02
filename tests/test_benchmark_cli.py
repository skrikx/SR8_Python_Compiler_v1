from pathlib import Path

from typer.testing import CliRunner

from sr8.cli import app
from sr8.eval.reports import write_run_report
from sr8.eval.types import (
    BenchmarkCaseResult,
    BenchmarkRunReport,
    BenchmarkSummary,
    DimensionScore,
)

runner = CliRunner()


def _mock_report(run_id: str, version: str, score: float) -> BenchmarkRunReport:
    result = BenchmarkCaseResult(
        case_id="mock_case",
        suite="founder",
        profile="prd",
        artifact_id="art_mock",
        readiness_status="pass",
        lint_status="pass",
        dimension_scores=[
            DimensionScore(dimension="faithfulness", score=score, passed=True),
            DimensionScore(dimension="completeness", score=score, passed=True),
            DimensionScore(dimension="constraint_integrity", score=score, passed=True),
            DimensionScore(dimension="readiness", score=score, passed=True),
            DimensionScore(dimension="trust_surface", score=score, passed=True),
            DimensionScore(dimension="transform_utility", score=score, passed=True),
        ],
        aggregate_score=score,
        passed=True,
        source_hash="hash_mock",
    )
    return BenchmarkRunReport(
        run_id=run_id,
        suite="founder",
        compiler_version=version,
        rubric_id="wf12.default",
        results=[result],
        summary=BenchmarkSummary(
            suite="founder",
            total_cases=1,
            passed_cases=1,
            failed_cases=0,
            average_score=score,
            average_dimension_scores={
                "faithfulness": score,
                "completeness": score,
                "constraint_integrity": score,
                "readiness": score,
                "trust_surface": score,
                "transform_utility": score,
            },
        ),
    )


def test_benchmark_run_cli_writes_reports(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["benchmark", "run", "--suite", "founder", "--out", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert "Average Score:" in result.stdout
    assert (tmp_path / "founder.json").exists()
    assert (tmp_path / "founder.md").exists()


def test_benchmark_compare_cli_writes_regression_report(tmp_path: Path) -> None:
    baseline_json, _ = write_run_report(_mock_report("base", "1.1.0", 0.7), tmp_path, "baseline")
    candidate_json, _ = write_run_report(
        _mock_report("candidate", "1.2.0", 0.9),
        tmp_path,
        "candidate",
    )

    result = runner.invoke(
        app,
        [
            "benchmark",
            "compare",
            str(baseline_json),
            str(candidate_json),
            "--out",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert "Summary Delta: 0.2" in result.stdout
    assert (tmp_path / "comparison.json").exists()
    assert (tmp_path / "comparison.md").exists()
