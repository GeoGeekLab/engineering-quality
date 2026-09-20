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
5. creates the GitHub Release when it does not exist, or reconciles an existing Release,
6. publishes or replaces the ZIP and SHA-256 checksum for that immutable tag.

Release publication is intentionally rerunnable. If the GitHub Release object already exists, the workflow updates its generated title and notes and uploads the expected assets with replacement enabled. A manually or partially created Release therefore does not require moving or recreating the tag.

## Version selection

- **Patch**: corrections that preserve the public skill contract.
- **Minor**: backward-compatible workflows, references, validation, or distribution features.
- **Major**: incompatible changes to the skill contract, routing semantics, required runtime assumptions, or packaged layout.

## Recovery

Published tags are immutable. Never repair a release by moving or reusing its tag.

If publication fails after the tag exists, preserve the tag and fix the publication path. The release workflow is designed to reconcile an already-created GitHub Release and replace the expected archive and checksum on a rerun.

If a release artifact itself is defective, fix forward with a new patch release rather than rebuilding different source content under the same version.
