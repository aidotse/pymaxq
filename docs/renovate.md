# Dependency Updates (Renovate)

Pinned, locked dependencies are good for reproducibility but they go stale: security patches
and new releases pile up until upgrading becomes a daunting, all-at-once chore.
[Renovate](https://docs.renovatebot.com/) automates the boring part — it watches your
dependencies and opens small, reviewable merge/pull requests as updates become available, so
you upgrade continuously instead of in painful batches.

Renovate is configured by `renovate.json` at the project root. We chose Renovate over
Dependabot specifically because it works on both GitLab and GitHub, matching this
template's dual-platform goal.

## What our config does

```jsonc
{
  "extends": ["config:recommended", ":dependencyDashboard", ":semanticCommits"],
  "lockFileMaintenance": { "enabled": true },
  ...
}
```

- **`config:recommended`** is Renovate's sensible baseline.
- **`:dependencyDashboard`** creates a single tracking issue listing all pending updates.
- **`:semanticCommits`** makes Renovate raise its PRs/MRs as Conventional Commits (`chore(deps): ...`),
  so they flow through the same [commitizen-driven versioning](versioning.md) as everything else.
- **`lockFileMaintenance`** periodically refreshes `uv.lock` so transitive dependencies don't
  silently drift.
- Package rules group dev-tooling bumps and pre-commit hook bumps so you review related
  updates together rather than one MR per package.

Renovate detects `pyproject.toml` + `uv.lock` via its `pep621` manager and keeps both in sync.
It also updates the pinned **pre-commit hook** revisions and the **SHA-pinned GitHub Actions**
(bumping the commit SHA *and* its `# vX` version comment) — so pinning for safety never means
going stale. See [Security](security.md) for why those are pinned.

## Turning it on

#MM: lets double check that this is included in the getting started guide!
Renovate needs a runner; the config alone does nothing until you activate it:

- **GitHub**: install the [Mend Renovate app](https://github.com/apps/renovate) on the repo.
  It reads `renovate.json` and starts opening PRs.
- **GitLab**: there is no hosted app for self-managed instances, so run the Renovate CLI from
  a scheduled CI job (a pipeline schedule that runs `renovate`), or use a shared
  org-level runner if your platform team provides one.

Until then `renovate.json` is simply waiting — it costs nothing and is ready the moment you
enable a runner.
