# Unit Testing and Coverage

We recommend [pytest](https://docs.pytest.org/en/stable/) as a testing framework, and use
[coverage](https://coverage.readthedocs.io/en/latest/index.html), as well as a
[coverage plugin for pytest](https://pypi.org/project/pytest-cov/) to generate coverage (statement / branch) reports
every time the tests are run.

Note that in the coverage settings in the `pyproject.toml`, you can specify a coverage threshold under which the tests
will fail. This is to encourage a thorough and organic testing strategy. Don't test as an afterthought, but rather
consider this as a non-negotiable part of the development cost.

When building the documentation, both the latest testing and coverage reports are used and uploaded as documentation
artifacts visible to anyone.

Your coverage report will be available at `<YOUR DOCS URL>/latest/exported/coverage/` and your test results will be
available at `<YOUR DOCS URL>/latest/exported/pytest.html?sort=result`.

## Testing across Python versions (nox)

`uv run poe test` runs the suite on a single interpreter and is the canonical run that produces the coverage report and
the badges/artifacts embedded in the docs. To prove your code works across *all* supported Python versions, the project
also uses [nox](https://nox.thea.codes/):

```bash
uv run poe test-all      # = nox -s tests
```

**What nox is.** nox runs your tests in fresh, isolated virtual environments — one per Python version. Unlike tox
(configured in an `.ini`), nox is configured in plain Python: a `noxfile.py` whose functions, each decorated with
`@nox.session`, describe one isolated run ("a session"). This project's session is essentially:

```python
PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]

@nox.session(python=PYTHON_VERSIONS)   # -> one session per version
def tests(session):
    session.run("pytest", ...)
```

Passing the list to `python=` expands `tests` into one session per interpreter, so `nox -s tests` spins up a 3.10–3.13
environment (with **uv** as the backend) and runs the suite in each. `PYTHON_VERSIONS` in `noxfile.py` is the **single
source of truth** for the matrix — CI runs the same `nox` session rather than re-listing versions.

**Why both tasks?** `poe test` is the fast local loop (one interpreter, plus coverage and the HTML/badge artifacts under
`docs/exported/`); `poe test-all` is the broad correctness check (every supported version, no coverage overhead) and is
what the CI matrix runs. Use `poe test` while coding; let CI (or `poe test-all` before a release) cover the matrix.
