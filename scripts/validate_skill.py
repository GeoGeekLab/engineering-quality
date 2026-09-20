#!/usr/bin/env python3
"""Validate repository structure, skill metadata, links, workflows, versioning, and evals."""

from __future__ import annotations

import json
import re
import sys

import run_evals
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
LINK_RE = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
ACTION_USE_RE = re.compile(r"\buses:\s*([^\s#]+)")
FULL_COMMIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_PATHS = (
    "SKILL.md",
    "VERSION",
    "CHANGELOG.md",
    ".github/dependabot.yml",
    "references/principles.md",
    "references/verification.md",
    "references/review-rubric.md",
    "references/language-profiles.md",
    "workflows/feature.md",
    "workflows/bug-fix.md",
    "workflows/refactor.md",
    "workflows/review.md",
    "workflows/debug.md",
    "workflows/performance.md",
    "evals/cases.json",
    "evals/schema.json",
    "evals/result-schema.json",
    "evals/README.md",
    "docs/compatibility.md",
    "docs/release.md",
    "scripts/project_checks.py",
    "scripts/run_evals.py",
    "scripts/package_skill.py",
    "scripts/release_check.py",
    "scripts/release_notes.py",
)


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return {}, [f"{path}: cannot read file: {exc}"]

    if not lines or lines[0].strip() != "---":
        return {}, [f"{path}: missing opening YAML frontmatter delimiter"]

    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return {}, [f"{path}: missing closing YAML frontmatter delimiter"]

    data: dict[str, str] = {}
    for number, line in enumerate(lines[1:end], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            errors.append(f"{path}:{number}: unsupported frontmatter line")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key or not value:
            errors.append(f"{path}:{number}: frontmatter key and value must be non-empty")
            continue
        data[key] = value
    return data, errors


def validate_frontmatter(root: Path) -> list[str]:
    path = root / "SKILL.md"
    data, errors = parse_frontmatter(path)
    if errors:
        return errors

    name = data.get("name", "")
    description = data.get("description", "")

    if not NAME_RE.fullmatch(name):
        errors.append("SKILL.md: name must use lowercase kebab-case")
    if not description:
        errors.append("SKILL.md: description is required")
    elif len(description) > 1024:
        errors.append("SKILL.md: description must not exceed 1024 characters")
    if "<" in description or ">" in description:
        errors.append("SKILL.md: description must not contain angle-bracket markup")
    return errors


def validate_structure(root: Path) -> list[str]:
    return [
        f"missing required path: {relative}"
        for relative in REQUIRED_PATHS
        if not (root / relative).exists()
    ]


def validate_version(root: Path) -> list[str]:
    path = root / "VERSION"
    try:
        version = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError) as exc:
        return [f"VERSION: cannot read file: {exc}"]

    errors: list[str] = []
    if not SEMVER_RE.fullmatch(version):
        errors.append("VERSION: expected stable semantic version X.Y.Z")

    changelog = root / "CHANGELOG.md"
    if changelog.is_file() and SEMVER_RE.fullmatch(version):
        text = changelog.read_text(encoding="utf-8")
        if not re.search(rf"(?m)^## {re.escape(version)} - \d{{4}}-\d{{2}}-\d{{2}}$", text):
            errors.append(f"CHANGELOG.md: missing dated section for {version}")
    return errors


def _local_target(markdown: Path, raw_target: str) -> Path | None:
    target = raw_target.strip().strip("<>")
    if not target or target.startswith("#"):
        return None
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
        return None

    target = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not target:
        return None
    return (markdown.parent / target).resolve()


def validate_markdown_links(root: Path) -> list[str]:
    errors: list[str] = []
    root_resolved = root.resolve()

    for markdown in sorted(root.rglob("*.md")):
        try:
            text = markdown.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{markdown.relative_to(root)}: cannot read file: {exc}")
            continue

        for raw_target in LINK_RE.findall(text):
            target = _local_target(markdown, raw_target)
            if target is None:
                continue
            try:
                target.relative_to(root_resolved)
            except ValueError:
                errors.append(
                    f"{markdown.relative_to(root)}: local link escapes repository: {raw_target}"
                )
                continue
            if not target.exists():
                errors.append(
                    f"{markdown.relative_to(root)}: broken local link: {raw_target}"
                )
    return errors


def validate_workflow_action_pins(root: Path) -> list[str]:
    workflows = root / ".github" / "workflows"
    if not workflows.is_dir():
        return ["missing .github/workflows directory"]

    errors: list[str] = []
    paths = sorted((*workflows.glob("*.yml"), *workflows.glob("*.yaml")))

    for workflow in paths:
        try:
            lines = workflow.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            errors.append(f"{workflow.relative_to(root)}: cannot read file: {exc}")
            continue

        for number, line in enumerate(lines, start=1):
            match = ACTION_USE_RE.search(line)
            if match is None:
                continue

            target = match.group(1).strip().strip('"').strip("'")
            if target.startswith("./"):
                continue

            if target.startswith("docker://"):
                if "@sha256:" not in target:
                    errors.append(
                        f"{workflow.relative_to(root)}:{number}: "
                        f"container action is not digest-pinned: {target}"
                    )
                continue

            if "@" not in target:
                errors.append(
                    f"{workflow.relative_to(root)}:{number}: action has no ref: {target}"
                )
                continue

            _, ref = target.rsplit("@", 1)
            if not FULL_COMMIT_SHA_RE.fullmatch(ref):
                errors.append(
                    f"{workflow.relative_to(root)}:{number}: "
                    f"action is not pinned to a full commit SHA: {target}"
                )

    return errors


def validate_evals(root: Path) -> list[str]:
    cases_path = root / "evals" / "cases.json"
    schema_path = root / "evals" / "schema.json"
    result_schema_path = root / "evals" / "result-schema.json"

    try:
        data = json.loads(cases_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"evals/cases.json: invalid JSON: {exc}"]

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"evals/schema.json: invalid JSON: {exc}"]

    try:
        result_schema = json.loads(result_schema_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"evals/result-schema.json: invalid JSON: {exc}"]

    errors: list[str] = []
    if not isinstance(schema, dict) or schema.get("type") != "array":
        errors.append("evals/schema.json: expected an array schema")
    if not isinstance(result_schema, dict) or result_schema.get("type") != "object":
        errors.append("evals/result-schema.json: expected an object schema")

    if not isinstance(data, list):
        return errors + ["evals/cases.json: expected an array"]

    errors.extend(f"evals/cases.json: {error}" for error in run_evals.validate_cases(data))
    return errors


def validate_repository(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_structure(root))
    if (root / "SKILL.md").exists():
        errors.extend(validate_frontmatter(root))
    if (root / "VERSION").exists():
        errors.extend(validate_version(root))
    if (root / "evals" / "cases.json").exists() and (root / "evals" / "schema.json").exists():
        errors.extend(validate_evals(root))
    errors.extend(validate_workflow_action_pins(root))
    errors.extend(validate_markdown_links(root))
    return errors


def main() -> int:
    errors = validate_repository(ROOT)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
