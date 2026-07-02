# Formatting, Linting, and Static Type Checking

As part of the quality assurance pipeline in this repo, your code is always passed through a formatting, linting, and static type checking process before it can be committed to the repo.
We use [ruff](https://github.com/astral-sh/ruff) for both formatting and linting, and [mypy](https://mypy-lang.org/) for static type checking.

Ruff is the modern, extremely fast (Rust-based) standard for Python code quality, and it deliberately does two jobs:

- **`ruff format`** formats your code in-place to a [PEP8](https://peps.python.org/pep-0008/)-compliant style — a drop-in replacement for [black](https://github.com/psf/black).
- **`ruff check`** lints your code, acting as a drop-in replacement for a wide set of standalone tools such as isort, pydocstyle, pyupgrade, autoflake, and many more. This is why this repo no longer depends on black, isort, or pyupgrade separately: ruff covers all of them, faster and from a single config.

Ruff is highly configurable directly in the `pyproject.toml` file. You can activate or deactivate rules and entire rulesets depending on how strict you want to be with your project; this repo has a meaningful default setting (under `[tool.ruff.lint]`, with rule families like pycodestyle, pyflakes, isort, pyupgrade, bugbear, and bandit security checks enabled) which can and should be adjusted to your own needs. If some rule violation simply does not make sense, you can either add the rule to the `ignore` list in `[tool.ruff.lint]`, or manually suppress it by appending a `# noqa: <rule ID>` to the offending line in your code.

Mypy is a static type checker that is however prone to false positives in certain circumstances. If this is the case you can manually suppress warnings by appending `# type: ignore` to the offending line. By default mypy is configured to encourage typing annotations in your code, which is also a common best practice.

All three run automatically via [pre-commit](precommit.md) before each commit, and again in the CI quality gate. You can run the whole set at any time with `uv run poe lint`.
