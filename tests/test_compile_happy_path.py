from pathlib import Path

from sr8.compiler import compile_intent


def test_compile_happy_path_markdown_fixture() -> None:
    fixture = Path("tests/fixtures/input_founder_ask.md")

    result = compile_intent(str(fixture))
    repeat = compile_intent(str(fixture))

    artifact = result.artifact
    required_fields = {
        "artifact_id",
        "artifact_version",
        "compiler_version",
        "created_at",
        "source",
        "objective",
        "scope",
        "exclusions",
        "constraints",
        "target_class",
        "authority_context",
        "dependencies",
        "assumptions",
        "success_criteria",
        "output_contract",
        "governance_flags",
        "validation",
        "lineage",
        "metadata",
    }

    assert required_fields.issubset(set(artifact.model_dump().keys()))
    assert artifact.objective.startswith("Build a local-first intent compiler core")
    assert artifact.source.source_hash == result.normalized_source.source_hash
    assert artifact.artifact_id == repeat.artifact.artifact_id
    assert result.receipt.status == "accepted"
    assert result.extracted_dimensions.scope
