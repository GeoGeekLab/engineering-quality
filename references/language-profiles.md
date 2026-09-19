# Language profiles

Repository configuration and established local style take precedence over this file. Prefer official toolchains and ecosystem conventions when local guidance is silent.

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

## .NET

Use the repository solution or project configuration and the pinned SDK when available. Preserve nullable-reference-type intent, async cancellation, disposal semantics, and public binary/API compatibility. Prefer `dotnet test`, configured analyzers, and formatter rules already present in the repository.

## Swift

Follow Swift API design guidelines and repository formatting rules. Preserve actor and isolation semantics, structured concurrency, cancellation, ownership, and error propagation. Treat force unwraps and unchecked concurrency escapes as explicit risk decisions rather than convenience.

## Dart and Flutter

Use repository-defined `dart analyze` or `flutter analyze` and test commands. Preserve null-safety assumptions, widget lifecycle cleanup, asynchronous error handling, and platform-specific behavior. Avoid rebuilding broad widget subtrees or adding state machinery without measured need.

## C and C++

Use the repository's compiler, build system, warning policy, sanitizers, and static analysis. Make ownership and lifetime explicit, avoid undefined behavior, preserve ABI constraints where public binaries are involved, and prefer RAII in C++ for owned resources.

## Ruby

Follow the repository's Ruby and Bundler versions, test runner, and lint configuration. Keep mutation and metaprogramming understandable, preserve exception context, avoid hidden global state, and verify database transaction behavior in framework code.

## PHP

Use the repository's Composer lockfile, static analyzer, formatter, and test runner. Preserve strict typing where enabled, validate boundary data, parameterize database access, keep framework lifecycle assumptions explicit, and distinguish recoverable application errors from programmer errors.

## SQL

Parameterize values, review query plans for performance-sensitive changes, make transaction boundaries explicit, account for isolation and locking, and make migrations safe for realistic data volume.

## Other languages

Prefer official formatter and style guidance, then project conventions, then ecosystem conventions. Do not transfer idioms mechanically from another language.
