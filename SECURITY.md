# Security policy

## Reporting a vulnerability

Do not publish vulnerability details in a public issue.

Preferred path:

1. open the repository's **Security** page,
2. choose **Report a vulnerability** when private vulnerability reporting is available,
3. include the affected version or commit, impact, reproduction steps, required preconditions, and mitigation ideas if known.

If the private-reporting control is not available, open a public issue containing **no vulnerability details** and ask the maintainer for a private disclosure channel. Do not include exploit code, secrets, affected private data, or reproduction details in that public issue.

The repository's governance baseline requires private vulnerability reporting to be enabled in GitHub settings. See [GitHub governance settings](docs/github-settings.md).

## Scope

The repository contains documentation and local helper scripts. Reports are especially relevant when a script can:

- execute unintended repository-controlled commands,
- escape its intended repository or temporary workspace,
- expose credentials or sensitive environment state,
- weaken artifact or release integrity,
- misclassify an unsafe operation as safe verification,
- let an evaluated agent read hidden rubric data or contaminate later evaluations.

The project-check helper does not install packages. It only executes discovered repository checks when both `--run` and `--trust-repository` are supplied.

The behavioral-evaluation runner also treats execution as a trust boundary: credentials must be forwarded explicitly and post-agent command checks require `--allow-workspace-execution`.

## Coordinated disclosure

Please allow maintainers reasonable time to investigate and prepare a fix or mitigation before public disclosure. Once remediation is available, maintainers should document affected versions and any required user action.
