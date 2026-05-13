# GitHub Lifecycle Playbook

Use this reference for full GitHub work that spans local Git, GitHub API, Actions, Releases, Pages, issues, PRs, and README polish.

## 1. Intake

Inspect before acting:

```bash
git status --short --branch
git remote -v
git branch --show-current
git log --oneline -5
```

For account-sensitive work, route through `$gh-account-router` instead of relying on ambient `gh` login.

```powershell
python C:\Users\harzva\.codex\skills\gh-account-router\scripts\gh_account_router.py --account harzva -- api user --jq .login
python C:\Users\harzva\.codex\skills\gh-account-router\scripts\gh_account_router.py --account saihao -- api user --jq .login
```

On macOS/Linux, use the same Python script path if installed, or normal `gh` where account routing is not needed.

## 2. Clone, Pull, Fetch, Sync

Use HTTPS remotes for cross-platform reliability:

```bash
git clone https://github.com/OWNER/REPO.git
git fetch --all --prune
git pull --ff-only
```

If local work exists, inspect before pulling:

```bash
git status --short
git diff --stat
```

Use a branch for non-trivial work:

```bash
git switch -c feature/name
```

## 3. Commit and Push

Stage only intentional files:

```bash
git add PATHS
git diff --cached --check
git commit -m "Concise change summary"
```

For routed HTTPS push on Windows:

```powershell
git config --local --unset-all credential.https://github.com.helper
git config --local --add credential.https://github.com.helper ""
git config --local --add credential.https://github.com.helper "!python C:/Users/harzva/.codex/skills/gh-account-router/scripts/gh_account_router.py --account harzva --credential-helper"
git push -u origin HEAD
```

Keep the remote clean:

```bash
git remote set-url origin https://github.com/OWNER/REPO.git
```

## 4. Repository Creation

Use `$gh-account-router` when choosing Harzva vs saihao/Just-Agent:

```powershell
python C:\Users\harzva\.codex\skills\gh-account-router\scripts\gh_account_router.py --account harzva -- repo create Harzva/REPO --public --description "..." --source . --remote origin --push
```

If ordinary git push fails, create the repo first, then use Contents API or Git Data API fallback.

## 5. Issues

Use issues for durable work tracking, bugs, feature requests, and release follow-up. Keep titles actionable and labels useful.

```bash
gh issue create --repo OWNER/REPO --title "..." --body "..." --label bug
gh issue list --repo OWNER/REPO --state open
gh issue close 123 --repo OWNER/REPO --comment "Resolved by ..."
```

For bulk triage, gather issues first and avoid changing labels until the taxonomy is clear.

## 6. Pull Requests

Prefer PRs for reviewable changes:

```bash
gh pr create --repo OWNER/REPO --base main --head BRANCH --title "..." --body "..."
gh pr view --repo OWNER/REPO --web
gh pr checks --repo OWNER/REPO
```

PR body should include summary, verification, risks, and screenshots or artifact links when relevant.

## 7. GitHub Actions

Use `$gh-actions-release-builder` for workflow implementation. Baseline expectations:

- `workflow_dispatch` for manual runs.
- Explicit `permissions`.
- `actions/checkout` and setup actions for runtimes.
- Artifacts with clear names and retention.
- Release jobs separated from CI jobs when write permissions are needed.
- No local build if the local machine lacks the target environment.

Check workflows:

```bash
gh workflow list --repo OWNER/REPO
gh run list --repo OWNER/REPO --limit 10
gh run view RUN_ID --repo OWNER/REPO --log-failed
```

## 8. Releases

Use Releases for versioned deliverables, APK/EXE/ZIP/packages, and public changelogs.

```bash
gh release create v0.1.0 dist/app.zip --repo OWNER/REPO --title "v0.1.0" --notes-file RELEASE_NOTES.md
gh release upload v0.1.0 dist/extra.zip --repo OWNER/REPO --clobber
gh release view v0.1.0 --repo OWNER/REPO
```

For automated releases, use tag-triggered Actions and attach artifacts from the workflow.

## 9. GitHub Pages

Prefer Actions-based Pages deployment:

- Static site source: build output such as `dist/`, `site/`, `docs/`, or generated docs.
- Use `actions/upload-pages-artifact` and `actions/deploy-pages`.
- Set `permissions: pages: write` and `id-token: write` only in the deploy workflow.
- Verify Pages URL and deployment status after push.

Use `$gh-actions-release-builder` to author the workflow.

## 10. README and Repository Presentation

Before public publishing or after major changes, use `$readme-design`.

README checklist:

- Clear project positioning and target user.
- Quick start and real commands.
- Screenshots, diagrams, demo links, artifact links, or Pages URL when available.
- Actual badges only: build, release, license, docs, Pages, package status.
- Installation, usage, architecture, roadmap, and known limitations.
- Correct account/repo links and no false claims about CI, Releases, or Pages.

## 11. Final Verification

Verify remote state:

```bash
gh repo view OWNER/REPO --json nameWithOwner,url,visibility,defaultBranchRef
git ls-remote --heads origin
gh release list --repo OWNER/REPO
gh run list --repo OWNER/REPO --limit 5
```

Final answer should include changed files, remote URL, branch, release/Page links, verification performed, and unresolved GitHub-side checks.
