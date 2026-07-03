# ruff: noqa: S603, S607
"""Bump the version from conventional commits and emit release state for CI.

Runs ``cz bump``; on success it writes ``bumped``/``version`` to the output file and pushes
the commit + tag, otherwise it records ``bumped=false`` so downstream release jobs no-op.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def _explain_push_failure() -> None:
    """Print an actionable hint for a rejected release push (usually branch protection)."""
    print(
        "\n"
        "Failed to push the version bump to the default branch. The bump commit and tag\n"
        "were created locally but could not be pushed, so the release did not complete.\n"
        "This is almost always a branch-protection authorization issue, not a bug: the\n"
        "release push needs permission to update the protected default branch.\n"
        "\n"
        "Grant it one of two ways (see your project's CI/release setup docs):\n"
        "  - add a branch-protection/ruleset bypass for the CI actor "
        "(e.g. github-actions[bot]), or\n"
        "  - create a token with 'contents: write' that is allowed to bypass protection\n"
        "    and expose it to this job (GitHub: the RELEASE_TOKEN secret; GitLab: CI_REPO_ACCESS).\n",
        file=sys.stderr,
    )


def main() -> None:
    """Run ``cz bump``, push the tag on success, and write CI release state to the output file."""
    parser = argparse.ArgumentParser(description="Bump version, push, and output state for CI.")
    parser.add_argument("out", nargs="?", default="bump.env", help="File to write state variables to")
    args = parser.parse_args()

    out_file = Path(args.out)

    print("Running commitizen bump...")
    # We do not use capture_output=True so that the user/CI still sees cz's standard logs
    result = subprocess.run(["cz", "bump", "--yes"], check=False)
    rc = result.returncode

    if rc == 0:
        # Get the newly created tag
        tag_proc = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"], text=True, capture_output=True, check=True
        )
        new_tag = tag_proc.stdout.strip()
        version = new_tag.lstrip("v")

        print(f"Writing state to {out_file}...")
        with open(out_file, "a") as f:
            f.write("bumped=true\n")
            f.write(f"version={version}\n")

        print(f"Pushing bump commit and tag {new_tag} to origin...")
        try:
            subprocess.run(["git", "push", "origin", "HEAD"], check=True)
            subprocess.run(["git", "push", "origin", new_tag], check=True)
        except subprocess.CalledProcessError as exc:
            _explain_push_failure()
            sys.exit(exc.returncode)

    elif rc in (3, 21):
        print(f"No release-worthy commits (cz exit {rc}); skipping release.")
        with open(out_file, "a") as f:
            f.write("bumped=false\n")
    else:
        print(f"cz bump failed unexpectedly (exit {rc}).", file=sys.stderr)
        sys.exit(rc)


if __name__ == "__main__":
    main()
