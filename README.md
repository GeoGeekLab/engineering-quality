# Engineering Quality

A portable engineering-quality playbook for implementation, debugging, refactoring, review, and performance work.

The repository is intentionally opinionated about process and deliberately conservative about style. It favors correct behavior, small coherent changes, local conventions, explicit contracts, and verification evidence over universal thresholds or fashionable abstractions.

## What it provides

- A compact `SKILL.md` that routes work without loading the whole library.
- Focused workflows for features, defects, refactors, reviews, debugging, and performance.
- Reference guides for design, testing, security, compatibility, concurrency, and language-specific conventions.
- A deterministic project-check discovery tool that never installs dependencies.
- Repository validation and tests with no third-party Python dependencies.
- Evaluation fixtures for regression-testing the playbook itself.

## Layout

```text
.
├── SKILL.md
├── references/
├── workflows/
├── scripts/
├── tests/
├── evals/
├── docs/
└── .github/workflows/
```

## Core contract

1. Understand the repository before changing it.
2. Define the observable contract and relevant invariants.
3. Make the smallest coherent change that solves the problem.
4. Follow local conventions before generic preferences.
5. Add or update tests for changed behavior.
6. Run the strongest relevant verification available.
7. Review the resulting diff for correctness, security, compatibility, concurrency, and maintainability.
8. Report verified facts separately from assumptions and unrun checks.

## Validation

Requires Python 3.10 or newer.

```bash
make check
```

To inspect likely quality commands for another repository without executing them:

```bash
python scripts/project_checks.py /path/to/repository
```

Add `--run` only when you intend to execute the discovered checks.

## Design stance

This project treats most numeric quality thresholds as heuristics rather than universal laws. A long function, repeated code, a large diff, or a coverage percentage can indicate risk, but context determines whether a change is actually worse.

Mechanical concerns should be delegated to formatters, linters, compilers, type checkers, test runners, and security tooling whenever possible. Human judgment is reserved for contracts, design, trade-offs, scope, and risk.

See [Engineering foundations](docs/foundations.md) for the public standards and engineering literature that inform the playbook.

## License

MIT
