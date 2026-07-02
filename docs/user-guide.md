# User Guide

Welcome! This guide walks through the core design principles behind this repo. It is inspired by best practices in the
software engineering community, and is intended to be general enough by making minimal assumptions on *what* you will be
coding, focusing rather on *how* to make this process efficient. Of course there are many tools out there that go much
further than what is used here; this repo gathers in essence the key ones, aiming to be as much as infrastructure
agnostic as possible.

The purpose of this repo is to help you design and manage better code faster and better, not to hinder you in the
software engineering process. Keep in mind that the tools here, like anything else, have learning curves and may seem
like hindrances at first, but will undoubtedly show their value once you get an idea of what is going on and why.

## Who is this for?

This guide and repo is meant for anyone that values code quality in their work. If you have a reason to start a new
Python project and want to do this in a principled way, this is a good starting point. This guide is written at a fairly
high level, but with an implicit assumption that you have some basic coding experience already, i.e. know how to use
`git` and have an otherwise high level understanding of how Python projects are structured and work.

## Toolset summary

This is an executive summary of the collection of tools / concepts used in this repository:

- Build system: [pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- Dependency manager: [uv](https://docs.astral.sh/uv/)
- Action runner: [poethepoet](https://github.com/nat-n/poethepoet) — run `uv run poe` to list tasks
- Linting & formatting: [ruff](https://docs.astral.sh/ruff/) (replaces black, isort, and pyupgrade)
- Static type checking: [mypy](https://mypy-lang.org/)
- Unit testing and coverage: [pytest](https://docs.pytest.org/) and
    [coverage](https://coverage.readthedocs.io/en/latest/index.html)
- Multi-version testing: [nox](https://nox.thea.codes/) across Python 3.10–3.13
- Dependency hygiene: [deptry](https://github.com/fpgmaas/deptry) (unused / missing / misplaced deps)
- Security: secret scanning with [gitleaks](https://github.com/gitleaks/gitleaks), `uv audit` for dependency
    vulnerabilities, and [zizmor](https://docs.zizmor.sh/) for GitHub Actions (see [Security](security.md))
- Dependency updates: [Renovate](https://docs.renovatebot.com/) (`renovate.json`)
- Documentation: [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) with API docs via
    [mkdocstrings](https://mkdocstrings.github.io/)
- Gated commits: [pre-commit](https://pre-commit.com/)
- Versioning: [Conventional Commits](https://www.conventionalcommits.org/) driven by
    [commitizen](https://commitizen-tools.github.io/commitizen/), applied to
    [git tags](https://git-scm.com/book/en/v2/Git-Basics-Tagging) (read at build time by hatch-vcs)
- Source code parametrization: [hydra](https://hydra.cc/)

Depending on how you generated the project, CI/CD runs via [GitHub Actions](https://docs.github.com/actions) and/or in
the [GitLab ecosystem](https://docs.gitlab.com/ee/ci/). Documentation is hosted with
[GitHub Pages](https://docs.github.com/pages) and/or [GitLab Pages](https://docs.gitlab.com/ee/user/project/pages/)
accordingly.

## Setup / installation

### 1. Install `uv`

If you don't have `uv` installed locally, install it via curl (macOS/Linux):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

*(For Windows or other methods, see the [official uv docs](https://docs.astral.sh/uv/getting-started/installation/)).*

### 2. Sync the environment

```bash
uv sync
```

This creates the `.venv` and installs the project (editable) plus the `dev` group. Optional agent/AI tooling lives
behind an extra: `uv sync --extra agent`. To reset, delete `.venv` and run `uv sync` again.

### 3. Test your installation

Run the default unit tests with `uv run poe test`, or the example Hydra script with `uv run scripts/example.py`. See all
available tasks with `uv run poe`.

### 4. Install the git hooks

```bash
uv run pre-commit install
```

This installs both the `pre-commit` hooks (see the full list in the pre-commit config) and the `commit-msg` hook that
validates your commit messages (see below).

## Conventional commits & versioning

Versioning is **automatic** and driven by your commit messages, so there are no manual version bumps. Write commits in
the [Conventional Commits](https://www.conventionalcommits.org/) format:

- `fix: ...` → patch release (e.g. `0.1.0` → `0.1.1`)
- `feat: ...` → minor release (e.g. `0.1.1` → `0.2.0`)
- a `feat!: ...` or a `BREAKING CHANGE:` footer → major release

A **release-worthy commit** is any commit whose Conventional-Commit type triggers a version bump: `fix:` (patch),
`feat:` (minor), or a breaking change (`!` or a `BREAKING CHANGE:` footer, major). Other types — `docs:`, `chore:`,
`test:`, `refactor:`, `ci:`, `style:` — do **not** trigger a release on their own; a push containing only those changes
produces no new version.

### Staying pre-1.0 (and how you eventually reach 1.0)

While the project is pre-1.0, `major_version_zero` is enabled: breaking changes are treated as a **minor** bump rather
than a major one, so a `0.x` release never automatically jumps to `1.0`. In other words, `feat!:` / `BREAKING CHANGE:`
on a `0.x` project bumps `0.3.0` → `0.4.0`, not `1.0.0`. This is intentional — pre-1.0 software is expected to break,
and it avoids an accidental "stable" `1.0` signal.

Reaching `1.0` is therefore a **deliberate, manual decision**, never something that happens on its own. When you are
ready to declare the API stable, either:

- run `uv run cz bump --major` to cut the `1.0.0` release explicitly, or
- turn `major_version_zero` off in the commitizen config, after which breaking changes bump the major version normally.

Until you take one of those steps, the project stays in the `0.x` series indefinitely.

The `commit-msg` hook rejects non-conforming messages locally. On merge to the default branch, CI runs
`uv run poe bump`: commitizen computes the next version from the commits since the last tag, updates `CHANGELOG.md`,
creates the git tag, and publishing follows. If there are no release-worthy commits, nothing is released.

You can preview the next changelog locally with `uv run poe changelog`.

## Repository settings

A few settings live in the hosting platform's UI. Most importantly, **protect the default branch**: the
`no-commit-to-branch` pre-commit hook only blocks direct commits *locally* (in each contributor's clone), so pair it
with server-side protection that requires changes to land via a reviewed PR/MR — and allow the release automation to
push the version bump (per-platform notes below).

### Enable Automatic Dependency Updates

This project includes a pre-configured [renovate.json](<(https://docs.renovatebot.com/)>) to keep your dependencies,
pre-commit hooks, and CI actions up to date automatically. To activate it on GitHub:

1. Navigate to the [Mend Renovate App](https://github.com/apps/renovate) on the GitHub Marketplace.
1. Click **Install** (or **Configure** if your organization already uses it).
1. Choose **Only select repositories** and select this project's repository.
1. Click **Save**.

> **Note:** Renovate will automatically read the `renovate.json` file at the root of this project. It will bundle
> development tooling updates into a single PR while opening individual PRs for production dependency updates to isolate
> test failures.

*(If you are hosting this project on GitLab, you will need to rely on your organization's internal Renovate bot or
configure a [GitLab Renovate runner](https://docs.renovatebot.com/modules/platform/gitlab/).)*

### If On GitHub...

- **Settings → Actions → General → Workflow permissions**: set **Read and write permissions** so the release workflow
    can push the bump commit/tag and create releases.
- **Branch protection** on `main`: enable **Require a pull request before merging** so collaborators can't push directly
    (the local `no-commit-to-branch` hook only guards each clone). Then let the release workflow push the bump — either
    add a bypass for `github-actions[bot]`, or create a fine-grained PAT with `contents: write`, store it as the
    `RELEASE_TOKEN` secret (the workflow prefers it over `GITHUB_TOKEN`), and allow it to bypass protection.
- **Pages**: go to **Settings → Pages** and set **Source** to **GitHub Actions**. Docs are deployed by the official
    GitHub Pages Actions from the release workflow run — there is no `gh-pages` branch, and only the single current
    version is published.
- **Publishing the package**:
    - *Default — PyPI via OIDC Trusted Publishing*: configure a
        [trusted publisher](https://docs.pypi.org/trusted-publishers/) on PyPI for this repo's `release.yml`. No secrets
        required.
    - *Private index instead*: set repo **variable** `PUBLISH_TARGET=private-index` and **variable** `PRIVATE_INDEX_URL`,
        plus secrets `PRIVATE_INDEX_USERNAME` / `PRIVATE_INDEX_PASSWORD`.

### If On GitLab...

Configure these under **Settings** for your project:

- **General → Badges** (optional): add a `Pipeline` badge, using your GitLab instance host with the `%{project_path}`
    placeholder for the link and `%{project_path}/badges/%{default_branch}/pipeline.svg` for the image.
- **Access Tokens**: create a project access token named `CI_REPO_ACCESS` with `read_repository` + `write_repository`
    scopes and a `Maintainer` role (it must be able to push the version bump commit + tag to the protected default
    branch).
- **CI/CD → Variables**:
    - Add `CI_REPO_ACCESS` (the token value) as **masked** and **not protected**.
    - Add `GIT_SSL_CAINFO` (type **File**) with any SSL certificates required to reach GitLab.
- **Repository → Protected branches**: protect the default branch and set *Allowed to push* so changes land only via
    merge requests — but allow `CI_REPO_ACCESS` (or Maintainers) to push so the automated bump can land.
- **Merge requests → Merge checks**: enable `Pipelines must succeed` and `All threads must be resolved`.
- **Pages**: no UI toggle is needed — GitLab Pages is served by the pipeline's reserved `pages` job, which publishes the
    `public/` directory. The single current version of the docs is served once that job runs on the default branch.
