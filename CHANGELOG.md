# Changelog

All notable changes to this project are documented here.

## Unreleased

- Make tagged-release publication rerunnable when a GitHub Release already exists, including metadata reconciliation and replacement of expected distribution assets.
- Add a regression check that prevents returning to a create-only release workflow.

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
