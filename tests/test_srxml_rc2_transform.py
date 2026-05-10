from xml.etree import ElementTree

from fastapi.testclient import TestClient
from typer.testing import CliRunner

import sr8.compiler.compile as compile_module
from sr8.api.app import app as api_app
from sr8.cli import app
from sr8.compiler import compile_intent
from sr8.io.exporters import load_artifact
from sr8.models.compile_config import CompileConfig
from sr8.models.intent_artifact import GovernanceFlags
from sr8.models.validation import ValidationIssue, ValidationReport
from sr8.profiles.registry import PROFILE_REGISTRY
from sr8.srxml import classify_srxml_route, render_srxml_rc2_artifact, validate_srxml_text
from sr8.storage.receipts import write_compilation_receipt
from sr8.storage.save import save_canonical_artifact
from sr8.storage.workspace import init_workspace
from sr8.transform.engine import transform_artifact

runner = CliRunner()


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


def test_compile_target_validation_accepts_valid_srxml_rc2() -> None:
    result = compile_intent(
        "Objective: Build an operator handoff\n"
        "Scope:\n"
        "- Write the handoff\n"
        "Success: Reviewer can execute it",
        config=CompileConfig(target="xml_srxml_rc2", validate_target=True),
    )

    assert result.target_validation is not None
    assert result.target_validation.target == "xml_srxml_rc2"
    assert result.target_validation.status == "accepted"
    assert result.target_validation.valid is True
    assert result.receipt.status == "accepted"
    assert result.artifact.metadata["compile_target"] == "xml_srxml_rc2"


def test_compile_target_requires_validate_flag() -> None:
    try:
        compile_intent(
            "Objective: Build an operator handoff\nScope:\n- Write it",
            config=CompileConfig(target="xml_srxml_rc2"),
        )
    except ValueError as exc:
        assert "--validate is required" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("compile target without validation should fail")


def test_compile_target_validation_rejects_invalid_srxml_rc2(monkeypatch) -> None:
    monkeypatch.setattr(
        compile_module,
        "render_srxml_rc2_artifact",
        lambda artifact: "<SRXML_Artifact><metadata /></SRXML_Artifact>",
    )

    result = compile_intent(
        "Objective: Build an operator handoff\nScope:\n- Write it",
        config=CompileConfig(target="xml_srxml_rc2", validate_target=True),
    )

    assert result.target_validation is not None
    assert result.target_validation.status == "rejected"
    assert result.target_validation.valid is False
    assert result.receipt.status == "rejected"
    assert result.target_validation.repair_actions


def test_compile_target_validation_blocks_incomplete_intent() -> None:
    result = compile_intent(
        "unclear",
        config=CompileConfig(target="xml_srxml_rc2", validate_target=True),
    )

    assert result.target_validation is not None
    assert result.target_validation.status == "blocked"
    assert result.receipt.status == "rejected"
    assert "requires human review" in " ".join(result.target_validation.repair_actions)
    assert "<repair_prompt>" in result.target_validation.content


def test_cli_compile_target_validation_writes_srxml_output(tmp_path) -> None:
    out_dir = tmp_path / "out"

    result = runner.invoke(
        app,
        [
            "compile",
            "Objective: Build an operator handoff\nScope:\n- Write it",
            "--target",
            "xml_srxml_rc2",
            "--validate",
            "--out",
            str(out_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Target Validation: xml_srxml_rc2 accepted" in result.stdout
    assert (out_dir / "latest_xml_srxml_rc2.xml").exists()


def test_cli_compile_target_validation_exits_nonzero_for_blocked_intent() -> None:
    result = runner.invoke(
        app,
        [
            "compile",
            "unclear",
            "--target",
            "xml_srxml_rc2",
            "--validate",
        ],
    )

    assert result.exit_code == 1
    assert "Target Validation: xml_srxml_rc2 blocked" in result.stdout
    assert "Repair:" in result.stdout


def test_api_compile_returns_srxml_target_validation(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SR8_WORKSPACE_PATH", str(tmp_path / ".sr8"))
    client = TestClient(api_app)

    response = client.post(
        "/compile",
        json={
            "source": "Objective: Build an operator handoff\nScope:\n- Write it",
            "profile": "generic",
            "target": "xml_srxml_rc2",
            "validate": True,
            "rule_only": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["target_validation"]["target"] == "xml_srxml_rc2"
    assert payload["target_validation"]["status"] == "accepted"
    assert payload["receipt"]["status"] == "accepted"


def test_compile_receipt_persists_srxml_target_validation(tmp_path) -> None:
    workspace = init_workspace(tmp_path / ".sr8")
    result = compile_intent(
        "Objective: Build an operator handoff\nScope:\n- Write it",
        config=CompileConfig(target="xml_srxml_rc2", validate_target=True),
    )
    artifact_path, _, _ = save_canonical_artifact(workspace, result.artifact)

    receipt, receipt_path = write_compilation_receipt(
        workspace,
        result=result,
        output_path=str(artifact_path),
    )

    assert receipt_path.exists()
    assert receipt.compile_target == "xml_srxml_rc2"
    assert receipt.compile_target_validation is not None
    assert receipt.compile_target_validation["status"] == "accepted"
