from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_skill


class ValidateSkillTests(unittest.TestCase):
    def test_repository_is_valid(self) -> None:
        self.assertEqual([], validate_skill.validate_repository(ROOT))

    def test_frontmatter_requires_kebab_case(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text(
                "---\nname: Bad_Name\ndescription: Example.\n---\n",
                encoding="utf-8",
            )
            errors = validate_skill.validate_frontmatter(root)
            self.assertTrue(any("kebab-case" in error for error in errors))

    def test_version_requires_semver(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "VERSION").write_text("v1.1\n", encoding="utf-8")
            (root / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
            errors = validate_skill.validate_version(root)
            self.assertTrue(any("semantic version" in error for error in errors))

    def test_local_link_validation_detects_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("[missing](docs/missing.md)\n", encoding="utf-8")
            errors = validate_skill.validate_markdown_links(root)
            self.assertEqual(1, len(errors))
            self.assertIn("broken local link", errors[0])


if __name__ == "__main__":
    unittest.main()
