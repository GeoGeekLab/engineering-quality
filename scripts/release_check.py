#!/usr/bin/env python3
"""Validate release-version and distribution invariants."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import package_skill
import validate_skill

ROOT = Path(__file__).resolve().parents[1]
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def read_version(root: Path = ROOT) -> str:
    return (root / "VERSION").read_text(encoding="utf-8").strip()


def _workflow_contains_any(text: str, candidates: tuple[str, ...]) -> bool:
    return any(candidate in text for candidate in candidates)


def validate_release_workflow(text: str) -> list[str]:
    errors: list[str] = []
    requirements = (
        ("release validation", ("scripts/release_check.py",)),
        ("package build", ("scripts/package_skill.py", "make package")),
        ("release notes", ("scripts/release_notes.py",)),
    )
    for label, candidates in requirements:
        if not _workflow_contains_any(text, candidates):
            errors.append(f"release workflow has no {label} step")

    rerun_requirements = (
        ("existing-release detection", "gh release view"),
        ("existing-release metadata reconciliation", "gh release edit"),
        ("existing-release asset reconciliation", "gh release upload"),
        ("asset replacement for safe reruns", "--clobber"),
        ("release branch trigger", 'release/v*.*.*'),
        ("release branch main-commit gate", "origin/main"),
        ("release tag creation", "git/refs"),
        ("artifact provenance", "actions/attest@"),
        ("provenance verification", "gh attestation verify"),
        ("release trigger branch cleanup", "git/refs/heads/${GITHUB_REF_NAME}"),
    )
    for label, marker in rerun_requirements:
        if marker not in text:
            errors.append(f"release workflow has no {label}")

    return errors


def check_release(root: Path = ROOT, tag: str | None = None) -> list[str]:
    errors = validate_skill.validate_repository(root)
    version = read_version(root)

    if not SEMVER_RE.fullmatch(version):
        errors.append(f"VERSION is not a stable semantic version: {version!r}")
        return errors

    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    if not re.search(rf"(?m)^## {re.escape(version)} - \d{{4}}-\d{{2}}-\d{{2}}$", changelog):
        errors.append(f"CHANGELOG.md has no dated section for {version}")

    if tag is not None and tag != f"v{version}":
        errors.append(f"tag {tag!r} does not match VERSION {version!r}")

    workflow = root / ".github" / "workflows" / "release.yml"
    if not workflow.is_file():
        errors.append("missing .github/workflows/release.yml")
    else:
        text = workflow.read_text(encoding="utf-8")
        errors.extend(validate_release_workflow(text))

    errors.extend(package_skill.reproducibility_check(root))
    return errors


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check release readiness.")
    parser.add_argument("--tag", help="optional tag name to validate against VERSION")
    return parser


def main() -> int:
    args = _parser().parse_args()
    errors = check_release(ROOT, args.tag)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Release check passed for {read_version(ROOT)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
