---
name: github-management-suite
description: "Cross-platform GitHub operations suite for repository management, clone/pull/fetch/branch/commit/push, account routing, remotes, issues, pull requests, reviews, Actions, Releases, GitHub Pages, README optimization, and upload failure recovery. Use when Codex needs to publish or synchronize code, create or repair repositories, operate GitHub issues/PRs, configure CI/CD workflows, upload release assets, deploy Pages, diagnose push failures, prepare a public GitHub project, or coordinate with `$gh-account-router`, `$gh-actions-release-builder`, `$readme-design`, and `$software-dev-pipeline`."
---

# GitHub Management Suite

Use this skill as the top-level GitHub operating guide. It should feel smooth for the local owner and for subscribers who do not share the owner's paths, tokens, aliases, or operating system.

Prefer portable GitHub workflows first: normal `git`, `gh`, GitHub REST API, and GitHub Actions. Use owner-specific helpers only after detecting that the local environment provides them.

## Skill Routing

- Use `$gh-account-router` whenever the local environment has it and the account, owner, token, remote, repository creation, or push identity matters.
- Use `$gh-actions-release-builder` for `.github/workflows/*.yml`, CI, build artifacts, release automation, and GitHub Pages workflows.
- Use `$readme-design` before publishing or after major feature work when the README should become more professional, visual, persuasive, or GitHub-friendly.
- Use `$software-dev-pipeline` when repository work is part of broader product delivery, release packaging, quality gates, or production hardening.
- If a linked helper skill is unavailable for a subscriber, fall back to plain `gh`, GitHub API, and the procedures in this skill instead of stopping.

## First-Run Decision Tree

1. If the user asks to "upload", "publish", "push", "sync", or "create repo":
   - Inspect local Git state.
   - Determine owner/account from remote URL, request text, or `gh api user`.
   - Push with clean HTTPS remote when possible.
   - If push fails, read `references/failure-recovery.md` and use API fallback.

2. If the user asks for Actions, build, packaging, release, or Pages:
   - Read `AGENTS.md` first.
   - If local build is disallowed or unavailable, create GitHub Actions instead of building locally.
   - Use `$gh-actions-release-builder` when available.

3. If the user asks for GitHub project polish:
   - Audit README, topics, license, releases, screenshots, workflows, and Pages.
   - Use `$readme-design` when available.
   - Keep claims tied to real repository files or remote state.

4. If the user asks to diagnose GitHub problems:
   - Run safe status checks first.
   - Run `scripts/github_upload_probe.py` for repeatable environment diagnostics.
   - Report the next safest path, not a long list of guesses.

## Default Workflow

1. Inspect repository state:
   - Read `AGENTS.md`, README, package/build metadata, `.github/`, remotes, branch state, and uncommitted changes.
   - Run safe checks such as `git status --short --branch`, `git remote -v`, and `gh auth status` or routed `gh api user`.
   - Never expose tokens, access files, credential helpers, or secret values.

2. Decide the GitHub operation:
   - Sync: clone, fetch, pull, merge, rebase, branch, commit, push.
   - Collaboration: issue triage, labels, milestones, PRs, reviews, discussions.
   - Automation: Actions CI, build, release, Pages, scheduled workflows.
   - Publishing: repository creation, README polish, topics, Releases, artifacts, Pages.
   - Recovery: push failures, permission mismatch, remote conflicts, branch protection, large files.

3. Choose the safest upload path:
   - Generic subscriber default: clean HTTPS remote plus `git push`.
   - Local managed-account default: HTTPS `git push` with `$gh-account-router` credential helper.
   - Account-sensitive or failing push: use routed `gh` commands when available, then API fallback.
   - Small file update: GitHub Contents API.
   - Multi-file fallback: Git Data API commit.
   - Binary/package output: `gh release create` or `gh release upload`.
   - SSH only after `ssh -T git@github.com` authenticates successfully.

4. Implement and verify:
   - Keep remotes credential-free HTTPS URLs such as `https://github.com/OWNER/REPO.git`.
   - Prefer non-interactive commands.
   - Verify remote state with `gh repo view`, `gh api`, `git ls-remote`, workflow run status, release asset lists, or Pages deployment status.
   - If a build is required and local environment is unavailable, put it in GitHub Actions rather than compiling locally.

## Full Lifecycle Reference

Read `references/subscriber-onboarding.md` when preparing the skill or a repository for someone who does not share this local machine, account aliases, or Windows paths.

Read `references/lifecycle-playbook.md` when the task involves more than one GitHub area, such as publish + README + Actions + Release.

Read `references/failure-recovery.md` when any upload, push, auth, remote, issue, release, Actions, or Pages operation fails.

Run `scripts/github_upload_probe.py` when you need a cross-platform check of local GitHub connectivity, `gh` auth, repo API access, and optional Contents API upload.

Read `references/operations-matrix.md` when choosing the correct tool for clone, push, issue, PR, Actions, Release, Pages, or fallback upload work.

## Professional Defaults

- Keep repository history clean but do not rewrite user work unless explicitly requested.
- Prefer PRs for shared repositories and direct push only when the user clearly owns the repo or asks for it.
- Use issue labels and milestones consistently; do not create noisy issues when a concise TODO in a PR body is enough.
- Create release notes from real changes, artifacts, and known limitations; do not invent features.
- Make GitHub Pages deployment reproducible from Actions instead of manual local uploads.
- Before public publishing, improve README structure with `$readme-design` and verify badges/links reflect actual repo capabilities.
- For public subscriber-facing repositories, provide a concise README, clear install/use path, and a troubleshooting command that works outside the owner's machine.
- After changes, report what was changed, what remote URL/branch/release/page was touched, and what still needs GitHub-side verification.
