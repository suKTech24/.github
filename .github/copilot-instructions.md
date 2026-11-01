# Copilot instructions

This is the organization-level `.github` repository for `ai-devops-learning`.
The full agent guide is [AGENTS.md](../AGENTS.md). Read it before making
changes. The most important rules are summarized here.

## Context

- Root `*.md` community health files, `.github/ISSUE_TEMPLATE/`, and
  `.github/pull_request_template.md` are **defaults for every repository in the
  organization**. Keep the wording generic.
- `profile/README.md` is the public organization profile.
- `workflow-templates/` holds starter workflows offered org-wide. Every
  `<name>.yml` needs a matching `<name>.properties.json` with `name` and
  `description`.
- `scripts/` and `tickets/_template/` are helpers that other repositories copy.
  Templates that depend on them must say so in their header comment.
- `.github/workflows/` is CI for this repository only.

## When writing or reviewing GitHub Actions YAML

- Pin every action to a full 40-character commit SHA with a version comment:
  `uses: actions/checkout@<sha> # v7.0.1`. Never invent a SHA. Never replace a
  SHA with a tag.
- Set top-level `permissions: contents: read`, and grant extra scopes per job
  only where needed.
- Add `timeout-minutes` to every job and `persist-credentials: false` to
  `actions/checkout`.
- Never interpolate untrusted `${{ github.event.* }}` text into `run:`. Pass it
  through `env:`.
- In templates, use `$default-branch` instead of `main`.

## Style

- Conventional Commits for commits and PR titles (`docs:`, `ci:`, `feat:`).
- YAML: 2-space indentation, `.yml` extension. Markdown: ATX headings, wrapped
  at about 80 columns. LF line endings.
- Never include secrets, tokens, or personal contact details.

## Validate

```bash
actionlint .github/workflows/*.yml workflow-templates/*.yml
npx markdownlint-cli2 "**/*.md"
```
