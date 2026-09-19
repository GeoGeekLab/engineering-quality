# Release engineering

Releases are versioned with Semantic Versioning and are expected to be reproducible from a tagged commit.

## Version contract

The canonical version is stored in `VERSION` without a leading `v`.

A release tag must be exactly:

```text
v<VERSION>
```

For example, `VERSION=1.1.0` requires tag `v1.1.0`.

The same version must have a dated section in `CHANGELOG.md`.

## Release gates

Before tagging:

```bash
make check
make package
```

`make check` validates:

- skill metadata and required repository structure,
- local Markdown links,
- version and changelog consistency,
- evaluation fixtures,
- Python compilation and unit tests,
- deterministic package construction,
- release-readiness invariants.

`make package` creates:

```text
dist/
├── engineering-quality-<version>.zip
└── engineering-quality-<version>.zip.sha256
```

The archive contains a `MANIFEST.sha256` file covering every packaged payload file.

## Tagging

After the release commit is merged to `main`:

```bash
git checkout main
git pull --ff-only
git tag -a "v$(cat VERSION)" -m "engineering-quality v$(cat VERSION)"
git push origin "v$(cat VERSION)"
```

Do not move or reuse a published release tag.

## Automated release

Pushing a matching `v*.*.*` tag triggers `.github/workflows/release.yml`.

The workflow:

1. checks that the tag matches `VERSION`,
2. runs the full validation suite,
3. creates the deterministic distribution archive,
4. extracts release notes from `CHANGELOG.md`,
5. publishes the ZIP and SHA-256 checksum to the GitHub Release.

## Version selection

- **Patch**: corrections that preserve the public skill contract.
- **Minor**: backward-compatible workflows, references, validation, or distribution features.
- **Major**: incompatible changes to the skill contract, routing semantics, required runtime assumptions, or packaged layout.

## Rollback

Published tags are immutable. If a release is defective, fix forward with a new patch release. If a GitHub Release needs to be hidden while a fix is prepared, do not rewrite the tag or archive under the same version.
