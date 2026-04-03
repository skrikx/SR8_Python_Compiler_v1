from sr8.frontdoor.chat_compile import chat_compile


def test_chat_compile_to_canonical() -> None:
    result = chat_compile(
        "compile: Objective: Create a launch plan\nScope:\n- Step one\nSuccess Criteria:\n- Ready"
    )
    assert result.status in {"compiled", "safe_alternative"}
    assert result.artifact is not None
    assert result.receipt is not None
    assert result.artifact.source.source_hash
