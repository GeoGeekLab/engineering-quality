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
- GitHub Actions dependency pinning,
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

The workflow separates construction from publication:

1. a read-only build job checks that the tag matches `VERSION`,
2. runs the full validation suite,
3. creates and checksum-verifies the distribution archive,
4. generates release notes and stages the release payload,
5. a separate publish job downloads and re-verifies that payload,
6. generates signed SLSA build-provenance attestations for the ZIP and checksum,
7. verifies the ZIP attestation with GitHub CLI,
8. creates the GitHub Release when it does not exist, or reconciles an existing Release,
9. publishes or replaces the ZIP and SHA-256 checksum for that immutable tag.

Release publication is intentionally rerunnable. If the GitHub Release object already exists, the workflow updates its generated title and notes and uploads the expected assets with replacement enabled. A manually or partially created Release therefore does not require moving or recreating the tag.

## Supply-chain controls

GitHub Actions dependencies are pinned to complete commit SHAs rather than mutable version tags. A repository validation check rejects non-SHA action references. Human-readable version comments remain next to the pins, and Dependabot is configured to propose GitHub Actions updates.

The build job has read-only repository access. Release write access and the OIDC token needed for provenance signing are granted only to the publish job. Jobs also use explicit timeouts, and workflow concurrency prevents stale CI runs or overlapping publication for the same ref.

Release artifacts carry two complementary integrity mechanisms:

- `.zip.sha256` verifies the downloaded archive bytes,
- GitHub artifact attestations bind the release artifact digest to the GitHub Actions build identity and workflow provenance.

After downloading a release archive, provenance can be checked with:

```bash
gh attestation verify engineering-quality-<version>.zip \
  --repo GeoGeekLab/engineering-quality
```

The checksum should still be verified independently:

```bash
sha256sum -c engineering-quality-<version>.zip.sha256
```

## Version selection

- **Patch**: corrections that preserve the public skill contract.
- **Minor**: backward-compatible workflows, references, validation, or distribution features.
- **Major**: incompatible changes to the skill contract, routing semantics, required runtime assumptions, or packaged layout.

## Recovery

Published tags are immutable. Never repair a release by moving or reusing its tag.

If publication fails after the tag exists, preserve the tag and fix the publication path. The release workflow is designed to reconcile an already-created GitHub Release and replace the expected archive and checksum on a rerun.

If a release artifact itself is defective, fix forward with a new patch release rather than rebuilding different source content under the same version.
