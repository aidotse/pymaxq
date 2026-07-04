"""Generation tests for the PyMaxQ Copier template.

These run ``copier`` against the template in this repo and assert the generated
project is structurally correct. They intentionally do NOT run ``uv sync`` /
``poe test`` (network-bound and slow); the template's CI runs the generated
project's own test suite end-to-end.

NOTE on the template source: while this repo is not git-tracked, copier reads the
working tree directly. Once it IS git-tracked, ``copier copy`` from a git source
uses the latest commit by default -- so CI must check out the ref under test (or
commit first), otherwise these tests would run against stale committed state. The
``vcs_ref="HEAD"`` below pins to HEAD when a git repo is present.
"""

import os
import re
from pathlib import Path

import copier
import pytest

# GitHub Actions expressions (${{ ... }}) legitimately contain `{{` and must NOT be
# mistaken for unrendered Jinja.
_GHA_EXPR = re.compile(r"\$\{\{.*?\}\}")

REPO_ROOT = Path(__file__).resolve().parent.parent

# project_name == package_name: a faithful round-trip of the upstream project,
# but degenerate -- it cannot exercise the slug->package_name derivation.
PYMAXQ = {
    "project_name": "pymaxq",
    "package_name": "pymaxq",
    "description": "A template for max quality Python projects",
    "author": "Mauricio Munoz",
    "email": "mauricio.munoz@ai.se",
    "group": "dev-tools",
}

# Hyphenated name: project_name != package_name. This is the case that actually
# tests the package rename and the project_name-vs-package_name URL handling.
HYPHEN = {
    "project_name": "my-cool-project",
    "description": "A cool project",
    "author": "Ada Lovelace",
    "email": "ada@example.com",
    "group": "acme",
    # package_name deliberately omitted -> exercises the default derivation.
}


def _generate(dst: Path, data: dict[str, str]) -> Path:
    copier.run_copy(
        str(REPO_ROOT),
        str(dst),
        data=data,
        defaults=True,
        overwrite=True,
        unsafe=True,
        vcs_ref="HEAD" if (REPO_ROOT / ".git").exists() else None,
    )
    return dst


def _all_text_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file()]


