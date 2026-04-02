from __future__ import annotations

from sr8.eval.types import BenchmarkRunReport, RegressionDimensionDelta, RegressionReport


def compare_benchmark_reports(
    baseline: BenchmarkRunReport,
    candidate: BenchmarkRunReport,
) -> RegressionReport:
    baseline_dimensions = baseline.summary.average_dimension_scores
    candidate_dimensions = candidate.summary.average_dimension_scores
    dimension_names = sorted(set(baseline_dimensions) | set(candidate_dimensions))

    dimension_deltas = [
        RegressionDimensionDelta(
            dimension=dimension,
            baseline_score=baseline_dimensions.get(dimension, 0.0),
            candidate_score=candidate_dimensions.get(dimension, 0.0),
            delta=round(
                candidate_dimensions.get(dimension, 0.0) - baseline_dimensions.get(dimension, 0.0),
                3,
            ),
        )
        for dimension in dimension_names
    ]

    baseline_cases = {result.case_id: result for result in baseline.results}
    candidate_cases = {result.case_id: result for result in candidate.results}
    shared_case_ids = sorted(set(baseline_cases) & set(candidate_cases))

    improvements: list[str] = []
    regressions: list[str] = []
    for case_id in shared_case_ids:
        delta = round(
            candidate_cases[case_id].aggregate_score - baseline_cases[case_id].aggregate_score,
            3,
        )
        if delta > 0:
            improvements.append(f"{case_id}: +{delta}")
        elif delta < 0:
            regressions.append(f"{case_id}: {delta}")

    return RegressionReport(
        baseline_run_id=baseline.run_id,
        candidate_run_id=candidate.run_id,
        baseline_version=baseline.compiler_version,
        candidate_version=candidate.compiler_version,
        summary_delta=round(candidate.summary.average_score - baseline.summary.average_score, 3),
        case_delta=candidate.summary.passed_cases - baseline.summary.passed_cases,
        dimension_deltas=dimension_deltas,
        regressions=regressions,
        improvements=improvements,
    )
