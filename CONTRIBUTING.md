# Contributing to SafeRL ProofStack

Thank you for your interest in contributing!

## Issues

- Use labels: `bug`, `feature`, `discussion`.
- Provide clear steps to reproduce for bugs, and detailed context for features.

## Pull Requests (PRs)

- All PRs must pass:
  - `lake build` (Lean proofs)
  - `pytest` (unit tests)
  - `black` (code style)
- Link related issues in your PR description.
- Keep PRs focused and minimal; open separate PRs for unrelated changes.

## Commit Style

- Use [Conventional Commits](https://www.conventionalcommits.org/):
  - `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, etc.
- Example: `feat: add pressure bounds template`

## CLA

- All contributors must sign off on their commits using the DCO:
  - `git commit -s`
- By signing off, you agree to the [Apache 2.0 License](LICENSE).

## Review Process

- PRs are reviewed for correctness, clarity, and compliance with project standards.
- Automated checks must pass before merge.
- Maintainers may request changes or clarifications.

---

We welcome your contributions to make SafeRL ProofStack better for everyone!
