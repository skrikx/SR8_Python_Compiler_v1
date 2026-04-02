from pathlib import Path

from sr8.eval.corpus import load_benchmark_cases
from sr8.eval.harness import run_benchmark_suite


def test_self_hosting_case_pack_is_complete() -> None:
    cases = load_benchmark_cases("self_hosting")

    assert len(cases) == 4
    assert {case.case_id for case in cases} == {
        "sr8_artifact_eval",
        "sr8_recompile_whitepaper",
        "sr8_release_transform",
        "sr8_workflow_compile",
    }


def test_self_hosting_suite_proves_compile_transform_and_recompile(tmp_path: Path) -> None:
    report = run_benchmark_suite("self_hosting", out_dir=tmp_path)
    result_map = {result.case_id: result for result in report.results}

    assert report.summary.total_cases == 4
    assert len(result_map["sr8_release_transform"].transform_checks) == 3
    assert all(check.success for check in result_map["sr8_release_transform"].transform_checks)
    assert result_map["sr8_recompile_whitepaper"].profile == "whitepaper_outline"
    assert Path(result_map["sr8_artifact_eval"].output_path or "").exists()
