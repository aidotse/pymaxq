# CLAUDE.md

**PyMaxQ is a [Copier](https://copier.readthedocs.io) template for "max quality" Python projects.** Its value is the
shipped toolchain/CI/scaffolding, *not* runtime code — `template/{{ package_name }}/pipeline.py` is throwaway demo
payload a generated project replaces. Rationale → `docs/design.md`. Full contributor guide → `docs/developing.md`
(source of truth for the mechanics below — read before non-trivial changes; this file is tripwires only).

## Two concerns — don't conflate them

- **Repo root** = *developing the template itself*: dogfooded toolchain (root `pyproject.toml`,
    `.pre-commit-config.yaml`, `renovate.json`, `.github/workflows/`), `copier.yml`, generation `tests/`, this repo's
    own `docs/` site. **None of it ships** — Copier renders only `template/`.
- **`template/`** = *what becomes the user's project* (`_subdirectory: template`). `.jinja` files render (suffix
    stripped); everything else copies verbatim. `template/{{ package_name }}/` is renamed to the user's package. Don't
    delete `template/{{ _copier_conf.answers_file }}.jinja` (enables `copier update`).
- Same root-vs-`template/` split applies to `pyproject.toml`, `.pre-commit-config.yaml`, `mkdocs.yaml`, `.gitignore` —
    editing the wrong one is a silent no-op. Which direction each syncs, and how `poe sync` + CI's `enforce-sync` job
    keep them from drifting → "Configuration Synchronization" in `docs/developing.md`.

## Docs: two audiences

Root `docs/*.md` (`ci.md`, `versioning.md`, `security.md`, `claude-code.md`, `hydra.md`, `uv.md`, `linting.md`,
`pyproject.md`, `deptry.md`, `renovate.md`, `poe.md`, `mkdocs.md`, `testing.md`, …) is this repo's **own** mkdocs site —
dogfooded-tooling reference for template contributors, never shipped. The generated project instead gets one
self-contained `docs/user-guide.md` (copied verbatim from root via a `copier.yml` `_tasks` entry) plus
`template/docs/reference.md.jinja` (mkdocstrings API reference). Changing generated-project-facing behavior? Update
`user-guide.md`, not a root deep-dive page.

## Before you touch anything (silent-failure tripwires)

- **edit → commit → test.** `copier`/`tests/` read **committed HEAD, not the working tree** (`vcs_ref="HEAD"`). Commit
    template changes before generating/testing, or you validate stale state.
- **`main` is protected** (`no-commit-to-branch`) — branch + PR. `ci.yml`'s `core-pipeline` job (calling
    `reusable-pipeline.yml`) runs `cz bump` on push to main, so write **Conventional Commits**
    (`feat:`/`fix:`/`BREAKING CHANGE`). There is no separate `release.yml`.
- **`.jinja` docs**: wrap literal Jinja / GH-Actions `${{ … }}` in `{% raw %}…{% endraw %}` or generation breaks
    (`test_no_unrendered_jinja`). Prefer plain `.md` for heavy template-syntax examples.
- **poe tasks are the CI contract** — CI files just call them; put logic in poe tasks, not CI YAML.
- **Tests**: the **hyphenated fixture** (`my-cool-project` → `my_cool_project`) is the meaningful one — exercises
    package rename + `project_name`-vs-`package_name` URL handling. `pymaxq` fixture is degenerate; keep the hyphenated
    assertions.

## Working on the template (via poe)

```bash
uv sync                    # dev env from root pyproject (copier, pytest, ruff, …)
uv run pre-commit install  # hooks (incl. commit-msg → Conventional Commits)
uv run poe lint            # ruff, mypy, gitleaks, zizmor, workflow checks, deptry, mdformat, hygiene
uv run poe test            # generation tests (tests/)
uv run poe sync            # regen root mkdocs.yaml/.pre-commit-config.yaml/.gitignore from template/ (CI-enforced clean)
uv run poe docs            # build this repo's own docs site
uv run poe generate        # render a sample from HEAD into .dogfood-site/ to inspect
```

`poe lint`/`poe test` skip `template/` (unrendered Jinja — validated in generated projects and by `tests/`).

## The generated project (everything under `template/`)

Same poe-is-the-CI-contract model, dogfooding root's own tools (ruff/mypy/deptry/pytest/nox/commitizen/pre-commit).
Tasks in `template/pyproject.toml.jinja`: `lint`, `deps-check`, `audit`, `test [cpus] [path]`, `test-all` (nox
3.10–3.13; `noxfile.py` is the version SoT), `build`, `bump`, `docs` — all covered end-to-end in the shipped
`docs/user-guide.md` (CI/CD, versioning, security, Claude Code, Hydra entrypoint, tooling conventions).

`ci_platform` (`gitlab`/`github`/`both`, default `github`) selects which CI files render. URLs use `project_name`, never
`package_name`; reference `repo_url`/`docs_url` from `copier.yml`, never hardcode hosts (`both` resolves to the GitHub
host).
