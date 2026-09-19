# Contributing

Contributions should improve the playbook's usefulness without turning it into a catalog of personal preferences.

## Principles

- Prefer a concrete failure mode or maintenance benefit over a style opinion.
- Keep rules conditional when context changes their value.
- Delegate mechanical policy to tooling when practical.
- Avoid universal numeric thresholds unless an external standard requires them.
- Keep `SKILL.md` compact; put optional depth in references or workflows.
- Add or update an evaluation case when changing behavior.
- Keep distribution and release invariants reproducible.

## Development

Requires Python 3.10 or newer.

```bash
make check
```

Before opening a change:

1. run repository validation,
2. run unit tests,
3. verify deterministic packaging,
4. inspect the complete diff,
5. update documentation or evaluation fixtures when behavior changes.

Build the clean distribution archive with:

```bash
make package
```

## Adding guidance

A new rule should answer:

- What concrete risk does it address?
- When should it apply?
- When should it not apply?
- Can a deterministic tool enforce it instead?
- Is an existing reference a better place for it?

## Adding a workflow

Workflows should be narrow, composable, and outcome-oriented. Avoid duplicating rules already covered by references.

## Changing runtime packaging

The packaged skill intentionally excludes repository-maintenance files such as tests, CI configuration, README content, and release tooling.

When a runtime file is added or moved:

1. update `scripts/package_skill.py`,
2. add or update package tests,
3. run `make package-check`,
4. inspect the archive manifest.

## Versioning and releases

Follow [docs/release.md](docs/release.md). Do not move published tags. A release branch must keep `VERSION`, `CHANGELOG.md`, package naming, and the eventual `v<VERSION>` tag consistent.

## Source material

Prefer primary sources, official language documentation, recognized standards, and original technical writing. Paraphrase rather than copying long passages. Record important foundations in `docs/foundations.md`.
