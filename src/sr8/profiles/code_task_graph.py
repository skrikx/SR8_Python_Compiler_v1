from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact
from sr8.profiles.base import ProfileDefinition, ProfileRule


def _has_dependencies(artifact: IntentArtifact) -> bool:
    return any(item.strip() for item in artifact.dependencies)


def _has_scope(artifact: IntentArtifact) -> bool:
    return any(item.strip() for item in artifact.scope)


CODE_TASK_GRAPH_PROFILE = ProfileDefinition(
    name="code_task_graph",
    target_class="code_task_graph",
    required_rules=(
        ProfileRule(
            code="VAL-PRO-CTG-001",
            message="code_task_graph requires scope tasks",
            path="scope",
            severity="error",
            check=_has_scope,
        ),
    ),
    warning_rules=(
        ProfileRule(
            code="VAL-PRO-CTG-002",
            message="code_task_graph should include dependencies",
            path="dependencies",
            severity="warning",
            check=_has_dependencies,
        ),
    ),
    supported_transform_targets=(
        "markdown_plan",
        "markdown_prompt_pack",
        "xml_promptunit_package",
        "xml_sr8_prompt",
        "xml_safe_alternative_package",
    ),
)
