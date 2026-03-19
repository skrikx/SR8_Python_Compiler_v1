from __future__ import annotations

from time import perf_counter

from sr8.compiler import CompileConfig, compile_intent
from sr8.diff.engine import semantic_diff
from sr8.lint.engine import lint_artifact


def test_performance_smoke_compile_validate_lint_diff() -> None:
    start_compile = perf_counter()
    left = compile_intent(
        source="tests/fixtures/product_prd.md",
        config=CompileConfig(profile="prd"),
    ).artifact
    right = compile_intent(
        source="tests/fixtures/founder_generic.md",
        config=CompileConfig(profile="generic"),
    ).artifact
    compile_elapsed = perf_counter() - start_compile

    start_lint = perf_counter()
    lint_report = lint_artifact(left, artifact_ref="left")
    lint_elapsed = perf_counter() - start_lint

    start_diff = perf_counter()
    diff_report = semantic_diff(left, right, left_ref="left", right_ref="right")
    diff_elapsed = perf_counter() - start_diff

    assert lint_report.status in {"pass", "warn", "fail"}
    assert diff_report.report_id.startswith("diff_")
    assert compile_elapsed < 3.0
    assert lint_elapsed < 1.0
    assert diff_elapsed < 1.0
