# ruff: noqa: S603, S607

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
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
        subprocess.run(["git", "push", "origin", "HEAD"], check=True)
        subprocess.run(["git", "push", "origin", new_tag], check=True)

    elif rc in (3, 21):
        print(f"No release-worthy commits (cz exit {rc}); skipping release.")
        with open(out_file, "a") as f:
            f.write("bumped=false\n")
    else:
        print(f"cz bump failed unexpectedly (exit {rc}).", file=sys.stderr)
        sys.exit(rc)


if __name__ == "__main__":
    main()
