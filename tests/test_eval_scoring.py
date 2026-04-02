from sr8.eval.corpus import load_benchmark_cases
from sr8.eval.harness import run_benchmark_case


def test_weak_case_trust_surface_scores_weakness_honestly() -> None:
    case = load_benchmark_cases("weak_inputs")[0]

    result = run_benchmark_case(case)
    score_map = {score.dimension: score for score in result.dimension_scores}

    assert score_map["trust_surface"].score == 1.0
    assert "trust_surface" not in result.failure_clusters
    assert score_map["readiness"].score < 1.0


def test_self_hosting_transform_case_requires_three_derivatives() -> None:
    cases = {case.case_id: case for case in load_benchmark_cases("self_hosting")}

    result = run_benchmark_case(cases["sr8_release_transform"])

    assert len(result.transform_checks) == 3
    assert all(check.success for check in result.transform_checks)
    assert {check.target for check in result.transform_checks} == {
        "markdown_prd",
        "markdown_plan",
        "markdown_prompt_pack",
    }
