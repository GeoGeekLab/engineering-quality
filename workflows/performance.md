# Performance workflow

1. Define the metric, workload, and target.
2. Establish a reproducible baseline with a benchmark, profile, query plan, or production-equivalent measurement.
3. Identify the measured bottleneck rather than guessing from code appearance.
4. Change one dominant factor while preserving correctness, cancellation, and failure behavior.
5. Compare against the same baseline and account for variance and warm-up effects.
6. Check secondary costs such as memory, CPU, I/O, complexity, contention, and operational risk.
7. Keep a stable regression benchmark or test when practical.
