from sr8.profiles.registry import get_profile, list_profiles


def test_profile_registry_contains_w04_profiles() -> None:
    names = list_profiles()
    assert "plan" in names
    assert "research_brief" in names
    assert "procedure" in names
    assert "media_spec" in names
    assert "prompt_pack" in names


def test_profile_metadata_contains_transform_capabilities() -> None:
    profile = get_profile("plan")
    assert profile.supports_target("markdown_plan")
    assert not profile.supports_target("markdown_prd")
