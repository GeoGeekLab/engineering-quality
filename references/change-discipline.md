# Change discipline

## One coherent purpose

A change should be explainable as one coherent unit. Tests, documentation, migrations, and generated artifacts necessary for that unit belong with it.

Unrelated cleanup, formatting churn, dependency upgrades, renames, and style migrations should normally be separate.

## Control the blast radius

Before editing, identify files that must change, files that might change if the design requires it, files that should not change, and contracts or persisted data crossing the boundary.

If the touched surface expands unexpectedly, re-evaluate the design rather than normalizing the expansion.

## Separate refactoring from behavior change

When substantial structural work is needed:

1. establish behavior-preserving tests,
2. perform the refactor,
3. verify unchanged behavior,
4. implement the behavior change.

Combine them only when separation creates greater risk or an unusable intermediate state.

## Preserve local consistency

Repository conventions outrank generic preferences unless the local pattern is directly causing the problem.

Do not use a focused task as an excuse to rename neighboring APIs, replace a library, reformat unrelated files, migrate a pattern across the codebase, or modernize syntax with no task benefit.

## Keep diffs reviewable

Diff size is a heuristic, not a quality score. The key question is whether a reviewer can understand intent, verify invariants, and distinguish mechanical changes from semantic ones.

Split work when independent concerns can be validated independently.

## Dependency changes

Before adding or upgrading a dependency, confirm necessity, existing alternatives, versioning impact, lockfile changes, runtime effects, and security and licensing implications.

## Generated code

Do not hand-edit generated output unless the repository explicitly requires it. Change the source and regenerate using the established command.

If generation cannot be run, report that explicitly.
