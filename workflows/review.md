# Review workflow

1. Understand intended behavior and relevant surrounding code.
2. Review the diff before reviewing file snapshots so scope and semantic change are visible.
3. Check correctness and data integrity, then security, compatibility, concurrency, test evidence, complexity, and finally non-automated style.
4. Validate findings against callers, contracts, and execution paths before asserting impact.
5. Assign severity using [review rubric](../references/review-rubric.md).
6. Lead the result with concrete findings. If none block the change, state verification limits and residual risk rather than claiming perfection.

Do not present speculative preferences as defects.
