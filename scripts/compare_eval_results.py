#!/usr/bin/env python3
"""Compare no-Skill and Skill behavioral-evaluation reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

INFRASTRUCTURE_CHECKS = {"skill_payload_integrity"}


def load_report(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: report must be a JSON object")
    cases = data.get("cases")
    if not isinstance(cases, list):
        raise ValueError(f"{path}: report.cases must be an array")
    return data


def _group_cases(report: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for index, case in enumerate(report["cases"]):
        if not isinstance(case, dict):
            raise ValueError(f"case[{index}] must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError(f"case[{index}].id must be a non-empty string")
        grouped.setdefault(case_id, []).append(case)

    for runs in grouped.values():
        runs.sort(key=lambda item: item.get("run_index", 1))
    return grouped


def _task_for(runs: list[dict[str, Any]], *, case_id: str) -> str:
    tasks = {run.get("task") for run in runs}
    if len(tasks) != 1 or not all(isinstance(task, str) for task in tasks):
        raise ValueError(f"{case_id}: runs do not share one task")
    return next(iter(tasks))


def _passed_count(runs: list[dict[str, Any]]) -> int:
    return sum(run.get("status") == "passed" for run in runs)


def _rate(passed: int, total: int) -> float:
    return passed / total if total else 0.0


def _format_rate(passed: int, total: int) -> str:
    return f"{passed}/{total} ({_rate(passed, total):.0%})"


def _mean_changed_files(runs: list[dict[str, Any]]) -> float:
    counts = [
        len(run.get("changed_files", []))
        for run in runs
        if isinstance(run.get("changed_files"), list)
    ]
    return sum(counts) / len(counts) if counts else 0.0


def _mean_duration(runs: list[dict[str, Any]]) -> float | None:
    values: list[float] = []
    for run in runs:
        agent = run.get("agent")
        if not isinstance(agent, dict):
            continue
        duration = agent.get("duration_seconds")
        if isinstance(duration, (int, float)) and duration >= 0:
            values.append(float(duration))
    return sum(values) / len(values) if values else None


def _format_duration(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}s"


def _format_delta(baseline: float, skill: float) -> str:
    return f"{(skill - baseline) * 100:+.0f} pp"


def _check_rates(
    grouped: dict[str, list[dict[str, Any]]],
) -> dict[str, tuple[int, int]]:
    totals: dict[str, list[int]] = {}
    for runs in grouped.values():
        for run in runs:
            checks = run.get("checks")
            if not isinstance(checks, list):
                continue
            for check in checks:
                if not isinstance(check, dict):
                    continue
                check_type = check.get("type")
                if (
                    not isinstance(check_type, str)
                    or check_type in INFRASTRUCTURE_CHECKS
                ):
                    continue
                pair = totals.setdefault(check_type, [0, 0])
                pair[1] += 1
                if check.get("status") == "passed":
                    pair[0] += 1
    return {key: (value[0], value[1]) for key, value in totals.items()}


def _summary_row(label: str, runs: list[dict[str, Any]]) -> str:
    passed = _passed_count(runs)
    duration = _mean_duration(runs)
    return (
        f"| {label} | {len(runs)} | {_format_rate(passed, len(runs))} | "
        f"{_mean_changed_files(runs):.2f} | {_format_duration(duration)} |"
    )


def compare_reports(
    baseline: dict[str, Any],
    skill: dict[str, Any],
) -> str:
    baseline_grouped = _group_cases(baseline)
    skill_grouped = _group_cases(skill)

    baseline_ids = set(baseline_grouped)
    skill_ids = set(skill_grouped)
    if baseline_ids != skill_ids:
        missing_from_skill = sorted(baseline_ids - skill_ids)
        missing_from_baseline = sorted(skill_ids - baseline_ids)
        raise ValueError(
            "case sets differ; "
            f"missing from Skill={missing_from_skill}, "
            f"missing from baseline={missing_from_baseline}"
        )

    for case_id in sorted(baseline_ids):
        baseline_task = _task_for(baseline_grouped[case_id], case_id=case_id)
        skill_task = _task_for(skill_grouped[case_id], case_id=case_id)
        if baseline_task != skill_task:
            raise ValueError(f"{case_id}: baseline and Skill tasks differ")

    baseline_runs = [
        run for case_id in sorted(baseline_grouped) for run in baseline_grouped[case_id]
    ]
    skill_runs = [
        run for case_id in sorted(skill_grouped) for run in skill_grouped[case_id]
    ]

    baseline_adapter = baseline.get("adapter", "unknown")
    skill_adapter = skill.get("adapter", "unknown")
    lines = [
        "# Skill A/B evaluation comparison",
        "",
        f"Baseline adapter: `{baseline_adapter}`  ",
        f"Skill adapter: `{skill_adapter}`",
        "",
        (
            "This comparison reports deterministic case outcomes, diff scope, and agent "
            "wall-clock time. Qualitative `must_do` / `must_not_do` rubric items remain "
            "manual review evidence and are not converted into an automatic score."
        ),
        "",
        "## Summary",
        "",
        "| Condition | Runs | Deterministic case pass rate | Mean changed files | Mean agent time |",
        "| --- | ---: | ---: | ---: | ---: |",
        _summary_row("No Skill", baseline_runs),
        _summary_row("Skill", skill_runs),
        "",
        "## Case-by-case",
        "",
        "| Case | No Skill | Skill | Pass-rate delta | Mean changed files (No Skill → Skill) | Mean agent time (No Skill → Skill) |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    for case_id in sorted(baseline_grouped):
        baseline_case = baseline_grouped[case_id]
        skill_case = skill_grouped[case_id]
        bp = _passed_count(baseline_case)
        sp = _passed_count(skill_case)
        br = _rate(bp, len(baseline_case))
        sr = _rate(sp, len(skill_case))
        lines.append(
            f"| `{case_id}` | {_format_rate(bp, len(baseline_case))} | "
            f"{_format_rate(sp, len(skill_case))} | {_format_delta(br, sr)} | "
            f"{_mean_changed_files(baseline_case):.2f} → "
            f"{_mean_changed_files(skill_case):.2f} | "
            f"{_format_duration(_mean_duration(baseline_case))} → "
            f"{_format_duration(_mean_duration(skill_case))} |"
        )

    baseline_checks = _check_rates(baseline_grouped)
    skill_checks = _check_rates(skill_grouped)
    check_types = sorted(set(baseline_checks) | set(skill_checks))
    lines.extend(
        [
            "",
            "## Deterministic check types",
            "",
            "| Check | No Skill | Skill | Pass-rate delta |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for check_type in check_types:
        bp, bt = baseline_checks.get(check_type, (0, 0))
        sp, st = skill_checks.get(check_type, (0, 0))
        lines.append(
            f"| `{check_type}` | {_format_rate(bp, bt)} | {_format_rate(sp, st)} | "
            f"{_format_delta(_rate(bp, bt), _rate(sp, st))} |"
        )

    lines.extend(
        [
            "",
            (
                "Infrastructure-only checks such as `skill_payload_integrity` are excluded "
                "from the check-type comparison so they do not inflate either condition."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare a no-Skill eval report with a Skill-enabled eval report."
    )
    parser.add_argument("baseline", type=Path, help="no-Skill JSON report")
    parser.add_argument("skill", type=Path, help="Skill-enabled JSON report")
    parser.add_argument("--output", type=Path, help="write Markdown comparison")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        rendered = compare_reports(load_report(args.baseline), load_report(args.skill))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
