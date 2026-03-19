from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact
from sr8.profiles.base import ProfileDefinition
from sr8.profiles.generic import GENERIC_PROFILE
from sr8.profiles.prd import PRD_PROFILE
from sr8.profiles.repo_audit import REPO_AUDIT_PROFILE

PROFILE_REGISTRY: dict[str, ProfileDefinition] = {
    "generic": GENERIC_PROFILE,
    "prd": PRD_PROFILE,
    "repo_audit": REPO_AUDIT_PROFILE,
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
