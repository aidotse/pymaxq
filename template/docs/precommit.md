# Precommit

[precommit](https://pre-commit.com/) is a tool that is used to run a series of so-called `hooks` on your codebase. Typically this happens when you commit - if any of the hooks fails, then you can't commit either. The idea is to make sure that you are only committing high quality code into your repository.

When setting up your project, after installing your dependencies, make sure to install this gated commit mechanism by running

```bash
uv run pre-commit install
```

which will make sure that your hooks run whenever you run `git commit...`, immediately before the actual process of committing your code. Note that this repo configures `default_install_hook_types: [pre-commit, commit-msg]`, so the single command above installs **both** the standard pre-commit hooks *and* the commit-message hook described below.

The configuration for this tool, i.e. specifying which hooks to run under what conditions, is specified in the `.pre-commit-config.yaml` file. There is typically no need to define your own hooks; these are available across several repositories and can be simply re-used as is, with any exceptions for your project. For example, you might want to avoid having your formatter from messing with your `docs` (documentation) directory.

As a default, we recommend a list of pretty standard file-hygiene hooks, followed by:

- **code formatting and linting** using [ruff](https://docs.astral.sh/ruff/) (`ruff format` and `ruff check` — these replace standalone black/isort/pyupgrade; see [linting](linting.md)),
- **static type checking** using [mypy](https://mypy-lang.org/),
- **commit-message validation** using [commitizen](https://commitizen-tools.github.io/commitizen/), which runs at the `commit-msg` stage and rejects any message that doesn't follow the [Conventional Commits](https://www.conventionalcommits.org/) format. This matters because your commit messages drive automated [versioning](versioning.md).

## Usage

By default, pre-commit will only run on staged files for efficiency reasons, and you shouldn't need to bother with calling the tool directly (it will run automatically each time you try to `git commit`). You can of course also run the checks manually on all files using

```bash
uv run pre-commit run --all-files
```

which is also exactly what the `uv run poe lint` task does.

In particular, if your CI pipeline is failing due to some failing hook (because e.g. someone in your team forgot to activate these hooks locally first), you can run this locally to find the offending file / line and fix it that way.

Some tools such as `ruff` will try to fix any offending files in order to speed up the committing process. In these cases, you can `git add ...` the modified files again and try to re-commit. Eventually you will end up only with errors that cannot be fixed automatically and that require manual intervention.
