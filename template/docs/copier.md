# Templating with Copier

This project was generated from the [PyMaxQ](https://gitlab.mgmt.ai.se/dev-tools/pymaxq)
template using [Copier](https://copier.readthedocs.io), a tool for scaffolding projects
from a template and — crucially — **keeping them up to date** with that template over time.

You do not need Copier for day-to-day development. You only reach for it in two situations:
generating a brand-new project, and pulling later template improvements into an existing one.

## How this project was generated

A new project is created by answering a short set of questions (project name, package name,
description, author, GitLab group, and the target CI platform):

```bash
uv tool install copier
copier copy https://gitlab.mgmt.ai.se/dev-tools/pymaxq path/to/my-project
```

Copier renders the template into your project and records your answers in a
`.copier-answers.yml` file at the project root. **Do not delete or hand-edit that file** —
it is what makes updates possible.

## Pulling in template updates

This is the main reason we use Copier rather than a one-shot generator. When the PyMaxQ
template gains a new tool, a CI fix, or a better default, you can pull those changes into
*this* project without losing your own work:

```bash
copier update           # run from the project root, on a clean git tree
```

Copier looks up the template (and the version) you last used from `.copier-answers.yml`,
re-renders against the newest template release, and applies the diff. Conflicts are surfaced
the same way a `git merge` would, for you to resolve. Because updates are diff-based, your
own edits to generated files are preserved wherever they don't collide with template changes.

A few practical notes:

- Commit or stash your work first; Copier refuses to update a dirty tree.
- To re-answer the questions (e.g. you renamed the project), add `copier update` flags such
  as `--data project_name=...`, or run `copier copy` again into a fresh directory.
- Updates follow the template's git tags, so the template must be released (tagged) for an
  update to be available.

## How the template itself is structured

You only need this section if you are *maintaining* the PyMaxQ template rather than consuming
it. The template repository separates "what becomes your project" from "files used to develop
the template":

- **`copier.yml`** (repo root) declares the questions and engine settings.
- **`template/`** holds everything that is rendered into a generated project (set via
  `_subdirectory: template`).
- Files ending in **`.jinja`** are rendered through Jinja2 and the suffix is stripped; every
  other file is copied **verbatim**. This is why GitHub Actions workflows (which contain
  `${{ ... }}`) are kept as plain files — they must not be run through Jinja.
- The directory named `{{ package_name }}/` is renamed to your package on generation, because
  Copier templates path names as well as file contents.
- CI files are included conditionally on the `ci_platform` answer using Copier's
  empty-filename-skip mechanism, so a GitLab-only project never ships GitHub workflows and
  vice-versa.

The template is itself tested: `tests/test_generation.py` generates throwaway projects and
asserts they are structurally correct (package renamed, no unrendered Jinja, the right CI
files present). Run them with `uv run --with copier --with pytest pytest tests/`.

The template even **documents itself by dogfooding**: its own `.github/workflows/docs.yml`
generates a project *from the template* (with the repo's GitHub identity), builds that
project's documentation, and deploys it to GitHub Pages. So the very page you are reading was
produced by the same `copier copy` → `poe docs` path a consumer uses — which means a broken
template can't publish green docs.
