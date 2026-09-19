<div align="center">

# engineering-quality

**Engineering discipline, encoded.**

`correctness → coherence → verification → evidence`

[![CI](https://github.com/GeoGeekLab/engineering-quality/actions/workflows/ci.yml/badge.svg)](https://github.com/GeoGeekLab/engineering-quality/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/GeoGeekLab/engineering-quality?style=flat-square)](https://github.com/GeoGeekLab/engineering-quality/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white)](.github/workflows/ci.yml)
[![Codex](https://img.shields.io/badge/Codex-ready-111111?style=flat-square&logo=openai&logoColor=white)](#codex--one-instruction)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-ready-D97757?style=flat-square&logo=anthropic&logoColor=white)](#claude-code)
[![ChatGPT](https://img.shields.io/badge/ChatGPT-skill-10A37F?style=flat-square&logo=openai&logoColor=white)](#chatgpt)

A portable engineering-quality playbook for implementation, debugging, refactoring, review, performance work, and evidence-based completion.

</div>

<p align="center">
  <img src="docs/assets/architecture.svg" alt="engineering-quality technical architecture" width="100%">
</p>

## Why this exists

Most code-quality guidance fails in one of two ways: it becomes a style manifesto, or it becomes a checklist that cannot prove anything.

**engineering-quality** takes a different position:

- correctness and safety outrank stylistic preference;
- repository-local conventions outrank generic taste;
- changes should be small, coherent, and reviewable;
- tests should encode behavior, not implementation trivia;
- compatibility, security, concurrency, and operability are part of quality;
- measurable concerns should be delegated to compilers, linters, type checkers, test runners, static analysis, and CI;
- completion requires evidence.

It is intentionally conservative about universal thresholds. Function length, coverage, complexity, and diff size are useful signals—not automatic verdicts.

## Install

### Codex — one instruction

Paste this into Codex:

```text
$skill-installer Install engineering-quality from https://github.com/GeoGeekLab/engineering-quality
```

That is the preferred Codex path: the built-in skill installer can fetch the repository and place the skill in a Codex-recognized location.

<details>
<summary><strong>Codex alternatives: cross-agent CLI and manual install</strong></summary>

Install globally with the cross-agent `skills` CLI:

```bash
npx -y skills@latest add GeoGeekLab/engineering-quality -g -a codex -y
```

Or install manually for the current user:

```bash
git clone https://github.com/GeoGeekLab/engineering-quality.git ~/.agents/skills/engineering-quality
```

Codex discovers skills from `.agents/skills` locations. If a newly installed skill is not visible immediately, restart the Codex session.

</details>

### Claude Code

Install globally with the cross-agent `skills` CLI:

```bash
npx -y skills@latest add GeoGeekLab/engineering-quality -g -a claude-code -y
```

Manual installation:

```bash
git clone https://github.com/GeoGeekLab/engineering-quality.git ~/.claude/skills/engineering-quality
```

Start a new Claude Code session after installation if the skill is not picked up by the current session.

### ChatGPT

For the cleanest installation, use the packaged ZIP attached to the latest GitHub Release:

**[Open the latest release](https://github.com/GeoGeekLab/engineering-quality/releases/latest)**

For a development checkout, build the same package locally:

```bash
make package
```

Then upload `dist/engineering-quality-<version>.zip` through the ChatGPT Skills interface available to your workspace.

> [!NOTE]
> ChatGPT Skills availability depends on the workspace plan, admin settings, and current product availability.

See [docs/compatibility.md](docs/compatibility.md) for the maintained host compatibility matrix and installation details.

Platform references: [Codex Skills](https://developers.openai.com/docs/build-skills) · [ChatGPT Skills](https://help.openai.com/en/articles/20001066) · [Claude Skills](https://www.anthropic.com/research/skills) · [skills CLI](https://github.com/vercel-labs/skills)

## Execution model

```text
RECON → CONTRACT → CHANGE → VERIFY → REVIEW → EVIDENCE
```

| Stage | Question |
| --- | --- |
| **Recon** | What does this repository already do, and what conventions does it enforce? |
| **Contract** | What behavior must change, what must remain stable, and what evidence proves completion? |
| **Change** | What is the smallest coherent implementation that satisfies the contract? |
| **Verify** | Which focused tests, static checks, builds, or risk-specific checks can falsify the change? |
| **Review** | What correctness, security, compatibility, concurrency, or maintainability risks remain? |
| **Evidence** | Which claims are verified, reasoned, or not yet verified? |

The core skill stays compact and loads deeper guidance only when the task requires it.

## Repository map

```text
engineering-quality/
├── SKILL.md                     # entry contract + routing
├── VERSION                      # canonical release version
├── workflows/
│   ├── feature.md
│   ├── bug-fix.md
│   ├── refactor.md
│   ├── review.md
│   ├── debug.md
│   └── performance.md
├── references/
│   ├── principles.md
│   ├── change-discipline.md
│   ├── verification.md
│   ├── testing.md
│   ├── security.md
│   ├── api-compatibility.md
│   ├── performance-concurrency.md
│   └── language-profiles.md
├── scripts/
│   ├── project_checks.py
│   ├── validate_skill.py
│   ├── package_skill.py
│   ├── release_check.py
│   └── release_notes.py
├── tests/
├── evals/
│   ├── cases.json
│   ├── schema.json
│   └── README.md
├── docs/
│   ├── compatibility.md
│   ├── foundations.md
│   ├── release.md
│   └── assets/
│       └── architecture.svg
└── .github/workflows/
    ├── ci.yml
    └── release.yml
```

### Progressive loading

`SKILL.md` is the router, not the encyclopedia.

It establishes the invariant set—correctness, scoped changes, local conventions, verification, diff review—and sends the task to the narrowest workflow and reference set. Security guidance is loaded for trust boundaries. Compatibility guidance is loaded for public contracts. Performance and concurrency guidance is loaded only when those risks are present.

That keeps the operating context small while preserving depth.

## Tooling

### Discover project checks

Inspect a repository and print conservative quality commands without running them:

```bash
python scripts/project_checks.py /path/to/repository
```

Execute discovered checks only when you explicitly opt in:

```bash
python scripts/project_checks.py /path/to/repository --run
```

The helper never installs dependencies.

It recognizes common project signals across Python, JavaScript/TypeScript, Go, Rust, JVM projects, .NET, Swift, Dart/Flutter, Make-based projects, and repository-defined scripts.

### Validate this repository

Requires Python 3.10 or newer.

```bash
make check
```

The validation pipeline covers:

```text
repository integrity
  ├── skill metadata + local links
  ├── VERSION + CHANGELOG consistency
  ├── evaluation fixtures + schema
  ├── Python compilation
  ├── unit tests
  ├── deterministic package verification
  └── release-readiness invariants
```

CI runs the contract across Python **3.10**, **3.12**, and **3.14**, then builds and verifies the distribution artifact.

### Build a clean distribution

```bash
make package
```

Produces:

```text
dist/
├── engineering-quality-<version>.zip
└── engineering-quality-<version>.zip.sha256
```

The ZIP contains only the runtime skill payload and an internal `MANIFEST.sha256`. Tests, CI configuration, README content, and release tooling are intentionally excluded.

Tagged releases are automated. See [docs/release.md](docs/release.md).

## Quality model

```text
quality =
    correctness
  + clarity
  + compatibility
  + security
  + verifiability
  - unnecessary complexity
  - unnecessary churn
```

This is not a numeric score. It is a design stance.

### Correctness first

A cleaner implementation that changes the wrong behavior is a regression.

### Small, coherent changes

A change should have one understandable purpose. Required tests, migrations, and documentation belong with that purpose; drive-by cleanup does not.

### Local consistency over generic preference

Existing repository architecture, naming, error semantics, and tooling have precedence unless they are directly responsible for the problem.

### Verification with evidence

```text
Verified     = executed and observed
Reasoned     = supported by inspection
Not verified = relevant check not run, with a concrete reason
```

Reasoning is useful. It is not execution evidence.

### Smells are signals

Long functions, duplicated code, broad diffs, low coverage, and high complexity can indicate risk. None of them is a universal defect by itself.

The job is to identify the underlying failure mode: coupling, obscurity, fragile invariants, unsafe boundaries, hidden compatibility cost, or difficult verification.

## Review rubric

Findings are classified by concrete impact:

| Severity | Meaning |
| --- | --- |
| **Blocker** | Incorrect behavior, data loss, security exposure, broken contract, or reliably failing verification. |
| **Major** | A material problem likely under realistic conditions or a significant maintenance/operational risk. |
| **Minor** | A bounded issue affecting clarity, resilience, test quality, or consistency. |
| **Note** | Optional improvement, question, or follow-up. |

Style disagreement alone is not a severity level.

## Design foundations

The playbook is informed by established engineering practice rather than one doctrine:

- [Google Engineering Practices](https://google.github.io/eng-practices/) — reviewability, small coherent changes, and codebase health.
- [Martin Fowler](https://refactoring.com/) — refactoring, code smells, testing, and evolutionary design.
- [A Philosophy of Software Design](https://web.stanford.edu/~ouster/cgi-bin/aposd.php) — complexity, information hiding, and deep modules.
- [OWASP ASVS](https://owasp.org/projects/asvs/) and [NIST SSDF](https://csrc.nist.gov/Projects/ssdf) — structured security requirements and secure development practice.
- [Hyrum's Law](https://www.hyrumslaw.com/) and [Semantic Versioning](https://semver.org/) — observable behavior and compatibility.
- Official ecosystem guidance including [PEP 8](https://peps.python.org/pep-0008/), [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments), and the [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/).

See [docs/foundations.md](docs/foundations.md) for the maintained source map.

## Contributing

Changes should improve engineering outcomes without turning the project into a catalog of personal preferences.

Before proposing a rule, ask:

```text
Does it address a concrete failure mode?
Does it apply conditionally?
Can deterministic tooling enforce it instead?
Does it belong in the core contract or an on-demand reference?
Can its behavior be evaluated?
```

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)

---

<div align="center">

**Build the right thing. Keep the diff coherent. Prove what works.**

</div>
