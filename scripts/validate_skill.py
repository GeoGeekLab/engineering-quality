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
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "GOVERNANCE.md",
    "SECURITY.md",
    ".github/dependabot.yml",
    ".github/CODEOWNERS",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/bug.yml",
    ".github/ISSUE_TEMPLATE/proposal.yml",
    ".github/ISSUE_TEMPLATE/compatibility.yml",
    ".claude-plugin/plugin.json",
    "agents/openai.yaml",
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
    "docs/github-settings.md",
    "docs/release.md",
    "scripts/project_checks.py",
    "scripts/run_evals.py",
    "scripts/host_eval_adapter.py",
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



def _parse_simple_yaml_sections(path: Path) -> tuple[dict[str, dict[str, str]], list[str]]:
    sections: dict[str, dict[str, str]] = {}
    errors: list[str] = []
    current: str | None = None

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return {}, [f"{path}: cannot read file: {exc}"]

    for number, raw in enumerate(lines, start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue

        if not raw.startswith(" "):
            stripped = raw.strip()
            if not stripped.endswith(":") or ":" in stripped[:-1]:
                errors.append(f"{path}:{number}: unsupported top-level YAML entry")
                current = None
                continue
            current = stripped[:-1].strip()
            if not current:
                errors.append(f"{path}:{number}: empty YAML section")
                continue
            sections.setdefault(current, {})
            continue

        if current is None or not raw.startswith("  ") or raw.startswith("   "):
            errors.append(f"{path}:{number}: expected two-space nested YAML entry")
            continue

        stripped = raw.strip()
        if ":" not in stripped:
            errors.append(f"{path}:{number}: expected key: value")
            continue

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            errors.append(f"{path}:{number}: key and value must be non-empty")
            continue

        if (
            len(value) >= 2
            and value[0] == value[-1]
            and value[0] in {'"', "'"}
        ):
            value = value[1:-1]
        sections[current][key] = value

    return sections, errors


def validate_openai_metadata(root: Path) -> list[str]:
    path = root / "agents" / "openai.yaml"
    sections, errors = _parse_simple_yaml_sections(path)
    if errors:
        return errors

    interface = sections.get("interface")
    if not interface:
        return ["agents/openai.yaml: interface mapping is required"]

    for key in ("display_name", "short_description", "default_prompt"):
        value = interface.get(key, "")
        if not value:
            errors.append(f"agents/openai.yaml: interface.{key} is required")

    policy = sections.get("policy", {})
    implicit = policy.get("allow_implicit_invocation")
    if implicit not in {"true", "false"}:
        errors.append(
            "agents/openai.yaml: policy.allow_implicit_invocation must be true or false"
        )

    return errors

def validate_structure(root: Path) -> list[str]:
    return [
        f"missing required path: {relative}"
        for relative in REQUIRED_PATHS
        if not (root / relative).exists()
    ]


def validate_claude_plugin(root: Path) -> list[str]:
    path = root / ".claude-plugin" / "plugin.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f".claude-plugin/plugin.json: invalid JSON: {exc}"]

    if not isinstance(data, dict):
        return [".claude-plugin/plugin.json: expected an object"]

    errors: list[str] = []
    if data.get("name") != "engineering-quality":
        errors.append(".claude-plugin/plugin.json: name must be engineering-quality")

    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(".claude-plugin/plugin.json: description is required")

    version = data.get("version")
    expected = (root / "VERSION").read_text(encoding="utf-8").strip()
    if version != expected:
        errors.append(
            f".claude-plugin/plugin.json: version {version!r} does not match VERSION {expected!r}"
        )

    repository = data.get("repository")
    if repository != "https://github.com/GeoGeekLab/engineering-quality":
        errors.append(".claude-plugin/plugin.json: canonical repository URL is required")

    if data.get("license") != "MIT":
        errors.append(".claude-plugin/plugin.json: license must be MIT")

    return errors


def validate_governance(root: Path) -> list[str]:
    errors: list[str] = []

    required_text = {
        ".github/CODEOWNERS": (
            "* @GeoGeekLab",
        ),
        ".github/ISSUE_TEMPLATE/config.yml": (
            "blank_issues_enabled: false",
            "SECURITY.md",
        ),
        ".github/ISSUE_TEMPLATE/bug.yml": (
            "name: Bug report",
            "body:",
        ),
        ".github/ISSUE_TEMPLATE/proposal.yml": (
            "name: Engineering-quality proposal",
            "body:",
        ),
        ".github/ISSUE_TEMPLATE/compatibility.yml": (
            "name: Host compatibility report",
            "body:",
        ),
        "SECURITY.md": (
            "--trust-repository",
            "--allow-workspace-execution",
        ),
        "GOVERNANCE.md": (
            "quality (3.10)",
            "quality (3.12)",
            "quality (3.14)",
            "package",
            "required approving-review count should remain **0**",
        ),
        "docs/github-settings.md": (
            "main-quality-gate",
            "release-tag-immutability",
            "Private vulnerability reporting",
            "GitHub Discussions",
        ),
    }

    for relative, markers in required_text.items():
        path = root / relative
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{relative}: cannot read file: {exc}")
            continue
        for required in markers:
            if required not in text:
                errors.append(f"{relative}: missing governance marker {required!r}")

    ci = root / ".github" / "workflows" / "ci.yml"
    if ci.is_file():
        text = ci.read_text(encoding="utf-8")
        for marker in ('quality:', 'package:', '- "3.10"', '- "3.12"', '- "3.14"'):
            if marker not in text:
                errors.append(
                    f".github/workflows/ci.yml: governance expects CI marker {marker!r}"
                )

    return errors


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
    if (root / "agents" / "openai.yaml").exists():
        errors.extend(validate_openai_metadata(root))
    if (root / ".claude-plugin" / "plugin.json").exists():
        errors.extend(validate_claude_plugin(root))
    errors.extend(validate_governance(root))
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
