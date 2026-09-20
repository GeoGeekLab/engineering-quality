# Distribution and discovery

Last reviewed: **2026-09-20**.

This document separates repository discoverability from external marketplace publication. A file in this repository is not evidence that a third-party directory has reviewed or published the project.

## Positioning

Primary one-line positioning:

> Evidence-first engineering quality for coding agents: preserve the repository contract, keep the diff tight, test the failure mode, and separate proof from belief.

Recommended GitHub repository description:

> Evidence-first engineering quality skill for Codex, Claude Code, ChatGPT, and other coding agents.

Primary search intents to serve naturally in README and documentation:

- coding agent engineering quality,
- coding agent skill,
- AI code review,
- software testing and verification,
- secure coding agent,
- compatibility-aware refactoring,
- Codex skill,
- Claude Code skill,
- ChatGPT skill,
- agent evaluation.

Do not repeat keywords mechanically. Use them where they describe an actual workflow or supported host.

## GitHub topics

Recommended topics:

```text
agent-skills
coding-agents
ai-coding
software-engineering
code-review
testing
verification
secure-coding
codex
claude-code
chatgpt
developer-tools
```

GitHub topics should describe actual project purpose and supported ecosystems. Keep the set focused rather than filling the 20-topic limit.

## Social preview

GitHub recommends a PNG, JPG, or GIF below 1 MB, with **1280 × 640 px** preferred for best rendering.

The preview should communicate only three things at thumbnail size:

```text
engineering-quality
Ship patches you can defend.
RECON → CONTRACT → CHANGE → VERIFY → REVIEW → EVIDENCE
```

Avoid tiny repository maps, badge walls, terminal screenshots, or claims such as "best" and "production-ready" that the image cannot substantiate.

The social preview is uploaded through repository Settings and is not stored as a runtime Skill asset.

## Release announcement

A release announcement should lead with the user problem and verifiable changes rather than a feature count.

Suggested structure:

1. one sentence describing the failure mode the project addresses,
2. three concrete capabilities,
3. one short before/after example,
4. installation link,
5. evidence link to the tagged release and CI,
6. explicit limitations, especially real-host behavioral evidence.

Avoid publishing aggregate model-performance claims until real host reports exist.

## OpenAI Plugin Directory

OpenAI's current submission flow accepts skill-only plugins. Publication is an external review process and requires more than a repository manifest.

Before submission, prepare the current required listing and review material, including:

- final Skill bundle,
- plugin name and short/long descriptions,
- logo and category,
- website/support/privacy/terms URLs as required by the submission,
- realistic starter prompts,
- **5 positive and 3 negative test cases** with expected behavior,
- release notes,
- verified publisher identity and the required organization permission.

The 14 executable repository evals are useful source material, but they are not automatically equivalent to the submission portal's reviewer-facing test cases. Select and rewrite the clearest cases for that context.

Do not claim Plugin Directory publication or OpenAI verification until the external review has actually completed.

Official reference:

- https://developers.openai.com/plugins/deploy/submission

## Claude Code distribution

The repository already supports local Claude Code skill installation and direct plugin loading through `.claude-plugin/plugin.json`.

Marketplace publication is a separate external distribution step. Recheck the current Claude Code plugin/marketplace documentation immediately before submission rather than freezing marketplace-specific process in this repository.

Official reference:

- https://code.claude.com/docs/en/plugins

## Community launch sequence

A low-noise launch sequence:

1. publish a verified GitHub release,
2. update GitHub repository metadata and social preview,
3. open a GitHub Discussion introducing the release and asking for concrete host compatibility reports,
4. submit to relevant vendor directories only when their review requirements are met,
5. share the release in developer communities where coding-agent verification, review, or secure software engineering is already on-topic,
6. route discovered defects back into executable eval cases.

Do not mass-post identical promotional copy across unrelated communities.

## Evidence to link

Prefer links that let readers inspect claims:

- latest tagged GitHub Release,
- release ZIP and SHA-256 sidecar,
- GitHub artifact attestation verification command,
- CI workflow,
- executable eval documentation,
- compatibility matrix with last-verified date,
- SECURITY.md and governance policy.

Stars, forks, and download counts are adoption signals, not engineering-quality evidence.

## Maintenance

Before each minor or major release:

- review README search intent and first-screen clarity,
- re-check host compatibility docs,
- re-check third-party installer pins,
- review GitHub topics for obsolete or missing terms,
- verify social preview still reflects current positioning,
- re-check vendor directory submission requirements,
- remove distribution claims that are no longer evidenced.
