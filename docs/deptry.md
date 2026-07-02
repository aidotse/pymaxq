# Dependency Hygiene (deptry)

Over a project's life, dependencies rot: you import a package you never declared (it works by accident because something
else pulls it in), or you declare a package and stop using it. [deptry](https://github.com/fpgmaas/deptry) scans your
source code and your `pyproject.toml` and flags these mismatches, so your declared dependencies stay an honest
description of what the code actually needs.

Run it with the poe task:

```bash
uv run poe deps-check
```

## What it checks

deptry classifies issues with stable rule codes:

- **DEP001 — missing**: a module is imported but not declared as a dependency.
- **DEP002 — unused**: a dependency is declared but never imported.
- **DEP003 — transitive**: a module is imported that you only get transitively (via another dependency), rather than
    declaring it directly. Relying on transitive deps is fragile — if the intermediary drops it, your code breaks.
- **DEP004 — misplaced dev dependency**: a development dependency is imported from code that ships (i.e. not from
    tests/tooling).

These map onto a simple discipline: *import it ⇒ declare it directly; declare it ⇒ import it.*

## Configuration

deptry is configured under `[tool.deptry]` in `pyproject.toml`. Because real projects always have a few legitimate
exceptions, ignores are explicit and rule-scoped:

```toml
[tool.deptry]
known_first_party = ["your_package"]
# dev-only orchestration that isn't shipped code
extend_exclude = ["noxfile.py"]

[tool.deptry.per_rule_ignores]
# headroom-ai is an optional `agent` extra, intentionally not imported by the package
DEP002 = ["headroom-ai"]
# pytest is imported by the test suite but is correctly a dev dependency
DEP004 = ["pytest"]
```

Keep these ignores few and commented — each one is a small promise that the mismatch is deliberate. When you remove a
dependency or stop using one, deptry is the tool that reminds you to tidy up. It also runs as a job in the CI quality
gate, so drift can't merge unnoticed.
