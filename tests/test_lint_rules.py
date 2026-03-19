from sr8.io.exporters import load_artifact
from sr8.lint.rules import evaluate_rules


def test_lint_rules_flag_weak_artifact() -> None:
    artifact = load_artifact("tests/fixtures/lint/weak_artifact.json")
    findings = evaluate_rules(artifact)
    rule_ids = {finding.rule_id for finding in findings}
    assert "L001" in rule_ids
    assert "L002" in rule_ids
    assert "L005" in rule_ids


def test_lint_rules_flag_contradiction() -> None:
    artifact = load_artifact("tests/fixtures/lint/contradictory_artifact.json")
    findings = evaluate_rules(artifact)
    rule_ids = {finding.rule_id for finding in findings}
    assert "L006" in rule_ids
