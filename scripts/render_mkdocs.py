import re
from pathlib import Path

HEADER = """\
# ==============================================================================
# WARNING: AUTO-GENERATED FILE
# This file is synced from template/mkdocs.yaml.jinja via `uv run poe sync`.
# DO NOT MODIFY THIS FILE DIRECTLY!
# Any changes made here will be overwritten. Make your changes in the template.
# ==============================================================================\n
"""

# PyMaxQ's own site keeps the AI Sweden identity that the template parametrizes/omits.
REPLACEMENTS = {
    r'site_name: ".*?"': "site_name: PyMaxQ",
    r'site_author: ".*?"': "site_author: AI Sweden",
    r'site_description: ".*?"': "site_description: A Copier template for max-quality Python projects.",
    r'site_url: ".*?"': "site_url: https://aidotse.github.io/pymaxq/",
    r'repo_url: ".*?"': "repo_url: https://github.com/aidotse/pymaxq",
    r"copyright: .*": "copyright: Copyright © 2026 AI Sweden",
    r"name: material": "name: material\n  logo: assets/dark_blue.svg",
}

# PyMaxQ's specific navigation tree, spliced in over the template's placeholder nav.
PYMAXQ_NAV = """nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - Design & Philosophy: design.md
  - Developing the template: developing.md
  - Contributing: process.md
  - Tooling:
    - Copier: copier.md
    - Claude Code: claude-code.md
    - CI: ci.md
    - Deptry: deptry.md
    - Hydra: hydra.md
    - Linting: linting.md
    - mkdocs: mkdocs.md
    - Poe: poe.md
    - Pre-commit: precommit.md
    - Pyproject.toml: pyproject.md
    - Renovate: renovate.md
    - Security: security.md
    - Testing: testing.md
    - uv: uv.md
    - versioning: versioning.md
  - FAQ: faq.md
  - License: license.md
  - Tests: exported/pytest.html
"""

# Re-add the AI Sweden social footer for PyMaxQ's own site (the template omits
# `extra.social` so generated projects don't inherit AI Sweden's socials).
SOCIAL = """
extra:
  social:
    - icon: simple/github
      link: https://github.com/aidotse
    - icon: fontawesome/brands/linkedin
      link: https://www.linkedin.com/company/aisweden
    - icon: fontawesome/solid/newspaper
      link: https://www.ai.se/en/newsletter
    - icon: simple/youtube
      link: https://www.youtube.com/channel/UC9tI59qEGKS_v1PMfWyGY1Q
    - icon: simple/spotify
      link: https://open.spotify.com/show/7z6xGzWQosx3346tpscfQc?si=81DsYQJVSNOO3diHMzoMFQ&nd=1&dlsi=6833fe515dc047b0
"""


def render_mkdocs(template_text: str) -> str:
    """Splice PyMaxQ's own site config into the template mkdocs.yaml.

    Pure transform (string in, string out) so it can be unit-tested without touching the
    filesystem; :func:`main` supplies the read/write. Substitutes PyMaxQ's metadata, replaces
    the template's placeholder nav (the ``^nav:.*?(?=\\n^[a-z_]+:)`` splice relies on another
    top-level key following ``nav:``), re-adds the AI Sweden social footer, and normalizes to
    exactly one trailing newline so re-running sync doesn't drift against the committed file.
    """
    content = template_text

    # 1. Replace Jinja template variables with PyMaxQ's metadata.
    for pattern, replacement in REPLACEMENTS.items():
        content = re.sub(pattern, replacement, content)

    # 2. Splice out the template's nav and inject PyMaxQ's nav. This matches from `nav:`
    #    up to the next top-level key (e.g. markdown_extensions:).
    content = re.sub(r"^nav:.*?(?=\n^[a-z_]+:)", PYMAXQ_NAV, content, flags=re.MULTILINE | re.DOTALL)

    # 3. Re-add the AI Sweden social footer.
    content = content.rstrip("\n") + "\n" + SOCIAL

    # 4. Prefix the auto-generated warning and normalize to one trailing newline.
    return (HEADER + content).rstrip("\n") + "\n"


def main() -> None:
    """Read the template mkdocs.yaml, render PyMaxQ's site config, and write it to the root."""
    template_text = Path("template/mkdocs.yaml.jinja").read_text()
    Path("mkdocs.yaml").write_text(render_mkdocs(template_text))
    print("Successfully rendered mkdocs.yaml from template/mkdocs.yaml.jinja!")


if __name__ == "__main__":
    main()
