# Developing the template

This page is for *contributing to PyMaxQ itself* — not for using a generated project. For setup instructions, see
`user-guide.md`, which apply to both this template as well as its rendered projects.

## Two distinct concerns

The repository cleanly separates the template from the machinery used to develop it:

- **Repo root** = developing the template: `copier.yml` (questions + engine settings), the generation `tests/`, this
    documentation (`docs/` + `mkdocs.yaml`), and the repo's **own** dogfooded toolchain (`pyproject.toml`,
    `.pre-commit-config.yaml`, `renovate.json`, `.github/workflows/`). **None of this is shipped** — Copier renders only
    `template/`.
- **`template/`** = what becomes the user's project. Files ending in `.jinja` are rendered (suffix stripped); everything
    else is copied verbatim. The `{{ package_name }}/` directory is renamed to the user's package on generation.

So: to change the *generated project's* build config, edit `template/pyproject.toml.jinja`; the **root `pyproject.toml`
is the template repo's own dev config** — different file, different purpose.

## Dogfooded toolchain

PyMaxQ uses the same tools it ships. Everything is a poe task:

```bash
uv sync                       # dev env (copier, pytest, ruff, mypy, pre-commit, commitizen)
uv run pre-commit install     # activate hooks (incl. commit-msg → Conventional Commits)
uv run poe lint               # ruff, mypy, gitleaks, zizmor, check-github-workflows, deptry, mdformat, etc.
uv run poe test               # the generation tests (pytest tests/)
uv run poe generate           # render a sample from HEAD into .dogfood-site/ to inspect
uv run poe docs               # build this documentation site (mkdocs build)
...
```

`poe lint`/`poe test` exclude `template/` — it's unrendered Jinja, validated instead in the generated project and by
`tests/`.

## Configuration Synchronization

Because PyMaxQ is built with the exact same toolchain it ships, we face a deduplication challenge: keeping the
template's rules in perfect sync with the repository's internal rules.

To solve this without duplicating code, PyMaxQ uses a strict **two-way data flow** strategy depending on the type of
file:

### 1. Root → User (Post-Generation Tasks)

For static files that require no Jinja templating, the single source of truth lives in the **PyMaxQ root directory**.

- **Example:** `renovate.json`
- **How it works:** We do not put a copy in the `template/` directory. Instead, Copier is configured with a
    post-generation task (`_tasks` in `copier.yml`). After a user generates a project, Copier dynamically copies the
    master file from the template's absolute source path (`{{ _src_path }}`) directly into the user's new repository.

### 2. Template → Root (Generate Locally, Enforce in CI)

For dynamic files that rely on Jinja variables (like `ci_platform`), or that require structural modifications to work
with PyMaxQ, the single source of truth lives inside the **`template/` directory**.

- **Examples:** `template/mkdocs.yaml.jinja`, `template/.pre-commit-config.yaml.jinja`,
    `.github/workflows/reusable-pipeline.yml`. For the full list see the `sync` task in `pyproject.toml`.
- **How it works:** We push these rules *up* into the PyMaxQ root so the repository can dogfood its own configurations.
    1. **Edit:** You make changes to the canonical `.jinja` files in the template.
    1. **Sync:** You run `uv run poe sync` locally. This script parses the templates, injects PyMaxQ's specific metadata
        (e.g., treating PyMaxQ as a `github` project), and overwrites the root `mkdocs.yaml`, `.pre-commit-config.yaml`,
        and `.gitignore` files.
    1. **Commit:** You commit both the `.jinja` modifications and the newly generated root files.

**CI Enforcement:** The `ci.yml` pipeline strictly enforces the "Template → Root" flow. If you modify a template but
forget to run the sync command, the pipeline runs the script, detects a `git diff` against your checked-in files, and
fails the build immediately.

## The git workflow

`main` is **protected** (the `no-commit-to-branch` hook blocks direct commits) — **work on a branch and merge via PR**.
Merging to `main` triggers `cz bump`, which versions the template from your Conventional Commit messages (`feat:` →
minor, `fix:` → patch, `BREAKING CHANGE` in the commit footer → major) and updates`CHANGELOG.md`. The bump commit
carries `[skip ci]`. The template isn't a package, so there's no publish — the release flow just tags + changelogs and
cuts a GitHub release.

> Warning: "Mind the generation loop" - `copier copy`/`copier update` and the generation tests (which pass
> `vcs_ref="HEAD"`) read **committed HEAD, not your working tree**. Commit template changes before generating or running
> the tests, or you'll silently validate stale state.

## CI: gate, release, and a dogfood test

PyMaxQ uses a unified CI/CD architecture driven by a centralized reusable workflow.

- **`ci.yml`** (PR + push to main) is the master trigger. It spins up two parallel tracks:
    - **`core-pipeline`**: Calls the centralized `reusable-pipeline.yml`. On PRs, it acts as a strict quality gate
        (`poe lint`, `poe test`, and a non-blocking `poe audit`). On merges to main, it acts as the continuous release
        engine: running `cz bump`, deploying MkDocs to GitHub Pages, and cutting the GitHub release.
    - **`e2e-dogfood`**: Generates a project from HEAD, `uv sync`s it, runs that project's *full* test matrix (3.10–3.13),
        builds its docs, and runs the entrypoint — the real proof a freshly generated project works end to end across
        versions.

So a broken template can't pass the e2e gate — quality is enforced on the template the same way the template enforces it
on you.
