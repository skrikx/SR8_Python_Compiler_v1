from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_release_and_launch_assets_exist() -> None:
    required_paths = [
        "RELEASE_CHECKLIST.md",
        "MAINTAINERS.md",
        "docs/oss-launch.md",
        "docs/triage.md",
        "docs/release-notes-policy.md",
        "docs/post-launch-ops.md",
        "docs/labels.md",
        "assets/release/release-summary.md",
        "assets/release/feature-matrix.md",
        "assets/release/install-snippets.md",
        "assets/release/first-release-notes.md",
        "assets/social/github-release-card.md",
        "assets/badges/README_BADGES.md",
    ]
    for path in required_paths:
        assert Path(path).exists(), path


def test_release_assets_have_expected_sections() -> None:
    checklist = _read("RELEASE_CHECKLIST.md")
    first_release_notes = _read("assets/release/first-release-notes.md")
    matrix = _read("assets/release/feature-matrix.md")

    assert "Rollback / Hotfix Baseline" in checklist
    assert "## Summary" in first_release_notes
    assert "## Added" in first_release_notes
    assert "| Surface | Status | Notes |" in matrix
