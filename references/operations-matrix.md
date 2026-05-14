# Operations Matrix

Use this matrix to pick the right GitHub path quickly.

| Goal | Preferred Tool | Fallback | Verify |
| --- | --- | --- | --- |
| Clone repo | `git clone https://github.com/OWNER/REPO.git` | Download archive | `git remote -v` |
| Pull updates | `git pull --ff-only` | `git fetch` then inspect | `git status --short --branch` |
| Create repo | `$gh-account-router` or `gh repo create` | GitHub REST API | `gh repo view OWNER/REPO` |
| Push source | `git push` over clean HTTPS remote | Git Data API commit | `git ls-remote --heads origin` |
| Upload one file | Contents API | `gh repo edit` or web UI | `gh api repos/OWNER/REPO/contents/PATH` |
| Upload binary | `gh release upload` | Actions artifact | `gh release view TAG` |
| Open issue | `gh issue create` | GitHub web/API | `gh issue view ID` |
| Open PR | `gh pr create` | Push branch and web PR | `gh pr checks` |
| Add CI/build | `$gh-actions-release-builder` | Manual workflow YAML | `gh run list` |
| Publish Pages | Pages Actions workflow | `docs/` branch/source settings | Pages deployment status |
| Polish README | `$readme-design` | Manual README checklist | GitHub rendered preview |
| Diagnose failure | `scripts/github_upload_probe.py` | Manual network/auth checks | JSON or markdown probe report |

## Default Upload Strategy

1. Try normal HTTPS `git push`.
2. If account identity is ambiguous and `$gh-account-router` exists, bind a repo-local credential helper and retry.
3. If push fails from network or permission mismatch, create or verify the repo through `gh`.
4. Use Contents API for tiny changes.
5. Use Git Data API for multi-file source commits.
6. Use Releases for archives, installers, APKs, EXEs, or other binaries.

## Do Not

- Do not put credentials in remote URLs.
- Do not commit generated build folders unless the repository intentionally tracks static output.
- Do not bypass branch protection unless explicitly asked and permitted.
- Do not claim CI, Pages, or Releases exist until verified.
