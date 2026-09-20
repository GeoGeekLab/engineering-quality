from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import host_eval_adapter


class HostEvalAdapterTests(unittest.TestCase):
    def test_codex_uses_noninteractive_workspace_write_mode(self) -> None:
        argv = host_eval_adapter.codex_argv("codex", "fix the bug")

        self.assertEqual("codex", argv[0])
        self.assertIn("exec", argv)
        self.assertIn("--ephemeral", argv)
        self.assertIn("--ignore-user-config", argv)
        self.assertIn("workspace-write", argv)
        self.assertEqual("fix the bug", argv[-1])

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

    def test_copy_skill_preserves_runtime_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "skill"
            entry = host_eval_adapter._copy_skill(ROOT / "SKILL.md", target)

            self.assertTrue(entry.is_file())
            self.assertTrue((target / "agents" / "openai.yaml").is_file())
            self.assertTrue((target / "references" / "verification.md").is_file())


if __name__ == "__main__":
    unittest.main()
