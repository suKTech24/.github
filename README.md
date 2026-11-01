# ai-devops-learning/.github

[![CI](https://github.com/ai-devops-learning/.github/actions/workflows/ci.yml/badge.svg)](https://github.com/ai-devops-learning/.github/actions/workflows/ci.yml)

Organization-wide defaults for **ai-devops-learning**: community health files,
issue and PR templates, the public organization profile, and reusable GitHub
Actions workflow templates.

## What's in here

| Path | Purpose | Scope |
| --- | --- | --- |
| [`profile/README.md`](profile/README.md) | Public organization profile page | Org profile |
| [`SECURITY.md`](SECURITY.md) | How to report vulnerabilities | Default for all repos |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | How to contribute | Default for all repos |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | Contributor Covenant 2.1 | Default for all repos |
| [`SUPPORT.md`](SUPPORT.md) | Where to get help | Default for all repos |
| [`GOVERNANCE.md`](GOVERNANCE.md) | Roles, decisions, security baseline | Default for all repos |
| [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/) | Bug and feature issue forms | Default for all repos |
| [`.github/pull_request_template.md`](.github/pull_request_template.md) | PR checklist | Default for all repos |
| [`workflow-templates/`](workflow-templates/) | Starter workflows | Offered to all repos |
| [`scripts/`](scripts/) | Helper scripts to copy into your repo | Copy as needed |
| [`tickets/_template/`](tickets/_template/) | Ticket file template used by the ticket script | Copy as needed |
| [`AGENTS.md`](AGENTS.md), [`CLAUDE.md`](CLAUDE.md), [`.github/copilot-instructions.md`](.github/copilot-instructions.md) | Instructions for AI coding agents | This repo |
| [`.github/workflows/`](.github/workflows/), `CODEOWNERS`, `dependabot.yml` | CI and ownership for this repo | This repo only |

A repository that has its own copy of a community health file uses that copy
instead of the default here.
See [GitHub's docs](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file).

## Workflow templates

In any repository in the organization, go to **Actions → New workflow** and
look for the section *By ai-devops-learning*.

| Template | What it does |
| --- | --- |
| [Node.js CI](workflow-templates/node-ci.yml) | `npm ci`, lint, test, and build across Node 20/22/24 |
| [Python CI](workflow-templates/python-ci.yml) | ruff and pytest across Python 3.11–3.13 |
| [Docker publish (GHCR)](workflow-templates/docker-publish.yml) | Multi-arch build and push to ghcr.io with SBOM, provenance, and attestation |
| [CodeQL analysis](workflow-templates/codeql.yml) | Security code scanning (`security-extended` queries) |
| [Dependency review](workflow-templates/dependency-review.yml) | Blocks PRs that add vulnerable or AGPL dependencies |
| [OpenSSF Scorecard](workflow-templates/scorecard.yml) | Supply-chain security posture score |
| [Lint workflows](workflow-templates/actionlint.yml) | actionlint on `.github/workflows/` |
| [Semantic PR title](workflow-templates/semantic-pr-title.yml) | Enforces Conventional Commits PR titles |
| [Stale](workflow-templates/stale.yml) | Closes inactive issues and PRs |
| [Create issues from tickets](workflow-templates/create-issues-from-tickets.yml) | Creates issues (and Project cards) from `tickets/` files. Needs the companion script; see below |

Every template follows the same hardening baseline:

- Actions pinned to full commit SHAs
- Least-privilege `permissions`
- `persist-credentials: false` on checkout
- Job timeouts
- Concurrency cancellation for superseded PR runs

> Workflow templates are available to all repositories when this `.github`
> repository is **public**. A private `.github` repository shares templates only
> on GitHub Enterprise plans.

## Scripts

| Script | What it does |
| --- | --- |
| [`create_issues_from_tickets.py`](scripts/create_issues_from_tickets.py) | Creates a GitHub issue for each `tickets/<ID>-<slug>/README.md` that doesn't have one yet, and optionally adds it to a Projects v2 board. Create-only: it never edits or closes existing issues. |

To use the ticket workflow in your repository:

1. Copy `scripts/create_issues_from_tickets.py` into your repository.
2. Copy `tickets/_template/` into your repository's `tickets/` folder.
3. Add the *Create issues from tickets* workflow from **Actions → New workflow**.
4. Create tickets by copying the template folder to `tickets/<ID>-<short-slug>/`.
   Get the next free ID with
   `python scripts/create_issues_from_tickets.py --next-id --repo <owner>/<repo>`.
5. Preview locally with `--dry-run`, which needs `gh` and PyYAML.

## Contributing

Changes here affect every repository in the organization. See
[CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md) (template rules
and validation commands). The `significant changes` process in
[GOVERNANCE.md](GOVERNANCE.md) applies to template and policy changes.
