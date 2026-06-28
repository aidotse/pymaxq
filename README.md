# PyMaxQ

[![CI](https://github.com/aidotse/pymaxq/actions/workflows/ci.yml/badge.svg)](https://github.com/aidotse/pymaxq/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-pymaxq-blue)](https://aidotse.github.io/pymaxq/)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/license/mit)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)

A [Copier](https://copier.readthedocs.io) template for **max-quality** Python projects —
batteries-included tooling and CI/CD that put a project under maximum quality pressure from
day one. Generate once, then pull in future template improvements with `copier update`.

📖 **Full documentation: <https://aidotse.github.io/pymaxq/>**

## Generate a project

```bash
uv tool install copier                                   # once
copier copy https://github.com/aidotse/pymaxq my-project # answer a few prompts
cd my-project
uv sync && uv run pre-commit install
git init && git add -A && git commit -m "chore: initial commit from pymaxq"
```

Copier prompts for the project name, package name, description, author, namespace, and
`ci_platform` (`github` default / `gitlab` / `both`), then renders accordingly. See
[Getting Started](https://aidotse.github.io/pymaxq/getting-started/) for details.

## What you get

A project wired for quality from the first commit:

- **[uv](https://docs.astral.sh/uv/)** deps/env/build · **[ruff](https://docs.astral.sh/ruff/)** lint+format · **[mypy](https://mypy-lang.org/)** types
- **[pytest](https://docs.pytest.org/)** + coverage, and **[nox](https://nox.thea.codes/)** across Python 3.10–3.13
- security baked in: **[gitleaks](https://github.com/gitleaks/gitleaks)**, **[zizmor](https://docs.zizmor.sh/)**, `uv audit`, ruff's bandit rules, SHA-pinned actions
- automatic versioning from [Conventional Commits](https://www.conventionalcommits.org/) (**[commitizen](https://commitizen-tools.github.io/commitizen/)**) + changelog
- GitHub-first, platform-agnostic CI/CD (GitHub Actions and/or GitLab CI), versioned docs ([Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)), and [Renovate](https://docs.renovatebot.com/)

The [Design & Philosophy](https://aidotse.github.io/pymaxq/design/) page explains the *why*.

## Developing the template

PyMaxQ dogfoods its own toolchain via poe:

```bash
uv sync                       # dev env (copier, pytest, ruff, mypy, pre-commit, commitizen)
uv run pre-commit install     # hooks, incl. commit-msg → Conventional Commits
uv run poe lint               # ruff, mypy, gitleaks, zizmor, hygiene
uv run poe test               # the generation tests
uv run poe docs               # build this documentation site
```

`main` is protected — **work on a branch and merge via PR**; merging triggers `cz bump`. See
[Developing the template](https://aidotse.github.io/pymaxq/developing/) for the full workflow,
including how the docs and CI are dogfooded.

## License

[MIT](LICENSE) © AI Sweden.
