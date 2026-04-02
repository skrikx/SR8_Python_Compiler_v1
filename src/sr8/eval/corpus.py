from __future__ import annotations

import json
from pathlib import Path

from sr8.eval.types import BenchmarkCase, BenchmarkExpectation, BenchmarkSuite

DEFAULT_CORPUS_ROOT = Path("benchmarks/corpus")
DEFAULT_EXPECTED_ROOT = Path("benchmarks/expected")


def list_available_suites(corpus_root: str | Path = DEFAULT_CORPUS_ROOT) -> tuple[str, ...]:
    root = Path(corpus_root)
    if not root.exists():
        return ()
    return tuple(sorted(path.name for path in root.iterdir() if path.is_dir()))


def _load_expectations(expected_root: Path, case_id: str) -> BenchmarkExpectation:
    expected_path = expected_root / f"{case_id}.json"
    if not expected_path.exists():
        return BenchmarkExpectation()
    payload = json.loads(expected_path.read_text(encoding="utf-8"))
    return BenchmarkExpectation.model_validate(payload)


def load_benchmark_cases(
    suite: BenchmarkSuite | str | None = None,
    corpus_root: str | Path = DEFAULT_CORPUS_ROOT,
    expected_root: str | Path = DEFAULT_EXPECTED_ROOT,
) -> list[BenchmarkCase]:
    root = Path(corpus_root)
    expected = Path(expected_root)
    suites = [suite] if suite not in {None, "all"} else list_available_suites(root)
    cases: list[BenchmarkCase] = []
    for suite_name in suites:
        suite_root = root / str(suite_name)
        for case_path in sorted(suite_root.glob("*.case.json")):
            payload = json.loads(case_path.read_text(encoding="utf-8"))
            case = BenchmarkCase.model_validate(payload)
            expectations = _load_expectations(expected, case.case_id)
            cases.append(case.model_copy(update={"expectations": expectations}))
    return cases
