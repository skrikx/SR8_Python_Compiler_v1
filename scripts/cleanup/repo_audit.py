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

    if args.check and any(finding.status == "missing" for finding in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
