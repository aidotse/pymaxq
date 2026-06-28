# Developing the template

This page is for *contributing to PyMaxQ itself* — not for using a generated project.

## Two distinct concerns

The repository cleanly separates the template from the machinery used to develop it:

- **Repo root** = developing the template: `copier.yml` (questions + engine settings), the
  generation `tests/`, this documentation (`docs/` + `mkdocs.yaml`), and the repo's **own**
  dogfooded toolchain (`pyproject.toml`, `.pre-commit-config.yaml`, `renovate.json`,
  `.github/workflows/`). **None of this is shipped** — Copier renders only `template/`.
- **`template/`** = what becomes the user's project. Files ending in `.jinja` are rendered
  (suffix stripped); everything else is copied verbatim. The `{{ package_name }}/` directory
  is renamed to the user's package on generation.

So: to change the *generated project's* build config, edit `template/pyproject.toml.jinja`; the
**root `pyproject.toml` is the template repo's own dev config** — different file, different
purpose.

## Dogfooded toolchain

PyMaxQ uses the same tools it ships. Everything is a poe task:

```bash
uv sync                       # dev env (copier, pytest, ruff, mypy, pre-commit, commitizen)
uv run pre-commit install     # activate hooks (incl. commit-msg → Conventional Commits)
uv run poe lint               # ruff, mypy, gitleaks, zizmor, check-github-workflows, hygiene
uv run poe test               # the generation tests (pytest tests/)
uv run poe generate           # render a sample from HEAD into .dogfood-site/ to inspect
uv run poe docs               # build this documentation site (mkdocs build)
```

`poe lint`/`poe test` exclude `template/` — it's unrendered Jinja, validated instead in the
generated project and by `tests/`.

## The git workflow

`main` is **protected** (the `no-commit-to-branch` hook blocks direct commits) — **work on a
branch and merge via PR**. Merging to `main` triggers `cz bump`, which versions the template
from your Conventional Commit messages (`feat:` → minor, `fix:` → patch, …) and updates
`CHANGELOG.md`. The bump commit carries `[skip ci]`. The template isn't a package, so there's
no publish — the release flow just tags + changelogs and cuts a GitHub release.

!!! warning "Mind the generation loop"
    `copier copy`/`copier update` and the generation tests (which pass `vcs_ref="HEAD"`) read
    **committed HEAD, not your working tree**. Commit template changes before generating or
    running the tests, or you'll silently validate stale state.

## CI: gate, release, and a dogfood test

- **`ci.yml`** (PR + push to main) runs `poe lint` + `poe test` + a non-blocking `poe audit`,
  plus an **e2e-dogfood** job: it generates a project from HEAD, `uv sync`s it, runs that
  project's *full* nox matrix (3.10–3.13), builds its docs, and runs the entrypoint — the real
  proof a freshly generated project works end to end across versions.
- **`release.yml`** (merge to main) runs `cz bump` and cuts the GitHub release.
- **`docs.yml`** builds *this* site and deploys it to GitHub Pages.

So the published docs are produced with the exact Material for MkDocs setup the template ships,
and a broken template can't pass the e2e gate — quality is enforced on the template the same way
the template enforces it on you.
