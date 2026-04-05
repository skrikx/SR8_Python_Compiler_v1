from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree

from sr8.frontdoor.xml_renderer import escape_xml_text

WORD_RE = re.compile(r"\w+")


def is_under_specified(text: str) -> bool:
    candidate = text.strip()
    if not candidate:
        return True
    word_count = len(WORD_RE.findall(candidate))
    if word_count < 6:
        return True
    lowered = candidate.lower()
    if "objective" not in lowered and "goal" not in lowered and "scope" not in lowered:
        return True
    return False


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_intake_template() -> str:
    template_path = _project_root() / "intake" / "COMPILER_INPUT_FORM.xml"
    return template_path.read_text(encoding="utf-8")


def render_intake_xml(original_intent: str) -> str:
    template = load_intake_template().rstrip()
    if not original_intent.strip():
        return template
    escaped = escape_xml_text(original_intent.strip())
    return f"{template}\n<!-- original_intent: {escaped} -->\n"


def extract_refined_intent(xml_text: str) -> str:
    candidate = xml_text.strip()
    if not candidate:
        return ""
    try:
        root = ElementTree.fromstring(candidate)
    except ElementTree.ParseError:
        return ""

    namespace = ""
    if root.tag.startswith("{") and "}" in root.tag:
        namespace = root.tag.split("}")[0].strip("{")

    def _find_text(tag: str) -> str:
        if namespace:
            element = root.find(f".//{{{namespace}}}{tag}")
        else:
            element = root.find(f".//{tag}")
        if element is not None and element.text:
            return element.text.strip()
        return ""

    goal = _find_text("goal")
    deliverables = []
    deliverable_items = (
        root.findall(f".//{{{namespace}}}deliverables/{{{namespace}}}item")
        if namespace
        else root.findall(".//deliverables/item")
    )
    for item in deliverable_items:
        if item.text and item.text.strip():
            deliverables.append(item.text.strip())

    constraints = []
    constraint_items = (
        root.findall(f".//{{{namespace}}}constraints/{{{namespace}}}item")
        if namespace
        else root.findall(".//constraints/item")
    )
    for item in constraint_items:
        if item.text and item.text.strip():
            constraints.append(item.text.strip())

    if not goal and not deliverables and not constraints:
        return ""

    lines: list[str] = []
    if goal:
        lines.append(f"Objective: {goal}")
    if deliverables:
        lines.append("Scope:")
        lines.extend(f"- {item}" for item in deliverables)
    if constraints:
        lines.append("Constraints:")
        lines.extend(f"- {item}" for item in constraints)
    return _collapse_spaces("\n".join(lines)).strip()


def _collapse_spaces(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text).replace(" \n", "\n").replace("\n ", "\n")
