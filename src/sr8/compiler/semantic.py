from __future__ import annotations

from dataclasses import dataclass

from sr8.compiler.planner import CompilePreview
from sr8.extract.rules import infer_authority_context, infer_target_class
from sr8.extract.signals import ExtractedDimensions, GovernanceSignals


@dataclass(slots=True)
class SemanticExpansionResult:
    dimensions: ExtractedDimensions
    compiler_derived_fields: set[str]


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        normalized = item.strip()
        if not normalized:
            continue
        key = normalized.casefold()
        if key in seen:
            continue
        seen.add(key)
        output.append(normalized)
    return output


def _normalize_sentence(text: str) -> str:
    candidate = text.strip()
    if not candidate:
        return ""
    normalized = candidate[0].upper() + candidate[1:]
    return normalized if normalized.endswith(".") else f"{normalized}."


def _deliverable_label(deliverable_hint: str) -> str:
    return deliverable_hint.replace("_", " ") if deliverable_hint else "artifact"


def _focus_phrase(preview: CompilePreview, source_text: str) -> str:
    candidate = preview.primary_focus.strip()
    if candidate:
        return candidate
    first_line = source_text.strip().splitlines()[0].strip() if source_text.strip() else ""
    return first_line or "the requested work"


def _derive_scope_items(focus: str, deliverable_hint: str) -> list[str]:
    deliverable = _deliverable_label(deliverable_hint)
    if deliverable_hint == "checklist":
        return _dedupe(
            [
                f"Define the readiness checks required for {focus}.",
                f"Cover validation, governance, and operator handoff steps for {focus}.",
                "Organize the result as an ordered checklist that can be executed end to end.",
            ]
        )
    if deliverable_hint in {"api", "compiler"}:
        return _dedupe(
            [
                f"Define the compile stages and operator-visible route handling for {focus}.",
                "Cover provenance, validation, and truthful receipt behavior.",
                "Preserve deterministic fallback behavior for under-specified input.",
            ]
        )
    if deliverable_hint in {"brief", "spec", "report"}:
        return _dedupe(
            [
                f"Define the core sections required to deliver the {deliverable} for {focus}.",
                f"Capture constraints, success criteria, and operator handoff details for {focus}.",
                "Package the result as a governed artifact instead of a loose note.",
            ]
        )
    return _dedupe(
        [
            f"Define the core work required to deliver {focus}.",
            (
                "Capture validation, governance, and operator handoff expectations "
                f"for the {deliverable}."
            ),
            (
                "Package the result into a structured artifact that can be reviewed "
                "without re-reading the source."
            ),
        ]
    )


def _derive_constraints(source_text: str, deliverable_hint: str) -> list[str]:
    lowered = source_text.lower()
    constraints: list[str] = []
    if "local-first" in lowered or "local first" in lowered:
        constraints.append("Keep the compile flow local-first and workspace-contained.")
    if "compiler" in lowered:
        constraints.append(
            "Do not present canonicalization or schema echoing as semantic compilation."
        )
    if "api" in lowered:
        constraints.append(
            "Make route selection and readiness outcomes explicit in operator-facing responses."
        )
    if "json" in lowered or "yaml" in lowered:
        constraints.append(
            "Preserve clean structured input handling alongside raw-intent compilation."
        )
    if not constraints:
        constraints.append(
            "Preserve truthful provenance, validation, and operator-facing receipts."
        )
    if deliverable_hint == "checklist":
        constraints.append(
            "Keep each checklist item actionable enough for an operator to execute directly."
        )
    constraints.append("Avoid hidden external dependencies in the primary compile path.")
    return _dedupe(constraints)[:3]


def _derive_success_criteria(focus: str, deliverable_hint: str) -> list[str]:
    deliverable = _deliverable_label(deliverable_hint)
    return _dedupe(
        [
            (
                f"The final {deliverable} covers scope, constraints, and output "
                f"expectations for {focus}."
            ),
            (
                "The operator can tell which fields came from the source and which "
                "were derived by the compiler."
            ),
            (
                "The result is actionable without forcing the user to restate the "
                "request as structured JSON or YAML."
            ),
        ]
    )


