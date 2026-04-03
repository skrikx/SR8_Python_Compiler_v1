from __future__ import annotations

import re
from xml.etree import ElementTree
from xml.sax.saxutils import escape

from sr8.frontdoor.package_models import GovernanceDecision
from sr8.models.intent_artifact import IntentArtifact
from sr8.models.receipts import CompilationReceipt

CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def sanitize_xml_text(text: str) -> str:
    return CONTROL_CHAR_RE.sub("", text)


def escape_xml_text(text: str) -> str:
    cleaned = sanitize_xml_text(text)
    return escape(cleaned, {"\"": "&quot;", "'": "&apos;"})


def _append_list(parent: ElementTree.Element, tag: str, items: list[str]) -> None:
    if not items:
        return
    container = ElementTree.SubElement(parent, tag)
    for item in items:
        entry = ElementTree.SubElement(container, "item")
        entry.text = sanitize_xml_text(item)


def _to_xml(root: ElementTree.Element) -> str:
    payload = ElementTree.tostring(root, encoding="unicode")
    return f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n{payload}"


def render_promptunit_package_xml(
    artifact: IntentArtifact,
    governance: GovernanceDecision,
    receipt: CompilationReceipt | None = None,
) -> str:
    root = ElementTree.Element("promptunit_package")
    meta = ElementTree.SubElement(root, "package_meta")
    ElementTree.SubElement(meta, "artifact_id").text = sanitize_xml_text(artifact.artifact_id)
    ElementTree.SubElement(meta, "profile").text = sanitize_xml_text(artifact.profile)
    ElementTree.SubElement(meta, "target_class").text = sanitize_xml_text(artifact.target_class)
    if receipt is not None:
        ElementTree.SubElement(meta, "receipt_id").text = sanitize_xml_text(receipt.receipt_id)
    governance_node = ElementTree.SubElement(meta, "governance")
    governance_node.set("status", governance.status)
    ElementTree.SubElement(governance_node, "reason").text = sanitize_xml_text(governance.reason)
    if governance.notes:
        _append_list(governance_node, "notes", governance.notes)

    ElementTree.SubElement(root, "objective").text = sanitize_xml_text(artifact.objective)
    _append_list(root, "scope", artifact.scope)
    _append_list(root, "constraints", artifact.constraints)
    _append_list(root, "dependencies", artifact.dependencies)
    _append_list(root, "success_criteria", artifact.success_criteria)
    _append_list(root, "output_contract", artifact.output_contract)

    return _to_xml(root)


def render_sr8_prompt_xml(artifact: IntentArtifact) -> str:
    root = ElementTree.Element("sr8_prompt")
    ElementTree.SubElement(root, "artifact_id").text = sanitize_xml_text(artifact.artifact_id)
    ElementTree.SubElement(root, "objective").text = sanitize_xml_text(artifact.objective)

    prompt_lines = [
        f"Objective: {artifact.objective}",
    ]
    if artifact.scope:
        prompt_lines.append("Scope:")
        prompt_lines.extend(f"- {item}" for item in artifact.scope)
    if artifact.constraints:
        prompt_lines.append("Constraints:")
        prompt_lines.extend(f"- {item}" for item in artifact.constraints)
    if artifact.success_criteria:
        prompt_lines.append("Success Criteria:")
        prompt_lines.extend(f"- {item}" for item in artifact.success_criteria)
    prompt_text = "\n".join(prompt_lines).strip()

    ElementTree.SubElement(root, "prompt").text = sanitize_xml_text(prompt_text)
    return _to_xml(root)


def render_safe_alternative_package_xml(
    artifact: IntentArtifact,
    governance: GovernanceDecision,
    suggested_alternative: str,
) -> str:
    root = ElementTree.Element("safe_alternative_package")
    meta = ElementTree.SubElement(root, "package_meta")
    ElementTree.SubElement(meta, "artifact_id").text = sanitize_xml_text(artifact.artifact_id)
    ElementTree.SubElement(meta, "profile").text = sanitize_xml_text(artifact.profile)
    governance_node = ElementTree.SubElement(meta, "governance")
    governance_node.set("status", governance.status)
    ElementTree.SubElement(governance_node, "reason").text = sanitize_xml_text(governance.reason)
    ElementTree.SubElement(root, "suggested_alternative").text = sanitize_xml_text(
        suggested_alternative
    )
    return _to_xml(root)
