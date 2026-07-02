# CLAUDE.md

**PyMaxQ is a [Copier](https://copier.readthedocs.io) template for "max quality" Python
projects.** Its value is the shipped toolchain/CI/scaffolding, *not* runtime code —
`template/{{ package_name }}/pipeline.py` is throwaway demo payload a generated project
replaces. Design rationale → `docs/design.md`. Full contributor guide → `docs/developing.md`
(read it before non-trivial changes; this file is only the tripwires + command contract).

## Two concerns — don't conflate them

- **Repo root** = *developing the template itself*: its own dogfooded toolchain (root
  `pyproject.toml`, `.pre-commit-config.yaml`, `renovate.json`, `.github/workflows/`), plus
  `copier.yml` (questions), `tests/` (generation tests), and this repo's own `docs/` site.
  **None of this root config ships** — copier renders only `template/`.
- **`template/`** = *what becomes the user's project* (`_subdirectory: template`).
  `.jinja` files are rendered (suffix stripped); everything else is copied verbatim.
  `template/{{ package_name }}/` is renamed to the user's package. Don't delete
  `template/{{ _copier_conf.answers_file }}.jinja` (it enables `copier update`).

> ⚠️ The root `pyproject.toml` is the **template's own dev config**. To change the *generated*
> project's build config, edit **`template/pyproject.toml.jinja`** — different file, different
> purpose. Same trap for every root-vs-`template/` pair. Full layout + template variables
> (`project_name`, `package_name`, `ci_platform`, …) → `docs/developing.md`.

## Before you touch anything (silent-failure tripwires)

- **edit → commit → test.** `copier`/`tests/` read **committed HEAD, not the working tree**
  (`vcs_ref="HEAD"`). Commit template changes before generating or running the tests, or you
  validate stale state. (Generate from the working tree via a *no-git* copy → copier falls
  back to `vcs_ref=None`.)
- **`main` is protected** (pre-commit's `no-commit-to-branch` blocks direct commits). Work on a
  branch, merge via PR. Merge → `release.yml` runs `cz bump`, so write **Conventional Commits**
  (`feat:`/`fix:`/`BREAKING CHANGE`).
- **`.jinja` docs**: wrap literal Jinja / GH-Actions `${{ … }}` in `{% raw %}…{% endraw %}` or
  generation breaks (`test_no_unrendered_jinja` catches it). Prefer plain `.md` for heavy
  template-syntax examples.
- **poe tasks are the CI contract** — CI files just call them. Put logic in poe tasks, not CI YAML.
- **Tests**: the **hyphenated fixture** (`my-cool-project` → `my_cool_project`) is the
  meaningful one — it exercises the package rename and `project_name`-vs-`package_name` URL
  handling. The `pymaxq` fixture is degenerate. Keep the hyphenated assertions.

## Working on the template (this repo's own toolchain, via poe)

```bash
uv sync                    # dev env from root pyproject (copier, pytest, ruff, …)
uv run pre-commit install  # hooks (incl. commit-msg → Conventional Commits)
uv run poe lint            # ruff, mypy, gitleaks, zizmor, workflow checks, hygiene
uv run poe test            # generation tests (tests/)
uv run poe docs            # build this repo's own docs site
uv run poe generate        # render a sample from HEAD into .dogfood-site/ to inspect
```
`poe lint`/`poe test` skip `template/` (unrendered Jinja — validated in generated projects and
by `tests/`). Task details → `docs/poe.md`; tool deep-dives → `docs/{uv,linting,pyproject,deptry,renovate,hydra,testing}.md`.

## The generated project (everything under `template/`)

Same poe-is-the-CI-contract model. Tasks in `template/pyproject.toml.jinja`: `lint`,
`deps-check`, `audit`, `test [cpus] [path]`, `test-all` (nox 3.10–3.13; `noxfile.py` is the
version SoT), `build`, `bump`, `docs`. Topic → where it's documented (`template/docs/` unless noted):

- **CI/CD** + baked-in gotchas (`fetch-depth: 0` + `fetch-tags`; cz exit 3/21 = no-release
  success; imperative `glab` release; zizmor-clean SHA-pinned actions) → `ci.md`
- **Versioning** (Conventional Commits → git tags via commitizen; `hatch-vcs`; no version string
  committed; `major_version_zero`) → `versioning.md`
- **Security** (gitleaks, zizmor when github, `uv audit`, ruff `S`, SHA-pinned actions) → `security.md`
- **Claude Code** as toolchain (docs + opt-in `.claude/statusline.sh`; `settings.json` *not* shipped) → `claude-code.md`
- **Hydra entrypoint** `scripts/example.py` → nested `_target_` instantiate → `getting-started.md` + the code
- **Tooling conventions** (ruff sole linter+formatter, mypy, deptry, loguru): config is SoT in
  `template/pyproject.toml.jinja`; reference deep-dives in root `docs/`.

`ci_platform` (`gitlab`/`github`/`both`, default `github`) selects which CI files render. URLs
use `project_name`, never `package_name`; reference `repo_url`/`docs_url` from `copier.yml`,
never hardcode hosts (`both` resolves to the GitHub host).
