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

    def test_release_notes_extract_current_version(self) -> None:
        version = release_check.read_version(ROOT)
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        notes = release_notes.extract_release_notes(changelog, version)
        self.assertIn("deterministic skill packaging", notes)
        self.assertNotIn("## 1.0.0", notes)


if __name__ == "__main__":
    unittest.main()
