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
        for required in ("scripts/release_check.py", "scripts/package_skill.py", "scripts/release_notes.py"):
            if required not in text:
                errors.append(f"release workflow does not invoke {required}")

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
