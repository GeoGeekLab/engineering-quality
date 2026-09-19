# Behavioral evaluations

The evaluation fixtures describe engineering decisions the skill should consistently encourage or reject.

They are not benchmark scores and do not attempt to reduce software quality to a single number.

## Schema

`cases.json` is validated against the repository's structural contract documented in `schema.json`.

Each case contains:

- `id`: stable kebab-case identifier,
- `task`: scenario under evaluation,
- `must_do`: behaviors expected from the engineering-quality contract,
- `must_not_do`: behaviors that would violate the contract.

## Coverage strategy

Cases target failure modes that are easy to miss with style-oriented checks:

- scope creep,
- compatibility breaks,
- speculative abstraction,
- unsupported completion claims,
- unsafe trust boundaries,
- unmeasured optimization,
- concurrency leaks,
- behavior-changing refactors,
- unnecessary dependencies,
- flaky-test masking,
- unsafe migrations,
- hand-edited generated output,
- swallowed errors,
- uncontrolled change expansion.

When the skill contract changes, update or add a case that would fail under the old behavior and pass under the intended behavior.
