"""Unit tests for the root-only template->root sync scripts (scripts/render_*.py) and the
release-state decision in scripts/bump.py.

CI's `enforce-sync` job already guarantees *no drift* (committed root files == what the
scripts regenerate). It cannot catch a *wrong* transform: bad logic regenerates a
wrong-but-stable file and stays green. These tests pin the transform behavior itself,
feeding the real committed template files through the pure render functions."""

from pathlib import Path

import pytest

from scripts.bump import release_decision
from scripts.render_gitignore import render_gitignore
from scripts.render_mkdocs import render_mkdocs
from scripts.render_precommit import render_precommit

TEMPLATE = Path("template")


def _one_trailing_newline(text: str) -> bool:
    """The committed files end in exactly one newline (pre-commit's end-of-file-fixer)."""
    return text.endswith("\n") and not text.endswith("\n\n")


# --- render_precommit -------------------------------------------------------


def test_render_precommit_renders_github_variant() -> None:
    """The root config is the 'github' render, so GitHub-specific hooks appear and the
    GitLab-only ones do not — this is what `enforce-sync` cannot verify on its own."""
    out = render_precommit((TEMPLATE / ".pre-commit-config.yaml.jinja").read_text())

    assert "check-github-workflows" in out
    assert "check-gitlab-ci" not in out


def test_render_precommit_adds_root_scaffolding() -> None:
    """The root-only exclusion and warning header must be present, with no leftover Jinja."""
    out = render_precommit((TEMPLATE / ".pre-commit-config.yaml.jinja").read_text())

    assert "exclude: '^template/'" in out
    assert "WARNING: AUTO-GENERATED FILE" in out
    assert "{{" not in out and "{%" not in out
    assert _one_trailing_newline(out)


# --- render_mkdocs ----------------------------------------------------------


def test_render_mkdocs_substitutes_pymaxq_identity() -> None:
    """PyMaxQ's own site keeps the AI Sweden identity that the template parametrizes/omits —
    the inverse of the generated-project test_docs_not_branded_with_template_owner."""
    out = render_mkdocs((TEMPLATE / "mkdocs.yaml.jinja").read_text())

    assert "site_name: PyMaxQ" in out
    assert "site_author: AI Sweden" in out
    assert "repo_url: https://github.com/aidotse/pymaxq" in out
    # The AI Sweden social footer is re-added (template omits `extra.social`).
    assert "https://www.linkedin.com/company/aisweden" in out
    assert "{{" not in out and "{%" not in out
    assert _one_trailing_newline(out)


def test_render_mkdocs_nav_splice_actually_happens() -> None:
    """Regression guard for the fragile `^nav:.*?(?=\\n^[a-z_]+:)` splice, which silently
    no-ops if `nav:` is no longer followed by a top-level key. Assert PyMaxQ's nav replaced
    the template's: PyMaxQ-only entries appear and template-only nav targets are gone."""
    out = render_mkdocs((TEMPLATE / "mkdocs.yaml.jinja").read_text())

    # PyMaxQ-only nav entries are present...
    assert "Design & Philosophy: design.md" in out
    assert "Developing the template: developing.md" in out
    # ...and the template's placeholder nav entries were spliced out.
    assert "API Reference: reference.md" not in out
    assert "Getting Started: user-guide.md" not in out
    # The following top-level key the splice depends on is preserved.
    assert "markdown_extensions:" in out


def test_render_mkdocs_nav_splice_noop_is_detectable() -> None:
    """Document the failure mode directly: with `nav:` as the last top-level block (no key
    following it) the splice cannot match, so PyMaxQ's nav is NOT injected. This is the
    scenario the regression test above protects the real template against."""
    no_following_key = 'site_name: "x"\nnav:\n  - Home: index.md\n'
    out = render_mkdocs(no_following_key)

    assert "Design & Philosophy: design.md" not in out  # splice did not fire
    assert "site_name: PyMaxQ" in out  # non-nav substitutions still work


# --- render_gitignore -------------------------------------------------------


def test_render_gitignore_layers_pymaxq_exclusions() -> None:
    """The root .gitignore is the shipped template one plus PyMaxQ's dev-only exclusions."""
    base = (TEMPLATE / ".gitignore").read_text()
    out = render_gitignore(base)

    assert ".dogfood-site/" in out  # PyMaxQ-only exclusion
    assert "WARNING: AUTO-GENERATED FILE" in out
    # A representative line from the shipped base is preserved.
    assert "__pycache__/" in out
    assert "__pycache__/" in base  # sanity: the marker really comes from the template
    assert _one_trailing_newline(out)


# --- bump.release_decision --------------------------------------------------


@pytest.mark.parametrize(
    ("rc", "expected"),
    [
        (0, "bump"),
        (3, "skip"),  # cz NoneIncrementExit
        (21, "skip"),  # cz NoCommitsFoundError
        (1, "fail"),
        (2, "fail"),
        (127, "fail"),
    ],
)
def test_release_decision(rc: int, expected: str) -> None:
    """The cz-exit-code contract: 0 bumps, the no-eligible-commits codes skip cleanly, and
    every other code is a hard failure that must abort the release pipeline."""
    assert release_decision(rc) == expected
