# Contributing

Thanks for taking the time to contribute to `ai-devops-learning`. This guide
applies to every repository in the organization that does not provide its own
`CONTRIBUTING.md`.

By participating, you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to contribute

- **Report a bug:** open an issue using the *Bug report* form.
- **Suggest a feature:** open an issue using the *Feature request* form.
- **Ask a question:** see [SUPPORT.md](SUPPORT.md). Please don't use issues for
  questions.
- **Report a security issue:** follow [SECURITY.md](SECURITY.md). Never open a
  public issue for it.
- **Submit a change:** follow the workflow below.

## Development workflow

1. **Discuss first** for anything bigger than a small fix. Open or comment on an
   issue so effort isn't wasted.
2. **Fork** the repository (or create a branch if you have write access).
3. **Branch** from the default branch using a descriptive name such as
   `feat/add-ghcr-template` or `fix/codeql-schedule`.
4. **Make focused commits.** One logical change per pull request.
5. **Run the repository's checks locally** (lint, test, build) before you push.
6. **Open a pull request** and fill in the template.

### Commit messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```text
<type>(<optional scope>): <short summary>

<optional body explaining what and why>
```

Common types: `feat`, `fix`, `docs`, `ci`, `chore`, `refactor`, `test`,
`build`, `perf`. Mark breaking changes with `!` (for example, `feat!:`) or a
`BREAKING CHANGE:` footer. Pull request titles must follow the same format,
because squash merges use the title as the commit message.

### Signing commits

Signed commits are strongly recommended and may be required by branch
protection. See
[signing commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits).

## Pull request checklist

- [ ] The PR title follows Conventional Commits
- [ ] The change is covered by tests, or the PR explains why that isn't needed
- [ ] Documentation is updated
- [ ] CI is green
- [ ] No secrets, credentials, or personal data are included

## Review process

- Every PR needs at least one approving review from a code owner.
- Maintainers aim to give a first response within 5 business days.
- PRs are squash-merged once they are approved and CI passes.
- PRs with no activity for 30 days may be closed as stale; you can reopen them.

## GitHub Actions guidelines

If your change touches workflows:

- Pin third-party actions to a **full commit SHA**, with the version in a
  trailing comment: `uses: actions/checkout@<sha> # v7.0.1`.
- Declare the least-privilege `permissions:`. Default to `contents: read`.
- Set `persist-credentials: false` on `actions/checkout` unless a later step
  needs to push.
- Never interpolate untrusted input (`github.event.*.title`, `body`,
  `head_ref`, and so on) directly into `run:`. Pass it through `env:` instead.
- Avoid `pull_request_target` unless you fully understand the risks.
- Add `timeout-minutes` to every job.

## AI-assisted contributions

AI coding tools are welcome. Agents should read [AGENTS.md](AGENTS.md). You
remain responsible for every line you submit: review it, test it, and make sure
you have the right to contribute it.

## License

By contributing, you agree that your contributions are licensed under the
license of the repository you are contributing to.
