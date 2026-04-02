from pathlib import Path

from sr8.eval.corpus import load_benchmark_cases
from sr8.eval.harness import run_benchmark_case, run_benchmark_suite


def test_run_benchmark_case_writes_outputs(tmp_path: Path) -> None:
    case = load_benchmark_cases("founder")[0]

    result = run_benchmark_case(case, out_dir=tmp_path)

    assert result.case_id == "founder_launch"
    assert result.output_path is not None
    assert Path(result.output_path).exists()
    assert len(result.dimension_scores) == 6
    assert all(check.success for check in result.transform_checks)


def test_run_benchmark_suite_builds_summary(tmp_path: Path) -> None:
    report = run_benchmark_suite("founder", out_dir=tmp_path)

    assert report.suite == "founder"
    assert report.summary.total_cases == 1
    assert report.summary.average_score > 0.6
    assert report.summary.passed_cases == 1
