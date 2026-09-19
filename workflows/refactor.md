# Refactor workflow

1. State the behavior that must remain unchanged, including public APIs, serialization, persistence, and side effects.
2. Run existing tests first; add characterization tests if important behavior is unprotected.
3. Decompose the transformation into small steps that keep the repository working.
4. Improve a concrete property such as coupling, ownership, module boundaries, duplicated policy, control flow, or invariant expression.
5. Run the same relevant tests before and after when possible and inspect the diff for semantic changes.
6. Stop when the stated property is improved.

Do not refactor merely to impose a personal style, and avoid mixing feature work into the same change.
