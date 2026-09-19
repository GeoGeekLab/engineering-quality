# Security policy

## Reporting a vulnerability

Please report security issues privately through GitHub's security reporting features when available. Do not publish exploit details in a public issue before a fix or mitigation is available.

A useful report includes the affected file or workflow, concrete impact, reproduction steps, required preconditions, and suggested mitigation if known.

## Scope

The repository contains documentation and local helper scripts. Reports are especially relevant when a script can execute unintended commands, escape its target repository, expose sensitive information, or misclassify an unsafe operation as a safe verification step.

The project-check helper does not install packages and executes discovered commands only when `--run` is explicitly supplied.
