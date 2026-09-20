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

    def test_workflow_actions_require_full_commit_sha(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            (workflows / "ci.yml").write_text(
                "steps:\n  - uses: actions/checkout@v7\n",
                encoding="utf-8",
            )

            errors = validate_skill.validate_workflow_action_pins(root)

            self.assertEqual(1, len(errors))
            self.assertIn("full commit SHA", errors[0])

    def test_workflow_accepts_sha_pins_and_local_actions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            (workflows / "ci.yml").write_text(
                "steps:\n"
                "  - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1\n"
                "  - uses: ./github/actions/local\n",
                encoding="utf-8",
            )

            self.assertEqual([], validate_skill.validate_workflow_action_pins(root))


    def test_openai_metadata_requires_interface_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata = root / "agents" / "openai.yaml"
            metadata.parent.mkdir(parents=True)
            metadata.write_text(
                "interface:\n"
                "  display_name: \"Engineering Quality\"\n"
                "policy:\n"
                "  allow_implicit_invocation: true\n",
                encoding="utf-8",
            )

            errors = validate_skill.validate_openai_metadata(root)

            self.assertTrue(
                any("short_description is required" in error for error in errors)
            )
            self.assertTrue(any("default_prompt is required" in error for error in errors))

    def test_openai_metadata_rejects_invalid_invocation_policy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata = root / "agents" / "openai.yaml"
            metadata.parent.mkdir(parents=True)
            metadata.write_text(
                "interface:\n"
                "  display_name: \"Engineering Quality\"\n"
                "  short_description: \"Engineering quality gate\"\n"
                "  default_prompt: \"Apply engineering-quality.\"\n"
                "policy:\n"
                "  allow_implicit_invocation: maybe\n",
                encoding="utf-8",
            )

            errors = validate_skill.validate_openai_metadata(root)

            self.assertTrue(any("must be true or false" in error for error in errors))

    def test_eval_validation_rejects_unsupported_case_keys(self) -> None:
        cases = [
            {
                "id": "sample-case",
                "task": "Example",
                "must_do": ["do this"],
                "must_not_do": ["not that"],
                "fixture": {"files": {"a.txt": "x\n"}},
                "checks": [{"type": "file_exists", "path": "a.txt"}],
                "unexpected": True,
            }
        ]

        import run_evals

        errors = run_evals.validate_cases(cases)

        self.assertTrue(any("unsupported keys" in error for error in errors))

if __name__ == "__main__":
    unittest.main()
