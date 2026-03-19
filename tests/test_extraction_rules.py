from pathlib import Path

from sr8.compiler import extract_dimensions, load_source, normalize_source


def test_extraction_rule_outputs_expected_dimensions() -> None:
    fixture = Path("tests/fixtures/input_product_concept.txt")

    loaded = load_source(str(fixture), source_type="text")
    normalized = normalize_source(loaded)
    dimensions = extract_dimensions(normalized)

    assert dimensions.objective == "Compile product intent into inspectable artifacts."
    assert "Capture objective, scope, constraints, and success criteria." in dimensions.scope
    assert "Avoid fabricated certainty." in dimensions.constraints
    assert dimensions.success_criteria
