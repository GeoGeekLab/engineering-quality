from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compare_eval_results


def make_run(
    case_id: str,
    *,
    status: str,
    run_index: int,
    changed_files: int,
    duration: float,
    check_status: str = "passed",
) -> dict:
    return {
        "id": case_id,
        "run_index": run_index,
        "status": status,
        "task": f"task for {case_id}",
        "agent": {"duration_seconds": duration},
        "changed_files": [f"file-{index}.py" for index in range(changed_files)],
        "checks": [
            {"type": "command", "status": check_status},
            {"type": "skill_payload_integrity", "status": "passed"},
        ],
        "rubric": {},
    }


class CompareEvalResultsTests(unittest.TestCase):
    def test_comparison_reports_repeated_case_rates_and_costs(self) -> None:
        baseline = {
            "adapter": "codex-model-no-skill",
            "cases": [
                make_run(
                    "sample",
                    status="failed",
                    run_index=1,
                    changed_files=3,
                    duration=4.0,
                    check_status="failed",
                ),
                make_run(
                    "sample",
                    status="passed",
                    run_index=2,
                    changed_files=1,
                    duration=2.0,
                ),
            ],
        }
        skill = {
            "adapter": "codex-model-skill",
            "cases": [
                make_run(
                    "sample",
                    status="passed",
                    run_index=1,
                    changed_files=1,
                    duration=3.0,
                ),
                make_run(
                    "sample",
                    status="passed",
                    run_index=2,
                    changed_files=1,
                    duration=5.0,
                ),
            ],
        }

        rendered = compare_eval_results.compare_reports(baseline, skill)

        self.assertIn("1/2 (50%)", rendered)
        self.assertIn("2/2 (100%)", rendered)
        self.assertIn("+50 pp", rendered)
        self.assertIn("2.00 → 1.00", rendered)
        self.assertIn("3.00s → 4.00s", rendered)
        self.assertNotIn("| `skill_payload_integrity` |", rendered)

    def test_comparison_rejects_different_case_sets(self) -> None:
        baseline = {
            "adapter": "baseline",
            "cases": [
                make_run(
                    "one",
                    status="passed",
                    run_index=1,
                    changed_files=1,
                    duration=1.0,
                )
            ],
        }
        skill = {
            "adapter": "skill",
            "cases": [
                make_run(
                    "two",
                    status="passed",
                    run_index=1,
                    changed_files=1,
                    duration=1.0,
                )
            ],
        }

        with self.assertRaisesRegex(ValueError, "case sets differ"):
            compare_eval_results.compare_reports(baseline, skill)

    def test_comparison_rejects_task_drift(self) -> None:
        baseline_run = make_run(
            "sample",
            status="passed",
            run_index=1,
            changed_files=1,
            duration=1.0,
        )
        skill_run = make_run(
            "sample",
            status="passed",
            run_index=1,
            changed_files=1,
            duration=1.0,
        )
        skill_run["task"] = "different task"

        with self.assertRaisesRegex(ValueError, "tasks differ"):
            compare_eval_results.compare_reports(
                {"adapter": "baseline", "cases": [baseline_run]},
                {"adapter": "skill", "cases": [skill_run]},
            )


if __name__ == "__main__":
    unittest.main()
