---
name: engineering-quality
description: Apply disciplined engineering-quality practices when implementing features, fixing defects, refactoring, reviewing changes, debugging failures, or optimizing performance. Use when correctness, scoped changes, tests, compatibility, security, maintainability, or verification evidence matter. Do not use for purely explanatory work that neither changes nor reviews code.
---

# Engineering Quality

Use this playbook to improve code without substituting generic preferences for repository context.

## Operating priorities

Apply these priorities in order:

1. Correctness and safety.
2. Explicit requirements, invariants, and compatibility.
3. Repository-local conventions and architecture.
4. Small, coherent, reviewable changes.
5. Maintainability and clarity.
6. Performance when evidence shows it matters.

Do not trade a higher priority for a lower one without an explicit reason.

## Start with reconnaissance

Before editing code:

1. Read repository instructions, contributor guidance, build files, and nearby tests.
2. Identify the public or observable behavior affected by the task.
3. Trace the smallest relevant call path and data flow.
4. Find existing patterns that solve a similar problem.
5. Identify likely verification commands from project configuration.
6. Note compatibility, security, concurrency, persistence, and migration boundaries that may be affected.

Prefer repository-defined commands over generic commands. If the repository does not make its checks obvious, use `scripts/project_checks.py` to discover candidates without executing them or installing anything. Treat discovered command names as labels, not proof that execution is safe.

Read [change discipline](references/change-discipline.md) when the task touches more than one concern or starts expanding in scope.

## Establish the contract

Before implementation, state internally:

- the behavior that must change,
- the behavior that must remain unchanged,
- the relevant invariants,
- the expected failure behavior,
- the compatibility boundary,
- the evidence that would demonstrate completion.

Do not invent requirements that are not supported by the task or repository.

For public interfaces, serialized data, schemas, command-line behavior, events, or persisted state, read [API and compatibility](references/api-compatibility.md).

## Select the workflow

Use the narrowest applicable workflow:

| Work | Workflow |
| --- | --- |
| New or changed behavior | [Feature](workflows/feature.md) |
| Defect or regression | [Bug fix](workflows/bug-fix.md) |
| Behavior-preserving structural change | [Refactor](workflows/refactor.md) |
| Change assessment | [Review](workflows/review.md) |
| Unknown failure cause | [Debug](workflows/debug.md) |
| Latency, throughput, memory, or contention | [Performance](workflows/performance.md) |

When work spans several categories, keep the implementation split into coherent stages and apply each workflow only where relevant.

## Make the change

Follow these rules:

- Prefer the smallest coherent change that fully satisfies the contract.
- Keep unrelated cleanup out of the change.
- Reuse existing abstractions when they are still appropriate.
- Do not create an abstraction solely to remove superficial duplication.
- Do not add a dependency when existing code or standard facilities are sufficient.
- Preserve names, layout, error conventions, and control-flow style unless there is a concrete reason to change them.
- Treat numeric thresholds such as function length, complexity, coverage, and diff size as investigation signals, not universal quality laws.
- Keep behavior changes and substantial refactors separate whenever practical.
- Add or update tests for changed behavior and regressions.

For deeper design guidance, read [principles](references/principles.md) and [testing](references/testing.md). For externally controlled input, authorization, secrets, command execution, parsing, cryptography, or sensitive data, read [security](references/security.md).

## Verify with evidence

Verification is part of the implementation, not a final formality.

Use the strongest relevant checks available, usually in this order:

1. Focused tests for changed behavior.
2. Formatter or formatting check.
3. Linter and static analysis.
4. Type checking or compilation.
5. Broader unit and integration tests.
6. Build or packaging checks.
7. Risk-specific checks such as migration tests, race detection, security scans, benchmarks, or compatibility tests.

Do not claim a check passed unless it was actually run and its result observed.

Do not install dependencies, update lockfiles, rewrite generated files, or run destructive commands merely to satisfy verification unless the task requires that action.

Read [verification](references/verification.md) for evidence rules and failure handling.

## Review the diff

Before completion, review the resulting diff rather than only the final files.

Check:

- contract compliance,
- edge and failure cases,
- unintended behavior changes,
- data validation and trust boundaries,
- authorization and information exposure,
- resource lifetime and cleanup,
- concurrency and ordering,
- API and data compatibility,
- test quality,
- unnecessary complexity,
- unrelated edits.

Use [review rubric](references/review-rubric.md) for severity and reporting.

For performance-sensitive or concurrent code, also read [performance and concurrency](references/performance-concurrency.md).

## Respect language conventions

Local repository conventions have precedence. When local guidance is absent, use the relevant section in [language profiles](references/language-profiles.md). Prefer official formatters and ecosystem-standard tooling over hand-enforced formatting rules.

## Completion contract

A completed change must distinguish:

- **Verified**: checks actually run and their outcomes.
- **Reasoned**: conclusions supported by code inspection but not executed.
- **Not verified**: relevant checks that could not be run, with the concrete reason.

Never represent reasoning as execution evidence. Never hide a failing check behind unrelated cleanup or retries.

Keep the final report concise: what changed, why, what was verified, and any remaining risk.
