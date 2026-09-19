# Feature workflow

1. Define acceptance examples, affected callers, failure behavior, and compatibility constraints.
2. Trace the existing path from input to effect and find the closest stable integration point.
3. Design the smallest complete slice that can be tested and reviewed coherently.
4. Add or update tests for new behavior and important failure cases.
5. Implement without speculative extension points or unrelated cleanup.
6. Run focused tests first, then repository quality gates and broader tests proportional to risk.
7. Review the diff for contract compliance and unintended public behavior.

If substantial refactoring is required, separate preparatory behavior-preserving work when practical.
