# Performance and concurrency

## Measure before optimizing

Define the metric and representative workload before changing code: latency distribution, throughput, CPU, memory, I/O, query count, contention, startup time, or artifact size.

Use a benchmark or profile. Optimize the measured bottleneck rather than a visually suspicious line.

## Preserve correctness

An optimization is incomplete if it weakens correctness, observability, cancellation, error handling, or maintainability without an explicit trade-off.

## Algorithmic work

Check asymptotic behavior alongside actual input size, cardinality, allocation, batching, round trips, query plans, serialization cost, and cache locality.

Watch for N+1 queries and repeated remote calls in loops.

## Concurrency invariants

Identify shared mutable state, ownership, synchronization, ordering, cancellation, timeout, lifecycle, and shutdown semantics before changing concurrent code.

Do not add concurrency merely to reduce apparent latency without measuring contention and downstream capacity.

## Common risks

Review for data races, deadlocks, lost updates, check-then-act races, duplicate work, unbounded queues or tasks, blocking work on event loops, cancellation leaks, resource leaks, starvation, and retry storms.

## Backpressure and limits

Bound externally driven work. Queues, pools, retries, batches, and parallelism should have explicit limits consistent with downstream capacity.

## Caches

Define key semantics, freshness, eviction, size bounds, concurrency behavior, negative caching, failure behavior, and observability before introducing a cache.
