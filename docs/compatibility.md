# Compatibility

engineering-quality follows the open Agent Skills directory model: a skill directory contains a required `SKILL.md` and may include scripts, references, and assets.

The repository keeps the core skill host-neutral. Host-specific installation is a distribution concern, not part of the engineering-quality contract.

## Support matrix

| Host | Status | Recommended installation | Discovery / package model |
| --- | --- | --- | --- |
| Codex | First-class | Built-in skill installer or `skills` CLI | `.agents/skills` |
| ChatGPT | First-class package | Upload a packaged skill | Skill ZIP / workspace skill |
| Claude Code | First-class | `skills` CLI or manual install | `~/.claude/skills` |
| Other Agent Skills hosts | Compatible by design | `skills` CLI where supported | Host-specific skill directory |

## Codex

Preferred interactive instruction:

```text
$skill-installer Install engineering-quality from https://github.com/GeoGeekLab/engineering-quality
```

Cross-agent CLI:

```bash
npx -y skills@latest add GeoGeekLab/engineering-quality -g -a codex -y
```

Manual user installation:

```bash
git clone https://github.com/GeoGeekLab/engineering-quality.git ~/.agents/skills/engineering-quality
```

Codex reads skills from repository, user, administrator, and system locations. Repository-scoped skills live under `.agents/skills`; user-scoped skills live under `$HOME/.agents/skills`.

## Claude Code

Cross-agent CLI:

```bash
npx -y skills@latest add GeoGeekLab/engineering-quality -g -a claude-code -y
```

Manual user installation:

```bash
git clone https://github.com/GeoGeekLab/engineering-quality.git ~/.claude/skills/engineering-quality
```

## ChatGPT

For a clean distribution package, use a release artifact or build one locally:

```bash
make package
```

The resulting archive is written to `dist/engineering-quality-<version>.zip` with a matching `.sha256` checksum.

Upload the ZIP through the ChatGPT Skills interface available to your workspace.

## Generic skills CLI

The open `skills` CLI can install from GitHub shorthand, a full Git URL, a direct skill path, or an archive:

```bash
npx skills add GeoGeekLab/engineering-quality
```

Use `-a <agent>` to target a supported host and `-g` for user-level installation.

## Compatibility policy

- The root `SKILL.md` contract is treated as the stable public interface.
- Host-specific instructions live in documentation instead of branching the core skill.
- References and workflows use relative paths so packaged and cloned installs behave the same.
- Runtime scripts use the Python standard library only.
- Packaging excludes repository-maintenance files that are not required to operate the skill.

## Source references

- Codex skills: https://developers.openai.com/docs/build-skills
- OpenAI skills customization: https://developers.openai.com/docs/customization
- Claude skills: https://www.anthropic.com/research/skills
- skills CLI: https://github.com/vercel-labs/skills
