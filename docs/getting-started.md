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

> **Before your first release — one-time platform setup.** For a green first pipeline, set two things in your host's UI
> (both detailed in [Repository settings](#repository-settings)): **(1)** protect the default branch *and* give CI a
> credential to push the release bump back to it — on GitHub a `RELEASE_TOKEN` secret (or a `github-actions[bot]`
> bypass), on GitLab a `CI_REPO_ACCESS` token — otherwise the release job can't push and the pipeline fails; and **(2)**
> on GitHub only, enable Pages (**Settings → Pages → Source: "GitHub Actions"**), which CI cannot do for you, otherwise
> the docs-deploy job fails. GitLab needs no Pages step.

From there, everything is a [poe](https://github.com/nat-n/poethepoet) task — `uv run poe lint`, `uv run poe test`,
`uv run poe test-all`, `uv run poe docs`, and so on. The generated project ships its own starter documentation.

## Repository settings

A few things are enabled in the hosting platform's UI (the generated project's own docs spell these out in detail):

- **Protected default branch** with merges via PR/MR (the `no-commit-to-branch` hook enforces this locally; enable
    server-side protection too).
- A **release token** so CI can push the version bump + tag back to the protected branch.
- **Publishing is opt-in.** Out of the box CI versions, changelogs, releases, and deploys the docs site, but does
    **not** publish your package or a Docker image until you opt in with repo variables (`PUBLISH_TARGET`,
    `BUILD_DOCKER`) — so a project that isn't ready to publish never sees a red pipeline. The generated project's own
    "Publishing" guide spells out the variables and credentials per platform.
- **GitHub Pages** (GitHub only) — **one-time manual step, before your first release.** Enable Pages under **Settings →
    Pages → Source: "GitHub Actions"**. CI cannot enable it for you: creating the Pages site needs a permission the
    default CI token never has (`administration: write`). Until it's enabled the docs-deploy job fails; once enabled it
    stays enabled and every release publishes. (On GitLab, Pages is served from the CI deployment with no setup.)

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
