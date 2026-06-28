# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

PyMaxQ is a **Copier template** for "max quality" Python projects — its value is the
tooling, CI/CD, and scaffolding, not runtime code. The example payload
(`template/{{ package_name }}/sorting.py` — sorting algorithms + a benchmark) is
throwaway demo code that exists to exercise the tooling; a generated project replaces it.

Users generate a project with [copier](https://copier.readthedocs.io):
```bash
copier copy <repo-url> path/to/my-project   # prompts for project_name, package_name, etc.
copier update                               # later: pull in template improvements
```

## Repository layout (two distinct concerns)

- **Repo root** = *developing the template itself*: `copier.yml` (questions + engine
  settings), this file, the landing `README.md`, `tests/` (generation tests), and
  `.github/workflows/docs.yml` — the **dogfood** workflow that generates a project from the
  template, builds its docs, and deploys to GitHub Pages. That is the template's *own* CI; it
  is not shipped to generated projects (those get their CI from `template/`).
- **`template/`** = *what becomes the user's project*. Copier renders this subdirectory
  (`_subdirectory: template`). Inside it:
  - Files ending in **`.jinja`** are rendered through Jinja and the suffix is stripped;
    **all other files are copied verbatim**. So edit `template/pyproject.toml.jinja`, not a
    root `pyproject.toml` (there isn't one).
  - The directory **`template/{{ package_name }}/`** is renamed to the user's package on
    generation (copier always templates path names).
  - `template/{{ _copier_conf.answers_file }}.jinja` writes `.copier-answers.yml` into
    generated projects so `copier update` works — don't remove it.

Template variables (defined in `copier.yml`): `project_name` (slug), `package_name`
(derived default: slug with `-`/spaces → `_`), `description`, `author`, `email`, `group`
(GitHub owner/org or GitLab namespace), and `ci_platform` (`gitlab` / `github` / `both`,
**default `github`** — selects which CI files render via copier's empty-filename-skip).
Pages/docs URLs use **`project_name`**, never `package_name`. **GitHub is the primary host:**
repo/docs host URLs are computed per-platform via `repo_url`/`docs_url` in `copier.yml`, and
`both` resolves to the GitHub host (`github.com`/`github.io`) — only a gitlab-only generation
uses the internal GitLab/Pages hosts. Reference `repo_url`/`docs_url`, don't hardcode hosts.

## Working on the template

```bash
# Run the template's own generation tests (no project deps needed)
uv run --with copier --with pytest pytest tests/ -v

# Manually generate to inspect output
uv tool run copier copy --defaults --data-file tests/answers.yml . /tmp/out
```

`tests/test_generation.py` generates with two fixtures and asserts structural
correctness. The **hyphenated fixture** (`my-cool-project` → `my_cool_project`) is the one
that actually exercises the package rename and the project_name-vs-package_name URL
handling — the `pymaxq` fixture is degenerate (the two names are identical), so keep the
hyphenated assertions when changing templates. The tests do not run `uv sync`/`poe test`
(network-bound); verify end-to-end manually by generating, then `cd /tmp/out && uv sync && uv run poe test`.

**This repo is git-tracked (branch `main`, tagged `v0.1.0`), so mind the loop: `edit → commit
→ test`.** `copier copy`/`copier update` and the tests (which pass `vcs_ref="HEAD"`) read
**committed HEAD, not the working tree** — so commit template changes before generating or
running the generation tests, or you'll silently validate stale state.

**Editing `.jinja` docs:** a rendered `.jinja` page that mentions Jinja or GitHub-Actions
`${{ }}` syntax must wrap those literals in `{% raw %}…{% endraw %}`, or Jinja parses the inner
`{{ }}` and generation breaks (`test_no_unrendered_jinja` catches it). Plain `.md` files (e.g.
`copier.md`) are the safer home for heavy template-syntax examples.

## The generated project (everything below lives under `template/`)

**poe tasks are the CI contract** — CI files just call them, so logic stays platform-agnostic.
Defined in `template/pyproject.toml.jinja`:
```bash
uv sync                       # .venv + dev group (headroom-ai is an optional `agent` extra)
uv run poe lint               # pre-commit: ruff, mypy, gitleaks, zizmor (GitHub-only), file hygiene
uv run poe deps-check         # deptry: unused / missing / misplaced deps
uv run poe audit              # uv audit (native, preview) — dependency CVEs
uv run poe test [cpus] [path] # single-version tests + coverage + artifacts (CPUS first!)
uv run poe test-all           # nox matrix across 3.10–3.13 (noxfile.py is the version SoT)
uv run poe build              # uv build (wheel + sdist)
uv run poe bump               # commitizen: version from commits + CHANGELOG + tag
uv run poe docs --verbose     # mkdocs build (incl. mkdocstrings API ref; run `poe test` first)
```

**Architecture of the generated project:**
- **Hydra entrypoint**: `scripts/example.py` loads `{{ package_name }}/configs/benchmark.yaml`
  and `hydra.utils.instantiate` builds the object graph from `_target_` keys.
- **Versioning = Conventional Commits → tags.** Commit messages drive the bump (`fix:`→patch,
  `feat:`→minor, `BREAKING CHANGE`→major; `major_version_zero` keeps breaking changes minor
  while < 1.0). `commitizen` (`version_provider = scm`) reads the latest tag, computes the
  next, writes `CHANGELOG.md` + the tag; `hatch-vcs` builds at that tag. No version string is
  committed. A `commit-msg` pre-commit hook validates messages. **There is no manual bump and
  no branch heuristic.**
- **CI/CD — one concept, two implementations** (`.gitlab-ci.yml` and/or `.github/workflows/`):
  - PR/MR → quality gate (`lint`, `deps-check`, `audit`, `test`, `test-all`).
  - Push to default branch → `poe bump`; if there are release-worthy commits it tags, and
    **publish/docs/release run as a continuation of the same pipeline** (via `needs:`), never
    a tag-triggered second run. The bump commit carries `[skip ci]`.
  - GitLab publishes to its package + container registries and GitLab Pages; GitHub publishes
    to PyPI via OIDC Trusted Publishing (or a private index when repo var
    `PUBLISH_TARGET=private-index`) and GitHub Pages.
  - **Gotchas baked in** (don't "fix" them away): GitHub checkouts use `fetch-depth: 0` +
    `fetch-tags` (else hatch-vcs/commitizen see no tags); the no-release case is treated as
    success (cz exit 3/21) and skips publish; the GitLab release is created imperatively with
    `glab` (the declarative `release:` keyword would fire with an empty tag on no-op pushes);
    GitHub Actions are SHA-pinned and checkouts/permissions are tuned so workflows pass zizmor
    at default strictness — keep them that way (Renovate maintains the pins).
- **Security** is layered in: `gitleaks` (secrets) and `zizmor` (GitHub Actions, only when
  `ci_platform` includes github) as pre-commit hooks, `uv audit` + ruff's bandit (`S`) rules in
  the gate, and SHA-pinned actions. Documented in `template/docs/security.md`.

**Tooling conventions** (in `template/pyproject.toml.jinja`): ruff is the sole linter+formatter
(line length 120, py310; bandit `S`/bugbear `B`; `I`/`UP` replace standalone isort/pyupgrade —
black/isort/pyupgrade were removed). mypy with `ignore_missing_imports`; Google docstrings;
`loguru` for logging. `deptry` ignores are in `[tool.deptry.per_rule_ignores]`.
