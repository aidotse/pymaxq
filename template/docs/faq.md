# FAQ

## Is this a template project? How do I use it for my own project?

Yes. This repository was generated from the [PyMaxQ](https://gitlab.mgmt.ai.se/dev-tools/pymaxq) template using [Copier](https://copier.readthedocs.io). To create your own project from the template, install copier and run `copier copy <template-url> path/to/my-project`, answering the prompts. To pull later improvements from the template into an existing project, run `copier update`. See [Templating with Copier](copier.md) for the full workflow.

## How do I specify my project dependencies?

You can specify your project dependencies directly in the `pyproject.toml` file, in either the `[project] -> dependencies=[...]` section for main (runtime) dependencies or the `[dependency-groups]` section for development dependencies. Optional features go under `[project.optional-dependencies]` as named extras — for example this template ships an `agent` extra, which you install with `uv sync --extra agent`. If in doubt, you can always just run `uv add <package>`; it will find the most recent version of your dependency that is compatible with your existing dependencies. Finally, install all your dependencies using `uv sync`, or only select groups with `uv sync --group=...`.

## How do I "reset" my virtual environment?

If you want to start from scratch, you can simply delete `.venv` and re-install dependencies with `uv sync`.

## How do I run scripts / executables in my project?

The `scripts/` directory is designed as a place for you to store your CLI and Python scripts. To run them, you need to make the virtual environment visible to them. So, if you have a script called `example.py`, instead of calling it with `python example.py`, you should make sure you are using the Python version & other dependencies installed in your virtual environment: `uv run scripts/example.py`.

As an example, to run the example script:

```bash
uv run scripts/example.py seed=1 num_runs=20 array_size=50
```

with any parameter assignments of your choice.

## Can I run parts of the pipeline manually/locally?

Yes — and this is by design. All the pipeline's logic lives in [poe tasks](poe.md) in `pyproject.toml`, and the CI file just calls them, so anything CI does you can reproduce locally. List the available tasks with `uv run poe`, then call any one, for example:

- Run the full lint/format/type-check gate: `uv run poe lint`
- Run the unit tests & coverage report: `uv run poe test`
- Run the test suite across all supported Python versions: `uv run poe test-all`
- Check dependency hygiene: `uv run poe deps-check`
- Audit dependencies for vulnerabilities: `uv run poe audit`
- Build the documentation locally: `uv run poe docs`

Note that some tasks may require the output of others (e.g. `docs` embeds the artifacts produced by `test`), so check their descriptions.
