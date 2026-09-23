#!/usr/bin/env python3
"""Run paired no-Skill and Skill behavioral evaluations."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import compare_eval_results
import run_evals


def _select_cases(
    cases: list[dict[str, Any]],
    selected_ids: list[str] | None,
) -> list[dict[str, Any]]:
    if not selected_ids:
        return cases
    selected = set(selected_ids)
    known = {case["id"] for case in cases}
    unknown = sorted(selected - known)
    if unknown:
        raise ValueError(f"unknown cases: {', '.join(unknown)}")
    return [case for case in cases if case["id"] in selected]


def _condition_order(run_index: int, case_index: int) -> tuple[str, str]:
    if (run_index + case_index) % 2:
        return ("baseline", "skill")
    return ("skill", "baseline")


def run_experiment(
    cases: list[dict[str, Any]],
    *,
    baseline_agent_command: str,
    skill_agent_command: str,
    baseline_label: str,
    skill_label: str,
    repeat: int,
    skill_root: Path,
    agent_timeout: int,
    check_timeout: int,
    allow_workspace_execution: bool,
    keep_workspaces: bool,
    workspace_parent: Path | None,
    pass_env: tuple[str, ...] = (),
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if repeat < 1:
        raise ValueError("repeat must be positive")

    baseline_results: list[dict[str, Any]] = []
    skill_results: list[dict[str, Any]] = []
    execution_order: list[dict[str, Any]] = []

    commands = {
        "baseline": baseline_agent_command,
        "skill": skill_agent_command,
    }
    result_lists = {
        "baseline": baseline_results,
        "skill": skill_results,
    }

    for run_index in range(1, repeat + 1):
        for case_index, case in enumerate(cases):
            order = _condition_order(run_index, case_index)
            execution_order.append(
                {
                    "id": case["id"],
                    "run_index": run_index,
                    "order": list(order),
                }
            )
            for condition in order:
                result = run_evals.evaluate_case(
                    case,
                    agent_command=commands[condition],
                    skill_root=skill_root,
                    agent_timeout=agent_timeout,
                    check_timeout=check_timeout,
                    allow_workspace_execution=allow_workspace_execution,
                    keep_workspace=keep_workspaces,
                    workspace_parent=workspace_parent,
                    pass_env=pass_env,
                    run_index=run_index,
                )
                result_lists[condition].append(result)

    baseline_report = run_evals.build_report(
        baseline_results,
        adapter_label=baseline_label,
        allow_workspace_execution=allow_workspace_execution,
        forwarded_environment=pass_env,
    )
    skill_report = run_evals.build_report(
        skill_results,
        adapter_label=skill_label,
        allow_workspace_execution=allow_workspace_execution,
        forwarded_environment=pass_env,
    )
    manifest = {
        "schema_version": 1,
        "design": "paired-counterbalanced",
        "repeat": repeat,
        "baseline_adapter": baseline_label,
        "skill_adapter": skill_label,
        "execution_order": execution_order,
    }
    return baseline_report, skill_report, manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run paired baseline and Skill-enabled evaluations with counterbalanced "
            "condition order."
        )
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=run_evals.DEFAULT_CASES,
        help="evaluation case file",
    )
    parser.add_argument(
        "--case",
        action="append",
        help="run only the named case; repeat to select multiple cases",
    )
    parser.add_argument("--baseline-agent-command", required=True)
    parser.add_argument("--skill-agent-command", required=True)
    parser.add_argument("--baseline-label", default="no-skill")
    parser.add_argument("--skill-label", default="skill")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument(
        "--skill-root",
        type=Path,
        default=run_evals.ROOT,
        help="source repository used to stage the runtime Skill payload",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--agent-timeout", type=int, default=900)
    parser.add_argument("--check-timeout", type=int, default=120)
    parser.add_argument(
        "--pass-env",
        action="append",
        default=[],
        metavar="NAME",
        help="forward one named environment variable to both agent conditions",
    )
    parser.add_argument("--allow-workspace-execution", action="store_true")
    parser.add_argument("--keep-workspaces", action="store_true")
    parser.add_argument("--workspace-parent", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    if args.repeat < 1 or args.repeat > 100:
        parser.error("--repeat must be between 1 and 100")
    if args.agent_timeout <= 0 or args.check_timeout <= 0:
        parser.error("timeouts must be positive")

    invalid_env_names = [
        name for name in args.pass_env if not run_evals.ENV_NAME_RE.fullmatch(name)
    ]
    if invalid_env_names:
        parser.error(
            "invalid --pass-env names: " + ", ".join(sorted(set(invalid_env_names)))
        )

    missing_env_names = [name for name in args.pass_env if name not in os.environ]
    if missing_env_names:
        parser.error(
            "--pass-env variables are not set: "
            + ", ".join(sorted(set(missing_env_names)))
        )

    try:
        cases = run_evals.load_cases(args.cases)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))

    errors = run_evals.validate_cases(cases)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    try:
        cases = _select_cases(cases, args.case)
    except ValueError as exc:
        parser.error(str(exc))

    if args.workspace_parent:
        args.workspace_parent.mkdir(parents=True, exist_ok=True)

    baseline_report, skill_report, manifest = run_experiment(
        cases,
        baseline_agent_command=args.baseline_agent_command,
        skill_agent_command=args.skill_agent_command,
        baseline_label=args.baseline_label,
        skill_label=args.skill_label,
        repeat=args.repeat,
        skill_root=args.skill_root,
        agent_timeout=args.agent_timeout,
        check_timeout=args.check_timeout,
        allow_workspace_execution=args.allow_workspace_execution,
        keep_workspaces=args.keep_workspaces,
        workspace_parent=args.workspace_parent,
        pass_env=tuple(args.pass_env),
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    baseline_path = args.output_dir / "baseline.json"
    skill_path = args.output_dir / "skill.json"
    manifest_path = args.output_dir / "experiment.json"
    comparison_path = args.output_dir / "comparison.md"

    baseline_path.write_text(
        json.dumps(baseline_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    skill_path.write_text(
        json.dumps(skill_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    comparison_path.write_text(
        compare_eval_results.compare_reports(baseline_report, skill_report) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote paired A/B evidence to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
