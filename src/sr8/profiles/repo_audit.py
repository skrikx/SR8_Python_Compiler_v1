from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact
from sr8.profiles.base import ProfileDefinition, ProfileRule


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def _has_repo_boundary(artifact: IntentArtifact) -> bool:
    corpus = " ".join([artifact.objective, *artifact.scope, *artifact.dependencies])
    return _contains_any(corpus, ("repo", "repository", "codebase", "system", "service"))


def _has_audit_criteria(artifact: IntentArtifact) -> bool:
    corpus = " ".join([*artifact.scope, *artifact.constraints, *artifact.success_criteria])
    return _contains_any(
        corpus,
        ("audit", "security", "quality", "lint", "typecheck", "test", "performance"),
    )


def _has_expected_outputs(artifact: IntentArtifact) -> bool:
    return any(item.strip() for item in artifact.output_contract)


def _has_validation_gates(artifact: IntentArtifact) -> bool:
    corpus = " ".join(
        [
            *artifact.constraints,
            *artifact.success_criteria,
            *artifact.output_contract,
        ]
    )
    return _contains_any(corpus, ("validate", "check", "gate", "receipt", "report", "pass"))


REPO_AUDIT_PROFILE = ProfileDefinition(
    name="repo_audit",
    target_class="repo_audit",
    required_rules=(
        ProfileRule(
            code="VAL-PRO-REP-001",
            message="repo_audit profile requires repo boundary signal",
            path="scope",
            severity="error",
            check=_has_repo_boundary,
        ),
        ProfileRule(
            code="VAL-PRO-REP-002",
            message="repo_audit profile requires audit criteria",
            path="constraints",
            severity="error",
            check=_has_audit_criteria,
        ),
        ProfileRule(
            code="VAL-PRO-REP-003",
            message="repo_audit profile requires expected outputs",
            path="output_contract",
            severity="error",
            check=_has_expected_outputs,
        ),
        ProfileRule(
            code="VAL-PRO-REP-004",
            message="repo_audit profile requires validation/checking expectations",
            path="success_criteria",
            severity="error",
            check=_has_validation_gates,
        ),
    ),
)
