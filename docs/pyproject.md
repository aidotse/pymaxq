# pyproject.toml

The `pyproject.toml` file is an implementation of [PEP 518](https://peps.python.org/pep-0518/) for building Python
projects. Basically, it allows users to specify which dependencies should be installed as part of the project, what
build backend to use, and to set various project- and tool- level configurations. It is an attempt to improve over the
long-standing [setuptools](https://pypi.org/project/setuptools/) / `setup.py` way of packaging Python projects. See the
previous link for some comparisons and rationale as to why configuring projects with `pyproject.toml` is generally
better.

In this project we use the `pyproject.toml` configuration file primarily for 3 purposes: dependency specification, tool
config specification, and task specification. Because we use `uv` as the dependency manager (as well as the build
system), dependency specification looks for example something like this:

```toml
[project]
...
requires-python = ">=3.10"

# Main dependencies
dependencies = [
    "loguru>=0.7.3",
    ...
]

[dependency-groups]
dev = [
    "pytest>=8.3.3",
    ...
]
...
```

Tool configs look something like this:

```toml
[tool.coverage.xml]
output = "docs/exported/coverage.xml"
```

Not all tools can be configured in this way; typically this will be specified in the tool's documentation. For example,
you can find the documentation for `coverage` in the example above
[here](https://coverage.readthedocs.io/en/latest/plugins.html).

Finally, we can also specify tasks directly in the `pyproject.toml` using
[poethepoet](https://github.com/nat-n/poethepoet). You can think of these as functions / scripts that are run as shell
commands that you can invoke yourself manually from the command line or in general from anywhere you have access to your
`uv` virtual environment. For example, this specifies a simple cleaning task:

```toml
# Clean temporary files from the repo
[tool.poe.tasks.clean]
shell = """
  rm -rf \
    .coverage \
    .mypy_cache \
    .pytest_cache \
    .ruff_cache \
    .site \
    public \
    __pycache__ \
    docs/exported
"""
```

## Tool configuration in this project

Beyond dependencies and tasks, several tools are configured here under their own `[tool.*]` tables, which is worth
knowing when you go looking for a setting:

- `[tool.ruff]` / `[tool.ruff.lint]` — formatting + linting rules (see [linting](linting.md)).
- `[tool.mypy]` — static type checking.
- `[tool.pytest.ini_options]` and `[tool.coverage.*]` — testing and coverage (see [testing](testing.md)).
- `[tool.commitizen]` — Conventional-Commits versioning (see [versioning](versioning.md)).
- `[tool.deptry]` — dependency hygiene, including any rule-scoped ignores (see [deptry](deptry.md)).
- `[tool.hatch.version]` — tells the build backend to derive the version from git tags.

Optional features live under `[project.optional-dependencies]` as named extras (this template ships an `agent` extra),
installed with `uv sync --extra <name>`.
