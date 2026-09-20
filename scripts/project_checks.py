#!/usr/bin/env python3
"""Discover project quality checks without installing dependencies."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Check:
    category: str
    source: str
    command: tuple[str, ...]

    def display(self) -> str:
        return shlex.join(self.command)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["command"] = list(self.command)
        return data


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return ""


def _read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _dedupe(checks: Iterable[Check]) -> list[Check]:
    seen: set[tuple[str, ...]] = set()
    result: list[Check] = []
    for check in checks:
        if check.command in seen:
            continue
        seen.add(check.command)
        result.append(check)
    return result


def _make_checks(root: Path) -> list[Check]:
    makefile = next((path for path in (root / "Makefile", root / "makefile") if path.exists()), None)
    if makefile is None:
        return []

    text = _read_text(makefile)
    targets = set(
        match.group(1)
        for match in re.finditer(r"(?m)^([A-Za-z0-9_.-]+)\s*:(?!=)", text)
    )

    mapping = (
        ("check", "verify"),
        ("verify", "verify"),
        ("lint", "lint"),
        ("typecheck", "types"),
        ("test", "test"),
    )
    return [
        Check(category, makefile.name, ("make", target))
        for target, category in mapping
        if target in targets
    ]


def _package_manager(root: Path, package: dict[str, object]) -> str:
    declared = package.get("packageManager")
    if isinstance(declared, str):
        name = declared.split("@", 1)[0]
        if name in {"npm", "pnpm", "yarn", "bun"}:
            return name

    for filename, name in (
        ("pnpm-lock.yaml", "pnpm"),
        ("yarn.lock", "yarn"),
        ("bun.lockb", "bun"),
        ("bun.lock", "bun"),
        ("package-lock.json", "npm"),
        ("npm-shrinkwrap.json", "npm"),
    ):
        if (root / filename).exists():
            return name
    return "npm"


def _node_checks(root: Path) -> list[Check]:
    package_path = root / "package.json"
    if not package_path.exists():
        return []

    package = _read_json(package_path)
    scripts = package.get("scripts")
    if not isinstance(scripts, dict):
        return []

    manager = _package_manager(root, package)
    mapping = (
        ("format:check", "format"),
        ("fmt:check", "format"),
        ("check:format", "format"),
        ("lint", "lint"),
        ("typecheck", "types"),
        ("type-check", "types"),
        ("check:types", "types"),
        ("test", "test"),
        ("test:unit", "test"),
        ("build", "build"),
        ("check", "verify"),
        ("verify", "verify"),
    )

    checks: list[Check] = []
    for script, category in mapping:
        if script in scripts:
            checks.append(Check(category, "package.json", (manager, "run", script)))
    return checks


def _python_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    pyproject = root / "pyproject.toml"
    text = _read_text(pyproject) if pyproject.exists() else ""
    python = sys.executable

    if "[tool.ruff" in text:
        checks.append(Check("lint", "pyproject.toml", (python, "-m", "ruff", "check", ".")))
    if "[tool.black]" in text:
        checks.append(Check("format", "pyproject.toml", (python, "-m", "black", "--check", ".")))
    if "[tool.mypy" in text:
        checks.append(Check("types", "pyproject.toml", (python, "-m", "mypy", ".")))
    if "[tool.pytest.ini_options]" in text or (root / "pytest.ini").exists():
        checks.append(Check("test", "pytest configuration", (python, "-m", "pytest")))
    if (root / "pyrightconfig.json").exists():
        checks.append(Check("types", "pyrightconfig.json", ("pyright",)))
    if (root / "tox.ini").exists():
        checks.append(Check("verify", "tox.ini", ("tox", "-q")))
    if (root / "noxfile.py").exists():
        checks.append(Check("verify", "noxfile.py", ("nox",)))
    return checks


def _go_checks(root: Path) -> list[Check]:
    if not (root / "go.mod").exists():
        return []
    return [
        Check("lint", "go.mod", ("go", "vet", "./...")),
        Check("test", "go.mod", ("go", "test", "./...")),
    ]


def _rust_checks(root: Path) -> list[Check]:
    if not (root / "Cargo.toml").exists():
        return []
    return [
        Check("format", "Cargo.toml", ("cargo", "fmt", "--", "--check")),
        Check(
            "lint",
            "Cargo.toml",
            ("cargo", "clippy", "--all-targets", "--all-features", "--", "-D", "warnings"),
        ),
        Check("test", "Cargo.toml", ("cargo", "test", "--all-features")),
    ]


def _java_checks(root: Path) -> list[Check]:
    if (root / "gradlew").exists():
        command = ("gradlew.bat", "check") if os.name == "nt" else ("./gradlew", "check")
        return [Check("verify", "Gradle wrapper", command)]
    if (root / "mvnw").exists():
        command = ("mvnw.cmd", "verify") if os.name == "nt" else ("./mvnw", "verify")
        return [Check("verify", "Maven wrapper", command)]
    if (root / "build.gradle").exists() or (root / "build.gradle.kts").exists():
        return [Check("verify", "Gradle build", ("gradle", "check"))]
    if (root / "pom.xml").exists():
        return [Check("verify", "Maven build", ("mvn", "verify"))]
    return []


def _dotnet_checks(root: Path) -> list[Check]:
    if any(root.glob("*.sln")) or any(root.glob("*.csproj")) or any(root.glob("*.fsproj")):
        return [Check("test", ".NET project", ("dotnet", "test"))]
    return []


def _swift_checks(root: Path) -> list[Check]:
    if (root / "Package.swift").exists():
        return [Check("test", "Package.swift", ("swift", "test"))]
    return []


def _dart_checks(root: Path) -> list[Check]:
    pubspec = root / "pubspec.yaml"
    if not pubspec.exists():
        return []
    text = _read_text(pubspec)
    tool = "flutter" if re.search(r"(?m)^\s*flutter\s*:", text) else "dart"
    return [
        Check("lint", "pubspec.yaml", (tool, "analyze")),
        Check("test", "pubspec.yaml", (tool, "test")),
    ]


def discover_checks(root: Path) -> list[Check]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"not a directory: {root}")

    checks: list[Check] = []
    for detector in (
        _make_checks,
        _node_checks,
        _python_checks,
        _go_checks,
        _rust_checks,
        _java_checks,
        _dotnet_checks,
        _swift_checks,
        _dart_checks,
    ):
        checks.extend(detector(root))
    return _dedupe(checks)


def run_checks(
    root: Path,
    checks: list[Check],
    timeout: int,
    *,
    trust_repository: bool = False,
) -> int:
    if not trust_repository:
        raise PermissionError(
            "refusing to execute repository checks without explicit repository trust"
        )

    print(
        "WARNING: executing repository-controlled checks from a repository you explicitly "
        "marked as trusted. These commands may run arbitrary code, access inherited "
        "environment variables, files, and network resources, and cause side effects.",
        file=sys.stderr,
    )

    failed = False
    for check in checks:
        print(f"\n[{check.category}] {check.source}")
        print(f"$ {check.display()}")
        try:
            completed = subprocess.run(
                check.command,
                cwd=root,
                check=False,
                timeout=timeout,
            )
            code = completed.returncode
        except FileNotFoundError:
            code = 127
            print(f"command not found: {check.command[0]}", file=sys.stderr)
        except subprocess.TimeoutExpired:
            code = 124
            print(f"timed out after {timeout}s", file=sys.stderr)

        if code != 0:
            failed = True
            print(f"failed with exit code {code}", file=sys.stderr)
    return 1 if failed else 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Discover quality-check candidates from repository configuration."
    )
    parser.add_argument("path", nargs="?", default=".", help="repository path")
    parser.add_argument(
        "--category",
        action="append",
        choices=("format", "lint", "types", "test", "build", "verify"),
        help="limit output or execution to one or more categories",
    )
    parser.add_argument("--json", action="store_true", help="print discovered checks as JSON")
    parser.add_argument(
        "--run",
        action="store_true",
        help="execute discovered checks; requires --trust-repository",
    )
    parser.add_argument(
        "--trust-repository",
        action="store_true",
        help=(
            "acknowledge that repository-defined checks may execute arbitrary "
            "repository-controlled code"
        ),
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1200,
        help="per-check timeout in seconds when --run is supplied",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.json and args.run:
        parser.error("--json and --run cannot be combined")
    if args.trust_repository and not args.run:
        parser.error("--trust-repository requires --run")
    if args.run and not args.trust_repository:
        parser.error(
            "--run requires --trust-repository because discovered checks may execute "
            "repository-controlled code"
        )
    if args.timeout <= 0:
        parser.error("--timeout must be positive")

    root = Path(args.path)
    try:
        checks = discover_checks(root)
    except ValueError as exc:
        parser.error(str(exc))

    if args.category:
        categories = set(args.category)
        checks = [check for check in checks if check.category in categories]

    if args.json:
        print(json.dumps([check.to_dict() for check in checks], indent=2))
        return 0

    if not checks:
        print("No candidate checks discovered.")
        return 0

    if not args.run:
        for check in checks:
            print(f"[{check.category}] {check.source}: {check.display()}")
        print(
            "\nDiscovery only: no commands were executed. Command names are not a safety "
            "boundary; execute only after establishing trust in the repository."
        )
        return 0

    return run_checks(
        root.resolve(),
        checks,
        args.timeout,
        trust_repository=args.trust_repository,
    )


if __name__ == "__main__":
    raise SystemExit(main())
