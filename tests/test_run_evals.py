from __future__ import annotations

import os
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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

    def test_agent_environment_does_not_inherit_unrequested_secrets(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "PATH": "/usr/bin",
                "CODEX_API_KEY": "explicit",
                "UNRELATED_SECRET": "do-not-forward",
                "HOME": "/sensitive/home",
            },
            clear=True,
        ):
            env = run_evals._isolated_environment(("CODEX_API_KEY",))

        self.assertEqual("explicit", env["CODEX_API_KEY"])
        self.assertNotIn("UNRELATED_SECRET", env)
        self.assertNotIn("HOME", env)

    def test_check_environment_uses_isolated_home(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            with mock.patch.dict(
                os.environ,
                {"PATH": "/usr/bin", "HOME": "/sensitive/home"},
                clear=True,
            ):
                env = run_evals._isolated_environment(home=home)

        self.assertEqual(str(home), env["HOME"])
        self.assertEqual(str(home), env["USERPROFILE"])

    def test_validate_cases_rejects_invalid_inline_python_check(self) -> None:
        case = self.sample_case()
        case["checks"] = [
            {
                "type": "command",
                "argv": ["{python}", "-c", "if True print('bad')"],
            }
        ]

        errors = run_evals.validate_cases([case])

        self.assertTrue(any("invalid inline Python" in error for error in errors))

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
                skill_root=ROOT,
                agent_timeout=30,
                check_timeout=30,
                allow_workspace_execution=True,
                keep_workspace=False,
                workspace_parent=None,
            )

        self.assertEqual("passed", result["status"])
        self.assertEqual(1, result["run_index"])
        self.assertEqual(["solution.py"], result["changed_files"])
        self.assertGreaterEqual(result["agent"]["duration_seconds"], 0)
        self.assertTrue(all(check["status"] == "passed" for check in result["checks"]))

    def test_command_checks_are_incomplete_without_execution_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            agent = self.make_agent(root)
            command = shlex.join([sys.executable, str(agent)])

            result = run_evals.evaluate_case(
                self.sample_case(),
                agent_command=command,
                skill_root=ROOT,
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
                skill_root=ROOT,
                agent_timeout=30,
                check_timeout=30,
                allow_workspace_execution=True,
                keep_workspace=False,
                workspace_parent=None,
            )

        self.assertEqual("failed", result["status"])
        self.assertEqual(2, result["agent"]["exit_code"])

    def test_agent_cannot_mutate_staged_skill_without_failing_case(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            agent = root / "mutating_agent.py"
            agent.write_text(
                "import os\n"
                "from pathlib import Path\n"
                "workspace = Path(os.environ['EQ_EVAL_WORKSPACE'])\n"
                "(workspace / 'solution.py').write_text('value = 1\\n', encoding='utf-8')\n"
                "skill = Path(os.environ['EQ_EVAL_SKILL_PATH'])\n"
                "skill.write_text(skill.read_text(encoding='utf-8') + '\\nmutated\\n', encoding='utf-8')\n"
                "print('verified')\n",
                encoding="utf-8",
            )
            command = shlex.join([sys.executable, str(agent)])

            result = run_evals.evaluate_case(
                self.sample_case(),
                agent_command=command,
                skill_root=ROOT,
                agent_timeout=30,
                check_timeout=30,
                allow_workspace_execution=True,
                keep_workspace=False,
                workspace_parent=None,
            )

        self.assertEqual("failed", result["status"])
        integrity = next(
            check for check in result["checks"]
            if check["type"] == "skill_payload_integrity"
        )
        self.assertEqual("failed", integrity["status"])
        self.assertIn("SKILL.md", integrity["changed_files"])

    def test_final_not_claim_any_ignores_negated_claim(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            result = run_evals.evaluate_check(
                {
                    "type": "final_not_claim_any",
                    "terms": ["fully verified"],
                },
                workspace=workspace,
                before={},
                after={},
                final_output="The repository is not fully verified because the service check is blocked.",
                allow_workspace_execution=False,
                command_timeout=30,
            )

        self.assertEqual("passed", result["status"])
        self.assertEqual([], result["matched"])

    def test_final_not_claim_any_does_not_treat_not_only_as_negation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            result = run_evals.evaluate_check(
                {
                    "type": "final_not_claim_any",
                    "terms": ["fully verified"],
                },
                workspace=workspace,
                before={},
                after={},
                final_output="The repository is not only fully verified but release-ready.",
                allow_workspace_execution=False,
                command_timeout=30,
            )

        self.assertEqual("failed", result["status"])

    def test_final_not_claim_any_rejects_positive_claim(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            result = run_evals.evaluate_check(
                {
                    "type": "final_not_claim_any",
                    "terms": ["fully verified"],
                },
                workspace=workspace,
                before={},
                after={},
                final_output="The repository is fully verified.",
                allow_workspace_execution=False,
                command_timeout=30,
            )

        self.assertEqual("failed", result["status"])
        self.assertEqual(["fully verified"], result["matched"])

    def test_command_no_changes_detects_generator_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            path = workspace / "generated.py"
            path.write_text("value = 1\n", encoding="utf-8")
            before = run_evals.snapshot_workspace(workspace)
            result = run_evals.evaluate_check(
                {
                    "type": "command_no_changes",
                    "argv": [
                        "{python}",
                        "-c",
                        "from pathlib import Path; Path('generated.py').write_text('value = 2\\n')",
                    ],
                },
                workspace=workspace,
                before=before,
                after=before,
                final_output="",
                allow_workspace_execution=True,
                command_timeout=30,
            )

        self.assertEqual("failed", result["status"])
        self.assertEqual(["generated.py"], result["executions"][0]["changed_files"])

    def test_command_no_changes_passes_idempotent_generator(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            path = workspace / "generated.py"
            path.write_text("value = 1\n", encoding="utf-8")
            before = run_evals.snapshot_workspace(workspace)
            result = run_evals.evaluate_check(
                {
                    "type": "command_no_changes",
                    "argv": [
                        "{python}",
                        "-c",
                        "from pathlib import Path; p = Path('generated.py'); p.write_text(p.read_text())",
                    ],
                },
                workspace=workspace,
                before=before,
                after=before,
                final_output="",
                allow_workspace_execution=True,
                command_timeout=30,
            )

        self.assertEqual("passed", result["status"])
        self.assertEqual([], result["executions"][0]["changed_files"])

    def test_report_records_only_forwarded_environment_names(self) -> None:
        report = run_evals.build_report(
            [],
            adapter_label="example-agent",
            allow_workspace_execution=False,
            forwarded_environment=("CODEX_API_KEY", "CODEX_API_KEY", "CUSTOM_PROVIDER"),
        )

        self.assertEqual(
            ["CODEX_API_KEY", "CUSTOM_PROVIDER"],
            report["forwarded_environment"],
        )

    def test_repeat_defaults_to_one_and_accepts_explicit_count(self) -> None:
        parser = run_evals._parser()

        self.assertEqual(1, parser.parse_args([]).repeat)
        self.assertEqual(5, parser.parse_args(["--repeat", "5"]).repeat)

    def test_cli_rejects_invalid_repeat(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            run_evals.main(["--validate-only", "--repeat", "0"])

        self.assertEqual(2, raised.exception.code)

    def test_cli_rejects_requested_environment_that_is_not_set(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as raised:
                run_evals.main(
                    [
                        "--validate-only",
                        "--pass-env",
                        "MISSING_CREDENTIAL",
                    ]
                )

        self.assertEqual(2, raised.exception.code)

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
            adapter_label="example-agent",
            allow_workspace_execution=True,
        )

        self.assertEqual("not automatically judged", report["evidence_scope"]["qualitative_rubric"])

    def test_staged_skill_excludes_eval_rubric(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            staged = run_evals.stage_skill_runtime(ROOT, Path(directory))

            self.assertTrue(staged.is_file())
            self.assertTrue((Path(directory) / "references" / "verification.md").is_file())
            self.assertFalse((Path(directory) / "evals").exists())
            self.assertFalse((Path(directory) / "tests").exists())

    def test_flaky_fixture_does_not_shadow_stdlib_token_module(self) -> None:
        cases = run_evals.load_cases(ROOT / "evals" / "cases.json")
        case = next(case for case in cases if case["id"] == "flaky-test")

        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            run_evals.materialize_fixture(case, workspace)
            self.assertFalse((workspace / "token.py").exists())
            completed = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    (
                        "from token_value import token; "
                        "assert token('job', 7) == 'job-0007'"
                    ),
                ],
                cwd=workspace,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

        self.assertEqual(0, completed.returncode, completed.stderr)

    def test_repository_cases_validate(self) -> None:
        cases = run_evals.load_cases(ROOT / "evals" / "cases.json")
        self.assertEqual([], run_evals.validate_cases(cases))
        self.assertEqual(17, len(cases))


if __name__ == "__main__":
    unittest.main()
