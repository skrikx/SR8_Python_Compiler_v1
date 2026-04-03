from __future__ import annotations

from sr8.frontdoor.governance import evaluate_governance, suggest_safe_alternative
from sr8.frontdoor.xml_renderer import render_safe_alternative_package_xml
from sr8.models.intent_artifact import IntentArtifact


def render_xml_safe_alternative_package(artifact: IntentArtifact) -> str:
    governance = evaluate_governance(artifact)
    suggested = suggest_safe_alternative(artifact)
    return render_safe_alternative_package_xml(artifact, governance, suggested)
