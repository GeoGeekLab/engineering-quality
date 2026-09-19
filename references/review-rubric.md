# Review rubric

Review for risk, not personal taste.

## Severity

### Blocker

The change can cause incorrect behavior, data loss, a security vulnerability, a broken contract, or a reliably failing build or test.

### Major

A material problem is likely under realistic conditions, or the design creates significant maintenance or operational risk.

### Minor

A bounded issue reduces clarity, test quality, resilience, or consistency but does not invalidate the change.

### Note

An optional improvement, question, or follow-up that should not be presented as required work.

Do not inflate severity to win a style disagreement.

## Review dimensions

### Contract and correctness

Check conditions, boundaries, partial failure, retries, duplicate delivery, ordering, time handling, precision, overflow, and cleanup.

### Design and complexity

Flag unnecessary abstraction, hidden coupling, duplicated policy, confusing ownership, and broad interfaces.

### Security and privacy

Inspect trust boundaries, authorization, injection surfaces, secret handling, sensitive logging, file and path operations, deserialization, network requests, and dependency changes.

### Compatibility

Check public APIs, command-line behavior, configuration, schemas, persisted state, events, serialized data, and externally observable errors.

### Concurrency and resources

Check synchronization, cancellation, timeouts, deadlocks, races, reentrancy, resource lifetime, and shutdown behavior.

### Tests

Tests should prove changed behavior and important failure modes without overfitting to private implementation.

### Operability

For production-facing changes, consider diagnostics, metrics, logs, rollout, rollback, migrations, and failure visibility.

## Reporting findings

A finding should contain severity, exact location, concrete failure or risk, triggering conditions, and the smallest useful corrective direction.
