# PyMaxQ

[![CI](https://github.com/aidotse/pymaxq/actions/workflows/ci.yml/badge.svg)](https://github.com/aidotse/pymaxq/actions/workflows/ci.yml)
[![Tests](https://aidotse.github.io/pymaxq/exported/tests.svg)](https://aidotse.github.io/pymaxq/exported/pytest.html)
[![Docs](https://img.shields.io/badge/docs-pymaxq-blue)](https://aidotse.github.io/pymaxq/)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/license/mit)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)

A [Copier](https://copier.readthedocs.io) template for **max-quality** Python projects — batteries-included tooling and
Github/Gitlab CI/CD that put a project under maximum quality pressure from day one. Generate once, then pull in future
template improvements with `copier update`. The name nods to *Max Q*, the moment of peak aerodynamic pressure during a
rocket launch.

📖 **Full documentation: <https://aidotse.github.io/pymaxq/>**

## Generate A Project

```bash
uv tool install copier
copier copy --trust https://github.com/aidotse/pymaxq my-project   # --trust: post-gen tasks run shell commands
cd my-project
uv sync
git init && git add -A
uv run poe lint                                  # auto-format the freshly rendered files (re-add if it changes any)
git add -A && git commit -m "feat: initial project scaffold"   # feat -> your first release (v0.1.0)
uv run pre-commit install                        # enable hooks *after* the first commit
git checkout -b feat/initial-setup               # main is protected; do further work on branches
```

> **Before your first release (one-time):** on GitHub, enable Pages (**Settings → Pages → Source: "GitHub Actions"**) —
> the docs-deploy job fails without it. For the release push, the platforms differ: on **GitHub**, once you protect the
> default branch (recommended — the shipped `no-commit-to-branch` hook and PR workflow assume it), give CI a way past
> that protection — a `RELEASE_TOKEN` secret or a `github-actions[bot]` bypass (leave `main` unprotected and the default
> token pushes the release itself, but then it isn't protected). On **GitLab**, a `CI_REPO_ACCESS` token is required
> either way — the pipeline authenticates the push with it, and the default branch is protected out of the box. Full
> per-platform steps:
> [Generated Project Guide → Repository settings](https://aidotse.github.io/pymaxq/user-guide/#repository-settings).

Copier prompts for the project name, package name, description, author, namespace, and`ci_platform` (`github` default /
`gitlab` / `both`), then renders accordingly. See [Getting Started](https://aidotse.github.io/pymaxq/getting-started/)
for details.

## What You Get

A project wired for quality from the first commit:

- **[pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)**, for modern project
    configuration
- **[uv](https://docs.astral.sh/uv/)** modern and fast deps/env/build
- **[pre-commit](https://pre-commit.com/)** for client-side, gated commits
- **[ruff](https://docs.astral.sh/ruff/)** lint+format
- **[mypy](https://mypy-lang.org/)** types
- **[pytest](https://docs.pytest.org/)** + coverage, live-wired to the docs via CI
- **[nox](https://nox.thea.codes/)** across Python 3.10–3.13
- **[deptry](https://github.com/fpgmaas/deptry)** for dependency hygiene
- **[renovate](https://docs.renovatebot.com/)** for automatic dependency updates
- **[hydra](https://hydra.cc/)** for flexible experiment configuration
- **[poethepoet](https://github.com/nat-n/poethepoet)**, a task runner for running custom tasks specified in your
    `pyproject.toml`
- **[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)** for modern docs, plugin generates API
    documentation directly from your source code's Google-style docstrings
- Security baked in: **[gitleaks](https://github.com/gitleaks/gitleaks)**, **[zizmor](https://docs.zizmor.sh/)**,
    `uv audit`, ruff's bandit rules, SHA-pinned actions
- Automatic versioning from [Conventional Commits](https://www.conventionalcommits.org/),
    (**[commitizen](https://commitizen-tools.github.io/commitizen/)**) + changelog, and automated code releases based on
    tags.
- Automatic **[Docker]**(https://www.docker.com/) image build and deployment
- GitHub-first, platform-agnostic CI/CD (GitHub Actions and/or GitLab CI)

> PyMaxQ is built with the same toolchain it ships — for example, this documentation is produced by the very `mkdocs`
> setup it gives you. This template's CI generates and validates a throwaway project from the template on every push.

## License

[MIT](https://github.com/aidotse/pymaxq/blob/main/LICENSE) © AI Sweden.
