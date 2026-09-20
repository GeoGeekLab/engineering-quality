# Governance

engineering-quality uses lightweight governance designed to preserve reviewability and evidence without creating ceremony that the maintainer structure cannot support.

## Roles

### Maintainer

A maintainer has repository write or administration access and is responsible for:

- protecting the public skill contract and release chain,
- reviewing compatibility and security impact,
- keeping required checks healthy,
- triaging issues and pull requests,
- enforcing the Code of Conduct,
- maintaining release and governance settings.

The current repository is maintained by `@GeoGeekLab`.

### Contributor

A contributor may open issues or pull requests. Contribution does not imply merge authority.

## Decision model

Technical decisions are based on the repository contract, observable failure modes, compatibility requirements, security boundaries, maintenance cost, and verification evidence.

Maintainers may decline changes that are correct in isolation but expand scope, duplicate existing guidance, weaken evidence, or create unsupported long-term commitments.

## Pull requests

Changes to `main` should go through a pull request and pass all required status checks.

The repository currently has a single maintainer. GitHub does not allow an author to satisfy an approval requirement on their own pull request, so the required approving-review count should remain **0** while only one write-capable maintainer exists. This is not an exemption from review discipline: the pull request, CI evidence, complete diff, and conversation-resolution requirements remain the review record.

When a second active maintainer with write access exists, governance should be tightened to:

- require at least one approving review,
- require CODEOWNER review for owned paths,
- dismiss stale approvals when new commits materially change the diff.

Do not enable those approval requirements before an independent reviewer can actually satisfy them.

## Required checks

The `main` ruleset should require these current CI check names:

- `quality (3.10)`
- `quality (3.12)`
- `quality (3.14)`
- `package`

If workflow job names change, update the ruleset in the same change or immediately after merge so protection does not silently point at obsolete checks.

## Merge policy

Squash merge is the preferred merge method because each pull request should represent one coherent change.

Recommended repository settings:

- enable squash merge;
- disable merge commits;
- disable rebase merge;
- enable automatic deletion of head branches;
- enable "Allow update branch";
- keep auto-merge optional; it must not bypass required checks.

## Tags and releases

Published `v*.*.*` tags are immutable project history.

A tag ruleset should target `v*.*.*` and block deletion and non-fast-forward updates. Release recovery must repair the GitHub Release object or fix forward with a new version; it must never move a published version tag.

See [release engineering](docs/release.md).

## Security

Security reports follow [SECURITY.md](SECURITY.md). Vulnerability details should not be posted in public issues before coordinated disclosure.

Private vulnerability reporting should be enabled in GitHub repository settings for this public repository.

## Community channels

Issues are for reproducible defects, host compatibility reports, and concrete engineering-quality proposals.

GitHub Discussions should be enabled for open-ended questions, design exploration, usage examples, and ideas that are not yet actionable defects or proposals. Once enabled, maintainers should move conversational topics there rather than turning the issue tracker into a support forum.

## Policy changes

Changes to this governance document require a pull request and the same repository checks as other changes. Platform-level GitHub settings should be reviewed whenever governance policy or CI job names change.
