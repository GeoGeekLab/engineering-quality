# Changelog

All notable changes to this project are documented here.

## Unreleased

- Make tagged-release publication rerunnable when a GitHub Release already exists, including metadata reconciliation and replacement of expected distribution assets.
- Add a regression check that prevents returning to a create-only release workflow.
- Pin GitHub Actions to immutable commit SHAs and enforce that policy in repository validation.
- Add Dependabot updates for GitHub Actions, bounded workflow execution, and concurrency controls.
- Split release construction from privileged publication and add signed artifact provenance with in-workflow verification.
- Upgrade artifact transport to current GitHub Actions releases, verify an upload/download round trip in CI, and use the current `actions/attest` provenance action.
- Make project-check discovery execution-safe by default: running discovered checks now requires explicit repository trust, with regression coverage and trust-boundary guidance.
- Replace prose-only behavioral eval fixtures with an executable miniature-repository harness, deterministic post-agent checks, hidden-rubric runtime staging, machine-readable reports, and CI self-tests that do not masquerade as real-model results.

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
