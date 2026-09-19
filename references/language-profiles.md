# Language profiles

Repository configuration and established local style take precedence over this file.

## Python

Prefer configured formatters, linters, type checkers, and test runners. Follow PEP 8 where local style is silent. Use context managers for owned resources, avoid broad exception handling, avoid mutable default arguments, and preserve exception chaining when translating errors.

## TypeScript and JavaScript

Use package scripts and the lockfile-selected package manager. Preserve strictness settings, prefer narrowing over unchecked assertions, validate external data, clean up asynchronous resources, and handle rejected promises and cancellation consistently.

`any` is not universally forbidden; its risk depends on boundary and purpose.

## Go

Use `gofmt` and repository-standard analysis. Follow official Go review and style guidance when local rules are silent. Preserve cancellation, avoid goroutine leaks, handle errors where context exists, and keep interfaces driven by consumer needs.

## Rust

Use `rustfmt`, compiler diagnostics, tests, and Clippy according to repository policy. Treat Clippy groups selectively. Model invariants in types where practical and keep `unsafe` boundaries small and documented.

## Java and JVM languages

Use the repository's Gradle or Maven wrapper when present. Preserve nullability and threading contracts, use structured resource management, avoid broad exception catches, and keep serialization and transaction boundaries explicit.

## SQL

Parameterize values, review query plans for performance-sensitive changes, make transaction boundaries explicit, account for isolation and locking, and make migrations safe for realistic data volume.

## Other languages

Prefer official formatter and style guidance, then project conventions, then ecosystem conventions. Do not transfer idioms mechanically from another language.
