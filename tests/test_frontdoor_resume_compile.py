from sr8.frontdoor.chat_compile import chat_compile


def test_frontdoor_resume_compile() -> None:
    intake_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<compiler_input_form xmlns=\"https://sros.cloud/schema/intake/v1\" version=\"1.0.0\">
  <compiler_input>
    <goal>Build a landing page launch brief</goal>
    <deliverables>
      <item>landing_page</item>
    </deliverables>
    <constraints>
      <item>Local-only</item>
    </constraints>
  </compiler_input>
</compiler_input_form>
"""
    result = chat_compile(f"resume: {intake_xml}")
    assert result.status in {"compiled", "safe_alternative"}
    assert result.artifact is not None
    assert result.artifact.objective
    assert result.promptunit_package_xml is not None
