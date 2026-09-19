#!/usr/bin/env python3
"""Extract one release section from CHANGELOG.md."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def extract_release_notes(changelog: str, version: str) -> str:
    header = re.compile(rf"(?m)^## {re.escape(version)} - \d{{4}}-\d{{2}}-\d{{2}}\s*$")
    match = header.search(changelog)
    if match is None:
        raise ValueError(f"no changelog section for {version}")

    next_header = re.search(r"(?m)^## ", changelog[match.end():])
    end = match.end() + next_header.start() if next_header else len(changelog)
    body = changelog[match.end():end].strip()
    if not body:
        raise ValueError(f"empty changelog section for {version}")
    return body + "\n"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract release notes from CHANGELOG.md.")
    parser.add_argument("--version", help="version without leading v")
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = _parser().parse_args()
    version = args.version or (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    try:
        notes = extract_release_notes(changelog, version)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(notes, encoding="utf-8")
        print(args.output)
    else:
        print(notes, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