def _derive_output_contract(deliverable_hint: str) -> list[str]:
    mapping = {
        "checklist": [
            "Launch checklist",
            "Validation gate summary",
            "Open risks or follow-up notes",
        ],
        "plan": [
            "Execution plan",
            "Milestone breakdown",
            "Validation summary",
        ],
        "brief": [
            "Structured brief",
            "Recommended next actions",
            "Known risks and constraints",
        ],
        "spec": [
            "Structured specification",
            "Acceptance summary",
            "Operator handoff notes",
        ],
        "api": [
            "Canonical intent artifact",
            "Compile route summary",
            "Validation and receipt trail",
        ],
        "compiler": [
            "Canonical intent artifact",
            "Provenance and lineage summary",
            "Operator receipt with compile truth",
        ],
    }
    return mapping.get(
        deliverable_hint,
        [
            "Structured artifact",
            "Validation summary",
            "Operator handoff notes",
        ],
    )


def _default_target_class(deliverable_hint: str) -> str:
    mapping = {
        "api": "governed_request",
        "audit": "repo_audit",
        "brief": "research_brief",
        "checklist": "plan",
        "compiler": "compiler_core",
        "plan": "plan",
        "report": "research_brief",
        "spec": "product_spec",
        "workflow": "procedure",
    }
    return mapping.get(deliverable_hint, "")


def expand_dimensions(
    source_text: str,
    base_dimensions: ExtractedDimensions,
    preview: CompilePreview,
) -> SemanticExpansionResult:
    compiler_derived_fields: set[str] = set()
    updates: dict[str, object] = {}
    focus = _focus_phrase(preview, source_text)

    if not base_dimensions.objective.strip():
        objective = _normalize_sentence(focus)
        if objective:
            updates["objective"] = objective
            compiler_derived_fields.add("objective")

    if not base_dimensions.scope:
        updates["scope"] = _derive_scope_items(focus, preview.deliverable_hint)
        compiler_derived_fields.add("scope")

    if not base_dimensions.constraints:
        updates["constraints"] = _derive_constraints(source_text, preview.deliverable_hint)
        compiler_derived_fields.add("constraints")

    if not base_dimensions.success_criteria:
        updates["success_criteria"] = _derive_success_criteria(focus, preview.deliverable_hint)
        compiler_derived_fields.add("success_criteria")

    if not base_dimensions.output_contract:
        updates["output_contract"] = _derive_output_contract(preview.deliverable_hint)
        compiler_derived_fields.add("output_contract")

    if not base_dimensions.assumptions:
        updates["assumptions"] = [
            "The source captures the primary goal but leaves execution detail to the compiler.",
        ]
        compiler_derived_fields.add("assumptions")

    if not base_dimensions.target_class.strip():
        inferred_target_class = infer_target_class(source_text) or _default_target_class(
            preview.deliverable_hint
        )
        if inferred_target_class:
            updates["target_class"] = inferred_target_class
            compiler_derived_fields.add("target_class")

    if not base_dimensions.authority_context.strip():
        authority_context = infer_authority_context(source_text)
        if authority_context:
            updates["authority_context"] = authority_context
            compiler_derived_fields.add("authority_context")

    expanded = base_dimensions.model_copy(update=updates)
    important_missing = [
        not expanded.objective.strip(),
        not bool(expanded.scope),
        not bool(expanded.constraints),
        not bool(expanded.success_criteria),
        not bool(expanded.output_contract),
    ]
    expanded = expanded.model_copy(
        update={
            "governance_flags": GovernanceSignals(
                ambiguous=not expanded.objective.strip(),
                incomplete=any(important_missing),
                requires_human_review=any(important_missing),
            )
        }
    )
    return SemanticExpansionResult(
        dimensions=expanded,
        compiler_derived_fields=compiler_derived_fields,
    )
