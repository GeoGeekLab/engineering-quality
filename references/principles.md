# Engineering principles

These principles guide judgment when no more specific repository rule applies.

## Optimize for understanding

Code is maintained far more often than it is initially written. Prefer designs whose behavior, ownership, and failure modes can be understood locally.

Favor explicit data flow over hidden coupling, narrow interfaces over broad reach, cohesive modules over collections of thin forwarding layers, stable invariants over repeated defensive checks, and names that expose intent.

Short code is not automatically simple. A compact implementation that couples unrelated concerns can be harder to change than a longer implementation with clear boundaries.

## Keep complexity where it belongs

Move complexity behind an interface only when the interface is meaningfully simpler than the implementation. An abstraction that merely renames a sequence of calls can increase indirection without reducing complexity.

A useful abstraction should hide a volatile detail, enforce an invariant, centralize a policy, reduce caller concepts, or provide a stable boundary around a changing subsystem.

## Prefer current needs over speculative flexibility

Design for requirements that are known or strongly evidenced. Avoid extension points, configuration knobs, generalized factories, and dependency layers that have no present use.

Future change is easier when current code is clear, well-tested, and loosely coupled.

## Treat duplication as evidence, not an automatic command

Before consolidating duplicated code, ask whether it represents the same concept, changes for the same reasons, can be named around a stable responsibility, and makes callers easier to understand.

If the answer is unclear, duplication can be cheaper than the wrong abstraction.

## Make invalid states difficult to represent

Validate and normalize data at trust boundaries where practical. Convert loose external input into representations with stronger invariants before it reaches domain logic.

Avoid scattering the same validation throughout internal code.

## Prefer boring dependencies

Every dependency adds upgrade, licensing, security, compatibility, and operational cost. Check existing facilities and the standard platform before adding one.

## Comments explain decisions

Comments are most valuable for non-obvious constraints, invariants, protocol requirements, workarounds, and trade-offs that future maintainers might otherwise undo. Do not restate clear code.

## Improve without widening the task

A change should leave the touched area no worse than before, but broad cleanup is not automatically part of every task. Larger refactors should normally be separate.
