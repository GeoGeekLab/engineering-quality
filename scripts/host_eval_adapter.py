#!/usr/bin/env python3
"""Native Codex and Claude Code adapters for executable behavioral evaluations."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASE_PROCESS_ENV = (
    "LANG",
    "LC_ALL",
    "PATH",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "TMPDIR",
    "WINDIR",
)


def _adapter_environment() -> dict[str, str]:
    env = {
        key: os.environ[key]
        for key in BASE_PROCESS_ENV
        if key in os.environ
    }
    forwarded = os.environ.get("EQ_EVAL_PASSED_ENV", "")
    for name in forwarded.split(","):
        name = name.strip()
        if name and name in os.environ:
            env[name] = os.environ[name]
    return env


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"missing required evaluation environment variable: {name}")
    return value


def _copy_skill(source_entry: Path, target: Path) -> Path:
    source = source_entry.resolve().parent
    shutil.copytree(source, target)
    return target / "SKILL.md"


def codex_argv(
    executable: str,
    task: str,
    model: str | None = None,
) -> list[str]:
    argv = [
        executable,
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--sandbox",
        "workspace-write",
    ]
    if model:
        argv.extend(("--model", model))
    argv.append(task)
    return argv


def claude_argv(
    executable: str,
    task: str,
    skill_dir: Path,
    model: str | None = None,
) -> list[str]:
    argv = [
        executable,
        "--bare",
        "--permission-mode",
        "auto",
        "--permission-prompts",
        "none",
        "--no-session-persistence",
        "--add-dir",
        str(skill_dir),
    ]
    if model:
        argv.extend(("--model", model))
    argv.extend(("-p", task))
    return argv


def _print_version(executable: str, env: dict[str, str], cwd: Path) -> None:
    try:
        completed = subprocess.run(
            [executable, "--version"],
            cwd=cwd,
            env=env,
            check=False,
            timeout=20,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return

    version = (completed.stdout or completed.stderr).strip()
    if version:
        print(f"[host-adapter] {version}", file=sys.stderr)


def run_codex(
    *,
    executable: str,
    task: str,
    workspace: Path,
    skill_entry: Path,
    model: str | None = None,
) -> int:
    with tempfile.TemporaryDirectory(prefix="engineering-quality-codex-home-") as directory:
        home = Path(directory)
        _copy_skill(
            skill_entry,
            home / ".agents" / "skills" / "engineering-quality",
        )
        env = _adapter_environment()
        env["HOME"] = str(home)
        env["USERPROFILE"] = str(home)
        env["CODEX_HOME"] = str(home / ".codex")
        Path(env["CODEX_HOME"]).mkdir(parents=True, exist_ok=True)

        _print_version(executable, env, workspace)
        try:
            completed = subprocess.run(
                codex_argv(executable, task, model),
                cwd=workspace,
                env=env,
                check=False,
            )
        except FileNotFoundError:
            print(f"Codex executable not found: {executable}", file=sys.stderr)
            return 127
        return completed.returncode


def run_claude_code(
    *,
    executable: str,
    task: str,
    workspace: Path,
    skill_entry: Path,
    model: str | None = None,
) -> int:
    with tempfile.TemporaryDirectory(
        prefix="engineering-quality-claude-home-"
    ) as directory:
        home = Path(directory)
        env = _adapter_environment()
        env["HOME"] = str(home)
        env["USERPROFILE"] = str(home)
        env["CLAUDE_CONFIG_DIR"] = str(home / ".claude")
        Path(env["CLAUDE_CONFIG_DIR"]).mkdir(parents=True, exist_ok=True)

        _print_version(executable, env, workspace)
        try:
            completed = subprocess.run(
                claude_argv(executable, task, skill_entry.resolve().parent, model),
                cwd=workspace,
                env=env,
                check=False,
            )
        except FileNotFoundError:
            print(f"Claude Code executable not found: {executable}", file=sys.stderr)
            return 127
        return completed.returncode


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a behavioral eval case through a native coding-agent CLI."
    )
    parser.add_argument("host", choices=("codex", "claude-code"))
    parser.add_argument(
        "--executable",
        help="override the host executable for controlled testing",
    )
    parser.add_argument(
        "--model",
        help="pin an explicit host model for reproducible behavioral evidence",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    try:
        task = _required_env("EQ_EVAL_TASK")
        workspace = Path(_required_env("EQ_EVAL_WORKSPACE")).resolve()
        skill_entry = Path(_required_env("EQ_EVAL_SKILL_PATH")).resolve()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not workspace.is_dir():
        print(f"evaluation workspace is not a directory: {workspace}", file=sys.stderr)
        return 2
    if not skill_entry.is_file():
        print(f"staged skill entry is not a file: {skill_entry}", file=sys.stderr)
        return 2

    if args.model:
        print(f"[host-adapter] model={args.model}", file=sys.stderr)

    if args.host == "codex":
        executable = args.executable or os.environ.get("EQ_CODEX_BIN", "codex")
        return run_codex(
            executable=executable,
            task=task,
            workspace=workspace,
            skill_entry=skill_entry,
            model=args.model,
        )

    executable = args.executable or os.environ.get("EQ_CLAUDE_BIN", "claude")
    return run_claude_code(
        executable=executable,
        task=task,
        workspace=workspace,
        skill_entry=skill_entry,
        model=args.model,
    )


if __name__ == "__main__":
    raise SystemExit(main())
