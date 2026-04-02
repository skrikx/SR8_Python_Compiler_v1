from __future__ import annotations

from pydantic import Field

from sr8.models.base import SR8Model


class GovernanceSignals(SR8Model):
    ambiguous: bool = False
    incomplete: bool = False
    requires_human_review: bool = False


class ExtractedDimensions(SR8Model):
    objective: str = ""
    scope: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    context_package: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    output_contract: list[str] = Field(default_factory=list)
    target_class: str = ""
    authority_context: str = ""
    governance_flags: GovernanceSignals = Field(default_factory=GovernanceSignals)
