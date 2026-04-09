import json
from pathlib import Path

import pytest
import yaml

from sr8.compiler import InvalidSourceInputError, InvalidStructuredInputError, load_source


def test_inline_json_is_detected_and_hashes_like_mapping_payload() -> None:
    inline_json = Path("tests/fixtures/input_json_payload.json").read_text(encoding="utf-8")
    mapping_payload = json.loads(inline_json)

    inline = load_source(inline_json)
    mapped = load_source(mapping_payload)

    assert inline.source_type == "json"
    assert inline.source_hash == mapped.source_hash


def test_yaml_hash_is_stable_across_path_and_mapping() -> None:
    yaml_path = Path("tests/fixtures/input_yaml_payload.yaml")
    payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))

    from_path = load_source(yaml_path, source_type="yaml")
    from_mapping = load_source(payload)

    assert from_path.source_hash == from_mapping.source_hash


def test_blank_source_is_rejected_with_structured_error() -> None:
    with pytest.raises(InvalidSourceInputError) as exc_info:
        load_source("   \n  ")

    assert exc_info.value.code == "invalid_source_input"


def test_invalid_json_source_is_rejected_with_structured_error() -> None:
    with pytest.raises(InvalidStructuredInputError) as exc_info:
        load_source('{"objective": ', source_type="json")

    assert exc_info.value.code == "invalid_structured_input"
    assert exc_info.value.details["source_type"] == "json"
