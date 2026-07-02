# uv

We use [uv](https://docs.astral.sh/uv/) by Astral for dependency and environment management. Written in Rust, `uv` is designed as a blazing-fast, drop-in replacement for standard Python packaging tools (`pip`, `pip-tools`, `virtualenv`, and `poetry`).

Here are the key advantages of using `uv` for this project:

- **Unmatched Speed**: `uv` is routinely 10x to 100x faster than standard Python package managers. Resolving dependencies, generating lockfiles, and installing packages takes fractions of a second.
- **Standardization**: Unlike older tools that rely on proprietary configuration formats, `uv` strictly adheres to modern Python packaging standards (PEP 621 for project metadata, PEP 735 for dependency groups). Your `pyproject.toml` is completely standard.
- **Disk Space Efficiency**: `uv` uses a global master cache. When you install a dependency into your project's local environment, `uv` uses advanced file system mechanics (like Copy-on-Write reflinks or hard links) to point to the cache rather than duplicating the files. This saves gigabytes of disk space across multiple projects.
- **All-in-One Toolchain**: `uv` manages your Python versions, virtual environments, lockfiles, and script execution all from a single, unified command-line interface.

## Basic concepts and use

Just like Poetry, `uv` uses a 2-stage process for dependency management. In the first stage, it reads the high-level dependency requirements you specified in `pyproject.toml` (e.g., `"hydra-core>=1.3.2"`) and resolves them into a mathematically strict, completely deterministic `uv.lock` file.

The `uv.lock` file is meant to be checked into your code version control system. This ensures that when other developers or the CI/CD pipeline check out your branch, they are guaranteed to get the exact same environment you used.

To create or update the lockfile, run:

```bash
uv lock
```

By default, `uv lock` will respect existing locked versions and only resolve new additions. If you want to force `uv` to systematically upgrade all your dependencies to their latest compatible versions, you run `uv lock --upgrade`.

Next, to actually install the dependencies defined in your lockfile into your local environment, run:

```bash
uv sync
```

This command will automatically create a `.venv` folder if one doesn't exist, and then perfectly synchronize it with the `uv.lock` file. It will install missing packages and uninstall packages that are no longer needed.

### Managing Dependency Groups (The `uv sync` Pitfall)

By default, running `uv sync` installs **everything**: your main project dependencies, the project code itself, and all dependency groups (like `dev` tools).

**The Pitfall:** A common mistake is running a plain `uv sync` inside a Dockerfile or CI deployment step. This accidentally bloats your production environment by dragging in gigabytes of linting tools, testing frameworks (`pytest`), and documentation generators that have no business being in production.

To control exactly what gets synced, `uv` provides specific flags (which you will see heavily utilized in our Dockerfiles and CI pipelines):

- **`uv sync --no-dev`**: Installs your main dependencies and the project itself, but explicitly excludes the `dev` group. This is standard for production builds.
- **`uv sync --only-group dev`**: Installs *only* the development tools, ignoring the main project dependencies.
- **`uv sync --no-install-project`**: Installs the requested dependencies but skips installing your actual source code. This is a massive optimization trick used in our Dockerfile to cache dependency layers independently from source code changes.

To add a tool specifically for development (like a new linter), assign it directly to the group:

```bash
uv add --group dev <my-dependency>
```

## The virtual environment

`uv` natively creates a `.venv` virtual environment directly in your project root. This keeps everything perfectly isolated. If your environment ever gets into a weird state, you can simply delete the `.venv` folder and run `uv sync` to instantly rebuild it from scratch.

To execute commands inside this isolated environment, simply prepend `uv run` to your command:

```bash
uv run python --version
uv run pytest
```

This completely bypasses the need to manually "activate" your environment (`source .venv/bin/activate`). `uv run` guarantees that the command uses the exact dependencies installed in the project.

### Ephemeral Environments for Scripts

`uv` has an incredibly powerful feature for running single-file Python scripts. If a script defines its dependencies using inline PEP 723 metadata, you can just execute it:

```bash
uv run script.py
```

`uv` will instantly spin up a temporary, invisible virtual environment, download the required dependencies, run the script, and then destroy the environment. It keeps your global system perfectly clean!

## Advanced Configuration: Environment Variables

Because `uv` is heavily optimized for CI/CD and containerized workloads, its behavior can be heavily customized using environment variables. You will see several of these defined in our `Dockerfile` and GitLab CI pipelines:

### 1. Authentication (`UV_INDEX_<NAME>_USERNAME` / `PASSWORD`)
When downloading internal packages from our private GitLab registry, `uv` needs to authenticate. Instead of hardcoding credentials, `uv` automatically maps environment variables to the package indexes defined in your `pyproject.toml`.

If your `pyproject.toml` contains `[[tool.uv.index]]` with `name = "my_project"`, `uv` will automatically look for variables named `UV_INDEX_MY_PROJECT_USERNAME` and `UV_INDEX_MY_PROJECT_PASSWORD` to authenticate the request.

### 2. Certificates (`UV_CERT_BUNDLE`)
When fetching packages from a private, internally-hosted registry (like GitLab), standard SSL verification will fail because the default Python images do not trust our company's internal Certificate Authority. Setting `UV_CERT_BUNDLE=/etc/ssl/certs/ca-certificates.crt` explicitly points `uv` to our newly injected internal certificates, allowing secure network requests to succeed.

### 3. Docker Optimizations
To force `uv` to behave perfectly inside Docker's layered file system, we set a few strict rules during the build:

- **`UV_LINK_MODE=copy`**: By default, `uv` tries to save space by using advanced file system "reflinks" or "hardlinks" from its global cache. Docker's overlay file system often rejects this (throwing an `os error 95`). Setting this to `copy` forces `uv` to perform standard file copies, ensuring stable Docker builds.
- **`UV_COMPILE_BYTECODE=1`**: Tells `uv` to pre-compile all downloaded `.py` files into `.pyc` (bytecode) during installation. This slightly increases the image build time but guarantees much faster application startup times in production.
- **`UV_PYTHON_DOWNLOADS=never`**: `uv` has the ability to fetch and install Python binaries from the internet if it thinks the environment needs them. In Docker, we already dictate the exact Python version via the base image (`FROM python:3.12-slim`). This variable forces `uv` to use the system Python and stops it from attempting unauthorized network downloads.

## Advanced Quirks & Tips

### 1. Global Tools and `uvx` (The `pipx` Replacement)
Since `uv` is an all-in-one toolchain, it completely replaces the need for `pipx`. Avoid adding global CLI tools (like `ruff` or `poethepoet`) to your local project dependencies if you just want to use the tool system-wide.

* **`uv tool install <package>`**: Installs a Python CLI tool into an isolated global environment, making it available anywhere on your system without polluting your project's `.venv`. (This is exactly how we install `poethepoet` in our CI pipelines!)
* **`uvx <command>`**: `uv`'s answer to Node's `npx`. If you want to run a tool once without permanently installing it, just type `uvx ruff check .`. `uv` will instantly download `ruff`, run the linting check, and discard the environment.

### 2. The Universal Lockfile
If you are coming from standard `pip` or `pip-tools`, you might be used to lockfiles (`requirements.txt`) being platform-specific.

`uv.lock` is mathematically **universal**. When you run `uv lock`, it resolves the dependency graph for Windows, macOS, and Linux, across all supported Python versions, simultaneously. A developer on an M3 Mac can safely commit the `uv.lock` file, and the GitLab CI runner (running Linux) will be able to install it perfectly.

### 3. The "Turn It Off and On Again" (Cache Busting)
Because `uv` relies heavily on its aggressive global cache for speed, the cache can occasionally get into a weird state (usually if a private package was re-published to the registry using the exact same version number).

If `uv sync` fails with bizarre checksum errors or a package isn't updating as expected, just nuke the cache:

```bash
uv cache clean
```

This forces `uv` to empty its internal directory and redownload everything fresh from the network on the next run.

## Security auditing (`uv audit`)

uv can also scan your dependencies for known security vulnerabilities, reading the same lockfile that defines your environment:

```bash
uv run poe audit        # = uv audit --preview-features audit-command
```

This checks your resolved dependencies against published advisory databases and fails if a known-vulnerable package is present. It runs in the CI quality gate, so a newly-disclosed vulnerability in even a transitive dependency surfaces on your next pipeline.

*(Note: at the time of writing `uv audit` is a uv preview feature; the task opts in explicitly to silence the experimental warning. If you need a fully stable auditor, `pip-audit` is a drop-in alternative.)*

## Anything else?

Check out the [uv documentation](https://docs.astral.sh/uv/) for more usage options, commands, and configuration options.
