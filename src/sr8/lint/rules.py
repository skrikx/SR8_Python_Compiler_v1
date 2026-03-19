from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from sr8.models.intent_artifact import IntentArtifact
from sr8.models.lint_finding import LintFinding

Severity = Literal["info", "warn", "error"]
Predicate = Callable[[IntentArtifact], bool]


@dataclass(frozen=True)
class PredicateRule:
    rule_id: str
    severity: Severity
    artifact_field: str
    message: str
    suggested_fix: str
    predicate: Predicate

    def evaluate(self, artifact: IntentArtifact) -> bool:
        return self.predicate(artifact)


def _has_text(value: str) -> bool:
    return value.strip() != ""


def _has_items(values: list[str]) -> bool:
    return any(item.strip() for item in values)


def _scope_vague(scope: list[str]) -> bool:
    vague_tokens = ("thing", "stuff", "something", "various", "etc")
    normalized = " ".join(scope).lower()
    return any(token in normalized for token in vague_tokens)


def _scope_exclusion_conflict(artifact: IntentArtifact) -> bool:
    scope_set = {item.strip().lower() for item in artifact.scope if item.strip()}
    exclusions_set = {item.strip().lower() for item in artifact.exclusions if item.strip()}
    return bool(scope_set & exclusions_set)


def _profile_signal_weak(artifact: IntentArtifact) -> bool:
    if artifact.profile == "prd":
        return not _has_items(artifact.exclusions)
    if artifact.profile == "procedure":
        return not _has_text(artifact.authority_context)
    if artifact.profile == "research_brief":
        corpus = " ".join(artifact.success_criteria + artifact.output_contract).lower()
        return "evidence" not in corpus
    return False


def _derivative_target_weak(artifact: IntentArtifact) -> bool:
    target = str(artifact.metadata.get("requested_transform_target", "")).strip()
    if target == "":
        return False
    return artifact.validation.readiness_status != "pass"


def _missing_authority_for_procedure(artifact: IntentArtifact) -> bool:
    return artifact.target_class == "procedure" and not _has_text(artifact.authority_context)


def _excessive_ambiguity_without_fallback(artifact: IntentArtifact) -> bool:
    ambiguous_tokens = ("maybe", "unclear", "tbd", "unknown")
    objective = artifact.objective.lower()
    ambiguity_hits = sum(token in objective for token in ambiguous_tokens)
    has_fallback = any("fallback" in constraint.lower() for constraint in artifact.constraints)
    return ambiguity_hits >= 2 and not has_fallback


LINT_RULES: tuple[PredicateRule, ...] = (
    PredicateRule(
        rule_id="L001",
        severity="error",
        artifact_field="objective",
        message="Missing or weak objective",
        suggested_fix="Provide a clear objective statement with actionable intent.",
        predicate=lambda artifact: _has_text(artifact.objective),
    ),
    PredicateRule(
        rule_id="L002",
        severity="warn",
        artifact_field="scope",
        message="Scope is empty or vague",
        suggested_fix="Add concrete scope items with explicit actions.",
        predicate=lambda artifact: _has_items(artifact.scope) and not _scope_vague(artifact.scope),
    ),
    PredicateRule(
        rule_id="L003",
        severity="warn",
        artifact_field="constraints",
        message="Constraints missing for profile/target that implies constraints",
        suggested_fix="Add operational or policy constraints for execution safety.",
        predicate=lambda artifact: _has_items(artifact.constraints),
    ),
    PredicateRule(
        rule_id="L004",
        severity="warn",
        artifact_field="success_criteria",
        message="Success criteria are absent or weak",
        suggested_fix="Define measurable success criteria.",
        predicate=lambda artifact: _has_items(artifact.success_criteria),
    ),
    PredicateRule(
        rule_id="L005",
        severity="warn",
        artifact_field="output_contract",
        message="Output contract is absent or underspecified",
        suggested_fix="Define output artifacts and expected structure.",
        predicate=lambda artifact: _has_items(artifact.output_contract),
    ),
    PredicateRule(
        rule_id="L006",
        severity="error",
        artifact_field="scope",
        message="Scope and exclusions contradict each other",
        suggested_fix="Remove overlapping items between scope and exclusions.",
        predicate=lambda artifact: not _scope_exclusion_conflict(artifact),
    ),
    PredicateRule(
        rule_id="L007",
        severity="warn",
        artifact_field="profile",
        message="Profile selected but profile-specific signals are weak",
        suggested_fix="Add profile-specific signals to satisfy profile intent.",
        predicate=lambda artifact: not _profile_signal_weak(artifact),
    ),
    PredicateRule(
        rule_id="L008",
        severity="warn",
        artifact_field="metadata.requested_transform_target",
        message="Requested transform target is incompatible with current artifact quality",
        suggested_fix="Improve artifact quality or choose a lighter transform target.",
        predicate=lambda artifact: not _derivative_target_weak(artifact),
    ),
    PredicateRule(
        rule_id="L009",
        severity="error",
        artifact_field="authority_context",
        message="Authority context missing for procedure-class artifact",
        suggested_fix="Set authority context or owner for procedure artifacts.",
        predicate=lambda artifact: not _missing_authority_for_procedure(artifact),
    ),
    PredicateRule(
        rule_id="L010",
        severity="warn",
        artifact_field="objective",
        message="Ambiguity markers present without fallback structure",
        suggested_fix="Add fallback constraints and remove ambiguous placeholders.",
        predicate=lambda artifact: not _excessive_ambiguity_without_fallback(artifact),
    ),
)


def evaluate_rules(artifact: IntentArtifact) -> list[LintFinding]:
    findings: list[LintFinding] = []
    for rule in LINT_RULES:
        if rule.evaluate(artifact):
            continue
        findings.append(
            LintFinding(
                rule_id=rule.rule_id,
                severity=rule.severity,
                message=rule.message,
                artifact_field=rule.artifact_field,
                suggested_fix=rule.suggested_fix,
            )
        )
    return findings
