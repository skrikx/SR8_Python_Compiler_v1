from sr8.frontdoor.chat_compile import chat_compile


def test_frontdoor_intake_fallback() -> None:
    result = chat_compile("compile: help")
    assert result.status == "intake_required"
    assert result.intake_xml is not None
    assert "compiler_input_form" in result.intake_xml.lower()
