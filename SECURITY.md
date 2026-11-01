# Security Policy

The `ai-devops-learning` organization takes the security of its repositories
seriously. This policy applies to every repository in the organization that
does not define its own `SECURITY.md`.

## Supported versions

Unless a repository states otherwise, security fixes are made only on the
default branch and the most recent release. Older releases do not receive
patches; upgrade to the latest release first.

## Reporting a vulnerability

**Please do not report security vulnerabilities through public GitHub issues,
discussions, or pull requests.**

Report them privately with GitHub's
[private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability):

1. Go to the affected repository's **Security** tab.
2. Click **Report a vulnerability**.
3. Fill in the advisory form.

Please include as much of the following as you can:

- The type of issue (for example, injection, credential exposure, privilege
  escalation in a workflow)
- The full paths of the affected source files
- The branch, tag, or commit SHA where the issue exists
- Any special configuration needed to reproduce it
- Step-by-step reproduction instructions
- Proof-of-concept or exploit code, if available
- The impact, including how an attacker might exploit it

## What to expect

| Stage | Target time |
| --- | --- |
| Acknowledge your report | 3 business days |
| Initial assessment and severity rating | 7 business days |
| Status updates | At least every 14 days until resolved |
| Fix for critical/high severity issues | 30 days, where feasible |

We follow coordinated disclosure. Once a fix is available, we publish a
[GitHub Security Advisory](https://docs.github.com/en/code-security/security-advisories),
request a CVE where appropriate, and credit you unless you ask to stay
anonymous.

## Scope

In scope:

- Source code in repositories owned by this organization
- GitHub Actions workflows and the shared
  [workflow templates](workflow-templates/) in this repository

Out of scope:

- Vulnerabilities in third-party dependencies that are already publicly known
  (report them upstream; Dependabot tracks them here)
- Findings from automated scanners with no demonstrated impact
- Social engineering, physical attacks, and denial-of-service testing

## Safe harbor

We will not take legal action against, or ask law enforcement to investigate,
anyone who researches in good faith under this policy. That means you:

- Avoid privacy violations, data destruction, and service disruption
- Access only the data needed to demonstrate the issue
- Give us reasonable time to fix the issue before disclosing it publicly
