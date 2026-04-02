from pathlib import Path


def test_ac5_fixture_floor() -> None:
    golden = list(Path("tests/fixtures/golden").glob("*.json"))
    assert len(golden) >= 25
