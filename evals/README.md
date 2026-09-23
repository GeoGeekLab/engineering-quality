# Behavioral evaluations

The evaluation suite exercises engineering decisions in temporary miniature Git repositories.

It is designed to answer a narrower and more defensible question than a benchmark score:

> Given a concrete repository and task, what did an agent actually change, what executable checks passed, and which qualitative expectations still require review?

The suite does not reduce engineering quality to one numeric score.

## Evidence layers

An evaluation result separates four kinds of evidence:

1. **Harness executed** — the runner materialized the fixture, invoked the configured agent adapter, captured output, and inspected the resulting workspace.
2. **Agent behavior executed** — the recorded diff and transcript came from an actual adapter process, not from static fixture validation.
3. **Deterministic checks executed** — file invariants, change-scope rules, tests, generators, or other commands were actually evaluated.
4. **Qualitative rubric not automatically judged** — `must_do` and `must_not_do` remain explicit review criteria unless a case maps them to deterministic checks.

A fake or deterministic adapter used by unit tests proves only that the harness works. It is not evidence that Codex, ChatGPT, Claude Code, or another coding agent passes the behavioral suite.

## Case structure

`cases.json` contains 14 executable scenarios. Each case defines:

- `id`: stable kebab-case identifier,
- `task`: the instruction exposed to the agent,
- `must_do`: qualitative behavior expected from the skill contract,
- `must_not_do`: qualitative behavior that violates the contract,
- `fixture.files`: the miniature repository materialized for the run,
- `checks`: deterministic evidence that can be evaluated after the agent exits.

The agent receives the task and repository fixture. The qualitative rubric is not injected into the agent prompt by the runner.

The skill itself is also staged through the same runtime payload contract used by packaging. The agent sees the staged `SKILL.md`, references, workflows, and runtime helper files, but not this repository's `evals/`, `tests/`, CI files, or evaluation runner source. This prevents a capable agent from simply reading the hidden rubric through the source checkout.

`schema.json` documents the case format. `result-schema.json` documents the machine-readable report envelope.

## Deterministic checks

The runner currently supports:

- required or allowed changed-file sets,
- file existence and absence,
- unchanged-file assertions,
- required or forbidden file content,
- final-output term assertions,
- executable commands with optional repetition.

Executable commands are useful for regression tests, compatibility tests, generators, and repeated flaky-test checks. They are not treated as inherently safe.

## Validate the suite

Fixture/schema validation is part of the repository quality gate:

```bash
make eval-validate
make check
```

Validation does not invoke an agent.

## Run a real agent adapter

The runner is host-neutral. Supply a command that can operate on the current working directory and accept the task through a placeholder or the exported environment variables.

Example:

```bash
python scripts/run_evals.py \
  --agent-command 'my-agent --prompt {task}' \
  --adapter-label my-agent-current \
  --allow-workspace-execution \
  --output eval-results/my-agent.json
```

Do not put credentials in `--agent-command` arguments. The report stores only the non-sensitive `--adapter-label`, not the raw adapter command. Agent stdout/stderr is preserved as evidence and may itself contain sensitive data, so treat result files accordingly.

Available command placeholders:

- `{task}`
- `{workspace}`
- `{skill}`
- `{case_id}`
- `{repo}`
- `{python}`

The same values are exported as:

- `EQ_EVAL_TASK`
- `EQ_EVAL_WORKSPACE`
- `EQ_EVAL_SKILL_PATH`
- `EQ_EVAL_CASE_ID`

Use `--case <id>` repeatedly to run a subset.

## Vendor-native adapters

The repository includes `scripts/host_eval_adapter.py` for current Codex and Claude Code CLI paths.

Codex:

```bash
python scripts/run_evals.py \
  --agent-command '{python} {repo}/scripts/host_eval_adapter.py codex' \
  --adapter-label codex-current \
  --pass-env CODEX_API_KEY \
  --allow-workspace-execution \
  --output eval-results/codex.json
```

The adapter installs the staged Skill into an isolated temporary user Skill directory and calls `codex exec` with an ephemeral workspace-write sandbox.

Claude Code:

```bash
python scripts/run_evals.py \
  --agent-command '{python} {repo}/scripts/host_eval_adapter.py claude-code' \
  --adapter-label claude-code-current \
  --pass-env ANTHROPIC_API_KEY \
  --allow-workspace-execution \
  --output eval-results/claude-code.json
```

The Claude adapter uses non-interactive print mode with `--bare`, auto permissions, no prompt responder, no session persistence, and an explicit staged Skill directory.

Adapter unit tests validate command construction and staged-skill handling. Those tests are **not** real model runs. A host is behaviorally verified only after an actual authenticated CLI run produces a saved report.

Each case receives a fresh runtime Skill staging directory. The harness hashes it before and after the agent exits. Any mutation produces a failing `skill_payload_integrity` check, so one case cannot rewrite the Skill used by later cases.

