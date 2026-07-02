# Getting Started

## Generate a project

Install [Copier](https://copier.readthedocs.io) once, then generate from the template's
git URL (or a local checkout):

```bash
uv tool install copier
copier copy https://github.com/aidotse/pymaxq path/to/my-project
```

Copier asks a short set of questions and renders the template accordingly:

| Prompt | Meaning |
| --- | --- |
| `project_name` | Project slug (lowercase, hyphens), e.g. `my-awesome-project`. Used in repo/docs URLs. |
| `package_name` | Importable package name (defaults to the slug with underscores). |
| `description` | One-line description. |
| `author` / `email` | Author name and email. |
| `group` | The namespace the repo lives under — GitHub owner/org **or** GitLab group. |
| `ci_platform` | `github` (default), `gitlab`, or `both`. |

**GitHub is the primary host.** With `github` or `both`, the generated repo/docs URLs and
the CI-status badge point at GitHub; a GitLab-only project uses the GitLab equivalents. For
`both`, GitHub is canonical and the GitLab pipeline runs as a mirror.

## Set it up

```bash
cd path/to/my-project
uv sync                      # create the virtualenv + install dependencies
uv run pre-commit install    # install the git hooks (incl. commit-msg validation)
git init && git add -A && git commit -m "chore: initial commit from pymaxq"
```

From there, everything is a [poe](https://github.com/nat-n/poethepoet) task — `uv run poe lint`,
`uv run poe test`, `uv run poe test-all`, `uv run poe docs`, and so on. The generated project
ships its own starter documentation.

## Repository settings

A few things are enabled in the hosting platform's UI (the generated project's own docs spell
these out in detail):

- **Protected default branch** with merges via PR/MR (the `no-commit-to-branch` hook enforces
  this locally; enable server-side protection too).
- A **release token** so CI can push the version bump + tag back to the protected branch.
- **Pages** source set to the CI deployment, and — on GitHub — a **PyPI Trusted Publisher** if
  you publish there.

## Stay up to date

Because the project is *generated* (not copied once), pull in later template improvements
without losing your own changes:

```bash
copier update     # run from inside the generated project, on a clean git tree
```

Copier reads the template + version you last used from `.copier-answers.yml`, re-renders
against the newest template release, and applies the diff — conflicts surface like a `git
merge`. Don't delete or hand-edit `.copier-answers.yml`; it's what makes updates work.

## The Contribution Lifecycle

PyMaxQ establishes a strict, predictable development loop. Once your project is generated, here is the standard lifecycle for contributing code:

* **Local Development:** Write your code and tests.
* **Pre-commit Execution:** When you run `git commit`, the pre-commit hooks intercept the action. They format code (Ruff), check types (Mypy), scan for secrets (Gitleaks), and ensure your commit message follows the Conventional Commits standard.
* **Manual Fixes:** If a hook fails (e.g., Mypy finds a type error), the commit is aborted. You fix the issue and commit again.
* **Pull Requests:** Direct commits to the main branch are blocked by default. You push your feature branch and open a PR.
* **CI Quality Gate:** The PR triggers the CI pipeline, which runs the exact same tooling (`poe lint`, `poe test`, `poe audit`) in a clean environment to ensure no local anomalies slip through.
* **Release & Versioning:** Once merged to the main branch, the CI pipeline reads your Conventional Commit messages, automatically calculates the next semantic version, generates a changelog, and tags the release.

For deeper insights into how the template itself is built and maintained, refer to the [Developing the template](developing.md) guide.
