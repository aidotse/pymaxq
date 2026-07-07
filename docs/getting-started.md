# Getting Started

## Generate a project

Install [Copier](https://copier.readthedocs.io) once, then generate from the template's git URL (or a local checkout):

```bash
uv tool install copier
copier copy --trust https://github.com/aidotse/pymaxq path/to/my-project
```

> **Note:** Generation requires a POSIX shell (Linux, macOS, or WSL/Git Bash on Windows) — `copier.yml`'s
> post-generation tasks run raw shell commands (`cp`, `mkdir -p`) that don't work in a native Windows shell. Because
> these tasks are unsafe, `copier copy` will also prompt to trust the template (or fail without `--trust` in
> non-interactive use).

Copier asks a short set of questions and renders the template accordingly:

| Prompt             | Meaning                                                                                  |
| ------------------ | ---------------------------------------------------------------------------------------- |
| `project_name`     | Project slug (lowercase, hyphens), e.g. `my-awesome-project`. Used in repo/docs URLs.    |
| `package_name`     | Importable package name (defaults to the slug with underscores).                         |
| `description`      | One-line description.                                                                    |
| `author` / `email` | Author name and email.                                                                   |
| `group`            | The namespace the repo lives under — GitHub owner/org **or** GitLab group.               |
| `ci_platform`      | `github` (default), `gitlab`, or `both`.                                                 |
| `gitlab_host`      | GitLab instance host (self-hosted or `gitlab.com`); only asked for GitLab-only projects. |

**GitHub is the primary host.** With `github` or `both`, the generated repo/docs URLs and the CI-status badge point at
GitHub; a GitLab-only project uses the GitLab equivalents. For `both`, GitHub is canonical and the GitLab pipeline runs
as a mirror.

## Set it up

```bash
cd path/to/my-project
uv sync                      # create the virtualenv + install dependencies
git init && git add -A       # start tracking the generated files
uv run poe lint              # auto-format the freshly rendered files (re-run + re-add if it reports changes)
git add -A
git commit -m "feat: initial project scaffold"   # feat -> your first release (v0.1.0), which deploys docs on push
uv run pre-commit install    # enable the git hooks for subsequent commits (incl. commit-msg validation)
git checkout -b feat/initial-setup               # branch off: main is protected by no-commit-to-branch
```

> **Why this order.** `uv run poe lint` runs the auto-fixing hooks (mdformat, `end-of-file-fixer`, `ruff-format`) over
> the freshly rendered files before you commit — it reports `Failed - files were modified` on that first pass, which is
> expected, so just `git add -A` and continue (it also skips `no-commit-to-branch`, so it works while still on `main`).
> Install the hooks *after* the initial commit: once installed, `no-commit-to-branch` would block committing on `main`.
> A `feat:` first commit cuts your first release (`v0.1.0`) on push, so the docs site and release publish immediately —
> a `chore:`/`docs:` message would produce no release, leaving the docs site and badges empty until your first feature.

> **Before your first release — one-time setup.** In your host's UI: **(1)** on GitHub, enable Pages (**Settings → Pages
> → Source: "GitHub Actions"**), or the docs-deploy job fails; and **(2)** once you protect the default branch
> (recommended — the shipped `no-commit-to-branch` hook and PR workflow assume it), give CI a way to push the release
> commit past that protection — a release-push credential (GitHub `RELEASE_TOKEN`, or a `github-actions[bot]` bypass;
> GitLab `CI_REPO_ACCESS`). Leave `main` unprotected and the default CI token pushes the release itself, but then it
> isn't protected. The full per-platform steps and the *why* are in the
> [Generated Project Guide → Repository settings](user-guide.md#repository-settings).

From there, everything is a [poe](https://github.com/nat-n/poethepoet) task — `uv run poe lint`, `uv run poe test`,
`uv run poe test-all`, `uv run poe docs`, and so on. The generated project ships its own starter documentation.

## Repository settings

After the first push, a handful of one-time settings in your host's UI get you to a green first pipeline and keep `main`
protected: protecting the default branch, giving CI a release-push credential, enabling GitHub Pages, and (optionally)
turning on package/Docker publishing. Because the generated project ships these instructions itself, they live in **one
place** — the [Generated Project Guide → Repository settings](user-guide.md#repository-settings) — rather than being
duplicated here.

## Stay up to date

Because the project is *generated* (not copied once), pull in later template improvements without losing your own
changes:

```bash
copier update     # run from inside the generated project, on a clean git tree
```

Copier reads the template + version you last used from `.copier-answers.yml`, re-renders against the newest template
release, and applies the diff — conflicts surface like a `git merge`. Don't delete or hand-edit `.copier-answers.yml`;
it's what makes updates work.

## The Contribution Lifecycle

PyMaxQ establishes a strict, predictable development loop. Once your project is generated, here is the standard
lifecycle for contributing code:

- **Local Development:** Write your code and tests.
- **Pre-commit Execution:** When you run `git commit`, the pre-commit hooks intercept the action. They format code
    (Ruff), check types (Mypy), scan for secrets (Gitleaks), and ensure your commit message follows the Conventional
    Commits standard.
- **Manual Fixes:** If a hook fails (e.g., Mypy finds a type error), the commit is aborted. You fix the issue and commit
    again.
- **Pull Requests:** Direct commits to the main branch are blocked by default. You push your feature branch and open a
    PR.
- **CI Quality Gate:** The PR triggers the CI pipeline, which runs the exact same tooling (`poe lint`, `poe test`,
    `poe audit`) in a clean environment to ensure no local anomalies slip through.
- **Release & Versioning:** Once merged to the main branch, the CI pipeline reads your Conventional Commit messages,
    automatically calculates the next semantic version, generates a changelog, and tags the release.

For deeper insights into how the template itself is built and maintained, refer to the
[Developing the template](developing.md) guide.
