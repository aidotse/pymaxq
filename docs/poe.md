# Poe the Poet / Action Runner

[poethepoet](https://github.com/nat-n/poethepoet) is an action runner that integrates well with `uv` and
`pyproject.toml`. As explained elsewhwere, you can use this tool to define any number of tasks in your `pyproject.toml`
that you can run from anywhere that your virtual environment is visible.

This task specification allows you, as the user, to specify the task itself e.g. as a bash script run in a shell, that
can take arguments as necessary. For example, consider the following task, which runs a sequence of commands to run unit
tests in your project, followed by generating a coverage report and exporting the results in both an `.xml` and `.html`
format.

```yaml
[tool.poe.tasks.test]
sequence = [
  { cmd = "pytest ${test}" },
  { cmd = "coverage xml" },
  { cmd = "coverage html" },
  { cmd = "coverage report" },
]
help = "Run unit testing and generate coverage report"
args = [
  { name = "tests", multiple = true, positional = true, default = "tests/unit", help = "Unit tests to run" }
]
```

Task names should start with `[tool.poe.tasks.<your task name>]`, and the body of the task itself can take one of a
couple of [predefined forms](https://poethepoet.natn.io/tasks/index.html), each of which have their intended use cases
and advantages / disadvantages. Arguments can be specified in a variety of ways, see more about that
[here](https://poethepoet.natn.io/guides/args_guide.html).

In particular, tasks can [refer to other tasks](https://poethepoet.natn.io/tasks/task_types/ref.html), allowing you to
build a highly modular functional-helper system directly in the `pyproject.toml` file.

In this project, we define highly modular and parameterizable tasks that are called / orchestrated from the CI script,
preferring to abstract away the complexity directly in the `pyproject.toml` file rather than in the CI file itself. This
allows us to remain agnostic of the CI system itself.

As seen in the CI file (`.gitlab-ci.yml`), it is also absolutely possible to run these tasks manually. For example, to
run the above task for code testing above, you can run

```bash
uv run poe test
```

Note that some tasks might consume outputs produced by other tasks and thus presuppose a current repo state whenever
they are run.

## The task contract

Because the pipeline logic lives here rather than in the CI file, the set of poe tasks effectively *is* the CI contract
— the same tasks are called from both the GitLab and GitHub pipelines (see [CI/CD](ci.md)). List them at any time with
`uv run poe`. The core tasks are:

| Task                    | What it does                                                                                   |
| ----------------------- | ---------------------------------------------------------------------------------------------- |
| `lint`                  | Run all pre-commit hooks (ruff format + check, mypy, file hygiene).                            |
| `deps-check`            | Dependency hygiene with [deptry](deptry.md).                                                   |
| `audit`                 | Security audit of dependencies (`uv audit`).                                                   |
| `test [cpus] [path]`    | Tests on one interpreter + coverage + artifacts.                                               |
| `test-all`              | The [nox](testing.md) matrix across all supported Python versions.                             |
| `build`                 | Build the wheel + sdist (`uv build`).                                                          |
| `bump`                  | Bump the version from commits, update CHANGELOG, create the tag ([commitizen](versioning.md)). |
| `changelog`             | Preview the changelog without bumping.                                                         |
| `docs` / `docs-version` | Build / version the documentation.                                                             |
| `export-test-artifacts` | Generate the test + coverage badges.                                                           |
| `clean`                 | Remove caches and generated artifacts.                                                         |

Tasks can call other tasks and take positional arguments (e.g. `poe test 4` runs with 4 xdist workers) — see their
`help` strings.
