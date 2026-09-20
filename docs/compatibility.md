# Compatibility

Last verified against official vendor documentation: **2026-09-20**.

engineering-quality keeps one host-neutral Agent Skills contract in `SKILL.md`, then adds host-specific distribution metadata and evaluation adapters around that core.

Compatibility claims in this repository are evidence-scoped:

- **format verified** means the packaged layout and metadata match the documented host contract,
- **adapter verified** means the repository's native evaluation adapter is exercised by unit tests against its CLI contract,
- **behavior verified** means a real host/model run produced a saved evaluation report,
- absence of a real-host report must not be described as behavioral compatibility evidence.

## Support matrix

| Host | Supported installation / loading path | Distribution state | Native eval path | Current evidence |
| --- | --- | --- | --- | --- |
| Codex | Repository/user Agent Skills locations or `$skill-installer` for local use | `agents/openai.yaml` included; reusable public distribution should use an OpenAI Plugin; this project is not yet published in the Plugin Directory | `codex exec --ephemeral --ignore-user-config --sandbox workspace-write` through `scripts/host_eval_adapter.py` | Format + adapter contract verified; no saved real Codex behavioral run yet |
| ChatGPT | Upload the packaged skill from Plugins → Skills → Create → Upload on eligible workspaces | Release ZIP includes OpenAI skill metadata; project is not yet a published Plugin | No local CLI adapter; uses the same packaged OpenAI skill payload | Package contract verified; no saved real ChatGPT behavioral run yet |
| Claude Code | Standalone skill under `~/.claude/skills`, or load the repository as a plugin | Repository includes `.claude-plugin/plugin.json`; not yet published in a Claude marketplace | `claude -p` in bare auto mode with the staged skill supplied through `--add-dir` | Format + adapter contract verified; no saved real Claude Code behavioral run yet |
| Other Agent Skills hosts | Host-specific skill directory when the host accepts the open Agent Skills layout | Portable skill ZIP contains only the host-neutral runtime plus OpenAI optional metadata | Generic `--agent-command` adapter | Format-oriented only unless a host-specific run is recorded |

## OpenAI: Codex

OpenAI documents local Agent Skills separately from reusable distribution.

For local development or experimentation, Codex discovers repository and user skills from `.agents/skills` locations, and the built-in `$skill-installer` can install a skill from another repository.

Example:

```text
$skill-installer Install engineering-quality from https://github.com/GeoGeekLab/engineering-quality
```

Manual user installation:

```bash
git clone https://github.com/GeoGeekLab/engineering-quality.git \
  ~/.agents/skills/engineering-quality
```

OpenAI's current guidance says local skill folders and `$skill-installer` are appropriate for local setup and experimentation. For reusable distribution, prefer an OpenAI Plugin.

This repository therefore includes:

```text
agents/openai.yaml
```

with display metadata, a default prompt, and implicit invocation enabled. The file is part of the release skill ZIP and is validated by the repository quality gate.

The project is **not** currently claiming to be published or OpenAI Verified in the Plugin Directory.

Official references:

- https://developers.openai.com/docs/build-skills
- https://developers.openai.com/docs/non-interactive-mode
- https://developers.openai.com/plugins/deploy/submission

## OpenAI: ChatGPT

ChatGPT Skills are currently documented for eligible **Business, Enterprise, Healthcare, and Edu** users, subject to workspace settings and product availability.

For an eligible workspace:

1. open **Plugins**,
2. open the **Skills** tab,
3. choose **Create**,
4. choose **Upload from your computer**,
5. upload the release artifact `engineering-quality-<version>.zip`.

The release ZIP is preferred over uploading an arbitrary source checkout because it contains only the declared runtime payload plus its internal manifest.

For broader reusable discovery across ChatGPT and Codex, OpenAI now uses the shared Plugin Directory. A skill-only plugin can be submitted through the OpenAI plugin submission process. Publication requires the external OpenAI review/submission flow and is not implied by files in this repository.

Official references:

- https://help.openai.com/en/articles/20001066
- https://help.openai.com/en/articles/20001256/
- https://developers.openai.com/plugins/deploy/submission

## Anthropic: Claude Code

Anthropic supports Agent Skills across Claude products. Claude Code supports standalone skills and plugins.

Standalone user installation:

```bash
git clone https://github.com/GeoGeekLab/engineering-quality.git \
  ~/.claude/skills/engineering-quality
```

This repository also includes:

```text
.claude-plugin/plugin.json
```

