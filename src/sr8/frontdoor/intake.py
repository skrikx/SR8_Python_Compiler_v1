from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree

from sr8.extract.adapters.rule_based import RuleBasedExtractionAdapter
from sr8.frontdoor.xml_renderer import escape_xml_text

WORD_RE = re.compile(r"\w+")


def analyze_intent_surface(text: str) -> dict[str, object]:
    candidate = text.strip()
    if not candidate:
        return {
            "word_count": 0,
            "intake_required": True,
            "recovery": {
                "intake_required": True,
                "missing_fields": ["objective", "scope", "constraints"],
                "weak_fields": [],
                "contradictory_fields": [],
                "suggested_prompt": (
                    "Provide a stronger intent package with explicit objective, "
                    "scope, constraints, success criteria, and output contract."
                ),
            },
        }
    adapter = RuleBasedExtractionAdapter()
    _, trace = adapter.extract(candidate)
    return {
        "word_count": len(WORD_RE.findall(candidate)),
        "intake_required": trace.recovery.intake_required,
        "recovery": trace.recovery.model_dump(mode="json"),
    }


def is_under_specified(text: str) -> bool:
    candidate = text.strip()
    if not candidate:
        return True
    analysis = analyze_intent_surface(candidate)
    raw_word_count = analysis.get("word_count", 0)
    word_count = raw_word_count if isinstance(raw_word_count, int) else 0
    if word_count < 6:
        return True
    return bool(analysis["intake_required"])


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
