# Governance

This document describes how the `ai-devops-learning` organization makes decisions. Individual repositories may add stricter rules of their own.

## Roles

| Role | Responsibilities | GitHub permission |
| --- | --- | --- |
| **Owner** | Organization settings, security, billing, granting maintainer access | Organization owner |
| **Maintainer** | Reviewing and merging PRs, triaging issues, cutting releases | `maintain` or `admin` on a repository |
| **Triager** | Labeling, deduplicating, and closing issues | `triage` |
| **Contributor** | Anyone who opens an issue or pull request | — |

The current maintainers of each repository are listed in its
`.github/CODEOWNERS` file.

## Decision making

- **Routine changes** (bug fixes, docs, dependency bumps) need one approving
  review from a code owner.
- **Significant changes** (new repositories, breaking changes, changes to
  shared workflow templates or org-wide policy) need an issue or discussion
  open for at least 3 business days and approval from two maintainers.
- When consensus can't be reached, organization owners make the final
  decision.

## Becoming a maintainer

Contributors with a sustained record of quality contributions and reviews may
be nominated by an existing maintainer. Owners approve nominations. Maintainers
who are inactive for 6 months may be moved to emeritus status, and their access
reduced.

## Security baseline

All repositories are expected to:

- Protect the default branch: require PR reviews and status checks, and block
  force pushes
- Enable Dependabot alerts and security updates, secret scanning with push
  protection, and private vulnerability reporting
- Run code scanning (see the CodeQL [workflow template](workflow-templates/))
- Require two-factor authentication for all members (enforced at the
  organization level)

## Changes to this document

Changes to governance follow the *significant changes* process above.
