<div align="center">

# engineering-quality

**Make coding agents prove their patches.**

`RECON → CONTRACT → CHANGE → VERIFY → REVIEW → EVIDENCE`

[![CI](https://github.com/GeoGeekLab/engineering-quality/actions/workflows/ci.yml/badge.svg)](https://github.com/GeoGeekLab/engineering-quality/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/GeoGeekLab/engineering-quality?style=flat-square)](https://github.com/GeoGeekLab/engineering-quality/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white)](.github/workflows/ci.yml)

**Less vibes. More invariants.**

<br>

<img src="assets/mascot/evi.jpg" alt="Evi" width="420">

</div>

## What it is

`engineering-quality` is a portable Agent Skill for implementation, review, debugging, refactoring, compatibility, security, and verification work.

It gives coding agents a compact operating protocol:

```text
read the repo
    ↓
model the contract
    ↓
patch the smallest coherent surface
    ↓
try to break it
    ↓
inspect the diff
    ↓
show the evidence
```

The point is simple:

```text
plausible patch ≠ correct patch
green test       ≠ complete evidence
clean diff        ≠ safe rollout
works             ≠ verified
```

## Install

### Codex

```text
$skill-installer Install engineering-quality from https://github.com/GeoGeekLab/engineering-quality
```

Manual install:

```bash
git clone https://github.com/GeoGeekLab/engineering-quality.git \
  ~/.agents/skills/engineering-quality
```

### Claude Code

Standalone Skill:

```bash
git clone https://github.com/GeoGeekLab/engineering-quality.git \
  ~/.claude/skills/engineering-quality
```

Plugin development:

```bash
claude --plugin-dir /path/to/engineering-quality
```

### ChatGPT

1. Open the [latest release](https://github.com/GeoGeekLab/engineering-quality/releases/latest).
2. Download `engineering-quality-<version>.zip`.
3. Open **Plugins → Skills → Create → Upload from your computer**.
4. Upload the ZIP.

### Cross-agent installer

```bash
npx -y skills@1.7.0 add GeoGeekLab/engineering-quality
```

Host setup notes: [docs/compatibility.md](docs/compatibility.md)

## Protocol

### 1. RECON

Read before editing.

- repository instructions
- architecture and ownership
- nearby tests
- public behavior
- data flow
- existing patterns
- verification commands
- compatibility and security surfaces

### 2. CONTRACT

Write down the invariant.

```text
must change
must stay stable
must reject
must remain compatible
must be verified
```

### 3. CHANGE

Keep the patch tight.

- no drive-by cleanup
- no abstraction for cosmetic deduplication
- no dependency without a reason
- no behavior change hidden inside a refactor
- no hand-editing generated output when a source generator exists

### 4. VERIFY

Start narrow, then widen.

```text
regression
→ focused tests
→ static checks
→ type / compile
→ broader suite
→ build / package
→ risk-specific probes
```

### 5. REVIEW

Read the diff like an attacker and a maintainer.

Check:

- correctness
- edge cases
- failure behavior
- compatibility
- authorization
- path and trust boundaries
- concurrency
- cleanup
- migrations
- generated code
- scope creep

### 6. EVIDENCE

Report what actually happened.

```text
Verified     = executed and observed
Reasoned     = supported by inspection
Not verified = still open
```

## Where it bites

The Skill is intentionally strict around failure modes that frequently survive a normal patch review:

```text
path traversal        → symlink escape → TOCTOU
object lookup         → authorization → cross-tenant access
schema rename         → mixed versions → rollback
parallelism           → ordering → cancellation / cleanup
public API change     → error type / code / message compatibility
generated code        → source of truth → generator drift
test failure          → retry luck → real flake cause
verification          → command exists → command actually ran
focused task          → unrelated red test → scope expansion
```

## Behavioral evals

The repository ships **17 executable miniature-repository scenarios**.

Current coverage includes:

- minimal bug fixes
- public contract evolution
- wrong abstractions
- verification evidence
- path traversal and symlink escape
- TOCTOU file replacement
- tenant authorization
- speculative performance work
- bounded concurrency and cancellation
- behavior-preserving refactors
- dependency pressure
- flaky tests
- mixed-version and rollback-safe migrations
- generated-code drift
- swallowed errors
- public error compatibility
- scope expansion under unrelated failures

Validate the suite:

```bash
python scripts/run_evals.py --validate-only
```

Run one case:

```bash
python scripts/run_evals.py \
  --case security-toctou \
  --agent-command 'my-agent --prompt {task}' \
  --adapter-label my-agent \
  --allow-workspace-execution
```

Run the full suite:

```bash
python scripts/run_evals.py \
  --agent-command 'my-agent --prompt {task}' \
  --adapter-label my-agent \
  --allow-workspace-execution \
  --output eval-results/my-agent.json
```

### Skill vs no-Skill

Native Codex and Claude Code adapters support a clean A/B switch:

```text
--skill-mode disabled
--skill-mode enabled
```

Repeat runs with fresh workspaces:

```bash
python scripts/run_evals.py \
  --agent-command '{python} {repo}/scripts/host_eval_adapter.py codex --model MODEL --skill-mode disabled' \
  --adapter-label codex-MODEL-no-skill \
  --repeat 5 \
  --allow-workspace-execution \
  --output eval-results/no-skill.json

python scripts/run_evals.py \
  --agent-command '{python} {repo}/scripts/host_eval_adapter.py codex --model MODEL --skill-mode enabled' \
  --adapter-label codex-MODEL-skill \
  --repeat 5 \
  --allow-workspace-execution \
  --output eval-results/skill.json
```

Compare:

```bash
python scripts/compare_eval_results.py \
  eval-results/no-skill.json \
  eval-results/skill.json \
  --output eval-results/comparison.md
```

The comparison reports:

```text
case pass rate
check-type pass rate
changed-file scope
agent wall-clock time
```

Qualitative rubric items stay visible for review instead of being flattened into one score.

More: [evals/README.md](evals/README.md)

## Hidden checks

The eval harness keeps second-order probes outside the fixture shown to the agent.

Examples:

```text
security-boundary
  visible:  ../ traversal
  hidden:   symlink escape

security-toctou
  visible:  normal nested read
  hidden:   replace validated file before open

concurrent-worker
  visible:  bounded concurrency + order
  hidden:   propagate failure + stop pending work

database-migration-rollout
  visible:  additive schema migration
  hidden:   backfill + old writer + rollback-safe write

generated-code-change
  visible:  generator + generated file
  hidden:   rerun generator and require zero diff
```

Two harness checks exist specifically for these cases:

- `final_not_claim_any` — rejects positive verification claims while allowing negated wording such as `not fully verified`.
- `command_no_changes` — executes a command and fails if it changes the workspace.

Inline hidden Python checks are compiled during `--validate-only`.

## Repository checks

Discover likely project checks:

```bash
python scripts/project_checks.py /path/to/repository
```

Run discovered checks after reviewing them:

```bash
python scripts/project_checks.py /path/to/repository \
  --run --trust-repository
```

Run this repository's full quality contract:

```bash
make check
```

That covers:

```text
repository integrity
├── Skill + host metadata
├── local links
├── governance contract
├── immutable GitHub Action pins
├── VERSION + CHANGELOG consistency
├── behavioral eval schema
├── behavioral eval fixtures
├── Python compilation
├── unit tests
├── package verification
└── release invariants
```

CI runs on Python **3.10**, **3.12**, and **3.14**.

## Release integrity

Tagged releases publish:

```text
engineering-quality-<version>.zip
engineering-quality-<version>.zip.sha256
```

The ZIP includes `MANIFEST.sha256`.

Verify:

```bash
sha256sum -c engineering-quality-<version>.zip.sha256

gh attestation verify engineering-quality-<version>.zip \
  --repo GeoGeekLab/engineering-quality
```

Package CI does a full round trip:

```text
build
→ SHA-256
→ upload
→ delete local copy
→ download
→ SHA-256
```

More: [docs/release.md](docs/release.md)

## Review protocol

Review findings are ranked by impact.

| Severity | Meaning |
| --- | --- |
| **Blocker** | Incorrect behavior, data loss, security exposure, broken contract, or reliably failing verification. |
| **Major** | Material failure under realistic conditions or significant operational / maintenance risk. |
| **Minor** | Bounded clarity, resilience, test-quality, or consistency issue. |
| **Note** | Optional improvement, question, or follow-up. |

A useful finding answers four questions:

```text
what can fail?
under what condition?
why does this diff allow it?
what evidence closes the finding?
```

## Quality model

Not this:

```text
quality =
    more abstraction
  + more comments
  + more tests
  + more patterns
```

Closer to this:

```text
quality =
    correctness
  + clarity
  + compatibility
  + security
  + verifiability
  - accidental complexity
  - unnecessary churn
```

No magic number. No style points.

## Repository layout

```text
SKILL.md                    core protocol
agents/openai.yaml          OpenAI Skill metadata
.claude-plugin/plugin.json  Claude Code plugin metadata

workflows/
├── feature.md
├── bug-fix.md
├── refactor.md
├── review.md
├── debug.md
└── performance.md

references/
├── principles.md
├── testing.md
├── verification.md
├── security.md
├── api-compatibility.md
├── performance-concurrency.md
└── change-discipline.md

scripts/
├── project_checks.py
├── run_evals.py
├── host_eval_adapter.py
├── compare_eval_results.py
├── package_skill.py
└── validate_skill.py

evals/
├── cases.json
├── schema.json
└── result-schema.json

docs/                       compatibility / release / distribution
assets/mascot/              Evi
.github/                    CI / release / repo policy
```

## Project status

- GitHub Actions are pinned to immutable commit SHAs.
- `main` and `v*.*.*` are protected by repository rulesets.
- Releases ship SHA-256 checksums and GitHub artifact attestations.
- Behavioral evals use fresh temporary Git repositories.
- The staged Skill payload is hashed before and after each run.
- Eval credentials are forwarded only when explicitly selected.
- Distribution ZIPs contain runtime Skill files, not repository-maintenance tooling.

## Contributing

Bring a failure mode, an invariant, or a measurable maintenance win.

Start with [CONTRIBUTING.md](CONTRIBUTING.md).

Security issues: [SECURITY.md](SECURITY.md)  
Governance: [GOVERNANCE.md](GOVERNANCE.md)  
Code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

**Read the repo. Respect the contract. Keep the patch tight. Prove the result.**

`works ≠ verified`

</div>
