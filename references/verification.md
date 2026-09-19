# Verification

Verification turns a plausible change into an evidenced change.

## Evidence hierarchy

Prefer evidence that exercises affected behavior directly:

1. reproduction or regression test,
2. focused unit or component tests,
3. integration or contract tests,
4. compiler, type checker, linter, and static analysis,
5. broader suites and builds,
6. manual inspection where execution is unavailable.

Static inspection supports a conclusion but does not substitute for an executable check when one is reasonably available.

## Use repository-defined checks first

Look for contributor documentation, make targets, package scripts, task-runner configuration, language build files, continuous-integration workflows, and test configuration.

## Narrow before broad

Run the fastest focused check that can fail for the behavior being changed, then broaden verification.

## Failure handling

When a check fails, determine whether the current change caused it, preserve useful output, fix in-scope causes, rerun the relevant check, and broaden verification again when appropriate.

Do not repeatedly rerun nondeterministic failures until they happen to pass.

## Environmental limitations

If a check cannot run because of missing tools, services, credentials, platform features, or network access, state the exact limitation.

Do not install packages, modify global state, start external services, or change repository configuration merely to manufacture successful verification unless the task permits it.

## Completion report

Use three evidence classes:

- **Verified** — command or test was run and result observed.
- **Reasoned** — conclusion comes from inspection or proof-like reasoning.
- **Not verified** — relevant check was not run, with reason.

A good completion report is short and falsifiable.
