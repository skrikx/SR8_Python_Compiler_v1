from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact
from sr8.profiles.base import ProfileDefinition
from sr8.profiles.code_task_graph import CODE_TASK_GRAPH_PROFILE
from sr8.profiles.generic import GENERIC_PROFILE
from sr8.profiles.media_spec import MEDIA_SPEC_PROFILE
from sr8.profiles.plan import PLAN_PROFILE
from sr8.profiles.prd import PRD_PROFILE
from sr8.profiles.procedure import PROCEDURE_PROFILE
from sr8.profiles.prompt_pack import PROMPT_PACK_PROFILE
from sr8.profiles.repo_audit import REPO_AUDIT_PROFILE
from sr8.profiles.research_brief import RESEARCH_BRIEF_PROFILE
from sr8.profiles.whitepaper_outline import WHITEPAPER_OUTLINE_PROFILE

PROFILE_REGISTRY: dict[str, ProfileDefinition] = {
    "generic": GENERIC_PROFILE,
    "prd": PRD_PROFILE,
    "repo_audit": REPO_AUDIT_PROFILE,
    "plan": PLAN_PROFILE,
    "research_brief": RESEARCH_BRIEF_PROFILE,
    "procedure": PROCEDURE_PROFILE,
    "media_spec": MEDIA_SPEC_PROFILE,
    "prompt_pack": PROMPT_PACK_PROFILE,
    "whitepaper_outline": WHITEPAPER_OUTLINE_PROFILE,
    "code_task_graph": CODE_TASK_GRAPH_PROFILE,
}


def get_profile(profile_name: str) -> ProfileDefinition:
    key = profile_name.strip().lower()
    if key not in PROFILE_REGISTRY:
        msg = f"Unknown profile '{profile_name}'. Expected one of: {', '.join(PROFILE_REGISTRY)}."
        raise ValueError(msg)
    return PROFILE_REGISTRY[key]


def apply_profile_overlay(artifact: IntentArtifact, profile_name: str) -> IntentArtifact:
    profile = get_profile(profile_name)
    return profile.apply(artifact)


def list_profiles() -> tuple[str, ...]:
    return tuple(PROFILE_REGISTRY.keys())
