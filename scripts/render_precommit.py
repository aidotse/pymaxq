from pathlib import Path

import jinja2

HEADER = """\
# ==============================================================================
# WARNING: AUTO-GENERATED FILE
# This file is synced from template/.pre-commit-config.yaml.jinja via `uv run poe sync`.
# DO NOT MODIFY THIS FILE DIRECTLY!
# Any changes made here will be overwritten. Make your changes in the template.
# ==============================================================================\n
\nexclude: '^template/'\n
"""


def render_precommit(template_text: str) -> str:
    """Render the template's pre-commit config for the root repository.

    Pure transform (string in, string out) so it can be unit-tested without touching the
    filesystem; :func:`main` supplies the read/write. The template is rendered as a 'github'
    project, prefixed with the auto-generated warning and the root-only `exclude: '^template/'`,
    and normalized to exactly one trailing newline so re-running sync doesn't drift against the
    committed file (pre-commit's end-of-file-fixer also normalizes to one trailing newline).
    """
    rendered: str = jinja2.Template(template_text).render(ci_platform="github")
    return (HEADER + rendered).rstrip("\n") + "\n"


def main() -> None:
    """Read the template pre-commit config, render it, and write it to the root directory."""
    template_text = Path("template/.pre-commit-config.yaml.jinja").read_text()
    Path(".pre-commit-config.yaml").write_text(render_precommit(template_text))
    print("Successfully rendered .pre-commit-config.yaml from template!")


if __name__ == "__main__":
    main()
