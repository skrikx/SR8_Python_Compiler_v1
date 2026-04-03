from __future__ import annotations

from sr8.frontdoor.governance import evaluate_governance
from sr8.frontdoor.xml_renderer import render_promptunit_package_xml
from sr8.models.intent_artifact import IntentArtifact


def render_xml_promptunit_package(artifact: IntentArtifact) -> str:
    governance = evaluate_governance(artifact)
    return render_promptunit_package_xml(artifact, governance, receipt=None)
