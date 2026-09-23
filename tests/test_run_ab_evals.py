from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_ab_evals


def sample_case(case_id: str) -> dict:
    return {
        "id": case_id,
        "task": f"task for {case_id}",
        "must_do": ["do"],
        "must_not_do": ["do not"],
        "fixture": {"files": {"app.py": "value = 1\n"}},
        "checks": [{"type": "changed_files_subset", "paths": ["app.py"]}],
    }


class RunAbEvalsTests(unittest.TestCase):
    def test_condition_order_is_counterbalanced(self) -> None:
        self.assertEqual(
            ("baseline", "skill"),
            run_ab_evals._condition_order(1, 0),
        )
        self.assertEqual(
            ("skill", "baseline"),
            run_ab_evals._condition_order(1, 1),
        )
        self.assertEqual(
            ("skill", "baseline"),
            run_ab_evals._condition_order(2, 0),
        )
        self.assertEqual(
            ("baseline", "skill"),
            run_ab_evals._condition_order(2, 1),
        )

    def test_run_experiment_pairs_conditions_and_records_order(self) -> None:
        calls: list[tuple[str, str, int]] = []

        def fake_evaluate(case: dict, *, agent_command: str, run_index: int, **kwargs):
            calls.append((case["id"], agent_command, run_index))
            return {
                "id": case["id"],
                "run_index": run_index,
                "status": "passed",
                "task": case["task"],
                "agent": {"duration_seconds": 1.0},
                "changed_files": [],
                "checks": [],
                "rubric": {},
            }

        with mock.patch.object(
            run_ab_evals.run_evals,
            "evaluate_case",
            side_effect=fake_evaluate,
        ):
            baseline, skill, manifest = run_ab_evals.run_experiment(
                [sample_case("one"), sample_case("two")],
                baseline_agent_command="baseline-command",
                skill_agent_command="skill-command",
                baseline_label="baseline",
                skill_label="skill",
                repeat=2,
                skill_root=ROOT,
                agent_timeout=30,
                check_timeout=30,
                allow_workspace_execution=False,
                keep_workspaces=False,
                workspace_parent=None,
            )

        self.assertEqual(
            [
                ("one", "baseline-command", 1),
                ("one", "skill-command", 1),
                ("two", "skill-command", 1),
                ("two", "baseline-command", 1),
                ("one", "skill-command", 2),
                ("one", "baseline-command", 2),
                ("two", "baseline-command", 2),
                ("two", "skill-command", 2),
            ],
            calls,
        )
        self.assertEqual(4, len(baseline["cases"]))
        self.assertEqual(4, len(skill["cases"]))
        self.assertEqual("paired-counterbalanced", manifest["design"])
        self.assertEqual(2, manifest["repeat"])
        self.assertEqual(
            ["baseline", "skill"],
            manifest["execution_order"][0]["order"],
        )
        self.assertEqual(
            ["skill", "baseline"],
            manifest["execution_order"][1]["order"],
        )


if __name__ == "__main__":
    unittest.main()
