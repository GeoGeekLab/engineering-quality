# Debug workflow

1. Capture the exact symptom, inputs, environment, timing, and last known good state.
2. Reduce the reproduction while preserving the failure.
3. Form a small set of competing hypotheses that make different predictions.
4. Use logs, assertions, tracing, debugger state, targeted tests, or controlled input changes to eliminate hypotheses one distinction at a time.
5. Trace the symptom back to the earliest state that violates the intended invariant.
6. Fix the responsible boundary rather than a downstream symptom.
7. Remove temporary diagnostics and preserve a regression test or durable diagnostic when useful.

Do not make broad code changes as a debugging technique.
