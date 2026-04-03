from __future__ import annotations

import re

SECTION_LABELS: dict[str, tuple[str, ...]] = {
    "objective": ("objective", "goal", "mission", "intent"),
    "scope": ("scope", "in scope", "scope of work"),
    "exclusions": ("exclusions", "out of scope", "non-goals", "non goals"),
    "constraints": ("constraints", "requirements", "limits"),
    "context_package": (
        "context package",
        "context",
        "background context",
        "reference material",
        "reference materials",
        "inputs",
    ),
    "assumptions": ("assumptions",),
    "dependencies": ("dependencies", "depends on"),
    "success_criteria": ("success criteria", "acceptance criteria", "definition of done"),
    "output_contract": ("output contract", "output expectations", "deliverables"),
    "target_class": ("target class", "target", "class"),
    "authority_context": ("authority context", "authority", "owner", "requester"),
}

TARGET_HINTS: dict[str, tuple[str, ...]] = {
    "compiler_core": ("compiler", "intent artifact", "ir", "intermediate representation"),
    "product_spec": ("product", "feature", "roadmap", "customer"),
    "repo_audit": ("repository", "codebase", "lint", "typecheck", "tests"),
    "whitepaper_outline": ("whitepaper", "outline", "thesis", "architecture paper"),
    "code_task_graph": ("task graph", "dependency graph", "implementation graph", "scheduler"),
    "landing_page": ("landing page", "landing-page", "landingpage"),
    "mvp_builder": ("mvp", "minimum viable product", "mvp builder"),
    "deep_research": ("deep research", "literature review", "research synthesis"),
    "governed_request": ("governance", "policy", "compliance"),
    "multimodal_brief": ("multimodal", "vision", "audio", "video"),
}

_HEADING_COLON_RE = re.compile(r"^\s*(?:#{1,6}\s*)?([A-Za-z][A-Za-z0-9 _/-]+?)\s*:\s*(.*)\s*$")
_MARKDOWN_HEADING_RE = re.compile(r"^\s*#{1,6}\s+(.+?)\s*$")
_LIST_PREFIX_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s*")


def _normalize_label(label: str) -> str:
    return " ".join(label.strip().lower().replace("_", " ").split())


def clean_item(line: str) -> str:
    return _LIST_PREFIX_RE.sub("", line.strip())


def _match_section_heading(line: str) -> tuple[str, str] | None:
    colon_match = _HEADING_COLON_RE.match(line)
    if colon_match:
        raw_label = _normalize_label(colon_match.group(1))
        inline_value = clean_item(colon_match.group(2))
        for section, labels in SECTION_LABELS.items():
            if raw_label in labels:
                return section, inline_value

    heading_match = _MARKDOWN_HEADING_RE.match(line)
    if heading_match:
        raw_label = _normalize_label(heading_match.group(1))
        for section, labels in SECTION_LABELS.items():
            if raw_label in labels:
                return section, ""
    return None


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_items: list[str] = []
    for item in items:
        normalized = item.strip()
        if not normalized:
            continue
        key = normalized.casefold()
        if key in seen:
            continue
        seen.add(key)
        unique_items.append(normalized)
    return unique_items


def collect_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {key: [] for key in SECTION_LABELS}
    active_section: str | None = None

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue

        heading = _match_section_heading(stripped)
        if heading is not None:
            active_section = heading[0]
            if heading[1]:
                sections[active_section].append(heading[1])
            continue

        if active_section is None:
            continue

        item = clean_item(stripped)
        if item:
            sections[active_section].append(item)

    for key, values in sections.items():
        sections[key] = dedupe(values)
    return sections


def infer_target_class(text: str) -> str:
    lowered = text.lower()
    best_name = ""
    best_score = 0
    for name, keywords in TARGET_HINTS.items():
        score = sum(1 for keyword in keywords if keyword in lowered)
        if score > best_score:
            best_score = score
            best_name = name
    return best_name


def infer_authority_context(text: str) -> str:
    lowered = text.lower()
    if "cto" in lowered:
        return "cto"
    if "founder" in lowered:
        return "founder"
    if "product manager" in lowered:
        return "product_manager"
    return ""
