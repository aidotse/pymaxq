# Security

Security is layered into this project at several points rather than bolted on at the end: it runs at commit time
(pre-commit hooks), in the CI quality gate, and through how dependencies and CI itself are pinned. This page summarizes
the posture; follow the links for the mechanics.

## Secret scanning (gitleaks)

[gitleaks](https://github.com/gitleaks/gitleaks) scans your changes for accidentally committed secrets — API keys,
tokens, credentials — going well beyond the standard `detect-private-key` hook (which only catches private keys). It
runs as a [pre-commit](precommit.md) hook and again in the CI quality gate, so a leaked secret is caught before it ever
reaches the remote.

## Workflow security (zizmor, GitHub Actions)

CI workflows are a common and under-scrutinized attack surface. [zizmor](https://docs.zizmor.sh/) is a static-analysis
tool for GitHub Actions that audits for issues such as template injection through `${{ }}` expressions, over-broad
`permissions`, credentials persisted into build artifacts, and unpinned actions. It runs as a pre-commit hook in
projects that ship GitHub workflows. The GitHub workflows in this template are written to pass zizmor at its **default**
strictness, demonstrating the hardening it asks for:

- `${{ ... }}` context is passed via `env:` rather than interpolated into `run:` scripts;
- `permissions:` are scoped to the individual job that needs them;
- checkouts set `persist-credentials: false` unless the job must push;
- every action is SHA-pinned (see below).

(GitLab CI has no equivalent zizmor pass; there the pipeline hardening lives in scoped tokens and protected-branch push
rules — see [CI/CD](ci.md).)

## Dependency vulnerabilities (`uv audit`)

[`uv audit`](https://docs.astral.sh/uv/) scans your locked dependencies against published vulnerability advisory
databases and fails if a known-vulnerable package is present. It runs in the CI quality gate, so a newly-disclosed
vulnerability in even a transitive dependency surfaces on your next pipeline.

## Insecure-code linting (ruff / bandit rules)

The [ruff](https://docs.astral.sh/ruff/) configuration enables the `S` (flake8-bandit) ruleset, which flags insecure
code patterns — `eval`, insecure temporary files, weak hashing, shell injection, and so on — as a normal part of
linting, with no extra tool to run.

## Supply chain: SHA-pinned actions (GitHub)

Third-party GitHub Actions are pinned to a full commit **SHA** (with a readable `# vX` comment), not a movable tag — so
a compromised or retagged action cannot silently change what your CI runs. [Renovate](https://docs.renovatebot.com/)
keeps these pins (and their version comments) current, so pinning doesn't mean going stale.

## Gated commits & branch protection

Beyond scanning, the [pre-commit](precommit.md) hooks include `detect-private-key`, `no-commit-to-branch` (stops direct
commits to protected branches), and `check-added-large-files`. Combined with the CI quality gate and protected-branch
settings (see [Getting Started](getting-started.md)), this keeps unreviewed or unsafe changes out of your default
branch.
