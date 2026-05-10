from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact
from sr8.srxml import render_srxml_rc2_artifact


def render_xml_srxml_rc2(artifact: IntentArtifact) -> str:
    return render_srxml_rc2_artifact(artifact)
