# Design & Philosophy

This page explains the design choices behind this project's setup, what they let you do, and why each tool was chosen.
Every choice has a dedicated deep-dive — follow the links for the mechanics.

The guiding principle is simple: **make the high-quality path the path of least resistance.** A project should arrive
already wired for testing, linting, typing, security, versioning, documentation, and releasing — so that quality is the
*default*, not a chore you bolt on later. (The name PyMaxQ nods to "max Q", the point of maximum aerodynamic pressure
during a launch: the tooling here puts your code under maximum quality pressure from the first commit.)

## What you get, end to end

From a single `copier copy`, you have a project that can:

- install and lock dependencies reproducibly, on any machine or CI runner ([uv](https://docs.astral.sh/uv/));
- format, lint, and type-check automatically on every commit ([ruff](https://docs.astral.sh/ruff/), mypy,
    [pre-commit](precommit.md));
- test on one interpreter with coverage, *and* across every supported Python version
    ([pytest](https://docs.pytest.org/), [nox](https://nox.thea.codes/));
- check dependency hygiene and scan for known vulnerabilities ([deptry](https://github.com/fpgmaas/deptry),
    [`uv audit`](https://docs.astral.sh/uv/));
- scan for leaked secrets and statically audit its CI workflows ([gitleaks + zizmor](security.md));
- version itself automatically from commit messages, with a generated changelog ([commitizen](versioning.md));
- build, publish, document, and release through CI on GitLab or GitHub ([CI/CD](ci.md), [Documentation](mkdocs.md));
- keep its dependencies current automatically ([Renovate](https://docs.renovatebot.com/));
- and pull in future improvements to the template it came from ([`copier update`](copier.md)).

## The cross-cutting design choices

A handful of decisions shape everything else:

**Logic lives in tasks, not in CI.** Every operation — lint, test, audit, build, bump, docs — is a
[poe task](https://github.com/nat-n/poethepoet) in `pyproject.toml`. The CI files only decide *when* to run them and
supply credentials. This is what makes the pipeline **infrastructure-agnostic**: the same task contract is implemented
by both the GitLab and GitHub pipelines with almost no duplicated logic, and anything CI does you can reproduce locally
with `uv run poe <task>`.

**GitHub-first, not GitHub-only.** `ci_platform` selects GitHub Actions, GitLab CI, or both. GitHub is the
primary/canonical host (repo, docs, badges); a GitLab-only project is fully supported with the internal-host
equivalents, and `both` runs GitLab as a mirror. The release *concept* is identical across platforms — only the glue
differs.

**One source of truth, everywhere.** The version is a git tag — no version string is committed,
[hatch-vcs](versioning.md) reads it at build time. The supported Python versions live only in `noxfile.py`. The
template's questions live only in `copier.yml`. Avoiding duplicated truth avoids drift.

**Automate the decisions humans get wrong.** You still make the judgment call by choosing the
[Conventional Commits](versioning.md) type (`fix:` vs `feat:` vs a breaking change); but once that's written, the
version math — what number to bump to, the changelog, the tag — is derived automatically, so there's no separate
"remember to bump the version" decision to get wrong. Dependency updates come from
[Renovate](https://docs.renovatebot.com/); coverage thresholds and dependency hygiene are *gated* (a failure blocks the
merge), while the security audit is deliberately *non-blocking* — a newly-disclosed upstream CVE surfaces in the
pipeline without wedging unrelated releases, so you triage it rather than have CI break on someone else's advisory. You
write code and good commit messages — the machine handles the bookkeeping.

**Config over hardcoding.** Runnable behaviour is parametrized with [Hydra](https://hydra.cc/), so experiments and runs
are reconfigurable from the command line without editing source.

**Updatable scaffolding.** Because a project is *generated* with [Copier](copier.md) rather than copied once, template
improvements flow downstream via `copier update` — your project stays connected to its source instead of forking away
from it on day one.

## Why these tools (state of the art)

The choices reflect the current (2024–2026) Python tooling consensus, deliberately consolidating many older,
single-purpose tools into a few fast, well-maintained ones:

| Concern                              | Choice                                 | Replaces / why it's the modern default                                                                          |
| ------------------------------------ | -------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Deps · env · build · publish · audit | **uv**                                 | pip + virtualenv + pip-tools + twine + pip-audit; Rust-fast, one lockfile, one tool                             |
| Lint + format                        | **ruff**                               | black + isort + flake8 + pyupgrade + pydocstyle; one fast tool, one config                                      |
| Git hooks / local gate               | **pre-commit**                         | ad-hoc git hooks; runs ruff, gitleaks, zizmor, commit-msg validation, and file hygiene before code is committed |
| Task running                         | **poethepoet**                         | Make / ad-hoc shell scripts; tasks live in `pyproject.toml`, runnable locally and in CI                         |
| Versioning                           | **commitizen** + Conventional Commits  | manual bumps / hand-rolled scripts; deterministic semver straight from history                                  |
| Multi-version testing                | **nox**                                | tox; sessions configured in Python, backed by uv                                                                |
| Dep hygiene · vuln scan              | **deptry** + `uv audit`                | manual review; automated in the quality gate                                                                    |
| Secrets · workflow security          | **gitleaks** + **zizmor**              | secret scanning beyond private keys; static security analysis of GitHub Actions                                 |
| Supply chain                         | **SHA-pinned actions** + Renovate      | pin every action to a commit SHA (not a movable tag); Renovate keeps the pins current                           |
| Documentation                        | **Material for MkDocs** + mkdocstrings | Sphinx; Markdown, API docs from docstrings                                                                      |
| Scaffolding                          | **Copier**                             | cookiecutter / hand-rolled scripts; supports *updates*, not just one-shot generation                            |
| Dependency updates                   | **Renovate**                           | Dependabot; works on GitLab **and** GitHub                                                                      |

None of this is locked in: each tool is configured in `pyproject.toml` (or its own small config file) and links to its
own upstream docs, so you can tune, swap, or remove any piece as your project's needs evolve.
