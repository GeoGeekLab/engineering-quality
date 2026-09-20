<div align="center">

# engineering-quality

**Evidence-first engineering quality for coding agents.**

A portable Agent Skill for **Codex, Claude Code, ChatGPT, and other coding agents** that makes implementation, code review, testing, debugging, refactoring, compatibility, and security work more disciplined and verifiable.

`read the repo → model the contract → patch narrowly → try to break it → inspect the diff → show the evidence`

[![CI](https://github.com/GeoGeekLab/engineering-quality/actions/workflows/ci.yml/badge.svg)](https://github.com/GeoGeekLab/engineering-quality/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/GeoGeekLab/engineering-quality?style=flat-square)](https://github.com/GeoGeekLab/engineering-quality/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white)](.github/workflows/ci.yml)

**Less taste. More invariants.**

</div>

## Why this exists

Coding agents are very good at producing plausible patches. Plausible is not the same as correct.

A patch can compile and still violate a public contract. Tests can pass while missing the failure mode. A refactor can be elegant while quietly widening scope. A verification command can itself execute untrusted repository code.

engineering-quality gives coding agents a compact engineering protocol:

```text
RECON → CONTRACT → CHANGE → VERIFY → REVIEW → EVIDENCE
```

The goal is not more process. The goal is a patch you can defend.

## Quick start

Host instructions were last checked against official vendor documentation on **2026-09-20**. See [host compatibility](docs/compatibility.md) for exact evidence levels.

### Codex

For local setup or experimentation:

```text
$skill-installer Install engineering-quality from https://github.com/GeoGeekLab/engineering-quality
```

Manual user install:

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

Or load the repository as a native single-skill plugin during development:

```bash
claude --plugin-dir /path/to/engineering-quality
```

### ChatGPT

On eligible ChatGPT Business, Enterprise, Healthcare, and Edu workspaces:

1. open the [latest GitHub Release](https://github.com/GeoGeekLab/engineering-quality/releases/latest),
2. download `engineering-quality-<version>.zip`,
3. in ChatGPT open **Plugins → Skills → Create → Upload from your computer**,
4. upload the ZIP.

### Optional cross-agent installer

The third-party Vercel Labs CLI is available as a convenience:

```bash
npx -y skills@1.7.0 add GeoGeekLab/engineering-quality
```

It is not treated as the vendor-native distribution authority for OpenAI or Anthropic.

## What changes when an agent uses it

Without an explicit engineering contract, a coding-agent answer can look like:

> Fixed the parser, cleaned up nearby helpers, and the tests look good.

engineering-quality pushes toward something more auditable:

> Contract: comma-delimited input remains valid; semicolon-delimited input must fail.  
> Scope: changed the parser and its regression test only; unrelated utility code was left untouched.  
> Verified: the focused regression test and repository checks passed.  
> Not verified: no production traffic replay was available.

That difference is the project.

It does not prescribe one architecture, testing framework, or coding style. It asks the agent to identify the repository's actual contract, make the smallest coherent change, attack that change with relevant checks, inspect the resulting diff, and state exactly what the evidence proves.

## Core guarantees

The Skill is built around a few priorities:

- **Correctness before aesthetics.** A beautiful implementation of the wrong behavior is still wrong.
- **Repository-local contract before generic taste.** Existing architecture, compatibility, error semantics, and tooling are evidence.
- **Small coherent changes.** Required tests, migrations, and docs belong in the patch; drive-by cleanup does not.
- **Security is part of correctness.** Trust boundaries, credentials, command execution, and unsafe defaults are first-class review concerns.
- **Compatibility is observable behavior.** Public APIs, schemas, CLI behavior, persistence, and deployment overlap are contracts until proven otherwise.
- **Evidence before confidence.** `Verified`, `Reasoned`, and `Not verified` mean different things.

## Evidence, not badges

This repository tries to make its own quality claims inspectable.

### Repository and package evidence

`make check` validates:

```text
repository integrity
  ├── Skill + host metadata
  ├── local links + governance contract
  ├── immutable GitHub Action pins
  ├── VERSION + CHANGELOG consistency
  ├── executable behavioral-eval fixtures
  ├── Python compilation + unit tests
  ├── deterministic package verification
  └── release-readiness invariants
```

CI runs the contract on Python **3.10**, **3.12**, and **3.14**.

The package job performs a real artifact round trip:

```text
build → SHA-256 → upload → delete local copy → download → SHA-256
```

### Release integrity

Tagged releases publish:

```text
engineering-quality-<version>.zip
engineering-quality-<version>.zip.sha256
```

The ZIP also contains an internal `MANIFEST.sha256`.

Verify a downloaded archive:

```bash
sha256sum -c engineering-quality-<version>.zip.sha256

gh attestation verify engineering-quality-<version>.zip \
  --repo GeoGeekLab/engineering-quality
```

Release artifacts are attested in GitHub Actions before publication. See [release engineering](docs/release.md).

### Behavioral evaluations

The repository contains **14 executable miniature-repository scenarios** covering defect fixes, compatibility changes, security boundaries, concurrency, dependency pressure, flaky tests, migrations, generated code, swallowed errors, and scope expansion.

Validate the harness:

```bash
python scripts/run_evals.py --validate-only
```

Run a real host through the adapter layer when credentials and the native CLI are available. See [behavioral evaluations](evals/README.md).

The evidence boundary is deliberate: CI proves that the harness and deterministic checks work. It does **not** claim that a real Codex, Claude Code, ChatGPT, or other model passed the suite unless an actual host run produced that evidence.

## How it works

| Stage | Agent behavior |
| --- | --- |
| **RECON** | Read architecture, conventions, ownership, checks, and sharp edges before editing. |
| **CONTRACT** | State what must change, what must remain stable, and what would prove success. |
| **CHANGE** | Modify the smallest coherent surface that satisfies the contract. |
| **VERIFY** | Try to falsify the patch with focused tests, static checks, builds, and risk-specific probes. |
| **REVIEW** | Inspect the complete diff for correctness, compatibility, security, concurrency, maintainability, and accidental scope. |
| **EVIDENCE** | Separate executed proof from inspection-based reasoning and unverified claims. |

`SKILL.md` is intentionally a bootloader rather than an encyclopedia. It loads the invariant set first, then routes into focused workflows and references only when needed.

## Tools included

### Discover repository checks safely

```bash
python scripts/project_checks.py /path/to/repository
```

Discovery does not execute the commands it finds.

A target named `test`, `lint`, or `check` is not automatically safe: Make recipes, package scripts, test discovery, wrappers, compiler hooks, and plugins can execute arbitrary repository-controlled code.

Execution therefore requires an explicit trust decision:

```bash
python scripts/project_checks.py /path/to/repository \
  --run --trust-repository
```

### Run behavioral evals

Generic adapter:

```bash
python scripts/run_evals.py \
  --agent-command 'my-agent --prompt {task}' \
  --adapter-label my-agent \
  --allow-workspace-execution \
  --output eval-results/my-agent.json
```

Native Codex and Claude Code adapter examples are documented in [evals/README.md](evals/README.md).

The runner uses fresh miniature Git repositories, hides the evaluation rubric from the agent, checks that the staged Skill was not mutated, and only forwards environment variables explicitly selected by the evaluator.

## Where it helps most

engineering-quality is designed for tasks where a plausible edit is not enough:

- feature implementation with an existing contract,
- bug fixes that need regression evidence,
- behavior-preserving refactors,
- code review focused on concrete failure modes,
- debugging under incomplete evidence,
- API/schema/migration compatibility,
- security-sensitive boundaries,
- concurrency and performance changes,
- generated-code workflows,
- coding-agent evaluation and verification.

It is not a linter, formatter, static analyzer, or replacement for the repository's own tests. It composes with those tools.

## Review protocol

Findings are classified by impact rather than taste:

| Severity | Meaning |
| --- | --- |
| **Blocker** | Incorrect behavior, data loss, security exposure, broken contract, or reliably failing verification. |
| **Major** | Material failure under realistic conditions or significant maintenance/operational risk. |
| **Minor** | Bounded clarity, resilience, test-quality, or consistency issue. |
| **Note** | Optional improvement, question, or follow-up. |

A useful review finding should answer:

```text
what can fail?
under what condition?
why does this diff make that possible?
what evidence would close the finding?
```

## Quality model

Not this:

```text
quality = more abstraction + more comments + more tests + more patterns
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

This is an ordering of concerns, not a numeric score.

## Repository structure

```text
SKILL.md                    portable behavioral contract
agents/openai.yaml          OpenAI Skill metadata
.claude-plugin/plugin.json  Claude Code plugin metadata
workflows/                  feature / bug-fix / refactor / review / debug / performance
references/                 verification / testing / security / compatibility / concurrency
scripts/                    validation / packaging / project checks / eval adapters
evals/                      executable behavioral fixtures + result schema
docs/                       compatibility / release / governance / distribution / mascot
assets/mascot/              Evi mascot + identity-system artwork
.github/                    CI / release / issue forms / CODEOWNERS
```

The release ZIP intentionally contains the runtime Skill payload rather than repository-maintenance files.

## Project status and trust boundaries

- Host installation guidance was last verified on **2026-09-20**.
- GitHub Actions dependencies are pinned to immutable commit SHAs and maintained by Dependabot.
- `main` and `v*.*.*` are protected by active GitHub rulesets.
- Releases use SHA-256 checksums and GitHub artifact attestations.
- Repository-defined checks execute only after explicit repository trust.
- Behavioral-eval reports distinguish deterministic evidence from qualitative rubric review.
- OpenAI Plugin Directory and Claude marketplace publication are **not** claimed until those external review/publication steps actually happen.

See [compatibility](docs/compatibility.md), [release engineering](docs/release.md), [governance](GOVERNANCE.md), [security](SECURITY.md), and [distribution](docs/distribution.md).

## Mascot: Evi

<div align="center">
  <img src="assets/mascot/evi.jpg" alt="Evi, the engineering-quality British Shorthair mascot" width="300">
</div>

**Evi (伊维)** is the engineering-quality mascot: a clean silver-blue British Shorthair kitten designed around the same traits the project values — careful, trustworthy, gentle, smart, and calm.

The canonical character is deliberately simple: **no badge, collar, clothes, tools, magnifying glass, ID card, or engineering props attached to the cat**. The mascot should stay recognizably Evi even when removed from all technical context.

See <a href="docs/mascot.md">the mascot identity guide</a> and <a href="assets/mascot/evi-identity-system.jpg">the complete identity-system sheet</a>.

## Contributing

Contributions should address a concrete failure mode or maintenance benefit, not merely introduce a preferred style.

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Participation is covered by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), and vulnerabilities follow [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

**Read the repo. Respect the contract. Keep the patch tight. Prove the result.**

`works ≠ verified`

</div>
