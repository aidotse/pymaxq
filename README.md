# PyMaxQ

A template for **max quality** Python projects — batteries-included tooling and
CI/CD that put a project under maximum pressure for quality from day one.

This repository is a [Copier](https://copier.readthedocs.io) template. Generating
from it gives you a ready-to-go Python project wired up with:

- **[uv](https://docs.astral.sh/uv/)** — dependency & environment management
- **[ruff](https://github.com/astral-sh/ruff)** — linting + formatting
- **[mypy](https://mypy-lang.org/)** — static type checking
- **[pytest](https://docs.pytest.org/)** (+ coverage, xdist, html) — testing
- **[pre-commit](https://pre-commit.com/)** — gated commits
- **[poethepoet](https://github.com/nat-n/poethepoet)** — task running
- **[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)** + **[mike](https://github.com/jimporter/mike)** — versioned docs
- **[Hydra](https://hydra.cc/)** — configuration
- Tag-based versioning (hatch-vcs) and a GitLab CI/CD pipeline

## Generate a project

```bash
# 1. Install copier (once)
uv tool install copier

# 2. Generate your project (from the template's git URL, or a local checkout)
copier copy https://gitlab.mgmt.ai.se/dev-tools/pymaxq path/to/my-project

# 3. Set it up
cd path/to/my-project
uv sync
uv run pre-commit install
git init && git add -A && git commit -m "chore: initial commit from pymaxq"
```

Copier will prompt for your project name, package name, description, author, and
GitLab group, then render the template accordingly.

## Stay up to date

Because projects are generated with Copier, you can pull in later improvements to
this template without losing your own changes:

```bash
copier update     # run from inside a generated project
```

## Repository layout

```
copier.yml      # template questions + engine settings
template/        # the content that becomes your project (rendered by Copier)
tests/           # generation tests for the template itself
```

To work on the template, edit files under `template/`. Files ending in `.jinja`
are rendered (the suffix is stripped); everything else is copied verbatim. The
package directory `{{ package_name }}/` is renamed to your package on generation.

Run the template's own tests with:

```bash
uv run --with copier --with pytest pytest tests/
```
