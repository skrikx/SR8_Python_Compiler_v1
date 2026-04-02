from pathlib import Path


def test_repo_structure_contract() -> None:
    required_paths = [
        ".github/workflows/ci.yml",
        ".github/workflows/docs-check.yml",
        ".github/workflows/frontend-ci.yml",
        ".github/workflows/hygiene.yml",
        ".github/workflows/release.yml",
        ".github/workflows/reusable-test.yml",
        ".github/workflows/reusable-build.yml",
        ".github/dependabot.yml",
        ".github/CODEOWNERS",
        ".github/pull_request_template.md",
        ".github/ISSUE_TEMPLATE",
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml",
        ".editorconfig",
        ".gitattributes",
        ".pre-commit-config.yaml",
        "scripts/cleanup/repo_audit.py",
        "scripts/cleanup/prune_stale_outputs.py",
        "scripts/cleanup/check_repo_layout.py",
        "docs/ci-and-quality-gates.md",
        "docs/install.md",
        "docs/repo-structure.md",
        "docs/release-automation.md",
        "docs/examples.md",
        "docs/bedrock-setup.md",
        "docs/public-api-exposure.md",
        "RELEASE_CHECKLIST.md",
    ]
    for path in required_paths:
        assert Path(path).exists(), path
