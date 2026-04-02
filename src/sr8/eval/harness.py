from __future__ import annotations

import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import cast

from sr8.compiler import CompileConfig, compile_intent
from sr8.eval.corpus import load_benchmark_cases
from sr8.eval.reports import build_run_summary
from sr8.eval.rubrics import get_default_rubric
from sr8.eval.scoring import build_case_result
from sr8.eval.types import (
    BenchmarkCase,
    BenchmarkCaseResult,
    BenchmarkRunReport,
    TransformCheck,
)
from sr8.extract.trace import coerce_extraction_trace
from sr8.io.writers import write_artifact
from sr8.lint.engine import lint_artifact
from sr8.models.intent_artifact import IntentArtifact
from sr8.transform.engine import transform_artifact, write_derivative
from sr8.utils.hash import stable_text_hash
from sr8.version import __version__


def _resolve_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_source_path(case: BenchmarkCase) -> Path:
    return _resolve_repo_root() / case.source_path


def _run_transforms(
    case: BenchmarkCase,
    artifact_output_root: Path | None,
    artifact: IntentArtifact,
) -> list[TransformCheck]:
    checks: list[TransformCheck] = []
    for target in case.transform_targets:
        try:
            result = transform_artifact(artifact, target=target)
            detail = "Transform completed."
            if artifact_output_root is not None:
                target_root = artifact_output_root / "derivatives" / case.case_id / target
                derivative_path, _ = write_derivative(result.derivative, target_root)
                detail = f"Transform completed and written to {derivative_path}."
            checks.append(
                TransformCheck(
                    target=target,
                    success=True,
                    detail=detail,
                    derivative_id=result.derivative.derivative_id,
                )
            )
        except ValueError as exc:
            checks.append(
                TransformCheck(
                    target=target,
                    success=False,
                    detail=str(exc),
                )
            )
    return checks


def run_benchmark_case(
    case: BenchmarkCase,
    out_dir: str | Path | None = None,
) -> BenchmarkCaseResult:
    source_path = _resolve_source_path(case)
    result = compile_intent(
        source=str(source_path),
        source_type=case.source_type,
        config=CompileConfig(profile=case.profile),
    )
    artifact = result.artifact
    lint_report = lint_artifact(artifact, artifact_ref=str(source_path))
    trace = coerce_extraction_trace(
        cast(Mapping[str, object] | None, artifact.metadata.get("extraction_trace"))
    )
    output_path: str | None = None
    artifact_output_root: Path | None = None
    if out_dir is not None:
        artifact_output_root = Path(out_dir)
        derivative_dir = artifact_output_root / "derivatives" / case.case_id
        artifact_dir = artifact_output_root / "artifacts" / case.case_id
        if artifact_dir.exists():
            shutil.rmtree(artifact_dir)
        if derivative_dir.exists():
            shutil.rmtree(derivative_dir)
        artifact_path, _ = write_artifact(artifact, artifact_dir, export_format="json")
        output_path = str(artifact_path)
    transform_checks = _run_transforms(case, artifact_output_root, artifact)
    return build_case_result(
        case=case,
        artifact=artifact,
        validation=artifact.validation,
        lint=lint_report,
        trace=trace,
        transform_checks=transform_checks,
        output_path=output_path,
    )


def run_benchmark_suite(
    suite: str | None = None,
    out_dir: str | Path | None = None,
    corpus_root: str | Path = "benchmarks/corpus",
    expected_root: str | Path = "benchmarks/expected",
) -> BenchmarkRunReport:
    cases = load_benchmark_cases(suite=suite, corpus_root=corpus_root, expected_root=expected_root)
    results = [run_benchmark_case(case, out_dir=out_dir) for case in cases]
    effective_suite = suite or "all"
    summary = build_run_summary(effective_suite, results)
    run_id = f"bench_{stable_text_hash(f'{effective_suite}:{__version__}:{len(results)}')[:12]}"
    return BenchmarkRunReport(
        run_id=run_id,
        suite=effective_suite,
        compiler_version=__version__,
        rubric_id=get_default_rubric().rubric_id,
        results=results,
        summary=summary,
    )
