# Changelog

All notable changes to this project are documented in this file.

This file is managed by [Commitizen](https://commitizen-tools.github.io/commitizen/) and is updated automatically on
each `poe bump` (driven by [Conventional Commits](https://www.conventionalcommits.org/)). Do not edit it by hand.

## v0.1.7 (2026-07-06)

### Fix

- trivial commit to force patch bump

## v0.1.6 (2026-07-06)

### Fix

- exclude CHANGELOG.md from mdformat
- suppress zizmor secrets-inherit finding in generated ci.yml

## v0.1.5 (2026-07-06)

### Fix

- use _copier_conf.src_path for post-copy tasks

## v0.1.4 (2026-07-06)

### Fix

- trivial commit
- trivial commit

## v0.1.3 (2026-07-04)

### Fix

- added tests for scripts, etc.

## v0.1.2 (2026-07-03)

### Fix

- **ci**: self-enable GitHub Pages so docs deploy no longer 404s

## v0.1.1 (2026-07-03)

### Fix

- **docs**: install mkdocstrings and repair broken doc links so the site builds

## v0.1.0 (2026-07-03)

### Feat

- enforce docstrings, parametrize GitLab host, wire report nav + dev docs
- enforce strict typing and close SOTA completeness gaps
- **template**: ship Claude Code guidance + a status-line utility
- **template**: GitHub-first host model + complete README badge row
- add gitleaks + zizmor; simplify get-latest-tag via commitizen
- PyMaxQ SOTA template

### Fix

- **release**: explain rejected bump push instead of dumping a traceback
- reset root CHANGELOG to unreleased state so first bump succeeds
- node24 updates and fix linting in CI
- migrate SHA pins to Node24
- correct docs-deploy dir, onboarding order, and README badge URLs
- **docs**: escape literal ${{ }} in security.md.jinja with raw blocks
- **ci**: scope Pages permissions to the deploy job in dogfood workflow
- **ci**: pass workflow context via env to avoid template-injection
- **ci**: SHA-pin actions and harden checkouts (zizmor clean)
- make get-latest-tag fall back to 0.0.0 when no remote/tags

### Refactor

- docs
- **docs**: dogfood the cp-then-build docs pattern (single-source home + license)
- **template**: replace sorting demo with a minimal transform pipeline
