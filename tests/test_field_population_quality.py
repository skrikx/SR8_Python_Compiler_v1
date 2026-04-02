from sr8.compiler import CompileConfig, compile_intent
from sr8.lint.engine import lint_artifact
from sr8.validate.engine import validate_artifact


def test_weak_input_remains_visibly_weak() -> None:
    artifact = compile_intent("unclear", config=CompileConfig(profile="generic")).artifact
    trace = artifact.metadata["extraction_trace"]
    statuses = {item["field_name"]: item["status"] for item in trace["confidence"]}
    assert statuses["scope"] in {"empty", "weak"}
    assert statuses["context_package"] in {"empty", "weak"}

    validation = validate_artifact(artifact)
    lint = lint_artifact(artifact, artifact_ref="inline")

    assert any(issue.code == "VAL-TRUST-900" for issue in validation.warnings)
    assert any(finding.rule_id == "L-TRUST-GOVERNANCE" for finding in lint.findings)


def test_field_population_quality_covers_context_and_contract_fields() -> None:
    artifact = compile_intent(
        (
            "Objective: Ship compiler hardening\n"
            "Context Package:\n- prior receipt\n- architecture notes\n"
            "Dependencies:\n- Python 3.11\n"
            "Assumptions:\n- local workspace exists\n"
            "Success Criteria:\n- tests pass\n"
            "Output Contract:\n- updated receipt\n"
            "Authority Context: maintainer\n"
        ),
        config=CompileConfig(profile="generic"),
    ).artifact
    trace = artifact.metadata["extraction_trace"]
    statuses = {item["field_name"]: item["status"] for item in trace["confidence"]}

    assert artifact.context_package == ["prior receipt", "architecture notes"]
    assert statuses["context_package"] == "explicit"
    assert statuses["dependencies"] == "explicit"
    assert statuses["assumptions"] == "explicit"
    assert statuses["success_criteria"] == "explicit"
    assert statuses["output_contract"] == "explicit"
