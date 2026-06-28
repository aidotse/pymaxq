# PyMaxQ

**A [Copier](https://copier.readthedocs.io) template for max-quality Python projects.**

PyMaxQ scaffolds a Python project that arrives already wired for testing, linting,
typing, security, versioning, documentation, and releasing — so quality is the
*default*, not something you bolt on later. The name nods to **max Q**, the point of
peak aerodynamic pressure during a launch: the tooling here puts your code under
maximum quality pressure from the very first commit.

It is **GitHub-first but platform-agnostic**: every operation is a [poe](https://github.com/nat-n/poethepoet)
task, and the same task contract is driven by a GitHub Actions *or* GitLab CI pipeline
(or both). Generate once, then pull in future template improvements with `copier update`.

## Quickstart

```bash
uv tool install copier                                   # once
copier copy https://github.com/aidotse/pymaxq my-project # answer a few prompts
cd my-project
uv sync && uv run pre-commit install                     # set up the environment + hooks
```

See [Getting Started](getting-started.md) for the prompts and the day-one workflow.

## What you get

A single `copier copy` gives you a project that can:

- install and lock dependencies reproducibly with **[uv](https://docs.astral.sh/uv/)**;
- format, lint, and type-check on every commit (**[ruff](https://docs.astral.sh/ruff/)**, **[mypy](https://mypy-lang.org/)**, **[pre-commit](https://pre-commit.com/)**);
- test with coverage on one interpreter *and* across Python 3.10–3.13 (**[pytest](https://docs.pytest.org/)**, **[nox](https://nox.thea.codes/)**);
- check dependency hygiene and scan for vulnerabilities (**deptry**, **`uv audit`**);
- scan for leaked secrets and statically audit its CI workflows (**[gitleaks](https://github.com/gitleaks/gitleaks)**, **[zizmor](https://docs.zizmor.sh/)**);
- version itself from [Conventional Commits](https://www.conventionalcommits.org/) with a generated changelog (**[commitizen](https://commitizen-tools.github.io/commitizen/)**);
- build, publish, document, and release through CI on GitHub or GitLab;
- keep its dependencies current automatically (**[Renovate](https://docs.renovatebot.com/)**).

The [Design & Philosophy](design.md) page explains *why* each of these was chosen.

!!! note "This site is dogfooded"
    PyMaxQ is documented with the **same** Material for MkDocs stack it ships to generated
    projects. And in CI it generates a throwaway project from itself and runs that project's
    full test matrix + docs build end-to-end — so a broken template can't ship green.
