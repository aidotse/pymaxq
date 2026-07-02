# The Contribution Process

The mental model of how software is developed has a big impact on how, for example, components like CI/CD pipelines are designed to work, and this here is no exception. The following is a high level description of the mental model used here. To be clear, this may not be a perfect solution for all situations and projects, and there are of course many other ways to accomplish the same things. As explained above, this repo attempts to capture the core set of best practices that therefore have the highest chance of generalizing to your project as well.

- We assume a simple, [trunk-based](https://trunkbaseddevelopment.com/) model, with the `main` branch being our default / primary branch and the single integration point.
- Feature branches branch off of `main` and merge back into it via a merge/pull request. There is no long-lived `release` branch.
- When committing to your local branch, [precommit](precommit.md) runs locally and automatically to make sure formatting, linting, type checking, and commit-message conventions are maintained.
- Merging from your feature branch to `main` requires, in addition, the full CI quality gate to pass (unit tests across all supported Python versions, dependency hygiene, and a security audit). The idea is to make sure that only tested, reliable, linted, and correctly formatted code is in `main` at any given point in time.
- Versioning is **driven by your commit messages**, not by which branch you merge into. We use [Conventional Commits](https://www.conventionalcommits.org/) and [commitizen](https://commitizen-tools.github.io/commitizen/) to apply [semantic versioning](https://semver.org/) automatically:
    - a `fix:` commit produces a **patch** release,
    - a `feat:` commit produces a **minor** release,
    - a breaking change (`feat!:` or a `BREAKING CHANGE:` footer) produces a **major** release (a minor bump while still pre-1.0).
- On a successful merge to `main`, the CI pipeline runs the bump: if the new commits warrant a release it tags the new version, updates the changelog, and then publishes the package, image, and documentation. If they don't (e.g. a docs-only change), nothing is released. See [Versioning & Releases](versioning.md) and [CI/CD](ci.md).

See the individual tool/concept descriptions for a deeper view into how each of these are accomplished, and how to work with each tool on a more technical level.
