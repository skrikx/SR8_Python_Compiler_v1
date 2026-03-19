from pathlib import Path

import pytest

from sr8.compiler import compile_intent, load_source


@pytest.mark.parametrize(
    ("input_source", "source_type"),
    [
        ("tests/fixtures/input_founder_ask.md", "markdown"),
        ("tests/fixtures/input_json_payload.json", "json"),
        ("tests/fixtures/input_yaml_payload.yaml", "yaml"),
        ("Objective: Build from raw text.\nScope:\n- Parse intent\n", "text"),
    ],
)
def test_compile_accepts_ingest_variants(input_source: str, source_type: str) -> None:
    result = compile_intent(input_source, source_type=source_type)

    assert result.artifact.source.source_type == source_type
    assert result.artifact.source.source_hash
    assert result.artifact.lineage.steps


def test_load_source_path_detection() -> None:
    source_intent = load_source(Path("tests/fixtures/input_founder_ask.md"))
    assert source_intent.source_type == "markdown"
    assert source_intent.origin is not None
