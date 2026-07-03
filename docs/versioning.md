# Versioning & Releases

This project follows [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`), but you never bump the version by
hand. The version is **derived from your commit messages** using
[Conventional Commits](https://www.conventionalcommits.org/) and applied automatically by
[commitizen](https://commitizen-tools.github.io/commitizen/). Git tags remain the single source of truth for the
version; commit messages just decide *how much* to bump.

## How the next version is decided

Write commits in the Conventional Commits format — a type prefix, then a description:

```text
fix: handle empty input in the pipeline        ->  PATCH  (0.1.0 -> 0.1.1)
feat: add a reverse transform                   ->  MINOR  (0.1.1 -> 0.2.0)
feat!: drop Python 3.9 support                  ->  MAJOR  (0.2.0 -> 1.0.0)
```

A `!` after the type, or a `BREAKING CHANGE:` footer, marks a breaking change. Types like `docs:`, `chore:`, `test:`,
`refactor:`, `ci:`, and `style:` are **not release-worthy** — on their own they do not trigger a version bump. A
*release-worthy* commit is therefore one whose type is `fix:` (→ patch), `feat:` (→ minor), or any breaking change (→
major).

**Getting to 1.0.** While the project is still pre-1.0, the `major_version_zero` setting keeps breaking changes at a
*minor* bump, so a `0.x` line never accidentally jumps to `1.0` just because you landed a `feat!:`. Reaching `1.0` is
therefore a **deliberate** act, not something that happens on its own: when you decide the API is stable, cut it
explicitly with `uv run cz bump --increment MAJOR` (or turn `major_version_zero` off in `pyproject.toml` so breaking
changes start bumping the major version normally).

A `commit-msg` git hook (installed by `uv run pre-commit install`) validates every message locally, so non-conforming
commits are caught before they land. See [precommit](precommit.md).

## What `poe bump` does

On a merge to the default branch, CI runs:

```bash
uv run poe bump        # = cz bump --yes
```

commitizen then, in one step:

1. reads the current version from the latest git tag,
1. scans the commits since that tag and computes the next version,
1. updates `CHANGELOG.md` (grouped by type),
1. commits the changelog and creates the new `vX.Y.Z` tag.

If there are **no release-worthy commits** (e.g. a docs-only or chore-only merge), `cz` exits without bumping and CI
treats that as "nothing to release" — no tag, no publish. You can preview the changelog entry locally at any time with
`uv run poe changelog`.

The bump commit carries a `[skip ci]` marker so it doesn't re-trigger the pipeline. Publishing runs as a continuation of
the same pipeline rather than off the tag — see [CI/CD](ci.md).

## Where the version actually lives

There is **no version string committed** anywhere in the source. `commitizen` is configured with
`version_provider = "scm"`, meaning it reads and writes the version via git tags. At build time, `hatch-vcs` derives the
package version from the latest tag (falling back to `0.0.0` when no tag exists, e.g. in a fresh checkout or a Docker
build without `.git`). This keeps a single source of truth and avoids the classic "forgot to bump the version file"
drift. You can print the current version at any time with `uv run poe get-latest-tag` (which calls `cz version -p`).

## What about the docs?

The documentation site is **single-version**: each release rebuilds and replaces the published site (there is no
per-version archive). It deploys automatically as part of the same release pipeline — via the GitHub Pages Actions on
GitHub, or the reserved `pages` job on GitLab. See [Documentation](mkdocs.md) and [CI/CD](ci.md) for the details.
