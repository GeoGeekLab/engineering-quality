# Bug-fix workflow

1. Establish the smallest reliable reproduction from a test, failing command, log evidence, or clearly traceable state.
2. Trace backward from the failure to the earliest incorrect state or decision; distinguish root cause from symptom.
3. When practical, add a regression test that fails before the fix and passes after it.
4. Apply the narrowest fix at the earliest appropriate boundary that restores the invariant.
5. Check adjacent boundary cases, alternate call paths, concurrency, time behavior, and compatibility.
6. Run the regression test, relevant local suite, and risk-specific checks.

If the original reproduction cannot be automated, rerun it explicitly and record the result.
