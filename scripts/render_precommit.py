from pathlib import Path

import jinja2


def render_precommit():
    """Renders the template's pre-commit config for the root repository."""
    content = Path("template/.pre-commit-config.yaml.jinja").read_text()

    # 1. Render the Jinja template pretending PyMaxQ is a 'github' project
    template = jinja2.Template(content)
    rendered = template.render(ci_platform="github")

    # 2. Prepend the root-specific exclusion and a warning comment
    HEADER = """\
# ==============================================================================
# WARNING: AUTO-GENERATED FILE
# This file is synced from template/.pre-commit-config.yaml.jinja via `uv run poe sync`.
# DO NOT MODIFY THIS FILE DIRECTLY!
# Any changes made here will be overwritten. Make your changes in the template.
# ==============================================================================\n

exclude: '^template/'\n
"""

    # 3. Write out the final config to the root directory
    Path(".pre-commit-config.yaml").write_text(HEADER + rendered)
    print("Successfully rendered .pre-commit-config.yaml from template!")


if __name__ == "__main__":
    render_precommit()