### Compare Skill vs no-Skill behavior

The native adapter can run the same task without exposing the staged Skill. The baseline is created by removing the Skill from the host environment, not by adding a prompt that tells the model to ignore it.

Keep the host, explicit model ID, case set, credentials, execution flags, and task text identical between conditions.

For comparative runs, prefer the paired runner. It executes the two conditions adjacent to each other for every case and alternates which condition goes first across cases and repetitions. This reduces systematic time/order bias relative to running one complete condition and then the other.

```bash
python scripts/run_ab_evals.py \
  --baseline-agent-command '{python} {repo}/scripts/host_eval_adapter.py codex --model MODEL --skill-mode disabled' \
  --skill-agent-command '{python} {repo}/scripts/host_eval_adapter.py codex --model MODEL --skill-mode enabled' \
  --baseline-label codex-MODEL-no-skill \
  --skill-label codex-MODEL-skill \
  --pass-env CODEX_API_KEY \
  --repeat 5 \
  --allow-workspace-execution \
  --output-dir eval-results/codex-MODEL
```

The output directory contains:

- `baseline.json` — raw no-Skill evidence,
- `skill.json` — raw Skill-enabled evidence,
- `experiment.json` — pairing and execution-order metadata,
- `comparison.md` — deterministic case/check rates, diff scope, and wall-clock comparison.

`scripts/compare_eval_results.py` remains available for comparing two previously produced reports. It rejects mismatched case sets, task drift, duplicate run indexes, and unpaired repetition sets.

### Manual real-host smoke workflow

`.github/workflows/real-host-ab.yml` provides a manual Codex smoke path once that workflow is present on the repository default branch.

Its defaults are deliberately explicit rather than floating:

- model: `gpt-5.6`,
- Codex CLI: `0.156.1`,
- case set: all 14 scenarios,
- repeat: 1, producing 28 agent runs.

The workflow also offers a six-case `high-signal` subset and repeat counts of 3 or 5. Larger repetitions increase API usage substantially and must be selected explicitly.

The workflow requires a repository secret named `CODEX_API_KEY`. Use a credential intended for unattended Codex evaluation rather than a broad personal credential. The runner forwards only that named variable to the host adapter; deterministic post-run command checks receive a narrower environment without the key.

The workflow records requested and observed Codex versions, model ID, repository SHA, repeat count, and case set in `metadata.json`, uploads the raw evidence for seven days, and writes the comparison table to the GitHub Actions job summary.

The comparison deliberately does not convert the qualitative `must_do` / `must_not_do` rubric into an automatic score. The infrastructure-only `skill_payload_integrity` check is also excluded from comparative check rates.

For publishable evidence, retain the raw JSON reports and review qualitative rubric items separately. Token usage is not currently normalized across host CLIs, so wall-clock time is the portable cost signal recorded by the harness.

See [host compatibility](../docs/compatibility.md) for the dated vendor documentation basis.

## Execution boundary

The agent adapter is a command chosen by the evaluator and may itself execute code. For publishable or comparative evidence, pass an explicit `--model <model-id>` to the native host adapter and use an adapter label that identifies the host/model configuration; default models can change over time.

The adapter does not inherit the evaluator's complete environment. By default it receives only basic process/runtime variables plus the `EQ_EVAL_*` case context. Credentials and provider configuration must be forwarded deliberately with repeatable `--pass-env NAME` flags. This keeps unrelated API keys, cloud credentials, and local configuration out of the evaluated process.

After the agent exits, some deterministic checks may execute code from the agent-modified workspace. That is disabled unless `--allow-workspace-execution` is supplied. The flag acknowledges this execution boundary; it does not make generated code safe.

Command checks receive an even narrower environment and a fresh temporary `HOME` / `USERPROFILE`, rather than the evaluator's real home directory. Filesystem and network isolation still require an external sandbox, container, VM, or restricted runner when the threat model requires it.

## Result semantics

Each case is reported as:

- `passed` — the agent command exited successfully and every configured deterministic check passed,
- `failed` — the agent failed or at least one deterministic check failed,
- `incomplete` — a relevant command check was intentionally not executed.

A `passed` case means the configured deterministic evidence passed. It does **not** mean every qualitative `must_do` item was automatically judged.

The report's `evidence_scope` field makes that limitation machine-readable.

## Coverage

The current scenarios cover:

- minimal defect fixes and regression scope,
- public-contract migration,
- incorrect abstraction pressure,
- honest verification reporting,
- path traversal boundaries,
- speculative performance optimization,
- bounded concurrency and ordering,
- behavior-preserving refactoring,
- unnecessary dependency pressure,
- flaky-test repair,
- mixed-version database migration,
- generated-code source-of-truth changes,
- swallowed errors,
- uncontrolled scope expansion.

When the skill contract changes, add or strengthen a case that can distinguish the old behavior from the intended behavior. Prefer executable invariants over prose-only expectations when the behavior can be measured.
