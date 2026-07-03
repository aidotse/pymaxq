import re
from pathlib import Path


def render_mkdocs() -> None:
    """Reads the template mkdocs.yaml and splices in PyMaxQ's specific configuration."""
    content = Path("template/mkdocs.yaml.jinja").read_text()

    # 1. Replace Jinja template variables with PyMaxQ's metadata
    replacements = {
        r'site_name: ".*?"': "site_name: PyMaxQ",
        r'site_author: ".*?"': "site_author: AI Sweden",
        r'site_description: ".*?"': "site_description: A Copier template for max-quality Python projects.",
        r'site_url: ".*?"': "site_url: https://aidotse.github.io/pymaxq/",
        r'repo_url: ".*?"': "repo_url: https://github.com/aidotse/pymaxq",
        # PyMaxQ's own site keeps the AI Sweden identity that the template parametrizes/omits.
        r"copyright: .*": "copyright: Copyright © 2026 AI Sweden",
        r"name: material": "name: material\n  logo: assets/dark_blue.svg",
    }

    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)

    # 2. Define PyMaxQ's specific navigation tree
    pymaxq_nav = """nav:
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

    # 3. Splice out the template's nav and inject PyMaxQ's nav
    # This matches from `nav:` up to the next top-level key (markdown_extensions:)
    content = re.sub(r"^nav:.*?(?=\n^[a-z_]+:)", pymaxq_nav, content, flags=re.MULTILINE | re.DOTALL)

    # 3b. Re-add the AI Sweden social footer for PyMaxQ's own site (the template omits
    # `extra.social` so generated projects don't inherit AI Sweden's socials).
    social = """
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
    content = content.rstrip("\n") + "\n" + social

    # 4. Write the generated file to the root directory
    HEADER = """\
# ==============================================================================
# WARNING: AUTO-GENERATED FILE
# This file is synced from template/mkdocs.yaml.jinja via `uv run poe sync`.
# DO NOT MODIFY THIS FILE DIRECTLY!
# Any changes made here will be overwritten. Make your changes in the template.
# ==============================================================================\n
"""
    # Normalize to exactly one trailing newline so re-running sync doesn't drift
    # against the committed file (which pre-commit's end-of-file-fixer also
    # normalizes to one trailing newline).
    final_content = (HEADER + content).rstrip("\n") + "\n"
    Path("mkdocs.yaml").write_text(final_content)
    print("Successfully rendered mkdocs.yaml from template/mkdocs.yaml.jinja!")


if __name__ == "__main__":
    render_mkdocs()