def test_no_unrendered_jinja(tmp_path: Path) -> None:
    """No file should contain leftover Jinja delimiters or the .jinja suffix.

    Uses ci_platform='both' so the GitHub workflows are covered too; GitHub Actions
    `${{ ... }}` expressions are stripped first so they aren't mistaken for Jinja.
    """
    out = _generate(tmp_path, {**HYPHEN, "ci_platform": "both"})
    for path in _all_text_files(out):
        assert not path.name.endswith(".jinja"), f"unrendered template file: {path}"
        # copier.md documents Copier's template syntax, so it intentionally contains
        # literal `{{ ... }}` examples (it's a plain .md, copied verbatim).
        # reusable-pipeline.yml is copied verbatim (never Jinja-rendered) and uses
        # docker/metadata-action's own `{{version}}`-style tag templates.
        if path.name in ("copier.md", "reusable-pipeline.yml"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        text = _GHA_EXPR.sub("", text)
        assert "{{" not in text and "{%" not in text, f"unrendered Jinja in {path}"


def test_package_dir_is_renamed(tmp_path: Path) -> None:
    """The {{ package_name }} dir becomes the derived underscore package name."""
    out = _generate(tmp_path, HYPHEN)
    assert (out / "my_cool_project").is_dir()
    assert (out / "my_cool_project" / "pipeline.py").is_file()
    assert not (out / "my-cool-project").exists()
    assert not (out / "pymaxq").exists()


def test_package_name_used_in_code(tmp_path: Path) -> None:
    """Imports and Hydra _target_ paths use the underscore package name."""
    out = _generate(tmp_path, HYPHEN)
    test_file = (out / "tests" / "unit" / "test_pipeline.py").read_text()
    assert "from my_cool_project.pipeline import" in test_file

    config = (out / "my_cool_project" / "configs" / "pipeline.yaml").read_text()
    assert "_target_: my_cool_project.pipeline.Pipeline" in config

    pyproject = (out / "pyproject.toml").read_text()
    assert 'packages = ["my_cool_project"]' in pyproject
    assert 'source = ["my_cool_project"]' in pyproject


def test_pages_urls_use_project_name_not_package_name(tmp_path: Path) -> None:
    """Regression: docs/pages URLs must use the slug (project_name), not the
    underscore package_name -- the bug that existed in the old .j2 templates.
    Pinned to gitlab so the host assertion is stable across default changes (per-platform
    host coverage lives in test_repo_and_docs_urls_match_platform)."""
    out = _generate(tmp_path, {**HYPHEN, "ci_platform": "gitlab"})
    for rel in ("mkdocs.yaml", "README.md"):
        text = (out / rel).read_text()
        assert "acme/my-cool-project" in text, f"{rel} should use the slug in URLs"
        assert "my_cool_project" not in text, f"{rel} leaked the package name into a URL"

    pyproject = (out / "pyproject.toml").read_text()
    assert "gitlab.com/acme/my-cool-project" in pyproject


def test_readme_badges_use_exported_docs_path(tmp_path: Path) -> None:
    """The README's coverage/tests badge URLs point at the single-version docs site's
    `/exported/` artifacts. The deploy publishes one version at the site root (there is
    no mike `/latest/` alias), so a `/latest/exported/...` path would 404."""
    out = _generate(tmp_path, HYPHEN)
    readme = (out / "README.md").read_text()
    for artifact in ("tests.svg", "coverage.svg", "pytest.html", "coverage/"):
        assert f"/exported/{artifact}" in readme, f"badge URL for {artifact} missing /exported/ path"
    assert "/latest/exported/" not in readme, "badge URL should not use a mike /latest/ prefix"


def test_readme_has_static_badges(tmp_path: Path) -> None:
    """The host-agnostic shields.io badges (Python versions, license, code style)
    render immediately and don't depend on a docs/CI deploy, so they belong on every
    generated README regardless of platform."""
    out = _generate(tmp_path, HYPHEN)
    readme = (out / "README.md").read_text()
    assert "img.shields.io/badge/python-" in readme
    assert "img.shields.io/badge/License-MIT" in readme
    assert "Code style: Ruff" in readme


def test_readme_ci_badge_matches_platform(tmp_path: Path) -> None:
    """The CI-status badge follows the same host convention as repo_url: GitHub is primary,
    so github/both get the GitHub Actions badge; only gitlab-only gets the pipeline badge."""
    for platform in ("github", "both"):
        readme = (_generate(tmp_path / platform, {**HYPHEN, "ci_platform": platform}) / "README.md").read_text()
        assert "/actions/workflows/ci.yml/badge.svg" in readme, f"{platform}: expected GitHub Actions badge"
        assert "/badges/main/pipeline.svg" not in readme, f"{platform}: unexpected GitLab pipeline badge"

    gl = (_generate(tmp_path / "gl", {**HYPHEN, "ci_platform": "gitlab"}) / "README.md").read_text()
    assert "/badges/main/pipeline.svg" in gl
    assert "/actions/workflows/ci.yml/badge.svg" not in gl


def test_ships_claude_code_assets(tmp_path: Path) -> None:
    """The generated project ships the opt-in, executable Claude Code status-line utility."""
    out = _generate(tmp_path, HYPHEN)
    statusline = out / ".claude" / "statusline.sh"
    assert statusline.is_file()
    assert statusline.read_text().startswith("#!/usr/bin/env bash")
    assert os.access(statusline, os.X_OK), "statusline.sh should ship executable"


def test_ships_task_copied_files(tmp_path: Path) -> None:
    """The `_tasks` in copier.yml `cp` five files into the generated project from the
    template repo root (`_src_path`), not from `template/`, so no `.jinja` rendering or
    `_exclude` guard protects them. A rename/move at the repo root would silently ship a
    project missing these; statusline.sh and reusable-pipeline.yml are covered elsewhere,
    so this pins the remaining four."""
    out = _generate(tmp_path, HYPHEN)
    for rel in ("renovate.json", "noxfile.py", "docs/user-guide.md", "scripts/bump.py"):
        assert (out / rel).is_file(), f"{rel} should be copied into the project by a _tasks entry"


def test_copier_answers_file_present(tmp_path: Path) -> None:
    """The answers file must be written so `copier update` works."""
    out = _generate(tmp_path, HYPHEN)
    answers = out / ".copier-answers.yml"
    assert answers.is_file()
    assert "project_name: my-cool-project" in answers.read_text()


def test_ships_py_typed_marker(tmp_path: Path) -> None:
    """The generated package ships a PEP 561 py.typed marker so downstream consumers
    get its inline type hints."""
    out = _generate(tmp_path, HYPHEN)
    assert (out / "my_cool_project" / "py.typed").is_file()


def test_license_names_copyright_holder(tmp_path: Path) -> None:
    """The generated MIT license carries a copyright line naming the author (the old
    verbatim template shipped MIT text with no copyright holder at all)."""
    out = _generate(tmp_path, HYPHEN)
    license_text = (out / "LICENSE.md").read_text()
    assert "MIT License" in license_text
    assert "Copyright (c) 2026 Ada Lovelace" in license_text


def test_api_reference_wired_into_nav(tmp_path: Path) -> None:
    """The mkdocstrings API reference page is listed in the generated site's nav
    (it previously shipped as an orphan page unreachable from navigation)."""
    out = _generate(tmp_path, HYPHEN)
    assert (out / "docs" / "reference.md").is_file()
    assert "reference.md" in (out / "mkdocs.yaml").read_text()


def test_docs_not_branded_with_template_owner(tmp_path: Path) -> None:
    """Generated projects must not inherit the template owner's (AI Sweden) branding:
    the copyright names the author and the AI Sweden socials/handles are absent."""
    out = _generate(tmp_path, HYPHEN)
    mkdocs = (out / "mkdocs.yaml").read_text()
    assert "Copyright © 2026 Ada Lovelace" in mkdocs
    for leaked in ("AI Sweden", "aidotse", "aisweden"):
        assert leaked not in mkdocs, f"template owner branding leaked into mkdocs.yaml: {leaked}"


def test_pymaxq_roundtrip_smoke(tmp_path: Path) -> None:
    """The upstream values still generate cleanly (degenerate name case)."""
    out = _generate(tmp_path, PYMAXQ)
    assert (out / "pymaxq" / "pipeline.py").is_file()
    assert (out / "pyproject.toml").read_text().count("{{") == 0


@pytest.mark.parametrize(
    ("platform", "repo_host", "docs_host", "leaked_host"),
    [
        # gitlab (no gitlab_host given) defaults to gitlab.com + its Pages scheme (<group>.gitlab.io).
        ("gitlab", "gitlab.com/acme/my-cool-project", "acme.gitlab.io/my-cool-project", "github.com"),
        ("github", "github.com/acme/my-cool-project", "acme.github.io/my-cool-project", "gitlab.com"),
        # GitHub is the primary host, so 'both' advertises the GitHub repo/docs URLs even
        # though the GitLab pipeline still runs as a mirror.
        ("both", "github.com/acme/my-cool-project", "acme.github.io/my-cool-project", "gitlab.com"),
    ],
)
def test_repo_and_docs_urls_match_platform(
    tmp_path: Path, platform: str, repo_host: str, docs_host: str, leaked_host: str
) -> None:
    """The active repo/docs URLs follow the chosen platform; the other host doesn't leak
    into them (regression: GitHub projects used to ship GitLab URLs). Scoped to the URL
    lines so unrelated mentions (social links, commented examples) aren't flagged."""
    out = _generate(tmp_path, {**HYPHEN, "ci_platform": platform})
    pyproject = (out / "pyproject.toml").read_text()
    mkdocs = (out / "mkdocs.yaml").read_text()

    def line_with(text: str, key: str) -> str:
        return next(ln for ln in text.splitlines() if key in ln)

    url_lines = {
        "Homepage": line_with(pyproject, "Homepage ="),
        "Documentation": line_with(pyproject, "Documentation ="),
        "site_url": line_with(mkdocs, "site_url:"),
        "repo_url": line_with(mkdocs, "repo_url:"),
    }
    assert repo_host in url_lines["Homepage"] and repo_host in url_lines["repo_url"]
    assert docs_host in url_lines["Documentation"] and docs_host in url_lines["site_url"]
    for name, line in url_lines.items():
        assert leaked_host not in line, f"{leaked_host} leaked into {name}: {line}"


def test_gitlab_self_hosted_host_flows_into_urls(tmp_path: Path) -> None:
    """A self-hosted gitlab_host flows into the repo/docs URLs, deriving the Pages host
    (gitlab.<x> -> pages.<x>) instead of the gitlab.com <group>.gitlab.io scheme."""
    out = _generate(tmp_path, {**HYPHEN, "ci_platform": "gitlab", "gitlab_host": "gitlab.example.com"})
    pyproject = (out / "pyproject.toml").read_text()
    mkdocs = (out / "mkdocs.yaml").read_text()
    assert "gitlab.example.com/acme/my-cool-project" in pyproject
    assert "pages.example.com/acme/my-cool-project" in mkdocs
    assert "gitlab.io" not in mkdocs, "self-hosted host must not fall back to the gitlab.com Pages scheme"
    assert "mgmt.ai.se" not in pyproject, "no hardcoded org host should remain"


def test_docs_nav_includes_test_and_coverage_reports(tmp_path: Path) -> None:
    """The generated site links the exported pytest + coverage HTML reports in its nav."""
    out = _generate(tmp_path, HYPHEN)
    mkdocs = (out / "mkdocs.yaml").read_text()
    assert "exported/pytest.html" in mkdocs
    assert "exported/coverage/index.html" in mkdocs


@pytest.mark.parametrize(
    ("platform", "gitlab_ci", "github_ci", "zizmor"),
    [
        ("gitlab", True, False, False),
        ("github", False, True, True),
        ("both", True, True, True),
    ],
)
def test_precommit_hooks_match_platform(
    tmp_path: Path, platform: str, gitlab_ci: bool, github_ci: bool, zizmor: bool
) -> None:
    """gitleaks/commitizen are always present; CI-schema and zizmor hooks are scoped to the
    chosen platform(s)."""
    out = _generate(tmp_path, {**HYPHEN, "ci_platform": platform})
    cfg = (out / ".pre-commit-config.yaml").read_text()
    assert "id: gitleaks" in cfg
    assert "id: commitizen" in cfg
    assert ("check-gitlab-ci" in cfg) is gitlab_ci
    assert ("check-github-workflows" in cfg) is github_ci
    assert ("id: zizmor" in cfg) is zizmor


@pytest.mark.parametrize(
    ("platform", "expect_gitlab", "expect_github"),
    [("gitlab", True, False), ("github", False, True), ("both", True, True)],
)
def test_ci_platform_selection(tmp_path: Path, platform: str, expect_gitlab: bool, expect_github: bool) -> None:
    """Only the CI files for the chosen platform(s) are generated."""
    out = _generate(tmp_path, {**HYPHEN, "ci_platform": platform})

    assert (out / ".gitlab-ci.yml").is_file() is expect_gitlab

    gh_ci = (out / ".github" / "workflows" / "ci.yml").is_file()
    gh_reusable = (out / ".github" / "workflows" / "reusable-pipeline.yml").is_file()
    assert gh_ci is expect_github
    assert gh_reusable is expect_github
    if not expect_github:
        assert not (out / ".github").exists(), "no .github dir should be generated"


@pytest.mark.parametrize(
    ("platform", "expect_ci_base"),
    [("gitlab", True), ("github", False), ("both", True)],
)
def test_docker_files_match_platform(tmp_path: Path, platform: str, expect_ci_base: bool) -> None:
    """The rendered Dockerfile ships on every platform and uses the underscore package name;
    docker/ci.base.Dockerfile is a GitLab-runner image, so copier.yml's `_exclude` drops it
    for github-only projects but keeps it for gitlab and both (parallel to the CI-file
    exclusions in test_ci_platform_selection, which this mirrors for the docker/ dir)."""
    out = _generate(tmp_path, {**HYPHEN, "ci_platform": platform})

    dockerfile = out / "docker" / "Dockerfile"
    assert dockerfile.is_file(), "Dockerfile should be generated on every platform"
    assert "my_cool_project" in dockerfile.read_text(), "Dockerfile should COPY the renamed package"

    assert (out / "docker" / "ci.base.Dockerfile").is_file() is expect_ci_base


@pytest.mark.parametrize(
    "bad_project_name",
    ["My-Cool-Project", "my cool project", ""],
)
def test_project_name_validator_rejects_invalid(tmp_path: Path, bad_project_name: str) -> None:
    """Uppercase, spaces, and empty values are all rejected by the project_name validator."""
    with pytest.raises(ValueError, match="project_name"):
        _generate(tmp_path, {**HYPHEN, "project_name": bad_project_name})


def test_project_name_validator_accepts_valid(tmp_path: Path) -> None:
    out = _generate(tmp_path, {**HYPHEN, "project_name": "my-cool-project"})
    assert (out / ".copier-answers.yml").is_file()


@pytest.mark.parametrize(
    "bad_package_name",
    ["My_Cool_Project", "my-cool-project", "my cool project"],
)
def test_package_name_validator_rejects_invalid(tmp_path: Path, bad_package_name: str) -> None:
    """Uppercase, hyphens, and spaces are all rejected by the package_name validator."""
    with pytest.raises(ValueError, match="package_name"):
        _generate(tmp_path, {**HYPHEN, "package_name": bad_package_name})


def test_package_name_validator_accepts_valid(tmp_path: Path) -> None:
    out = _generate(tmp_path, {**HYPHEN, "package_name": "my_cool_project"})
    assert (out / "my_cool_project").is_dir()


@pytest.mark.parametrize(
    "bad_email",
    ["bad-email", "a@b", "@.", ""],
)
def test_email_validator_rejects_invalid(tmp_path: Path, bad_email: str) -> None:
    """Missing @, missing domain dot, and empty values are all rejected by the email validator."""
    with pytest.raises(ValueError, match="email"):
        _generate(tmp_path, {**HYPHEN, "email": bad_email})


def test_email_validator_accepts_valid(tmp_path: Path) -> None:
    out = _generate(tmp_path, {**HYPHEN, "email": "ada@example.com"})
    answers = (out / ".copier-answers.yml").read_text()
    assert "ada@example.com" in answers


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
