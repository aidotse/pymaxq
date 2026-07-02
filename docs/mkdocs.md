# Documentation

This template ships a documentation site built with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) and configured in `mkdocs.yaml`. You write pages as Markdown under `docs/`, and `mkdocs build` renders them into a static site. The navigation is defined under the `nav:` key in `mkdocs.yaml`, so when you add a page, add it there too.

## API reference from docstrings (mkdocstrings)

In addition to hand-written pages, the [mkdocstrings](https://mkdocstrings.github.io/) plugin generates API documentation directly from your source code's Google-style docstrings. The [API Reference](reference.md) page is as simple as a one-line directive per module:

```markdown
::: your_package.your_module
```

so your reference docs stay in sync with the code for free — as long as you keep writing docstrings, which [ruff](https://docs.astral.sh/ruff/) helps enforce.

## Building and deploying

Build the site locally with:

```bash
uv run poe docs
```

(run `uv run poe test` first, since the site embeds the coverage and test-result artifacts under `exported/`).

The site is **single-version**: each release rebuilds and *replaces* the published site — there is no per-version archive to navigate. Deployment is automated as part of a release: when a new version is tagged on the default branch, the docs are rebuilt and published. See [CI/CD](ci.md) for the pipeline details. Both hosting platforms are supported out of the box:

- **On GitHub**, the release workflow builds the site and deploys it with the official GitHub Pages Actions (`actions/upload-pages-artifact` + `actions/deploy-pages`) straight from the workflow run — there is **no `gh-pages` branch** to manage. Set **Settings → Pages → Source** to **GitHub Actions** (see [Getting Started](getting-started.md)).
- **On GitLab**, the pipeline deploys the built site to GitLab Pages via the reserved `pages` job, which serves the generated `public/` directory.

Your documentation is then served from your project's Pages URL (linked from the badges in your `README`, and shown in your repository's Pages settings).
