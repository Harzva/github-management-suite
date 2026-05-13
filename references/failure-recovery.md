# Failure Recovery

Use this reference when any GitHub operation fails. Diagnose first, then pick the narrowest fallback.

## Fast Triage

Check:

```bash
git status --short --branch
git remote -v
git ls-remote origin
gh auth status
```

Account-sensitive check:

```powershell
python C:\Users\harzva\.codex\skills\gh-account-router\scripts\gh_account_router.py --account harzva -- api user --jq .login
python C:\Users\harzva\.codex\skills\gh-account-router\scripts\gh_account_router.py --account saihao -- api user --jq .login
```

Run the probe when the environment is uncertain:

```bash
python scripts/github_upload_probe.py --repo OWNER/REPO --write-probe
```

With account router:

```powershell
python scripts\github_upload_probe.py --repo Harzva/REPO --router C:\Users\harzva\.codex\skills\gh-account-router\scripts\gh_account_router.py --account harzva --write-probe
```

## Recommended Fallback Order

1. Clean HTTPS remote + routed credential helper.
2. `gh` repo/API operation through `$gh-account-router`.
3. Contents API for one-file updates.
4. Git Data API for multi-file commits.
5. Release asset upload for binaries.
6. SSH only after SSH auth is proven.

## Common Failures

### `Repository not found`

Likely causes:

- Wrong owner or repo name.
- Token belongs to a different account.
- Private repo permission mismatch.
- Remote URL points at an account alias rather than the canonical owner.

Fix:

```bash
git remote set-url origin https://github.com/OWNER/REPO.git
gh repo view OWNER/REPO --json nameWithOwner,url,visibility
```

If using managed accounts, verify canonical login with `$gh-account-router`.

### `Permission denied` or `403`

Likely causes:

- Wrong token/account.
- Token lacks `repo`, `workflow`, `pages`, or release permission.
- Branch protection blocks direct push.

Fix:

- Route through the correct account.
- Push a branch and open a PR.
- For Actions or Pages, check repo settings and workflow permissions.

### Push timeout or TLS failure

Likely causes:

- Temporary network failure to GitHub HTTPS.
- Proxy/firewall instability.
- Large packfile.

Fix:

```bash
git -c http.lowSpeedLimit=1 -c http.lowSpeedTime=30 push
```

If it still fails, use Git Data API fallback for source files or release upload for binaries.

### Non-fast-forward rejection

Fix:

```bash
git fetch origin
git status --short --branch
git pull --ff-only
```

If fast-forward is impossible, inspect divergent commits and choose merge, rebase, or PR. Do not force push unless explicitly requested and safe.

### Protected branch

Fix:

- Push a feature branch.
- Create a PR.
- Wait for required checks.
- Do not bypass protection unless the user asks and has permission.

### File too large

GitHub rejects files over normal Git limits. Use:

- GitHub Release assets for packaged binaries.
- Git LFS only when the repo is intended to support LFS.
- `.gitignore` for build output that should not be committed.

### Actions workflow fails

Use `$gh-actions-release-builder`.

```bash
gh run list --repo OWNER/REPO --limit 10
gh run view RUN_ID --repo OWNER/REPO --log-failed
```

Fix the workflow or project metadata, then push again. Do not claim build success until GitHub Actions passes.

### Pages deployment fails

Check:

- Pages source is set to GitHub Actions when using Pages actions.
- Workflow has `pages: write` and `id-token: write`.
- Build output path exists.
- Base path is correct for project pages.

### Release upload fails

Check:

- Tag exists or `gh release create` creates it.
- Asset path exists and is not empty.
- Use `--clobber` only when intentionally replacing an asset.
- For large files, prefer release assets over repository commits.

## Reporting Failures

Report:

- Exact failing command category, not raw secrets.
- Account and owner used.
- Remote URL without credentials.
- Whether API fallback was attempted.
- Next safest recovery path.
