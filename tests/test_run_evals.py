from __future__ import annotations

import json
import shlex
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_evals


class EvalRunnerTests(unittest.TestCase):
    def sample_case(self) -> dict:
        return {
            "id": "sample-case",
            "task": "Set value to 1 and report verification.",
            "must_do": ["change the value"],
            "must_not_do": ["claim success without evidence"],
            "fixture": {"files": {"solution.py": "value = 0\n"}},
            "checks": [
                {"type": "changed_files_include", "paths": ["solution.py"]},
                {"type": "changed_files_subset", "paths": ["solution.py"]},
                {"type": "file_contains", "path": "solution.py", "text": "value = 1"},
                {
                    "type": "command",
                    "argv": [
                        "{python}",
                        "-c",
                        "from solution import value; raise SystemExit(0 if value == 1 else 1)",
                    ],
                },
                {"type": "final_contains_any", "terms": ["verified"]},
            ],
        }

    def make_agent(self, root: Path, *, exit_code: int = 0) -> Path:
        script = root / "agent.py"
        script.write_text(
            "import os\n"
            "from pathlib import Path\n"
            "workspace = Path(os.environ['EQ_EVAL_WORKSPACE'])\n"
            "(workspace / 'solution.py').write_text('value = 1\\n', encoding='utf-8')\n"
            "print('verified by deterministic check')\n"
            f"raise SystemExit({exit_code})\n",
            encoding="utf-8",
        )
        return script

    def test_validate_cases_rejects_unsafe_fixture_path(self) -> None:
        case = self.sample_case()
        case["fixture"]["files"] = {"../escape.py": "bad\n"}

        errors = run_evals.validate_cases([case])

        self.assertTrue(any("unsafe fixture path" in error for error in errors))

    def test_evaluate_case_runs_agent_and_deterministic_checks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            agent = self.make_agent(root)
            command = shlex.join([sys.executable, str(agent)])

            result = run_evals.evaluate_case(
                self.sample_case(),
                agent_command=command,
                skill=ROOT / "SKILL.md",
                agent_timeout=30,
                check_timeout=30,
                allow_workspace_execution=True,
                keep_workspace=False,
                workspace_parent=None,
            )

        self.assertEqual("passed", result["status"])
        self.assertEqual(["solution.py"], result["changed_files"])
        self.assertTrue(all(check["status"] == "passed" for check in result["checks"]))

    def test_command_checks_are_incomplete_without_execution_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            agent = self.make_agent(root)
            command = shlex.join([sys.executable, str(agent)])

            result = run_evals.evaluate_case(
                self.sample_case(),
                agent_command=command,
                skill=ROOT / "SKILL.md",
                agent_timeout=30,
                check_timeout=30,
                allow_workspace_execution=False,
                keep_workspace=False,
                workspace_parent=None,
            )

        self.assertEqual("incomplete", result["status"])
        command_check = next(
            check for check in result["checks"] if check["type"] == "command"
        )
        self.assertEqual("not_run", command_check["status"])

    def test_agent_failure_fails_case(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            agent = self.make_agent(root, exit_code=2)
            command = shlex.join([sys.executable, str(agent)])

            result = run_evals.evaluate_case(
                self.sample_case(),
                agent_command=command,
                skill=ROOT / "SKILL.md",
                agent_timeout=30,
                check_timeout=30,
                allow_workspace_execution=True,
                keep_workspace=False,
                workspace_parent=None,
            )

        self.assertEqual("failed", result["status"])
        self.assertEqual(2, result["agent"]["exit_code"])

    def test_report_does_not_claim_qualitative_rubric_was_judged(self) -> None:
        result = {
            "id": "sample-case",
            "status": "passed",
            "task": "example",
            "agent": {},
            "changed_files": [],
            "checks": [],
            "rubric": {},
        }

        report = run_evals.build_report(
            [result],
            agent_command="example-agent",
            allow_workspace_execution=True,
        )

        self.assertEqual("not automatically judged", report["evidence_scope"]["qualitative_rubric"])

    def test_repository_cases_validate(self) -> None:
        cases = run_evals.load_cases(ROOT / "evals" / "cases.json")
        self.assertEqual([], run_evals.validate_cases(cases))
        self.assertEqual(14, len(cases))


if __name__ == "__main__":
    unittest.main()
