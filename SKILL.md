---
name: github-management-suite
description: "Manage the full GitHub repository lifecycle across platforms: clone, pull, branch, commit, push, account routing, remotes, pull requests, issues, Actions, Releases, GitHub Pages, README optimization, and upload failure recovery. Use when Codex needs to publish or synchronize code, create or repair repositories, operate GitHub issues/PRs, configure CI/CD workflows, upload release assets, deploy Pages, diagnose push failures, or coordinate with `$gh-account-router`, `$gh-actions-release-builder`, `$readme-design`, and `$software-dev-pipeline`."
---

# GitHub Management Suite

Use this skill as the top-level GitHub operating guide. It is intentionally cross-platform: prefer commands and workflows that work on Windows PowerShell, macOS/Linux shells, and GitHub-hosted runners. When platform-specific syntax matters, state it explicitly.

## Skill Routing

- Use `$gh-account-router` whenever the account, owner, token, remote, repository creation, or push identity matters.
- Use `$gh-actions-release-builder` for `.github/workflows/*.yml`, CI, build artifacts, release automation, and GitHub Pages workflows.
- Use `$readme-design` before publishing or after major feature work when the README should become more professional, visual, persuasive, or GitHub-friendly.
- Use `$software-dev-pipeline` when repository work is part of broader product delivery, release packaging, quality gates, or production hardening.

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
   - Normal Harzva code sync: HTTPS `git push` with `$gh-account-router` credential helper.
   - Account-sensitive or failing push: use routed `gh` commands and API fallback.
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

Read `references/lifecycle-playbook.md` when the task involves more than one GitHub area, such as publish + README + Actions + Release.

Read `references/failure-recovery.md` when any upload, push, auth, remote, issue, release, Actions, or Pages operation fails.

Run `scripts/github_upload_probe.py` when you need a cross-platform check of local GitHub connectivity, `gh` auth, repo API access, and optional Contents API upload.

## Professional Defaults

- Keep repository history clean but do not rewrite user work unless explicitly requested.
- Prefer PRs for shared repositories and direct push only when the user clearly owns the repo or asks for it.
- Use issue labels and milestones consistently; do not create noisy issues when a concise TODO in a PR body is enough.
- Create release notes from real changes, artifacts, and known limitations; do not invent features.
- Make GitHub Pages deployment reproducible from Actions instead of manual local uploads.
- Before public publishing, improve README structure with `$readme-design` and verify badges/links reflect actual repo capabilities.
- After changes, report what was changed, what remote URL/branch/release/page was touched, and what still needs GitHub-side verification.
