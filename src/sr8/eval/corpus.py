from __future__ import annotations

import json
from pathlib import Path

from sr8.eval.types import BenchmarkCase, BenchmarkExpectation, BenchmarkSuite
from sr8.utils.paths import resolve_trusted_local_path

DEFAULT_CORPUS_ROOT = Path("benchmarks/corpus")
DEFAULT_EXPECTED_ROOT = Path("benchmarks/expected")
VIRTUAL_SUITES = ("adversarial", "experimental", "llm_required", "rules_required")
RULES_REQUIRED_SUITES = ("founder", "procedure", "self_hosting")


def list_available_suites(corpus_root: str | Path = DEFAULT_CORPUS_ROOT) -> tuple[str, ...]:
    try:
        root = resolve_trusted_local_path(corpus_root, must_exist=True)
    except (FileNotFoundError, ValueError):
        return ()
    discovered = tuple(sorted(path.name for path in root.iterdir() if path.is_dir()))
    return tuple(sorted((*discovered, *VIRTUAL_SUITES)))


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
    root = resolve_trusted_local_path(corpus_root, must_exist=True)
    expected = resolve_trusted_local_path(expected_root)
    if suite == "rules_required":
        suites = list(RULES_REQUIRED_SUITES)
    elif suite == "llm_required":
        suites = []
    elif suite in {"adversarial", "experimental"}:
        suites = []
    elif suite is None or suite == "all":
        suites = list(RULES_REQUIRED_SUITES)
    else:
        suites = [suite]
    cases: list[BenchmarkCase] = []
    for suite_name in suites:
        suite_root = root / str(suite_name)
        for case_path in sorted(suite_root.glob("*.case.json")):
            payload = json.loads(case_path.read_text(encoding="utf-8"))
            case = BenchmarkCase.model_validate(payload)
            expectations = _load_expectations(expected, case.case_id)
            cases.append(case.model_copy(update={"expectations": expectations}))
    return cases
