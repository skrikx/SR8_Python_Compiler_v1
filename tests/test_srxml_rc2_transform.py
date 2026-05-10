from xml.etree import ElementTree

from sr8.compiler import compile_intent
from sr8.io.exporters import load_artifact
from sr8.models.intent_artifact import GovernanceFlags
from sr8.models.validation import ValidationIssue, ValidationReport
from sr8.profiles.registry import PROFILE_REGISTRY
from sr8.srxml import classify_srxml_route, render_srxml_rc2_artifact, validate_srxml_text
from sr8.transform.engine import transform_artifact


def _text(root: ElementTree.Element, path: str) -> str:
    current = root
    for part in path.split("."):
        found = None
        for child in list(current):
            tag = child.tag.split("}", 1)[-1] if "}" in child.tag else child.tag
            if tag == part:
                found = child
                break
        assert found is not None
        current = found
    return "".join(current.itertext()).strip()


def test_srxml_rc2_transform_renders_validator_backed_xml() -> None:
    artifact = load_artifact("tests/fixtures/compiled_prd_artifact.json")

    result = transform_artifact(artifact, target="xml_srxml_rc2")
    xml_text = result.derivative.content
    validation = validate_srxml_text(xml_text)
    root = ElementTree.fromstring(xml_text)

    assert validation.valid, validation.as_dict()
    assert result.derivative.transform_target == "xml_srxml_rc2"
    assert result.derivative.metadata["output_format"] == "xml"
    assert _text(root, "metadata.artifact_type") == "blueprint_design_doc"
    assert _text(root, "metadata.depth_tier") == "D2_PRODUCTION"
    assert artifact.source.source_hash in xml_text
    assert artifact.lineage.compile_run_id in xml_text
    assert "<receipt_type>srxml_validation_receipt</receipt_type>" in xml_text


def test_srxml_rc2_blocked_state_preserves_repair_context() -> None:
    artifact = load_artifact("tests/fixtures/compiled_prd_artifact.json")
    blocked = artifact.model_copy(
        update={
            "objective": "",
            "governance_flags": GovernanceFlags(
                ambiguous=True,
                incomplete=True,
                requires_human_review=True,
            ),
            "validation": ValidationReport(
                report_id="val_blocked_srxml_fixture",
                readiness_status="fail",
                summary="Validation fail: objective is missing.",
                errors=[
                    ValidationIssue(
                        code="VAL-TEST-MISSING-OBJECTIVE",
                        message="objective is required",
                        path="objective",
                    )
                ],
            ),
        }
    )

    route = classify_srxml_route(blocked)
    xml_text = render_srxml_rc2_artifact(blocked)
    validation = validate_srxml_text(xml_text)

    assert route.blocked is True
    assert validation.valid, validation.as_dict()
    assert "<repair_prompt>" in xml_text
    assert "SR8 canonical validation status is fail." in xml_text
    assert "<status>blocked</status>" in xml_text


def test_srxml_rc2_validator_rejects_missing_artifact_type() -> None:
    xml_text = """<?xml version="1.0" encoding="UTF-8"?>
<SRXML_Artifact schema_version="1.0.0-rc2">
  <metadata><artifact_id>bad.fixture</artifact_id><title>Bad</title><version>1.0.0</version><status>draft</status><depth_tier>D1_OPERATIONAL</depth_tier><runtime_targets><runtime_target>SR8</runtime_target></runtime_targets></metadata>
  <mission><primary_objective>Bad</primary_objective><success_definition>Fails.</success_definition></mission>
  <scope><in_scope><item>Bad</item></in_scope><out_of_scope><item>None</item></out_of_scope><scope_lock>one_pass_lock</scope_lock></scope>
  <output_contract><format>xml</format><completion_definition>Fail.</completion_definition></output_contract>
</SRXML_Artifact>"""

    validation = validate_srxml_text(xml_text)

    assert validation.valid is False
    assert any(error.rule_id == "L-MISSING_ARTIFACT_TYPE" for error in validation.errors)


def test_all_profiles_allow_srxml_rc2_transform_target() -> None:
    unsupported = [
        profile_name
        for profile_name, profile in PROFILE_REGISTRY.items()
        if not profile.supports_target("xml_srxml_rc2")
    ]

    assert unsupported == []


def test_compile_then_transform_to_srxml_rc2() -> None:
    result = compile_intent(
        "Objective: Build an operator handoff\n"
        "Scope:\n"
        "- Write the handoff\n"
        "Success: Reviewer can execute it",
    )

    derivative = transform_artifact(result.artifact, target="xml_srxml_rc2").derivative
    validation = validate_srxml_text(derivative.content)

    assert validation.valid, validation.as_dict()
    assert "<source_hash>" in derivative.content
