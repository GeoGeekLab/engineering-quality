# Contributing

Contributions should improve usefulness without turning the playbook into a catalog of personal preferences.

## Principles

- Prefer a concrete failure mode or maintenance benefit over a style opinion.
- Keep rules conditional when context changes their value.
- Delegate mechanical policy to tooling when practical.
- Avoid universal numeric thresholds unless an external standard requires them.
- Keep `SKILL.md` compact; put optional depth in references or workflows.
- Add or update an evaluation case when changing behavior.

## Development

Requires Python 3.10 or newer.

```bash
make check
```

Before opening a change, run repository validation and unit tests, inspect the complete diff, and update documentation or evaluation fixtures when behavior changes.

## Adding guidance

A new rule should answer what concrete risk it addresses, when it applies, when it does not apply, whether a deterministic tool can enforce it, and whether an existing reference is a better home.

## Source material

Prefer primary sources, official language documentation, recognized standards, and original technical writing. Paraphrase rather than copying long passages. Record important foundations in `docs/foundations.md`.
