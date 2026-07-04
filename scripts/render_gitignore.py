from pathlib import Path

HEADER = """\
# ==============================================================================
# WARNING: AUTO-GENERATED FILE
# This file is synced from template/.gitignore via `uv run poe sync`.
# DO NOT MODIFY THIS FILE DIRECTLY!
# Any changes made here will be overwritten. Make your changes in the template.
# ==============================================================================\n
"""

# PyMaxQ's own dev-only exclusions, layered on top of the shipped template .gitignore.
PYMAXQ_SPECIFICS = """
.dogfood-site/
mkdocs.yaml
docs/index.md
docs/license.md
"""


def render_gitignore(base_text: str) -> str:
    """Combine the template .gitignore with PyMaxQ's internal dev exclusions.

    Pure transform (string in, string out) so it can be unit-tested without touching the
    filesystem; :func:`main` supplies the read/write. Normalized to exactly one trailing
    newline so re-running sync doesn't drift against the committed file (pre-commit's
    end-of-file-fixer also normalizes to one trailing newline).
    """
    return (HEADER + PYMAXQ_SPECIFICS + base_text).rstrip("\n") + "\n"


def main() -> None:
    """Read the template .gitignore, append PyMaxQ's exclusions, and write it to the root."""
    base_text = Path("template/.gitignore").read_text()
    Path(".gitignore").write_text(render_gitignore(base_text))
    print("Successfully rendered .gitignore from template!")


if __name__ == "__main__":
    main()
