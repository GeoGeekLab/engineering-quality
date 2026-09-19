from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import package_skill


class PackageSkillTests(unittest.TestCase):
    def test_package_contains_runtime_files_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive, checksum = package_skill.build_package(ROOT, Path(directory))
            self.assertEqual([], package_skill.inspect_package(archive, ROOT))
            self.assertTrue(checksum.is_file())

            with zipfile.ZipFile(archive) as handle:
                names = set(handle.namelist())

            self.assertIn("engineering-quality/SKILL.md", names)
            self.assertIn("engineering-quality/references/principles.md", names)
            self.assertIn("engineering-quality/workflows/review.md", names)
            self.assertIn("engineering-quality/scripts/project_checks.py", names)
            self.assertIn("engineering-quality/MANIFEST.sha256", names)
            self.assertNotIn("engineering-quality/README.md", names)
            self.assertFalse(any("/tests/" in name for name in names))
            self.assertFalse(any("/.github/" in name for name in names))

    def test_package_is_reproducible(self) -> None:
        self.assertEqual([], package_skill.reproducibility_check(ROOT))

    def test_sidecar_checksum_matches_archive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive, checksum = package_skill.build_package(ROOT, Path(directory))
            expected = checksum.read_text(encoding="utf-8").split()[0]
            actual = hashlib.sha256(archive.read_bytes()).hexdigest()
            self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
