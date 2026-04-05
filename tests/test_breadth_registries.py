from sr8.registry import (
    list_artifact_families,
    list_delivery_targets,
    list_entry_modes,
)


def test_breadth_registries_include_frontdoor_modes() -> None:
    assert "chat_compile" in list_entry_modes()
    assert "intake_resume_compile" in list_entry_modes()


def test_breadth_registries_include_new_families() -> None:
    families = list_artifact_families()
    assert "promptunit_package" in families
    assert "sr8_prompt" in families
    assert "landing_page_package" in families
    assert "mvp_builder_package" in families
    assert "deep_research_package" in families
    assert "governed_request_package" in families
    assert "multimodal_brief" in families


def test_breadth_registries_include_delivery_targets() -> None:
    targets = list_delivery_targets()
    assert "xml_package" in targets
    assert "frontend_render" in targets
