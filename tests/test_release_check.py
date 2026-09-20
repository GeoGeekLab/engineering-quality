from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import release_check
import release_notes


class ReleaseCheckTests(unittest.TestCase):
    def test_repository_is_release_ready(self) -> None:
        self.assertEqual([], release_check.check_release(ROOT))

    def test_matching_tag_is_accepted(self) -> None:
        version = release_check.read_version(ROOT)
        self.assertEqual([], release_check.check_release(ROOT, f"v{version}"))

    def test_wrong_tag_is_rejected(self) -> None:
        errors = release_check.check_release(ROOT, "v999.0.0")
        self.assertTrue(any("does not match VERSION" in error for error in errors))

    def test_release_workflow_reconciles_existing_release(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(
            encoding="utf-8"
        )
        self.assertEqual([], release_check.validate_release_workflow(workflow))

    def test_create_only_release_workflow_is_rejected(self) -> None:
        workflow = """
        python scripts/release_check.py
        make package
        python scripts/release_notes.py
        gh release create "$GITHUB_REF_NAME"
        """
        errors = release_check.validate_release_workflow(workflow)
        self.assertTrue(any("existing-release detection" in error for error in errors))
        self.assertTrue(any("asset replacement" in error for error in errors))

    def test_release_workflow_requires_guarded_release_branch_path(self) -> None:
        workflow = """
        on:
          push:
            tags:
              - "v*.*.*"
        python scripts/release_check.py
        make package
        python scripts/release_notes.py
        gh release view "$GITHUB_REF_NAME"
        gh release edit "$GITHUB_REF_NAME"
        gh release upload "$GITHUB_REF_NAME" --clobber
        actions/attest@0123456789012345678901234567890123456789
        gh attestation verify artifact.zip
        """
        errors = release_check.validate_release_workflow(workflow)
        self.assertTrue(any("release branch trigger" in error for error in errors))
        self.assertTrue(any("main-commit gate" in error for error in errors))
        self.assertTrue(any("release tag creation" in error for error in errors))

    def test_release_notes_extract_current_version(self) -> None:
        version = release_check.read_version(ROOT)
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        notes = release_notes.extract_release_notes(changelog, version)
        self.assertIn("signed build provenance", notes)
        self.assertNotIn("## 1.0.0", notes)


if __name__ == "__main__":
    unittest.main()
