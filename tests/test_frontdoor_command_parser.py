from sr8.frontdoor.command_parser import parse_chat_invocation


def test_frontdoor_parses_compile_prefix() -> None:
    parsed = parse_chat_invocation("compile: ship a launch plan")
    assert parsed.action == "compile"
    assert parsed.content == "ship a launch plan"
    assert parsed.entry_mode == "chat_compile"


def test_frontdoor_parses_resume_prefix() -> None:
    parsed = parse_chat_invocation("resume: <compiler_input_form />")
    assert parsed.action == "resume_intake"
    assert parsed.entry_mode == "intake_resume_compile"
