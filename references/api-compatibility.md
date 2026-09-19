# API and compatibility

Compatibility includes every observable contract another component can depend on, not only formally documented APIs.

## Identify observable behavior

Consider exported functions and types, HTTP and RPC endpoints, command-line behavior, configuration, schemas, serialized fields, events, file formats, ordering, and machine-consumed errors.

A behavior can become a dependency even when it was not intended as one.

## Classify the change

Determine whether the change is additive, behavior-changing but compatible, deprecating, breaking, or migration-related.

Use the repository's versioning and deprecation policy. Where semantic versioning applies, classify the public contract accordingly.

## Prefer additive evolution

For independently deployed systems, prefer add-before-remove, dual-read, compatibility windows, and backfills before enforcing new constraints.

Avoid synchronized deployment assumptions unless the system guarantees them.

## Data compatibility

For persisted or serialized data, ask whether old code can read new data, new code can read old data, rollback remains safe, defaults are stable, and unknown fields are handled intentionally.

## Error compatibility

Changing an exception type, error code, status code, or machine-consumed message can be breaking even if successful behavior is unchanged.

## Removal

Before removing behavior, search for callers, configuration references, documentation, migrations, telemetry, and external integrations.

Absence of an in-repository caller does not prove absence of external consumers.