Claude Code supports a single-skill plugin with `SKILL.md` directly at the plugin root, so a cloned repository can be loaded for development with:

```bash
claude --plugin-dir /path/to/engineering-quality
```

The manifest version is required to match the repository `VERSION` file.

The project is **not** currently claiming marketplace publication.

Official references:

- https://www.anthropic.com/research/skills
- https://code.claude.com/docs/en/quickstart
- https://code.claude.com/docs/en/plugins
- https://code.claude.com/docs/en/cli-reference

## Third-party installer

The `skills` CLI from Vercel Labs remains a useful cross-agent convenience, but it is not the vendor-native distribution authority for either OpenAI or Anthropic.

Optional examples:

```bash
npx skills add GeoGeekLab/engineering-quality
npx skills add GeoGeekLab/engineering-quality -g -a codex
npx skills add GeoGeekLab/engineering-quality -g -a claude-code
```

Do not describe `npx skills` as the preferred OpenAI or Anthropic installation path.

Reference:

- https://github.com/vercel-labs/skills

## Native behavioral evaluation adapters

The executable eval harness can call the current vendor-native CLIs.

### Codex

```bash
python scripts/run_evals.py \
  --agent-command '{python} {repo}/scripts/host_eval_adapter.py codex' \
  --adapter-label codex-current \
  --pass-env CODEX_API_KEY \
  --allow-workspace-execution \
  --output eval-results/codex.json
```

The adapter installs the staged runtime skill into an isolated temporary `$HOME/.agents/skills/engineering-quality`, isolates `CODEX_HOME`, and invokes the current non-interactive Codex path:

```text
codex exec --ephemeral --ignore-user-config --sandbox workspace-write <task>
```

For unattended authentication, OpenAI documents `CODEX_API_KEY` for `codex exec`; trusted automation can also use `CODEX_ACCESS_TOKEN` or workload-identity variables when appropriate. Forward only the variables the run actually needs with repeated `--pass-env NAME` flags. Do not put credentials in the adapter command string.

The runner does not inherit the caller's complete environment. The adapter receives only basic process variables plus names explicitly selected with `--pass-env`, then creates an isolated temporary `HOME` and `CODEX_HOME`.

### Claude Code

```bash
python scripts/run_evals.py \
  --agent-command '{python} {repo}/scripts/host_eval_adapter.py claude-code' \
  --adapter-label claude-code-current \
  --pass-env ANTHROPIC_API_KEY \
  --allow-workspace-execution \
  --output eval-results/claude-code.json
```

The adapter invokes a controlled current CLI path:

```text
claude --bare --permission-mode auto --permission-prompts none \
  --no-session-persistence --add-dir <staged-skill> -p <task>
```

`--bare` suppresses unrelated local hooks, commands, agents, plugins, MCP configuration, memory, and CLAUDE.md loading while Claude Code still permits Skills from an explicit `--add-dir`. Auto mode remains a safety decision layer; a denied action can terminate a headless run rather than being silently bypassed.

Claude Code's current non-interactive mode accepts environment authentication such as `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, or `CLAUDE_CODE_OAUTH_TOKEN`. Other provider-specific variables can be forwarded individually when required. The adapter creates an isolated temporary `HOME` and `CLAUDE_CONFIG_DIR`, so a behavioral run does not silently consume the evaluator's ordinary saved Claude login or personal configuration.

The adapters print the installed host CLI version into captured stderr so a real evaluation result retains version evidence. The runner never forwards unrelated host secrets by default.

## Evaluation integrity

Each case receives a fresh staged copy of the runtime skill payload.

The harness hashes that staged payload before and after the agent run. If an agent or adapter mutates the Skill itself, the case fails with a `skill_payload_integrity` finding. This prevents one case from rewriting the Skill and contaminating later evaluations.

Real behavioral compatibility is established only by saved reports from actual vendor runtimes. Unit tests for the adapters prove command construction and staging behavior, not model performance.

## Compatibility policy

- `SKILL.md` remains the portable behavioral contract.
- OpenAI-specific metadata lives in `agents/openai.yaml`.
- Claude plugin distribution metadata lives in `.claude-plugin/plugin.json`.
- The portable release ZIP includes OpenAI skill metadata but excludes repository-only Claude plugin and evaluation tooling.
- Host documentation is date-stamped and should be rechecked against official vendor docs before a release that changes installation or compatibility claims.
- Third-party installers are documented as conveniences, not vendor-native authorities.
- A host is never described as behaviorally verified without an actual saved host evaluation result.
