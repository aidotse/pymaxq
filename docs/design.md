# Design & Philosophy

The guiding principle is simple: **make the high-quality path the path of least resistance.**
A generated project arrives already wired for testing, linting, typing, security, versioning,
documentation, and releasing — so quality is the *default*, not a chore you bolt on later.

Every tool below has a dedicated deep-dive **in the generated project's own documentation**;
this page is the bird's-eye rationale.

## The cross-cutting design choices

A handful of decisions shape everything else:

**Logic lives in tasks, not in CI.** Every operation — lint, test, audit, build, bump, docs —
is a [poe](https://github.com/nat-n/poethepoet) task in `pyproject.toml`. The CI files only
decide *when* to run them and supply credentials. This is what makes the pipeline
**infrastructure-agnostic**: the same task contract is implemented by both the GitHub and
GitLab pipelines with almost no duplicated logic, and anything CI does you can reproduce
locally with `uv run poe <task>`.

**GitHub-first, not GitHub-only.** `ci_platform` selects GitHub Actions, GitLab CI, or both.
GitHub is the primary/canonical host (repo, docs, badges); a GitLab-only project is fully
supported with the internal-host equivalents, and `both` runs GitLab as a mirror. The release
*concept* is identical across platforms — only the glue differs.

**One source of truth, everywhere.** The version is a git tag — no version string is committed;
`hatch-vcs` reads it at build time. The supported Python versions live only in `noxfile.py`.
The template's questions live only in `copier.yml`. Avoiding duplicated truth avoids drift.

**Automate the decisions humans get wrong.** Version bumps are derived from
[Conventional Commits](https://www.conventionalcommits.org/), not human judgement; dependency
updates come from [Renovate](https://docs.renovatebot.com/); coverage thresholds, dependency
hygiene, and security advisories are *gated*, not advisory. You write code and good commit
messages — the machine handles the bookkeeping.

**Config over hardcoding.** Runnable behaviour is parametrized with [Hydra](https://hydra.cc/),
so experiments and runs are reconfigurable from the command line without editing source.

**Updatable scaffolding.** Because a project is *generated* with [Copier](https://copier.readthedocs.io)
rather than copied once, template improvements flow downstream via `copier update` — your
project stays connected to its source instead of forking away on day one.

## Why these tools (state of the art)

The choices reflect the current (2024–2026) Python tooling consensus, deliberately
consolidating many older, single-purpose tools into a few fast, well-maintained ones:

| Concern | Choice | Replaces / why it's the modern default |
| --- | --- | --- |
| Deps · env · build · publish · audit | **uv** | pip + virtualenv + pip-tools + twine + pip-audit; Rust-fast, one lockfile, one tool |
| Lint + format | **ruff** | black + isort + flake8 + pyupgrade + pydocstyle; one fast tool, one config |
| Task running | **poethepoet** | Make / ad-hoc shell scripts; tasks live in `pyproject.toml`, runnable locally and in CI |
| Versioning | **commitizen** + Conventional Commits | manual bumps / hand-rolled scripts; deterministic semver straight from history |
| Multi-version testing | **nox** | tox; sessions configured in Python, backed by uv |
| Dep hygiene · vuln scan | **deptry** + `uv audit` | manual review; automated in the quality gate |
| Secrets · workflow security | **gitleaks** + **zizmor** | secret scanning beyond private keys; static security analysis of GitHub Actions |
| Supply chain | **SHA-pinned actions** + Renovate | pin every action to a commit SHA (not a movable tag); Renovate keeps the pins current |
| Documentation | **Material for MkDocs** + mkdocstrings + mike | Sphinx; Markdown, API docs from docstrings, versioned |
| Scaffolding | **Copier** | cookiecutter / hand-rolled scripts; supports *updates*, not just one-shot generation |
| Dependency updates | **Renovate** | Dependabot; works on GitLab **and** GitHub |

None of this is locked in: each tool is configured in `pyproject.toml` (or its own small config
file) and documented on its own page in the generated project, so you can tune, swap, or remove
any piece as your project's needs evolve.
