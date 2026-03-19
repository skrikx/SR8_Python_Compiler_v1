from sr8.io.exporters import load_artifact
from sr8.models.schema_version import SchemaVersion
from sr8.storage.load import load_derivative


def test_schema_version_constants_present() -> None:
    version = SchemaVersion()
    assert version.canonical_schema == "1.0.0"
    assert version.derivative_schema == "1.0.0"


def test_stored_artifact_fixture_compatible_with_current_schema() -> None:
    artifact = load_artifact("tests/fixtures/stored_artifact_sample.json")
    assert artifact.artifact_version == SchemaVersion().canonical_schema


def test_stored_derivative_fixture_compatible_with_current_schema() -> None:
    derivative = load_derivative("tests/fixtures/stored_derivative_sample.json")
    assert derivative.parent_artifact_version == SchemaVersion().derivative_schema
