from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

from sr8.extract.rules import SECTION_LABELS, collect_sections
from sr8.extract.signals import ExtractedDimensions
from sr8.models.source_intent import SourceIntent

WORD_RE = re.compile(r"\w+")
WEAK_INTENT_TOKENS = (
    "something",
    "stuff",
    "unclear",
    "unknown",
    "maybe",
    "tbd",
    "todo",
    "helpful",
    "soon",
    "fast",
    "quickly",
    "whatever",
    "anything",
    "help",
)
STOPWORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "be",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "that",
    "the",
    "this",
    "to",
    "with",
    "your",
}
DELIVERABLE_HINTS = (
    "checklist",
    "plan",
    "brief",
    "spec",
    "workflow",
    "guide",
    "audit",
    "api",
    "compiler",
    "report",
    "roadmap",
    "summary",
)

IMPORTANT_FIELDS = ("objective", "scope", "constraints", "success_criteria", "output_contract")
MATERIAL_DERIVED_FIELDS = ("scope", "constraints", "success_criteria", "output_contract")
TEXT_FIELDS = ("objective", "target_class", "authority_context")
LIST_FIELDS = (
    "scope",
    "exclusions",
    "constraints",
    "context_package",
    "assumptions",
    "dependencies",
    "success_criteria",
    "output_contract",
)
STRUCTURE_FIELDS = (*TEXT_FIELDS, *LIST_FIELDS)

CANONICALIZE_IMPORTANT_THRESHOLD = 4
SEMANTIC_IMPORTANT_DERIVED_MIN = 2


