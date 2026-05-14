# Subscriber Onboarding

Use this reference when the repository or skill must work for people who do not share the owner's local paths, GitHub aliases, tokens, or operating system.

## Portability Rules

- Prefer `git`, `gh`, and GitHub API instructions that work on Windows, macOS, and Linux.
- Treat owner-specific paths such as `C:\Users\harzva\...` as optional accelerators, not requirements.
- When mentioning `$gh-account-router`, explain the plain `gh` fallback.
- Keep remotes as credential-free HTTPS URLs.
- Never ask subscribers to paste tokens into remote URLs, README files, workflow YAML, or prompts.
- Make GitHub Actions the build environment when a local build environment may be unavailable.

## First-Time Subscriber Flow

1. Confirm tools:

```bash
git --version
gh --version
python --version
```

2. Authenticate with GitHub:

```bash
gh auth login
gh api user --jq .login
```

3. Probe the environment:

```bash
python scripts/github_upload_probe.py --repo OWNER/REPO
```

4. If write diagnostics are needed and the user owns the repository:

```bash
python scripts/github_upload_probe.py --repo OWNER/REPO --write-probe
```

5. For source publishing:

```bash
git remote set-url origin https://github.com/OWNER/REPO.git
git push -u origin HEAD
```

6. If push fails, switch to `references/failure-recovery.md`.

## Public Repository Expectations

A subscriber-facing GitHub repository should provide:

- What the skill does in the first screen.
- Who should use it.
- Install or copy path.
- Common invocation prompt.
- What optional companion skills improve the workflow.
- A safe diagnostic command.
- Clear limitations and security notes.

## Companion Skills

- `$gh-account-router`: optional owner-local acceleration for managed accounts.
- `$gh-actions-release-builder`: optional deeper workflow authoring.
- `$readme-design`: optional repository presentation polish.
- `$software-dev-pipeline`: optional product release and quality strategy.

If these are unavailable, continue with this skill's plain GitHub CLI and API guidance.
