#!/usr/bin/env python3
"""Build and verify a deterministic engineering-quality skill archive."""

from __future__ import annotations

import argparse
import hashlib
import re
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "engineering-quality"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

REQUIRED_FILES = (
    "SKILL.md",
    "VERSION",
    "LICENSE",
    "agents/openai.yaml",
    "scripts/project_checks.py",
)
REQUIRED_DIRS = ("references", "workflows")
OPTIONAL_DIRS = ("assets",)


def read_version(root: Path = ROOT) -> str:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not version:
        raise ValueError("VERSION is empty")
    return version


def payload_files(root: Path = ROOT) -> list[Path]:
    root = root.resolve()
    files: list[Path] = []

    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.is_file():
            raise ValueError(f"missing package file: {relative}")
        files.append(path)

    for relative in REQUIRED_DIRS:
        directory = root / relative
        if not directory.is_dir():
            raise ValueError(f"missing package directory: {relative}")
        files.extend(path for path in directory.rglob("*") if path.is_file())

    for relative in OPTIONAL_DIRS:
        directory = root / relative
        if directory.is_dir():
            files.extend(path for path in directory.rglob("*") if path.is_file())

    unique: dict[str, Path] = {}
    for path in files:
        if path.is_symlink():
            raise ValueError(f"package payload must not contain symlinks: {path}")
        resolved = path.resolve()
        resolved.relative_to(root)
        relative = resolved.relative_to(root).as_posix()
        unique[relative] = resolved

    return [unique[key] for key in sorted(unique)]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def manifest_text(root: Path, files: list[Path]) -> str:
    lines = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        digest = sha256_bytes(path.read_bytes())
        lines.append(f"{digest}  {relative}")
    return "\n".join(lines) + "\n"


def _zip_info(name: str, executable: bool = False) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    mode = 0o755 if executable else 0o644
    info.external_attr = (mode & 0xFFFF) << 16
    return info


def build_package(root: Path = ROOT, output_dir: Path | None = None) -> tuple[Path, Path]:
    root = root.resolve()
    output_dir = (output_dir or root / "dist").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    version = read_version(root)
    files = payload_files(root)
    archive = output_dir / f"{PACKAGE_NAME}-{version}.zip"
    checksum = output_dir / f"{archive.name}.sha256"
    prefix = f"{PACKAGE_NAME}/"

    with zipfile.ZipFile(
        archive,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as handle:
        for path in files:
            relative = path.relative_to(root).as_posix()
            arcname = prefix + relative
            executable = relative.startswith("scripts/")
            handle.writestr(_zip_info(arcname, executable), path.read_bytes())

        manifest = manifest_text(root, files).encode("utf-8")
        handle.writestr(_zip_info(prefix + "MANIFEST.sha256"), manifest)

    archive_digest = sha256_bytes(archive.read_bytes())
    checksum.write_text(f"{archive_digest}  {archive.name}\n", encoding="utf-8")
    return archive, checksum


def inspect_package(archive: Path, root: Path = ROOT) -> list[str]:
    root = root.resolve()
    expected_files = payload_files(root)
    prefix = f"{PACKAGE_NAME}/"
    expected_names = {
        prefix + path.relative_to(root).as_posix()
        for path in expected_files
    }
    expected_names.add(prefix + "MANIFEST.sha256")

    errors: list[str] = []
    with zipfile.ZipFile(archive, "r") as handle:
        names_list = handle.namelist()
        names = set(names_list)
        if len(names) != len(names_list):
            errors.append("package contains duplicate archive paths")

        missing = sorted(expected_names - names)
        unexpected = sorted(names - expected_names)
        if missing:
            errors.append("package missing: " + ", ".join(missing))
        if unexpected:
            errors.append("package contains unexpected files: " + ", ".join(unexpected))

        manifest_name = prefix + "MANIFEST.sha256"
        if manifest_name not in names:
            return errors + ["package has no MANIFEST.sha256"]

        manifest_lines = handle.read(manifest_name).decode("utf-8").splitlines()
        manifest: dict[str, str] = {}
        for line in manifest_lines:
            if "  " not in line:
                errors.append(f"invalid manifest line: {line}")
                continue
            digest, relative = line.split("  ", 1)
            if not SHA256_RE.fullmatch(digest):
                errors.append(f"invalid manifest digest: {digest}")
                continue
            if relative in manifest:
                errors.append(f"duplicate manifest path: {relative}")
                continue
            manifest[relative] = digest

        expected_relative = {
            path.relative_to(root).as_posix()
            for path in expected_files
        }
        if set(manifest) != expected_relative:
            errors.append("manifest file set does not match payload")

        for relative, digest in manifest.items():
            name = prefix + relative
            if name not in names:
                continue
            actual = sha256_bytes(handle.read(name))
            if actual != digest:
                errors.append(f"manifest checksum mismatch: {relative}")

    return errors


def reproducibility_check(root: Path = ROOT) -> list[str]:
    with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
        a, _ = build_package(root, Path(first))
        b, _ = build_package(root, Path(second))
        errors = inspect_package(a, root)
        if a.read_bytes() != b.read_bytes():
            errors.append("package build is not deterministic")
        return errors


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a deterministic skill distribution archive.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify package integrity and reproducibility without keeping artifacts",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()

    if args.check:
        errors = reproducibility_check(ROOT)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1
        files = payload_files(ROOT)
        print(f"Package verification passed ({len(files)} payload files).")
        return 0

    archive, checksum = build_package(ROOT, args.output_dir)
    errors = inspect_package(archive, ROOT)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(archive)
    print(checksum)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
