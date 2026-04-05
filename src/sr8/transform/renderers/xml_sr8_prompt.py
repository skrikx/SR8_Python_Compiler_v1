from __future__ import annotations

from sr8.frontdoor.xml_renderer import render_sr8_prompt_xml
from sr8.models.intent_artifact import IntentArtifact


def render_xml_sr8_prompt(artifact: IntentArtifact) -> str:
    return render_sr8_prompt_xml(artifact)
