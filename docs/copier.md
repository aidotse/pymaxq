# Templating with Copier

[Copier](https://copier.readthedocs.io) is a tool for scaffolding projects from a template and — crucially — **keeping
them up to date** with that template over time.

You do not need Copier for day-to-day development. You only reach for it in two situations: generating a brand-new
project, and pulling later template improvements into an existing one.

## Generating new projects

A new project is created by answering a short set of questions (project name, package name, description, author,
namespace — GitHub owner/org or GitLab group — and the target CI platform):

```bash
uv tool install copier
copier copy https://github.com/aidotse/pymaxq path/to/my-project
```

Copier renders the template into your project and records your answers in a `.copier-answers.yml` file at the project
root. **Do not delete or hand-edit that file** — it is what makes updates possible.

## Pulling in template updates

This is the main reason we use Copier rather than a one-shot generator. When the PyMaxQ template gains a new tool, a CI
fix, or a better default, you can pull those changes into a previously generated project without losing your own work:

```bash
copier update           # run from the project root, on a clean git tree
```

Copier looks up the template (and the version) you last used from `.copier-answers.yml`, re-renders against the newest
template release, and applies the diff. Conflicts are surfaced the same way a `git merge` would, for you to resolve.
Because updates are diff-based, your own edits to generated files are preserved wherever they don't collide with
template changes.

A few practical notes:

- Commit or stash your work first; Copier refuses to update a dirty tree.
- To re-answer the questions (e.g. you renamed the project), add `copier update` flags such as
    `--data project_name=...`, or run `copier copy` again into a fresh directory.
- Updates follow the template's git tags, so the template must be released (tagged) for an update to be available.

## How the template itself is structured

You only need this section if you are *maintaining* the PyMaxQ template rather than consuming it. The template
repository separates "what becomes your project" from "files used to develop the template":

- **`copier.yml`** (repo root) declares the questions and engine settings.
- **`template/`** holds everything that is rendered into a generated project (set via `_subdirectory: template`).
- Files ending in **`.jinja`** are rendered through Jinja2 and the suffix is stripped; every other file is copied
    **verbatim**. This is why GitHub Actions workflows (which contain `${{ ... }}`) are kept as plain files — they must
    not be run through Jinja.
- The directory named `{{ package_name }}/` is renamed to your package on generation, because Copier templates path
    names as well as file contents.
- CI files are included conditionally on the `ci_platform` answer using Copier's empty-filename-skip mechanism, so a
    GitLab-only project never ships GitHub workflows and vice-versa.

The template is itself tested: `tests/test_generation.py` generates throwaway projects and asserts they are structurally
correct (package renamed, no unrendered Jinja, the right CI files present). After `uv sync`, run them with
`uv run poe test`.

The template **dogfoods its own toolchain**: PyMaxQ is developed with the same uv + poe + pre-commit + commitizen setup
it ships, its documentation site is built with this same Material for MkDocs stack, and its CI generates a throwaway
project on every push to prove the template still generates, tests, and builds end-to-end — so a broken template can't
ship green.
