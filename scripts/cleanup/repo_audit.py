from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIRS = (
    REPO_ROOT / ".sr8",
    REPO_ROOT / "benchmarks",
    REPO_ROOT / "dist",
    REPO_ROOT / "build",
)
DISALLOWED_TRACKED_FILES = (
    REPO_ROOT / "SR8_Compiler_v1_Workflows.zip",
    REPO_ROOT / "SR8_updated_zip_audit.md",
    REPO_ROOT / "sr8_v1_compiler_first_run.txt",
)
EXPECTED_EMPTY_DIRS = (
    REPO_ROOT / "artifacts",
    REPO_ROOT / "receipts",
)


@dataclass(slots=True)
class AuditFinding:
    path: str
    status: str
    detail: str


def audit_repository() -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    required = [
        REPO_ROOT / ".github" / "workflows" / "ci.yml",
        REPO_ROOT / ".github" / "workflows" / "release.yml",
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs" / "release-automation.md",
    ]
    for path in required:
        findings.append(
            AuditFinding(
                path=str(path.relative_to(REPO_ROOT)),
                status="present" if path.exists() else "missing",
                detail="required repo surface" if path.exists() else "required file is missing",
            )
        )
    for directory in DEFAULT_OUTPUT_DIRS:
        if directory.exists():
            findings.append(
                AuditFinding(
                    path=str(directory.relative_to(REPO_ROOT)),
                    status="present",
                    detail="generated output directory exists",
                )
            )
    for path in DISALLOWED_TRACKED_FILES:
        findings.append(
            AuditFinding(
                path=str(path.relative_to(REPO_ROOT)),
                status="unexpected" if path.exists() else "clean",
                detail="release-noise file should not be tracked"
                if path.exists()
                else "release-noise file absent",
            )
        )
    for directory in EXPECTED_EMPTY_DIRS:
        non_placeholder = [
            item.name
            for item in sorted(directory.iterdir())
            if item.name != ".gitkeep"
        ] if directory.exists() else []
        findings.append(
            AuditFinding(
                path=str(directory.relative_to(REPO_ROOT)),
                status="unexpected" if non_placeholder else "clean",
                detail="contains tracked runtime outputs: " + ", ".join(non_placeholder)
                if non_placeholder
                else "placeholder-only directory",
            )
        )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit repo hygiene and release surface.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail on any missing required surface.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = parser.parse_args()

    findings = audit_repository()
    if args.json:
        print(json.dumps([asdict(item) for item in findings], indent=2, sort_keys=True))
    else:
        for finding in findings:
            print(f"{finding.status}: {finding.path} - {finding.detail}")

    if args.check and any(finding.status in {"missing", "unexpected"} for finding in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
