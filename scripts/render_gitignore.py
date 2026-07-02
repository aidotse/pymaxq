from pathlib import Path


def render_gitignore():
    """Reads the template .gitignore and appends PyMaxQ's internal dev exclusions."""
    base_content = Path("template/.gitignore").read_text()

    pymaxq_specifics = """
.dogfood-site/
mkdocs.yaml
docs/index.md
docs/license.md\n
"""

    HEADER = """\
# ==============================================================================
# WARNING: AUTO-GENERATED FILE
# This file is synced from template/mkdocs.yml.jinja via `uv run poe sync`.
# DO NOT MODIFY THIS FILE DIRECTLY!
# Any changes made here will be overwritten. Make your changes in the template.
# ==============================================================================\n
"""

    # Write the combined output to the root directory
    Path(".gitignore").write_text(HEADER + pymaxq_specifics + base_content)
    print("Successfully rendered .gitignore from template!")


if __name__ == "__main__":
    render_gitignore()
