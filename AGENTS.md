# AGENTS.md

Instructions for AI coding agents (Claude Code, Copilot, Codex, Cursor, and
others) working in this repository. Humans should start with
[CONTRIBUTING.md](CONTRIBUTING.md).

## What this repository is

This is the organization-level `.github` repository for `ai-devops-learning`.
GitHub treats it specially:

- **Root community health files** (`SECURITY.md`, `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `SUPPORT.md`, `GOVERNANCE.md`) and
  `.github/ISSUE_TEMPLATE/` and `.github/pull_request_template.md` are used as
  **defaults for every repository in the organization** that lacks its own copy.
- **`profile/README.md`** is rendered on the organization's public profile page.
- **`workflow-templates/`** contains starter workflows offered to every
  repository under *Actions → New workflow*.
- **`.github/workflows/`** contains CI for *this* repository only.
- `.github/CODEOWNERS` and `.github/dependabot.yml` apply to *this* repository
  only. They are **not** inherited.

Changes here affect the whole organization. Keep them small and deliberate.

## Layout

```text
.
├── profile/README.md            # Org profile page
├── workflow-templates/          # <name>.yml + <name>.properties.json pairs
├── scripts/                     # Helper scripts that repos copy (used by some templates)
├── tickets/_template/           # Ticket file template for create_issues_from_tickets.py
├── .github/
│   ├── ISSUE_TEMPLATE/          # Org-default issue forms
│   ├── pull_request_template.md # Org-default PR template
│   ├── workflows/ci.yml         # Lints this repo
│   ├── copilot-instructions.md  # Copilot summary of this file
│   ├── CODEOWNERS
│   └── dependabot.yml
├── AGENTS.md / CLAUDE.md        # Agent instructions (CLAUDE.md imports this)
└── *.md                         # Org-default community health files
```

## Commands

There is no build. Validate changes with the same checks CI runs:

```bash
# Lint workflows and workflow templates (https://github.com/rhysd/actionlint)
actionlint .github/workflows/*.yml workflow-templates/*.yml

# Lint Markdown
npx markdownlint-cli2 "**/*.md"

# Every template must have a valid, matching properties file
for f in workflow-templates/*.yml; do
  p="${f%.yml}.properties.json"
  test -f "$p" && jq -e '.name and .description' "$p" >/dev/null || echo "BAD: $f"
done
```

## Rules for workflow templates

When adding or editing anything in `workflow-templates/`:

1. **Add files in pairs:** `foo.yml` plus `foo.properties.json` with at least
   `name` and `description`. Add `iconName` (`"octicon <name>"`),
   `categories`, and `filePatterns` where they make sense.
2. **Use `$default-branch`** instead of hard-coding `main`.
3. **Pin every action to a full 40-character commit SHA** with the version as a
   trailing comment. Look up the SHA with
   `git ls-remote https://github.com/<owner>/<repo> refs/tags/<tag>^{}`. Never
   invent a SHA.
4. **Declare least privilege:** `permissions: contents: read` at the top level,
   with extra scopes granted per job only where needed.
5. **Harden every job:** `timeout-minutes`, a `concurrency` group where
   re-runs are wasteful, and `persist-credentials: false` on checkout.
6. **Don't inject untrusted input:** never put `${{ github.event.* }}` text
   fields directly into `run:`. Use `env:`.
7. **Keep templates generic.** No org-specific secrets, hostnames, or repo
   names. Put a short header comment at the top of each template explaining
   what it does and what to customize.
8. Update the template table in [README.md](README.md).
   If a template depends on a file in `scripts/`, say so in its header comment.
   Templates copy only the workflow file, so users must copy the script too.
9. If you change a rule in this file, update the summary in
   `.github/copilot-instructions.md` to match.

## Rules for community health files

- Keep wording generic enough to apply to any repository in the organization.
- Don't publish personal email addresses or phone numbers. Route private
  contact through GitHub features (private vulnerability reporting, report
  content).
- `CODE_OF_CONDUCT.md` is the verbatim Contributor Covenant 2.1. Change only
  the enforcement contact line.

## Conventions

- Conventional Commits for commit messages and PR titles (`docs:`, `ci:`,
  `feat:`, and so on).
- Markdown: wrap at about 80 columns, one sentence or clause per line is fine,
  and use ATX headings (`#`).
- YAML: 2-space indentation, `.yml` extension.
- Line endings: LF (enforced by `.editorconfig` and `.gitattributes`).

## Boundaries

- Do **not** commit secrets, tokens, or `.env` files.
- Do **not** loosen `permissions:` or replace SHA pins with tags to "fix" a
  failing check.
- Do **not** push to `main` directly. Open a pull request.
- Ask a human before deleting a workflow template. Other repositories may
  depend on it.
