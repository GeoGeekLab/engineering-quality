# Testing

Tests are executable statements about behavior.

## Test the contract

Prefer assertions about observable results, state transitions, emitted effects, and failure behavior over private implementation details.

## Cover risk, not a universal percentage

Coverage can reveal unexecuted code, but a numeric target does not prove useful tests.

Prioritize critical business rules, regressions, boundary values, invalid input, permission boundaries, failure and retry paths, serialization, compatibility, and concurrency-sensitive behavior.

Use repository coverage policy when one exists.

## Regression fixes

For a reproducible defect, prefer a test that fails before the fix and passes after it. Exercise the smallest public or stable boundary that demonstrates the defect.

## Test pyramid as a cost model

Use many fast tests for local logic, fewer integration tests for subsystem boundaries, and a small number of end-to-end tests for critical journeys. The right mix depends on architecture.

## Determinism

Control unstable inputs such as time, randomness, concurrency scheduling, networks, filesystem state, environment, locale, and timezone when practical.

Do not hide nondeterminism with indiscriminate retries.

## Test doubles

Use a test double when it creates a stable boundary around something slow, nondeterministic, destructive, or externally controlled. Avoid mocks that merely duplicate implementation structure.

## Property tests

Consider property-based or generative testing when the input space is large and the invariant is clearer than a list of examples.

## Database and migration tests

Verify constraints and migration behavior against a realistic engine when feasible. In-memory substitutes can miss locking, types, collations, query planning, and transaction behavior.
