from time import perf_counter

from sr8.compiler import CompileConfig, compile_intent
from sr8.validate.engine import validate_artifact


def test_performance_gate_smoke() -> None:
    start_small = perf_counter()
    small = compile_intent(
        "Objective: small\nScope:\n- a\n",
        config=CompileConfig(profile="generic"),
    ).artifact
    elapsed_small = perf_counter() - start_small

    medium_source = "\n".join(["Scope:"] + [f"- item {i}" for i in range(40)])
    start_medium = perf_counter()
    medium = compile_intent(
        f"Objective: medium\n{medium_source}",
        config=CompileConfig(profile="plan"),
    ).artifact
    elapsed_medium = perf_counter() - start_medium

    start_validate = perf_counter()
    report = validate_artifact(medium)
    elapsed_validate = perf_counter() - start_validate

    assert small.artifact_id.startswith("art_")
    assert report.readiness_status in {"pass", "warn", "fail"}
    assert elapsed_small < 2.0
    assert elapsed_medium < 2.0
    assert elapsed_validate < 1.0
