from pathlib import Path


def render_gitignore():
    """Reads the template .gitignore and appends PyMaxQ's internal dev exclusions."""
    base_content = Path("template/.gitignore").read_text()

    pymaxq_specifics = """
.dogfood-site/
mkdocs.yaml
docs/index.md
docs/license.md
"""

    HEADER = """\
# ==============================================================================
# WARNING: AUTO-GENERATED FILE
# This file is synced from template/.gitignore via `uv run poe sync`.
# DO NOT MODIFY THIS FILE DIRECTLY!
# Any changes made here will be overwritten. Make your changes in the template.
# ==============================================================================\n
"""

    # Write the combined output to the root directory. Normalize to exactly one
    # trailing newline so re-running sync doesn't drift against the committed file
    # (which pre-commit's end-of-file-fixer also normalizes to one trailing newline).
    content = (HEADER + pymaxq_specifics + base_content).rstrip("\n") + "\n"
    Path(".gitignore").write_text(content)
    print("Successfully rendered .gitignore from template!")


if __name__ == "__main__":
    render_gitignore()