def _normalize_key(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", " ").replace("-", " ").split())


FIELD_ALIASES: dict[str, set[str]] = {
    field_name: {
        _normalize_key(field_name),
        *(_normalize_key(label) for label in SECTION_LABELS.get(field_name, ())),
    }
    for field_name in STRUCTURE_FIELDS
}


@dataclass(slots=True)
class SourceStructureProfile:
    source_structure_kind: str
    source_supplied_fields: set[str]
    source_values: dict[str, object]
    word_count: int
    specificity_score: int
    weak_signal_hits: list[str]
    deliverable_hint: str
    primary_focus: str
    canonicalize_ready: bool
    can_semantically_expand: bool


@dataclass(slots=True)
class CompilePreview:
    compile_kind: str
    source_structure_kind: str
    source_supplied_fields: set[str]
    source_values: dict[str, object]
    word_count: int
    specificity_score: int
    weak_signal_hits: list[str]
    deliverable_hint: str
    primary_focus: str
    reason: str


def _flatten_strings(value: object) -> list[str]:
    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []
    if isinstance(value, Mapping):
        items: list[str] = []
        for nested_key, nested_value in value.items():
            nested_items = _flatten_strings(nested_value)
            if nested_items:
                items.extend(nested_items)
            else:
                key_text = str(nested_key).strip()
                if key_text:
                    items.append(key_text)
        return items
    if isinstance(value, list):
        items = []
        for item in value:
            items.extend(_flatten_strings(item))
        return items
    if value is None:
        return []
    cleaned = str(value).strip()
    return [cleaned] if cleaned else []


def _coerce_text(value: object) -> str:
    flattened = _flatten_strings(value)
    return flattened[0] if flattened else ""


def _coerce_list(value: object) -> list[str]:
    seen: set[str] = set()
    items: list[str] = []
    for item in _flatten_strings(value):
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        items.append(item)
    return items


def _structured_source_values(payload: Mapping[str, object]) -> dict[str, object]:
    values: dict[str, object] = {}
    for raw_key, raw_value in payload.items():
        normalized_key = _normalize_key(str(raw_key))
        field_name = next(
            (
                candidate
                for candidate, aliases in FIELD_ALIASES.items()
                if normalized_key in aliases
            ),
            None,
        )
        if field_name is None:
            continue
        if field_name in TEXT_FIELDS:
            text_value = _coerce_text(raw_value)
            if text_value:
                values[field_name] = text_value
        else:
            list_value = _coerce_list(raw_value)
            if list_value:
                values[field_name] = list_value
    return values


def _outline_source_values(text: str) -> dict[str, object]:
    sections = collect_sections(text)
    values: dict[str, object] = {}
    for field_name in TEXT_FIELDS:
        section_values = sections[field_name]
        if section_values:
            values[field_name] = section_values[0]
    for field_name in LIST_FIELDS:
        section_values = sections[field_name]
        if section_values:
            values[field_name] = section_values
    return values


def _detect_structure_kind(source_intent: SourceIntent, source_values: Mapping[str, object]) -> str:
    if source_intent.source_type == "json":
        return "structured_json"
    if source_intent.source_type == "yaml":
        return "structured_yaml"
    if source_intent.source_type == "markdown":
        return "markdown_outline" if source_values else "markdown_raw"
    return "text_outline" if source_values else "raw_text"


def _detect_deliverable_hint(text: str) -> str:
    lowered = text.lower()
    for hint in DELIVERABLE_HINTS:
        if hint in lowered:
            return hint
    return ""


def _extract_primary_focus(
    text: str,
    source_values: Mapping[str, object],
    deliverable_hint: str,
) -> str:
    objective = str(source_values.get("objective", "")).strip()
    candidate = objective or text.strip().splitlines()[0].strip()
    lowered = candidate.lower()
    if " for " in lowered:
        return candidate.split(" for ", 1)[1].strip(" .")
    if " to " in lowered:
        return candidate.split(" to ", 1)[1].strip(" .")
    if deliverable_hint and deliverable_hint in lowered:
        return candidate.strip(" .")
    return candidate.strip(" .")


def _specificity_score(
    text: str,
    source_supplied_fields: set[str],
    deliverable_hint: str,
    weak_signal_hits: list[str],
) -> int:
    words = [token.casefold() for token in WORD_RE.findall(text)]
    meaningful_tokens = {
        token for token in words if len(token) > 2 and token not in STOPWORDS
    }
    score = len(meaningful_tokens)
    score += len(source_supplied_fields) * 2
    if deliverable_hint:
        score += 2
    score -= len(weak_signal_hits) * 3
    return max(score, 0)


def _can_semantically_expand(
    *,
    source_supplied_fields: set[str],
    word_count: int,
    specificity_score: int,
    weak_signal_hits: list[str],
    deliverable_hint: str,
) -> bool:
    if word_count < 4 and not source_supplied_fields:
        return False
    if specificity_score < 4 and len(source_supplied_fields & set(IMPORTANT_FIELDS)) < 2:
        return False
    if weak_signal_hits and specificity_score < 6 and not deliverable_hint:
        return False
    return True


def inspect_source_structure(source_intent: SourceIntent) -> SourceStructureProfile:
    source_text = source_intent.normalized_content or source_intent.raw_content
    parsed_payload = source_intent.metadata.get("parsed_payload")
    if isinstance(parsed_payload, Mapping):
        source_values = _structured_source_values(parsed_payload)
    else:
        source_values = _outline_source_values(source_text)

    source_supplied_fields = {
        field_name
        for field_name in STRUCTURE_FIELDS
        if field_name in source_values and bool(source_values[field_name])
    }
    word_count = len(WORD_RE.findall(source_text))
    lowered = source_text.lower()
    weak_signal_hits = [token for token in WEAK_INTENT_TOKENS if token in lowered]
    deliverable_hint = _detect_deliverable_hint(source_text)
    specificity_score = _specificity_score(
        source_text,
        source_supplied_fields,
        deliverable_hint,
        weak_signal_hits,
    )
    canonicalize_ready = (
        source_intent.source_type in {"json", "yaml"}
        or len(source_supplied_fields & set(IMPORTANT_FIELDS)) >= CANONICALIZE_IMPORTANT_THRESHOLD
    )
    can_semantically_expand = _can_semantically_expand(
        source_supplied_fields=source_supplied_fields,
        word_count=word_count,
        specificity_score=specificity_score,
        weak_signal_hits=weak_signal_hits,
        deliverable_hint=deliverable_hint,
    )
    return SourceStructureProfile(
        source_structure_kind=_detect_structure_kind(source_intent, source_values),
        source_supplied_fields=source_supplied_fields,
        source_values=source_values,
        word_count=word_count,
        specificity_score=specificity_score,
        weak_signal_hits=weak_signal_hits,
        deliverable_hint=deliverable_hint,
        primary_focus=_extract_primary_focus(source_text, source_values, deliverable_hint),
        canonicalize_ready=canonicalize_ready,
        can_semantically_expand=can_semantically_expand,
    )


def build_compile_preview(source_intent: SourceIntent) -> CompilePreview:
    profile = inspect_source_structure(source_intent)
    if profile.source_structure_kind in {"structured_json", "structured_yaml"}:
        compile_kind = "canonicalize_structured"
        reason = "Structured input already supplies governed canonical fields."
    elif profile.canonicalize_ready:
        compile_kind = "canonicalize_structured"
        reason = "Source already supplies most important intent dimensions."
    elif profile.can_semantically_expand:
        compile_kind = "semantic_compile"
        reason = "Compiler can materially derive missing intent dimensions from the source."
    else:
        compile_kind = "needs_intake"
        reason = "Source is too vague for truthful semantic expansion."
    return CompilePreview(
        compile_kind=compile_kind,
        source_structure_kind=profile.source_structure_kind,
        source_supplied_fields=profile.source_supplied_fields,
        source_values=profile.source_values,
        word_count=profile.word_count,
        specificity_score=profile.specificity_score,
        weak_signal_hits=profile.weak_signal_hits,
        deliverable_hint=profile.deliverable_hint,
        primary_focus=profile.primary_focus,
        reason=reason,
    )


def merge_source_values(
    extracted: ExtractedDimensions,
    source_values: Mapping[str, object],
) -> ExtractedDimensions:
    updates: dict[str, object] = {}
    for field_name in TEXT_FIELDS:
        value = source_values.get(field_name)
        if isinstance(value, str) and value.strip():
            updates[field_name] = value
    for field_name in LIST_FIELDS:
        value = source_values.get(field_name)
        if isinstance(value, list) and value:
            updates[field_name] = value
    if not updates:
        return extracted
    return extracted.model_copy(update=updates)


def build_recovery_summary(
    *,
    compile_kind: str,
    source_supplied_fields: set[str],
    compiler_derived_fields: list[str],
    unresolved_fields: list[str],
    weak_signal_hits: list[str],
) -> dict[str, object]:
    missing_fields = [field for field in IMPORTANT_FIELDS if field in unresolved_fields]
    recovered_fields = [
        field
        for field in IMPORTANT_FIELDS
        if field not in source_supplied_fields
        and field in compiler_derived_fields
        and field not in missing_fields
    ]
    weak_fields: list[str] = []
    if compile_kind == "needs_intake":
        weak_fields = [
            field
            for field in IMPORTANT_FIELDS
            if field not in missing_fields and field not in source_supplied_fields
        ]
        if not weak_fields and weak_signal_hits:
            weak_fields = ["objective"]
    needed = [
        field.replace("_", " ")
        for field in (*missing_fields, *weak_fields)
    ]
    suggested_prompt = ""
    if compile_kind == "needs_intake":
        joined = ", ".join(dict.fromkeys(needed))
        suggested_prompt = (
            f"Provide a stronger intent package with explicit {joined}."
            if joined
            else (
                "Provide a stronger intent package with explicit objective, scope, "
                "constraints, success criteria, and output contract."
            )
        )
    return {
        "intake_required": compile_kind == "needs_intake",
        "missing_fields": missing_fields,
        "recovery_applied": bool(recovered_fields),
        "recovered_fields": recovered_fields,
        "weak_fields": weak_fields,
        "contradictory_fields": [],
        "suggested_prompt": suggested_prompt,
    }
