from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import host_eval_adapter


class HostEvalAdapterTests(unittest.TestCase):
    def test_adapter_environment_forwards_only_explicit_names(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "PATH": "/usr/bin",
                "EQ_EVAL_PASSED_ENV": "ANTHROPIC_API_KEY",
                "ANTHROPIC_API_KEY": "explicit",
                "UNRELATED_SECRET": "do-not-forward",
            },
            clear=True,
        ):
            env = host_eval_adapter._adapter_environment()

        self.assertEqual("explicit", env["ANTHROPIC_API_KEY"])
        self.assertNotIn("UNRELATED_SECRET", env)
        self.assertNotIn("EQ_EVAL_PASSED_ENV", env)

    def test_codex_uses_noninteractive_workspace_write_mode(self) -> None:
        argv = host_eval_adapter.codex_argv("codex", "fix the bug")

        self.assertEqual("codex", argv[0])
        self.assertIn("exec", argv)
        self.assertIn("--ephemeral", argv)
        self.assertIn("--ignore-user-config", argv)
        self.assertIn("workspace-write", argv)
        self.assertEqual("fix the bug", argv[-1])

    def test_codex_disabled_skill_mode_does_not_install_skill(self) -> None:
        with mock.patch.object(host_eval_adapter, "_copy_skill") as copy_skill:
            with mock.patch.object(host_eval_adapter, "_print_version"):
                with mock.patch.object(
                    host_eval_adapter.subprocess,
                    "run",
                    return_value=mock.Mock(returncode=0),
                ):
                    exit_code = host_eval_adapter.run_codex(
                        executable="codex",
                        task="fix",
                        workspace=Path("."),
                        skill_entry=Path("/tmp/staged-skill/SKILL.md"),
                        skill_mode="disabled",
                    )

        self.assertEqual(0, exit_code)
        copy_skill.assert_not_called()

    def test_codex_model_can_be_pinned(self) -> None:
        argv = host_eval_adapter.codex_argv("codex", "fix", "gpt-test")

        self.assertIn("--model", argv)
        self.assertIn("gpt-test", argv)

    def test_claude_uses_bare_auto_mode_and_explicit_skill_directory(self) -> None:
        skill = Path("/tmp/staged-skill")
        argv = host_eval_adapter.claude_argv("claude", "fix the bug", skill)

        self.assertEqual("claude", argv[0])
        self.assertIn("--bare", argv)
        self.assertIn("--permission-mode", argv)
        self.assertIn("auto", argv)
        self.assertIn("--permission-prompts", argv)
        self.assertIn("none", argv)
        self.assertIn("--no-session-persistence", argv)
        self.assertIn("--add-dir", argv)
        self.assertIn(str(skill), argv)
        self.assertIn("-p", argv)
        self.assertEqual("fix the bug", argv[-1])

    def test_claude_disabled_skill_mode_omits_skill_directory(self) -> None:
        argv = host_eval_adapter.claude_argv("claude", "fix", None)

        self.assertNotIn("--add-dir", argv)
        self.assertEqual("fix", argv[-1])

    def test_claude_model_can_be_pinned(self) -> None:
        argv = host_eval_adapter.claude_argv(
            "claude", "fix", Path("/tmp/staged-skill"), "claude-test"
        )

        self.assertIn("--model", argv)
        self.assertIn("claude-test", argv)

    def test_copy_skill_preserves_runtime_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            target = root / "target"
            (source / "agents").mkdir(parents=True)
            (source / "references").mkdir(parents=True)
            (source / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
            (source / "agents" / "openai.yaml").write_text(
                "interface:\n  display_name: test\n",
                encoding="utf-8",
            )
            (source / "references" / "verification.md").write_text(
                "# Verification\n",
                encoding="utf-8",
            )

            entry = host_eval_adapter._copy_skill(source / "SKILL.md", target)

            self.assertTrue(entry.is_file())
            self.assertTrue((target / "agents" / "openai.yaml").is_file())
            self.assertTrue((target / "references" / "verification.md").is_file())


if __name__ == "__main__":
    unittest.main()
