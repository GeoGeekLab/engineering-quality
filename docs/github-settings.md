# GitHub governance settings

This file is the repository-side source of truth for GitHub settings that cannot be enforced by committed files alone.

Last audited through the GitHub API: **2026-09-20**.

## Observed state before this governance change

At audit time:

- no repository rulesets were configured,
- GitHub Discussions was disabled,
- squash, merge-commit, and rebase merge methods were all enabled,
- merged branches were not deleted automatically,
- pull-request branches did not expose the update-branch control,
- private vulnerability reporting could not be verified through the connected GitHub integration,
- classic branch protection could not be read through the connected integration and is therefore not assumed absent.

## Main branch ruleset

Create an **active branch ruleset** named `main-quality-gate`.

Target:

- default branch only.

Bypass:

- no routine bypass actors.

Rules:

- restrict deletions,
- block force pushes,
- require linear history,
- require a pull request before merging,
- required approving reviews: **0** while the repository has only one write-capable maintainer,
- require all review conversations to be resolved,
- allow squash merges for protected-branch pull requests,
- require status checks before merging,
- require branches to be up to date before merging.

Required status checks:

- `quality (3.10)`
- `quality (3.12)`
- `quality (3.14)`
- `package`

Why review count is zero is documented in [GOVERNANCE.md](../GOVERNANCE.md). Increase it to one and require CODEOWNER review only after an independent write-capable maintainer exists.

If any CI job is renamed, update this ruleset together with the workflow change. A stale required-check name can block every merge.

## Release tag ruleset

Create an **active tag ruleset** named `release-tag-immutability`.

Target:

- tags matching `v*.*.*`.

Rules:

- restrict deletions,
- restrict updates.

Do **not** restrict tag creation; the release process must still be able to create a new version tag.

Published versions are repaired through the Release object or superseded by a new version. Existing version tags are never moved.

## Repository merge settings

Set:

- squash merge: **enabled**,
- merge commits: **disabled**,
- rebase merge: **disabled**,
- automatically delete head branches: **enabled**,
- allow pull-request branches to be updated: **enabled**,
- default squash title: pull request title or commit + PR title according to maintainer preference.

Auto-merge may be enabled because required checks remain authoritative, but it is optional.

## Security settings

For this public repository:

- enable **Private vulnerability reporting**,
- keep Dependabot alerts and security updates enabled when available,
- subscribe maintainers to security-alert notifications.

Private vulnerability reporting gives reporters a structured private disclosure path and avoids forcing exploit details into public issues.

## Community settings

Enable **GitHub Discussions**.

Recommended use:

- Issues: reproducible defects, compatibility reports, actionable proposals.
- Discussions: questions, usage patterns, design exploration, examples, and early ideas.
- Security advisories: vulnerability details.

Disable the repository Wiki unless the project intentionally chooses to maintain a second documentation surface. The versioned `docs/` directory should remain the canonical documentation source.

## Verification after changing settings

Re-read the repository API and ruleset pages and confirm:

- `has_discussions` is true,
- only squash merge is enabled,
- `delete_branch_on_merge` is true,
- `allow_update_branch` is true,
- `main-quality-gate` is active with the four required CI checks,
- `release-tag-immutability` is active for `v*.*.*`,
- private vulnerability reporting exposes a **Report a vulnerability** path on the Security page.

Do not mark a platform setting as complete solely because this document requests it.
