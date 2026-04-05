from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from sr8.eval.types import (
    BenchmarkCaseResult,
    BenchmarkRunReport,
    BenchmarkSummary,
    DimensionId,
    RegressionReport,
)


def build_run_summary(suite: str, results: list[BenchmarkCaseResult]) -> BenchmarkSummary:
    total_cases = len(results)
    passed_cases = sum(1 for result in results if result.passed)
    failed_cases = total_cases - passed_cases
    average_score = round(
        sum(result.aggregate_score for result in results) / total_cases if total_cases else 0.0,
        3,
    )
    dimension_scores: dict[DimensionId, list[float]] = {}
    failure_clusters: dict[str, int] = {}
    for result in results:
        for score in result.dimension_scores:
            dimension_scores.setdefault(score.dimension, []).append(score.score)
        for cluster in result.failure_clusters:
            failure_clusters[cluster] = failure_clusters.get(cluster, 0) + 1
    average_dimension_scores = cast(
        dict[DimensionId, float],
        {
            dimension: round(sum(values) / len(values), 3)
            for dimension, values in sorted(dimension_scores.items())
        },
    )
    return BenchmarkSummary(
        suite=suite,
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        average_score=average_score,
        average_dimension_scores=average_dimension_scores,
        failure_clusters=dict(sorted(failure_clusters.items())),
    )


def _render_run_report_markdown(report: BenchmarkRunReport) -> str:
    lines = [
        f"# Benchmark Report: {report.suite}",
        "",
        f"- Run ID: `{report.run_id}`",
        f"- Compiler Version: `{report.compiler_version}`",
        f"- Rubric: `{report.rubric_id}`",
        f"- Total Cases: {report.summary.total_cases}",
        f"- Passed Cases: {report.summary.passed_cases}",
        f"- Failed Cases: {report.summary.failed_cases}",
        f"- Average Score: {report.summary.average_score}",
        "",
        "## Average Dimension Scores",
    ]
    for dimension, score in report.summary.average_dimension_scores.items():
        lines.append(f"- `{dimension}`: {score}")
    lines.extend(["", "## Failure Clusters"])
    if report.summary.failure_clusters:
        for cluster, count in report.summary.failure_clusters.items():
            lines.append(f"- `{cluster}`: {count}")
    else:
        lines.append("- none")
    lines.extend(["", "## Cases"])
    for result in report.results:
        lines.append(
            f"- `{result.case_id}`: score={result.aggregate_score} "
            f"passed={result.passed} readiness={result.readiness_status}"
        )
    return "\n".join(lines) + "\n"


def _render_regression_markdown(report: RegressionReport) -> str:
    lines = [
        "# Benchmark Regression Report",
        "",
        f"- Baseline Run: `{report.baseline_run_id}` ({report.baseline_version})",
        f"- Candidate Run: `{report.candidate_run_id}` ({report.candidate_version})",
        f"- Summary Delta: {report.summary_delta}",
        f"- Case Delta: {report.case_delta}",
        "",
        "## Dimension Deltas",
    ]
    for delta in report.dimension_deltas:
        lines.append(
            f"- `{delta.dimension}`: {delta.delta} "
            f"({delta.baseline_score} -> {delta.candidate_score})"
        )
    lines.extend(["", "## Improvements"])
    if report.improvements:
        lines.extend(f"- {item}" for item in report.improvements)
    else:
        lines.append("- none")
    lines.extend(["", "## Regressions"])
    if report.regressions:
        lines.extend(f"- {item}" for item in report.regressions)
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_run_report(
    report: BenchmarkRunReport,
    out_dir: str | Path,
    file_stem: str | None = None,
) -> tuple[Path, Path]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = file_stem or report.suite.replace("/", "_")
    json_path = output_dir / f"{stem}.json"
    markdown_path = output_dir / f"{stem}.md"
    latest_path = output_dir / "latest.json"
    json_path.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")
    markdown_path.write_text(_render_run_report_markdown(report), encoding="utf-8")
    latest_path.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")
    return json_path, markdown_path


def write_regression_report(
    report: RegressionReport,
    out_dir: str | Path,
    file_stem: str = "comparison",
) -> tuple[Path, Path]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{file_stem}.json"
    markdown_path = output_dir / f"{file_stem}.md"
    json_path.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")
    markdown_path.write_text(_render_regression_markdown(report), encoding="utf-8")
    return json_path, markdown_path


def load_run_report(path: str | Path) -> BenchmarkRunReport:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return BenchmarkRunReport.model_validate(payload)
