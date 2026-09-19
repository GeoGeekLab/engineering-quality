from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import project_checks


class ProjectChecksTests(unittest.TestCase):
    def make_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        return temp, Path(temp.name)

    def test_node_uses_declared_package_manager_and_safe_scripts(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        (root / "package.json").write_text(
            json.dumps(
                {
                    "packageManager": "pnpm@10.0.0",
                    "scripts": {
                        "format": "prettier --write .",
                        "format:check": "prettier --check .",
                        "lint": "eslint .",
                        "typecheck": "tsc --noEmit",
                        "test": "vitest run",
                        "build": "tsc",
                    },
                }
            ),
            encoding="utf-8",
        )

        checks = project_checks.discover_checks(root)
        commands = [check.command for check in checks]

        self.assertIn(("pnpm", "run", "format:check"), commands)
        self.assertIn(("pnpm", "run", "lint"), commands)
        self.assertIn(("pnpm", "run", "typecheck"), commands)
        self.assertIn(("pnpm", "run", "test"), commands)
        self.assertNotIn(("pnpm", "run", "format"), commands)

    def test_python_discovers_only_configured_tools(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        (root / "pyproject.toml").write_text(
            "[tool.ruff]\nline-length = 100\n\n"
            "[tool.mypy]\nstrict = true\n\n"
            "[tool.pytest.ini_options]\naddopts = '-q'\n",
            encoding="utf-8",
        )

        checks = project_checks.discover_checks(root)
        rendered = [check.display() for check in checks]

        self.assertTrue(any("ruff check ." in command for command in rendered))
        self.assertTrue(any("mypy ." in command for command in rendered))
        self.assertTrue(any("-m pytest" in command for command in rendered))
        self.assertFalse(any("black --check" in command for command in rendered))

    def test_rust_and_go_checks_are_discovered(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        (root / "Cargo.toml").write_text("[package]\nname='sample'\n", encoding="utf-8")
        (root / "go.mod").write_text("module example.test/sample\n", encoding="utf-8")

        commands = [check.command for check in project_checks.discover_checks(root)]

        self.assertIn(("go", "vet", "./..."), commands)
        self.assertIn(("go", "test", "./..."), commands)
        self.assertIn(("cargo", "fmt", "--", "--check"), commands)
        self.assertIn(("cargo", "test", "--all-features"), commands)

    def test_makefile_targets_are_conservative(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        (root / "Makefile").write_text(
            "check:\n\t@echo check\n\n"
            "test:\n\t@echo test\n\n"
            "deploy:\n\t@echo deploy\n",
            encoding="utf-8",
        )

        commands = [check.command for check in project_checks.discover_checks(root)]

        self.assertIn(("make", "check"), commands)
        self.assertIn(("make", "test"), commands)
        self.assertNotIn(("make", "deploy"), commands)

    def test_empty_repository_has_no_checks(self) -> None:
        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        self.assertEqual([], project_checks.discover_checks(root))


if __name__ == "__main__":
    unittest.main()
