# GitHub Management Suite

> A Codex skill for smooth GitHub repository operations: sync, publish, issues, PRs, Actions, Releases, Pages, README polish, and upload recovery.

[![Skill](https://img.shields.io/badge/Codex-skill-blue)](./SKILL.md)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)](./scripts/github_upload_probe.py)
[![GitHub](https://img.shields.io/badge/GitHub-operations-181717)](https://github.com/Harzva/github-management-suite)

## What It Does

`github-management-suite` is the top-level GitHub workflow skill for Codex. It helps an agent decide how to safely operate a repository across:

| Area | Covered |
| --- | --- |
| Source sync | clone, fetch, pull, branch, commit, push |
| Repository setup | remotes, owner/account checks, repository creation |
| Collaboration | issues, pull requests, review checks |
| Automation | GitHub Actions, CI, build artifacts, Pages workflows |
| Delivery | Releases, release assets, versioned artifacts |
| Presentation | README optimization with `$readme-design` |
| Recovery | push failures, auth mismatches, API fallback, SSH checks |

## Recommended Companion Skills

- `$gh-account-router` for owner/account/token routing.
- `$gh-actions-release-builder` for professional Actions workflows.
- `$readme-design` for public repository presentation.
- `$software-dev-pipeline` for product release quality gates.

The suite still works without those helpers by falling back to plain `git`, `gh`, and GitHub API workflows.

## Quick Start

Use the skill in Codex:

```text
Use $github-management-suite to publish this repo to GitHub, optimize the README, add Actions release automation, and recover safely if push fails.
```

Run the portable probe:

```bash
python scripts/github_upload_probe.py --repo OWNER/REPO
```

With a write probe, only for repositories you own:

```bash
python scripts/github_upload_probe.py --repo OWNER/REPO --write-probe
```

## Skill Layout

```text
github-management-suite/
  SKILL.md
  agents/openai.yaml
  references/
    lifecycle-playbook.md
    failure-recovery.md
    operations-matrix.md
    subscriber-onboarding.md
  scripts/
    github_upload_probe.py
```

## When To Use

- "Push this project to GitHub."
- "Create the repository and publish it under the right account."
- "Fix why GitHub push keeps failing."
- "Add Actions build/release workflow."
- "Upload APK/EXE/ZIP to GitHub Release."
- "Deploy this site to GitHub Pages."
- "Make the README look professional before publishing."
- "Triage issues and prepare a PR."

## Safety Defaults

- Keep remotes credential-free.
- Do not print or commit tokens.
- Prefer HTTPS remotes and `gh` API fallback.
- Use GitHub Actions for builds when local build environments are unavailable.
- Verify remote state before claiming success.

## Distribution Note

No license file is declared yet. Add one before treating the repository as broadly reusable open source.
