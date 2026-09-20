#!/usr/bin/env python3
"""Run executable behavioral evaluations against an external coding-agent adapter."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import package_skill

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "evals" / "cases.json"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CASE_KEYS = {"id", "task", "must_do", "must_not_do", "fixture", "checks"}
FIXTURE_KEYS = {"files"}
CHECK_KEYS = {
    "type",
    "paths",
    "path",
    "text",
    "terms",
    "argv",
    "repeat",
    "exit_code",
}
SUPPORTED_CHECKS = {
    "changed_files_include",
    "changed_files_subset",
    "command",
    "file_absent",
    "file_contains",
    "file_exists",
    "file_not_contains",
    "file_unchanged",
    "final_contains_all",
    "final_contains_any",
    "final_not_contains_any",
}


def load_cases(path: Path = DEFAULT_CASES) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("evaluation cases must be a JSON array")
    return data


def _safe_relative(path: str) -> bool:
    candidate = Path(path)
    return bool(path) and not candidate.is_absolute() and ".." not in candidate.parts


def validate_cases(cases: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()

    for index, case in enumerate(cases):
        label = f"case[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{label}: expected object")
            continue

        extra_case_keys = sorted(set(case) - CASE_KEYS)
        if extra_case_keys:
            errors.append(f"{label}: unsupported keys: {', '.join(extra_case_keys)}")

        case_id = case.get("id")
        if not isinstance(case_id, str) or not NAME_RE.fullmatch(case_id):
            errors.append(f"{label}: id must use lowercase kebab-case")
        elif case_id in seen:
            errors.append(f"{label}: duplicate id {case_id}")
        else:
            seen.add(case_id)
            label = case_id

        for key in ("task", "must_do", "must_not_do", "fixture", "checks"):
            if key not in case:
                errors.append(f"{label}: missing {key}")

        task = case.get("task")
        if not isinstance(task, str) or not task.strip():
            errors.append(f"{label}: task must be a non-empty string")

        for key in ("must_do", "must_not_do"):
            value = case.get(key)
            if not isinstance(value, list) or not value or not all(
                isinstance(item, str) and item.strip() for item in value
            ):
                errors.append(f"{label}: {key} must be a non-empty string list")

        fixture = case.get("fixture")
        if not isinstance(fixture, dict):
            errors.append(f"{label}: fixture must be an object")
        else:
            extra_fixture_keys = sorted(set(fixture) - FIXTURE_KEYS)
            if extra_fixture_keys:
                errors.append(
                    f"{label}: unsupported fixture keys: {', '.join(extra_fixture_keys)}"
                )
            files = fixture.get("files")
            if not isinstance(files, dict) or not files:
                errors.append(f"{label}: fixture.files must be a non-empty object")
            else:
                for path, content in files.items():
                    if not isinstance(path, str) or not _safe_relative(path):
                        errors.append(f"{label}: unsafe fixture path {path!r}")
                    if not isinstance(content, str):
                        errors.append(f"{label}: fixture file {path!r} must be text")

        checks = case.get("checks")
        if not isinstance(checks, list) or not checks:
            errors.append(f"{label}: checks must be a non-empty list")
            continue

        for check_index, check in enumerate(checks):
            check_label = f"{label}.checks[{check_index}]"
            if not isinstance(check, dict):
                errors.append(f"{check_label}: expected object")
                continue
            extra_check_keys = sorted(set(check) - CHECK_KEYS)
            if extra_check_keys:
                errors.append(
                    f"{check_label}: unsupported keys: {', '.join(extra_check_keys)}"
                )

            check_type = check.get("type")
            if check_type not in SUPPORTED_CHECKS:
                errors.append(f"{check_label}: unsupported check type {check_type!r}")
                continue

            if check_type == "command":
                argv = check.get("argv")
                if not isinstance(argv, list) or not argv or not all(
                    isinstance(item, str) and item for item in argv
                ):
                    errors.append(f"{check_label}: command argv must be a non-empty string list")
                repeat = check.get("repeat", 1)
                if not isinstance(repeat, int) or repeat < 1 or repeat > 20:
                    errors.append(f"{check_label}: repeat must be between 1 and 20")
            elif check_type in {"changed_files_include", "changed_files_subset"}:
                paths = check.get("paths")
                if not isinstance(paths, list) or not all(
                    isinstance(item, str) and _safe_relative(item) for item in paths
                ):
                    errors.append(f"{check_label}: paths must be safe relative paths")
            elif check_type in {
                "file_absent",
                "file_exists",
                "file_unchanged",
            }:
                path = check.get("path")
                if not isinstance(path, str) or not _safe_relative(path):
                    errors.append(f"{check_label}: path must be a safe relative path")
            elif check_type in {"file_contains", "file_not_contains"}:
                path = check.get("path")
                text = check.get("text")
                if not isinstance(path, str) or not _safe_relative(path):
                    errors.append(f"{check_label}: path must be a safe relative path")
                if not isinstance(text, str) or not text:
                    errors.append(f"{check_label}: text must be non-empty")
            elif check_type in {
                "final_contains_all",
                "final_contains_any",
                "final_not_contains_any",
            }:
                terms = check.get("terms")
                if not isinstance(terms, list) or not terms or not all(
                    isinstance(item, str) and item for item in terms
                ):
                    errors.append(f"{check_label}: terms must be a non-empty string list")

    return errors


def materialize_fixture(case: dict[str, Any], workspace: Path) -> None:
    for relative, content in case["fixture"]["files"].items():
        path = workspace / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def stage_skill_runtime(source_root: Path, target: Path) -> Path:
    source_root = source_root.resolve()
    target.mkdir(parents=True, exist_ok=True)
    for source in package_skill.payload_files(source_root):
        relative = source.relative_to(source_root)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
    return target / "SKILL.md"


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_workspace(workspace: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in sorted(workspace.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        relative = path.relative_to(workspace).as_posix()
        snapshot[relative] = _file_digest(path)
    return snapshot


def changed_files(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(
        path
        for path in set(before) | set(after)
        if before.get(path) != after.get(path)
    )


def initialize_git(workspace: Path) -> None:
    commands = (
        ("git", "init", "-q"),
        ("git", "config", "user.email", "eval@example.invalid"),
        ("git", "config", "user.name", "engineering-quality eval"),
        ("git", "add", "."),
        ("git", "commit", "-qm", "baseline"),
    )
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=workspace,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"failed to initialize evaluation git repository: {shlex.join(command)}\n"
                f"{completed.stderr.strip()}"
            )


def _format_agent_command(
    raw: str,
    *,
    case: dict[str, Any],
    workspace: Path,
    skill: Path,
) -> list[str]:
    tokens = shlex.split(raw)
    replacements = {
        "case_id": case["id"],
        "task": case["task"],
        "workspace": str(workspace),
        "skill": str(skill),
    }
    formatted: list[str] = []
    for token in tokens:
        for key, value in replacements.items():
            token = token.replace("{" + key + "}", value)
        formatted.append(token)
    return formatted


def run_agent(
    command: str,
    *,
    case: dict[str, Any],
    workspace: Path,
    skill: Path,
    timeout: int,
) -> dict[str, Any]:
    argv = _format_agent_command(command, case=case, workspace=workspace, skill=skill)
    env = os.environ.copy()
    env.update(
        {
            "EQ_EVAL_CASE_ID": case["id"],
            "EQ_EVAL_TASK": case["task"],
            "EQ_EVAL_WORKSPACE": str(workspace),
            "EQ_EVAL_SKILL_PATH": str(skill),
        }
    )
    try:
        completed = subprocess.run(
            argv,
            cwd=workspace,
            env=env,
            check=False,
            timeout=timeout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return {
            "adapter": Path(argv[0]).name if argv else "",
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "adapter": Path(argv[0]).name if argv else "",
            "exit_code": 124,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timed_out": True,
        }


def _resolve_argv(argv: list[str]) -> list[str]:
    return [sys.executable if item == "{python}" else item for item in argv]


def _read_optional(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None


def _check_environment() -> dict[str, str]:
    allowed = (
        "HOME",
        "LANG",
        "LC_ALL",
        "PATH",
        "SYSTEMROOT",
        "TEMP",
        "TMP",
        "TMPDIR",
        "WINDIR",
    )
    return {key: os.environ[key] for key in allowed if key in os.environ}


def evaluate_check(
    check: dict[str, Any],
    *,
    workspace: Path,
    before: dict[str, str],
    after: dict[str, str],
    final_output: str,
    allow_workspace_execution: bool,
    command_timeout: int,
) -> dict[str, Any]:
    check_type = check["type"]
    result: dict[str, Any] = {"type": check_type, "status": "failed"}

    if check_type == "changed_files_include":
        changed = set(changed_files(before, after))
        required = set(check["paths"])
        missing = sorted(required - changed)
        result.update(
            {
                "status": "passed" if not missing else "failed",
                "changed_files": sorted(changed),
                "missing": missing,
            }
        )
        return result

    if check_type == "changed_files_subset":
        changed = set(changed_files(before, after))
        allowed = set(check["paths"])
        unexpected = sorted(changed - allowed)
        result.update(
            {
                "status": "passed" if not unexpected else "failed",
                "changed_files": sorted(changed),
                "unexpected": unexpected,
            }
        )
        return result

    if check_type == "file_exists":
        exists = (workspace / check["path"]).is_file()
        result.update({"status": "passed" if exists else "failed", "path": check["path"]})
        return result

    if check_type == "file_absent":
        absent = not (workspace / check["path"]).exists()
        result.update({"status": "passed" if absent else "failed", "path": check["path"]})
        return result

    if check_type == "file_unchanged":
        path = check["path"]
        unchanged = before.get(path) == after.get(path) and path in before
        result.update({"status": "passed" if unchanged else "failed", "path": path})
        return result

    if check_type in {"file_contains", "file_not_contains"}:
        path = workspace / check["path"]
        content = _read_optional(path)
        expected = check["text"]
        contains = content is not None and expected in content
        passed = contains if check_type == "file_contains" else not contains
        result.update(
            {
                "status": "passed" if passed else "failed",
                "path": check["path"],
                "text": expected,
            }
        )
        return result

    if check_type in {
        "final_contains_all",
        "final_contains_any",
        "final_not_contains_any",
    }:
        haystack = final_output.casefold()
        terms = [term.casefold() for term in check["terms"]]
        matches = [term for term in terms if term in haystack]
        if check_type == "final_contains_all":
            passed = len(matches) == len(terms)
        elif check_type == "final_contains_any":
            passed = bool(matches)
        else:
            passed = not matches
        result.update(
            {
                "status": "passed" if passed else "failed",
                "terms": check["terms"],
                "matched": matches,
            }
        )
        return result

    if check_type == "command":
        if not allow_workspace_execution:
            result.update(
                {
                    "status": "not_run",
                    "reason": (
                        "workspace execution disabled; rerun with "
                        "--allow-workspace-execution after accepting the risk of "
                        "executing agent-modified code"
                    ),
                }
            )
            return result

        argv = _resolve_argv(check["argv"])
        repeat = check.get("repeat", 1)
        expected_exit = check.get("exit_code", 0)
        executions: list[dict[str, Any]] = []
        passed = True
        for _ in range(repeat):
            try:
                completed = subprocess.run(
                    argv,
                    cwd=workspace,
                    check=False,
                    timeout=command_timeout,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=_check_environment(),
                )
                execution = {
                    "exit_code": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                }
                if completed.returncode != expected_exit:
                    passed = False
            except subprocess.TimeoutExpired as exc:
                execution = {
                    "exit_code": 124,
                    "stdout": exc.stdout or "",
                    "stderr": exc.stderr or "",
                    "timed_out": True,
                }
                passed = False
            executions.append(execution)
        result.update(
            {
                "status": "passed" if passed else "failed",
                "argv": argv,
                "expected_exit_code": expected_exit,
                "executions": executions,
            }
        )
        return result

    raise AssertionError(f"unhandled check type: {check_type}")


def evaluate_case(
    case: dict[str, Any],
    *,
    agent_command: str,
    skill: Path,
    agent_timeout: int,
    check_timeout: int,
    allow_workspace_execution: bool,
    keep_workspace: bool,
    workspace_parent: Path | None,
) -> dict[str, Any]:
    if keep_workspace:
        workspace = Path(
            tempfile.mkdtemp(
                prefix=f"engineering-quality-{case['id']}-",
                dir=workspace_parent,
            )
        )
        cleanup = lambda: None
    else:
        temp = tempfile.TemporaryDirectory(
            prefix=f"engineering-quality-{case['id']}-",
            dir=workspace_parent,
        )
        workspace = Path(temp.name)
        cleanup = temp.cleanup

    try:
        materialize_fixture(case, workspace)
        initialize_git(workspace)
        before = snapshot_workspace(workspace)

        agent = run_agent(
            agent_command,
            case=case,
            workspace=workspace,
            skill=skill,
            timeout=agent_timeout,
        )
        after = snapshot_workspace(workspace)
        final_output = f"{agent['stdout']}\n{agent['stderr']}".strip()

        checks = [
            evaluate_check(
                check,
                workspace=workspace,
                before=before,
                after=after,
                final_output=final_output,
                allow_workspace_execution=allow_workspace_execution,
                command_timeout=check_timeout,
            )
            for check in case["checks"]
        ]

        statuses = {check["status"] for check in checks}
        if agent["exit_code"] != 0 or "failed" in statuses:
            status = "failed"
        elif "not_run" in statuses:
            status = "incomplete"
        else:
            status = "passed"

        result = {
            "id": case["id"],
            "status": status,
            "task": case["task"],
            "agent": agent,
            "changed_files": changed_files(before, after),
            "checks": checks,
            "rubric": {
                "must_do": case["must_do"],
                "must_not_do": case["must_not_do"],
                "note": (
                    "Rubric text is retained for human/LLM review and is not automatically "
                    "counted as passed unless represented by deterministic checks."
                ),
            },
        }

        if keep_workspace:
            result["workspace"] = str(workspace)

        return result
    finally:
        cleanup()


def build_report(
    results: list[dict[str, Any]],
    *,
    adapter_label: str,
    allow_workspace_execution: bool,
) -> dict[str, Any]:
    statuses = [result["status"] for result in results]
    if "failed" in statuses:
        status = "failed"
    elif "incomplete" in statuses:
        status = "incomplete"
    else:
        status = "passed"

    return {
        "schema_version": 1,
        "status": status,
        "evidence_scope": {
            "harness": "executed",
            "agent_behavior": "executed",
            "deterministic_checks": (
                "executed" if allow_workspace_execution else "partial"
            ),
            "qualitative_rubric": "not automatically judged",
        },
        "adapter": adapter_label,
        "cases": results,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run behavioral eval fixtures against an external agent command. "
            "The command executes in a temporary git repository."
        )
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES,
        help="evaluation case file",
    )
    parser.add_argument(
        "--case",
        action="append",
        help="run only the named case; repeat to select multiple cases",
    )
    parser.add_argument(
        "--agent-command",
        help=(
            "adapter command; placeholders: {task}, {workspace}, {skill}, {case_id}. "
            "The same values are also exported as EQ_EVAL_* environment variables. "
            "Do not put secrets in command arguments"
        ),
    )
    parser.add_argument(
        "--adapter-label",
        default="external-agent",
        help="non-sensitive adapter/model label stored in the report",
    )
    parser.add_argument(
        "--skill-root",
        type=Path,
        default=ROOT,
        help=(
            "source repository used to stage the runtime skill payload; evals and tests "
            "are excluded using the distribution package contract"
        ),
    )
    parser.add_argument("--output", type=Path, help="write machine-readable JSON report")
    parser.add_argument("--agent-timeout", type=int, default=900)
    parser.add_argument("--check-timeout", type=int, default=120)
    parser.add_argument(
        "--allow-workspace-execution",
        action="store_true",
        help=(
            "allow deterministic command checks to execute agent-modified workspace code; "
            "use only after accepting that execution risk"
        ),
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="validate fixtures and checks without invoking an agent",
    )
    parser.add_argument(
        "--keep-workspaces",
        action="store_true",
        help="preserve temporary workspaces for debugging",
    )
    parser.add_argument(
        "--workspace-parent",
        type=Path,
        help="parent directory for temporary evaluation workspaces",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.agent_timeout <= 0 or args.check_timeout <= 0:
        parser.error("timeouts must be positive")

    try:
        cases = load_cases(args.cases)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))

    errors = validate_cases(cases)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if args.case:
        selected = set(args.case)
        known = {case["id"] for case in cases}
        unknown = sorted(selected - known)
        if unknown:
            parser.error(f"unknown cases: {', '.join(unknown)}")
        cases = [case for case in cases if case["id"] in selected]

    if args.validate_only:
        print(f"Validated {len(cases)} executable evaluation cases.")
        return 0

    if not args.agent_command:
        parser.error("--agent-command is required unless --validate-only is used")

    if args.workspace_parent:
        args.workspace_parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="engineering-quality-skill-") as skill_temp:
        staged_skill = stage_skill_runtime(args.skill_root, Path(skill_temp))
        results = [
            evaluate_case(
                case,
                agent_command=args.agent_command,
                skill=staged_skill,
                agent_timeout=args.agent_timeout,
                check_timeout=args.check_timeout,
                allow_workspace_execution=args.allow_workspace_execution,
                keep_workspace=args.keep_workspaces,
                workspace_parent=args.workspace_parent,
            )
            for case in cases
        ]

    report = build_report(
        results,
        adapter_label=args.adapter_label,
        allow_workspace_execution=args.allow_workspace_execution,
    )

    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)

    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
