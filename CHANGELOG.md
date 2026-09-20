# Changelog

All notable changes to this project are documented here.

## Unreleased

## 1.2.2 - 2026-09-20

- Give GitHub CLI an explicit repository context in the checkout-free publish job so Release creation no longer depends on local Git repository discovery.

## 1.2.1 - 2026-09-20

- Fix missing-tag detection so GitHub CLI 404 response bodies cannot be misclassified as an existing tag SHA.
- Keep privileged GitHub Release publication checkout-free by removing redundant local-Git tag verification after the workflow has already established the remote tag invariant.

## 1.2.0 - 2026-09-20

- Repair the release trust chain and make GitHub Release publication safely rerunnable without moving published tags.
- Harden the GitHub Actions supply chain with immutable action SHAs, Dependabot updates, bounded execution, least-privilege release jobs, artifact round-trip verification, and signed build provenance.
- Make repository-check execution explicit about trust: discovery remains read-only, while execution requires `--run --trust-repository`.
- Replace prose-only eval fixtures with 14 executable miniature-repository scenarios, deterministic post-agent checks, hidden-rubric staging, machine-readable results, and strict evidence semantics.
- Add current Codex, ChatGPT, and Claude Code metadata/guidance plus native Codex and Claude Code eval adapters with credential, home-directory, and Skill-integrity isolation.
- Add repository governance: CODEOWNERS, structured Issue Forms, Code of Conduct, security disclosure routing, active branch/tag rulesets, required CI checks, Discussions, and squash-only merge policy.
- Rework the README around quick start, concrete before/after behavior, searchable use cases, and inspectable evidence; add a maintained distribution/discovery playbook.
- Add a guarded `release/v<VERSION>` automation path that can create the immutable release tag only from the exact current `main` commit and removes its trigger branch after successful publication.

## 1.1.0 - 2026-09-19

- Add deterministic skill packaging with an internal SHA-256 manifest and external archive checksum.
- Add release-readiness checks that keep VERSION, changelog, tag names, repository structure, and package contents consistent.
- Add automated tagged-release workflow with generated release notes and packaged artifacts.
- Add a maintained compatibility matrix and release engineering playbook.
- Add an evaluation schema and expand behavioral coverage for dependency changes, flaky tests, migrations, generated code, error handling, and scope expansion.
- Expand language guidance to cover .NET, Swift, Dart/Flutter, C/C++, Ruby, and PHP.
- Extend CI with package construction and artifact verification.

## 1.0.0 - 2026-09-19

- Establish the stable engineering-quality skill contract.
- Add focused workflows for feature work, defect fixes, refactoring, review, debugging, and performance.
- Add references for design, verification, testing, security, compatibility, concurrency, and language conventions.
- Add project-check discovery, repository validation, unit tests, evaluation fixtures, and continuous integration.
- Add the technical architecture diagram and deployment guidance for Codex, Claude Code, and ChatGPT.
