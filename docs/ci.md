# CI/CD

> Continuous Integration / Continuous Delivery: the practice of automatically building, testing, and releasing your code
> so that every change is validated and shippable.

The guiding principle here is that **the CI file contains no logic** — all of it lives in
[poe tasks](https://github.com/nat-n/poethepoet) in `pyproject.toml`. The CI file is thin platform glue: *when* to run,
*what* credentials to use, and *where* to deploy. This is what lets the same pipeline concept be implemented for both
GitLab and GitHub with almost no duplicated logic.

## The release lifecycle (one concept, two implementations)

Whatever the platform, the pipeline implements the same three-phase concept:

- **On a merge request / pull request → the quality gate.** Run `lint`, `deps-check`, `audit`, `test` (single version +
    coverage), and `test-all` (the [nox](https://nox.thea.codes/) matrix). Nothing is versioned or published; this phase
    only answers "is this change healthy?".
- **On a push to the default branch → version.** Run `poe bump`. `commitizen` inspects the commits since the last tag
    and, if any warrant a release, writes `CHANGELOG.md`, creates the `vX.Y.Z` tag, and pushes both. If nothing warrants
    a release, the job succeeds and the publish steps are skipped. See [Versioning & Releases](versioning.md).
- **Immediately after a successful bump → publish.** Build and publish the package, build and push the Docker image,
    deploy the docs, and create the release entry.

## Why publishing is a *continuation*, not a tag-triggered pipeline

A natural design would be "push a tag, let a separate tag pipeline publish." We deliberately do **not** do that. The
bump commit carries a `[skip ci]` marker so it can't re-trigger the pipeline and cause an infinite bump loop — but
`[skip ci]` would *also* suppress a tag-triggered pipeline, so the tag could never reliably start publishing. Instead,
the publish jobs run as a **continuation of the same pipeline run** that performed the bump (wired with `needs:`), gated
on whether a bump actually happened. This is robust on both platforms and keeps the two implementations symmetric.

## Docs deployment (single-version)

Docs are **single-version** — there is no per-version docs archive. On **GitHub**, docs deploy via the official GitHub
Pages Actions (`actions/upload-pages-artifact` + `actions/deploy-pages`) directly from the workflow run, so there is no
`gh-pages` branch to maintain. On **GitLab**, docs deploy via the reserved `pages` job, which serves the built site from
the `public/` directory to GitLab Pages.

## GitLab implementation (`.gitlab-ci.yml`)

Pipelines run on merge request events and on pushes to the default branch (not on tags). The (default) stages are
`.pre → setup → test → version → release`:

> New to GitLab CI? Key terms

```
A **stage** is a phase that runs after the previous one completes (jobs in the same stage run in parallel). **`needs:`**
lets a job start the moment specific jobs finish, forming a DAG across stages. **`allow_failure: true`** lets a job fail
without failing the pipeline. **`rules:`** decide *when* a job runs (e.g. default-branch only). A **dotenv artifact**
(`artifacts:reports:dotenv`) exports variables — like `BUMPED` and the new version — from one job into the environment
of later jobs. **`CI_REPO_ACCESS`** is a token allowed to push to the protected default branch, so the automated bump
can land.
```

- **`build-ci-image`** (`.pre`): builds the custom CI image (with internal CA certs) used by the Python jobs, via Docker
    BuildKit on a shell runner.
- **`setup`**: `uv sync` to build and cache the environment (`.venv` + `.uv-cache`, keyed on `uv.lock`); later jobs
    consume the cache.
- **`lint` / `deps-check` / `audit` / `run-tests` / `test-matrix`** (`test`): the quality gate, each calling its poe
    task. `audit` is `allow_failure: true` so a freshly-disclosed advisory surfaces without hard-blocking a release.
- **`version-bump`** (`version`, default branch only): runs `cz bump`. On a real bump it pushes the commit + tag using
    the `CI_REPO_ACCESS` token and records `BUMPED=true` plus the new version in a dotenv artifact; on a no-op it
    records `BUMPED=false`.
- **`release` stage** (all `needs: version-bump`, each guarded by `BUMPED`): `publish-package` (`uv build` +
    `uv publish` to the GitLab PyPI registry), `build-and-push-image` (versioned Docker image to the container
    registry), `build-docs` + `pages` (the reserved `pages` job serving the single-version site from `public/` to GitLab
    Pages), and `gitlab-release` (creates the release entry with `glab`). Each no-ops cleanly when nothing was released.

Required project settings (tokens, protected-branch push rights, `GIT_SSL_CAINFO`) are listed under "Repository settings
→ GitLab" in [Getting Started](getting-started.md).

## GitHub implementation (`.github/workflows/`)

The same concept, split into a thin entry-point workflow and a reusable workflow that holds every actual job:

> New to GitHub Actions? Key terms

```
A **workflow** is a YAML file of **jobs**; each job runs **steps** on a fresh runner. A workflow whose only trigger is
`on: workflow_call` is a **reusable workflow** — it defines no triggers of its own and is instead invoked from another
workflow via `uses: ./path/to/workflow.yml`, with the caller passing `inputs` and (optionally) `secrets: inherit`.
**`needs:`** makes a job wait for another, and **`if: needs.bump.outputs.bumped == 'true'`** runs a job only when an
upstream job's **output** says a release happened (jobs publish `outputs` that downstream jobs read). **`permissions:`**
scope a job's automatic `GITHUB_TOKEN` to least privilege; **`id-token: write`** turns on OIDC so `uv publish`
authenticates to PyPI without a stored token (Trusted Publishing). A **PAT** in the `RELEASE_TOKEN` secret is needed
only to push past branch protection.
```

- **`ci.yml`** is the entry point: it runs on pull requests and pushes to `main`, and contains a single job,
    `core-pipeline`, which does nothing but `uses: ./.github/workflows/reusable-pipeline.yml` — invoking the reusable
    workflow below with `build_docker` / `publish_pypi` inputs and `secrets: inherit`. There is no separate
    `release.yml`; the release-stage jobs live in the same reusable workflow as the quality gate.
- **`reusable-pipeline.yml`** declares `on: workflow_call` only (it is never triggered directly) and holds every job,
    structured in the same three phases described above:
    - **Quality gate** (always runs, on PRs and pushes alike): `quality` (`lint`/`deps-check`/`audit`/`test`) and
        `test-matrix` (`poe test-all`). Every checkout uses `fetch-depth: 0` + `fetch-tags` so hatch-vcs and commitizen
        can see the tag history. All actions are **SHA-pinned** (with a version comment, Renovate-maintained) and the
        workflows are written to pass [zizmor](security.md) at default strictness.
    - **Version** — the **`bump`** job (`needs: [quality, test-matrix]`, gated
        `if: github.event_name == 'push' && github.ref == 'refs/heads/main'`) runs `cz bump`, pushes the commit + tag, and
        exposes `bumped` and `version` as job outputs.
    - **Release** — **`publish`**, **`build-and-push-image`**, and **`docs`** each `needs: bump` and run only
        `if: needs.bump.outputs.bumped == 'true'` (`publish` and `build-and-push-image` are additionally gated on the
        caller-supplied `publish_pypi` / `build_docker` inputs). `publish` does `uv build` then `uv publish`, using PyPI
        **OIDC Trusted Publishing** by default (tokenless, via `id-token: write`) or a private index when the repo
        variable `PUBLISH_TARGET=private-index` is set. `build-and-push-image` builds the image with
        `docker/build-push-action`, using registry-based BuildKit caching (`cache-from`/`cache-to` against a `:buildcache`
        tag) and pushes to `ghcr.io/${{ github.repository }}`, tagged with the release's semver version and `latest`.
        `docs` builds the single-version site and uploads it as a Pages artifact; the downstream **`deploy-docs`** job
        (`needs: docs`) deploys it via the official GitHub Pages Actions (`actions/upload-pages-artifact` +
        `actions/deploy-pages`) straight from the workflow run, with no `gh-pages` branch. **`github-release`** (also
        `needs: bump`, same `bumped` gate) creates the release entry.

GitHub-pushed commits/tags don't re-trigger workflows, which (together with `[skip ci]`) prevents loops without a PAT.
Required settings (workflow write permissions, branch-protection bypass, Pages source, PyPI trusted publisher) are under
"Repository settings → GitHub" in [Getting Started](getting-started.md).
