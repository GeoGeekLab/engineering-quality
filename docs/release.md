# Release engineering

Releases are versioned with Semantic Versioning and are expected to be reproducible from a protected `main` commit.

## Version contract

The canonical version is stored in `VERSION` without a leading `v`.

A release tag must be exactly:

```text
v<VERSION>
```

For example, `VERSION=1.2.0` requires tag `v1.2.0`.

The same version must have a dated section in `CHANGELOG.md`. Host manifests that carry a version, such as `.claude-plugin/plugin.json`, must match `VERSION`.

## Release gates

Before release:

```bash
make check
make package
```

`make check` validates:

- Skill and host metadata,
- governance and local Markdown links,
- immutable GitHub Actions dependencies,
- version and changelog consistency,
- executable evaluation fixtures,
- Python compilation and unit tests,
- deterministic package construction,
- release-workflow invariants.

`make package` creates:

```text
dist/
├── engineering-quality-<version>.zip
└── engineering-quality-<version>.zip.sha256
```

The archive contains a `MANIFEST.sha256` covering every packaged payload file.

## Preferred release path

After the release commit is merged to protected `main`, create a release trigger branch that points **exactly** at the current `main` commit:

```bash
git checkout main
git pull --ff-only
git push origin HEAD:"release/v$(cat VERSION)"
```

Pushing `release/v<VERSION>` triggers `.github/workflows/release.yml`.

The workflow refuses the release unless:

- the branch name exactly matches `release/v<VERSION>`,
- the branch commit exactly matches the current remote `main`,
- repository and package release checks pass.

Only after those gates pass does the privileged publish job create the immutable `v<VERSION>` tag at that commit.

After successful publication, the workflow deletes the temporary release trigger branch. The immutable tag and GitHub Release remain as the release history.

## Manual tag path

A manually created matching tag remains supported:

```bash
git checkout main
git pull --ff-only
git tag -a "v$(cat VERSION)" -m "engineering-quality v$(cat VERSION)"
git push origin "v$(cat VERSION)"
```

A matching `v*.*.*` tag triggers the same build, attestation, and publication path.

Do not move or reuse a published release tag.

## Automated release

The workflow separates construction from publication:

1. resolve the expected tag from `VERSION`,
2. for a release branch, prove that it points exactly at current `main`,
3. run the full repository and release validation suite in a read-only build job,
4. build and checksum-verify the distribution,
5. generate release notes and stage the payload through GitHub Actions artifacts,
6. in the privileged publish job, create the version tag when the guarded release-branch path is used,
7. download and re-verify the staged payload,
8. use GitHub's `actions/attest` action to generate signed build provenance for the ZIP and checksum,
9. verify the ZIP attestation with GitHub CLI,
10. create the GitHub Release when absent or reconcile its metadata/assets when it already exists,
11. remove the temporary release trigger branch after a successful branch-triggered release.

Publication is intentionally rerunnable. If the GitHub Release object already exists, the workflow updates its generated title and notes and replaces the expected assets. A manually or partially created Release therefore does not require moving or recreating the tag.

## Supply-chain controls

GitHub Actions dependencies are pinned to complete commit SHAs rather than mutable version tags. Repository validation rejects non-SHA external action references, and Dependabot proposes GitHub Actions updates.

CI exercises the artifact transport path rather than merely validating YAML: it builds and verifies the package, uploads it, removes the local distribution, downloads the artifact again, and re-verifies the SHA-256 sidecar.

The release build job has read-only repository access. Release write access, attestation storage permission, artifact metadata permission, and the OIDC token used for Sigstore-backed provenance signing exist only in the publish job.

Release artifacts carry two complementary integrity mechanisms:

- `.zip.sha256` verifies the archive bytes,
- GitHub artifact attestations bind the artifact digest to GitHub Actions provenance.

After downloading a release archive:

```bash
sha256sum -c engineering-quality-<version>.zip.sha256

gh attestation verify engineering-quality-<version>.zip \
  --repo GeoGeekLab/engineering-quality
```

## Version selection

- **Patch**: corrections that preserve the public Skill contract.
- **Minor**: backward-compatible workflows, references, validation, distribution, or evaluation features.
- **Major**: incompatible changes to the Skill contract, routing semantics, required runtime assumptions, or packaged layout.

## Recovery

Published `v*.*.*` tags are protected by the repository's active tag ruleset. Never repair a release by moving or reusing its tag.

If publication fails after the tag exists, preserve the tag and fix the publication path. The release workflow can reconcile an existing GitHub Release and replace the expected archive and checksum on a rerun.

If an artifact itself is defective, fix forward with a new patch release rather than rebuilding different source content under the same version.
