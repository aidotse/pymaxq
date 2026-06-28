## Unreleased

### Feat

- **template**: GitHub-first host model + complete README badge row
- add gitleaks + zizmor; simplify get-latest-tag via commitizen

### Fix

- **docs**: escape literal ${{ }} in security.md.jinja with raw blocks
- **ci**: scope Pages permissions to the deploy job in dogfood workflow
- **ci**: pass workflow context via env to avoid template-injection
- **ci**: SHA-pin actions and harden checkouts (zizmor clean)

### Refactor

- **template**: replace sorting demo with a minimal transform pipeline

## v0.1.0 (2026-06-26)

### Feat

- PyMaxQ SOTA template

### Fix

- make get-latest-tag fall back to 0.0.0 when no remote/tags
