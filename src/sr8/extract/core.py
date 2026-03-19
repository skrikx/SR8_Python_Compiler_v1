from __future__ import annotations

from sr8.extract.rules import collect_sections, infer_authority_context, infer_target_class
from sr8.extract.signals import ExtractedDimensions, GovernanceSignals


def _fallback_objective(text: str) -> str:
    for line in text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        if cleaned.startswith("#"):
            continue
        if cleaned.endswith(":"):
            continue
        return cleaned
    return ""


def extract_dimensions(normalized_source: str) -> ExtractedDimensions:
    sections = collect_sections(normalized_source)

    objective_items = sections["objective"]
    objective = objective_items[0] if objective_items else _fallback_objective(normalized_source)

    target_items = sections["target_class"]
    target_class = target_items[0] if target_items else infer_target_class(normalized_source)

    authority_items = sections["authority_context"]
    authority_context = (
        authority_items[0] if authority_items else infer_authority_context(normalized_source)
    )

    incomplete = not bool(
        sections["scope"] or sections["constraints"] or sections["success_criteria"]
    )
    ambiguous = objective == ""
    governance = GovernanceSignals(
        ambiguous=ambiguous,
        incomplete=incomplete,
        requires_human_review=ambiguous or incomplete,
    )

    return ExtractedDimensions(
        objective=objective,
        scope=sections["scope"],
        exclusions=sections["exclusions"],
        constraints=sections["constraints"],
        assumptions=sections["assumptions"],
        dependencies=sections["dependencies"],
        success_criteria=sections["success_criteria"],
        output_contract=sections["output_contract"],
        target_class=target_class,
        authority_context=authority_context,
        governance_flags=governance,
    )
