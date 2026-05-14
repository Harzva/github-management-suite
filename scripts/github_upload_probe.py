#!/usr/bin/env python3
"""Cross-platform GitHub operations probe.

Checks local tools, GitHub connectivity, gh authentication, repository access,
optional Contents API writes, optional git push, optional release asset upload,
and optional SSH auth. It never prints token values.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import time
from pathlib import Path


TOKEN_RE = re.compile(r"(gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+|x-access-token:[^@\s]+)")


def redact(text: str) -> str:
    return TOKEN_RE.sub("[REDACTED_TOKEN]", text)


def run(cmd: list[str], cwd: str | None = None, timeout: int = 60) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        return proc.returncode, redact(proc.stdout.strip())
    except FileNotFoundError as exc:
        return 127, f"missing command: {exc.filename}"
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return 124, redact(f"timeout after {timeout}s\n{output}".strip())


def gh_args(args: argparse.Namespace, extra: list[str]) -> list[str]:
    if args.router:
        if not args.account:
            raise SystemExit("--account is required when --router is used")
        return [sys.executable, args.router, "--account", args.account, "--", *extra]
    return ["gh", *extra]


def tcp_tls(host: str, port: int = 443, timeout: int = 10) -> tuple[bool, str]:
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host):
                return True, "reachable"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def tcp_plain(host: str, port: int, timeout: int = 10) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "reachable"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def add(results: list[dict[str, object]], method: str, ok: bool, detail: str = "") -> None:
    results.append({"method": method, "ok": bool(ok), "detail": detail})


def has_ok(results: list[dict[str, object]], method: str) -> bool:
    return any(item["method"] == method and bool(item["ok"]) for item in results)


def write_json_temp(payload: dict[str, object]) -> str:
    handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".json")
    with handle:
        json.dump(payload, handle, separators=(",", ":"))
    return handle.name


def contents_probe(args: argparse.Namespace, results: list[dict[str, object]]) -> None:
    if not args.repo:
        add(results, "Contents API upload", False, "--repo is required")
        return
    stamp = time.strftime("%Y%m%d-%H%M%S")
    content = base64.b64encode(f"contents api ok {stamp}\n".encode("utf-8")).decode("ascii")
    body_path = write_json_temp({"message": f"Probe Contents API {stamp}", "content": content})
    try:
        code, output = run(
            gh_args(
                args,
                [
                    "api",
                    "-X",
                    "PUT",
                    f"repos/{args.repo}/contents/probes/contents-api-{stamp}.txt",
                    "--input",
                    body_path,
                ],
            ),
            timeout=args.timeout,
        )
        detail = f"probes/contents-api-{stamp}.txt" if code == 0 else output
        add(results, "Contents API upload", code == 0, detail)
    finally:
        Path(body_path).unlink(missing_ok=True)


def git_push_probe(args: argparse.Namespace, results: list[dict[str, object]]) -> None:
    if not args.repo:
        add(results, "HTTPS git push", False, "--repo is required")
        return
    git = shutil.which("git")
    if not git:
        add(results, "HTTPS git push", False, "git is missing")
        return

    stamp = time.strftime("%Y%m%d-%H%M%S")
    branch = f"probe/git-push-{stamp}"
    with tempfile.TemporaryDirectory(prefix="github-upload-probe-") as tmp:
        commands = [
            ([git, "init", "-b", "main"], None),
            ([git, "config", "user.name", "GitHub Probe"], None),
            ([git, "config", "user.email", "github-probe@example.invalid"], None),
        ]
        for cmd, _ in commands:
            code, output = run(cmd, cwd=tmp, timeout=args.timeout)
            if code != 0:
                add(results, "HTTPS git push", False, output)
                return

        Path(tmp, "git-push-probe.txt").write_text(f"git push ok {stamp}\n", encoding="utf-8")
        for cmd in ([git, "add", "git-push-probe.txt"], [git, "commit", "-m", f"Probe HTTPS git push {stamp}"]):
            code, output = run(cmd, cwd=tmp, timeout=args.timeout)
            if code != 0:
                add(results, "HTTPS git push", False, output)
                return

        remote = f"https://github.com/{args.repo}.git"
        code, output = run([git, "remote", "add", "origin", remote], cwd=tmp, timeout=args.timeout)
        if code != 0:
            add(results, "HTTPS git push", False, output)
            return

        if args.router and args.account:
            helper = f"!{sys.executable} {args.router} --account {args.account} --credential-helper"
            run([git, "config", "--local", "--unset-all", "credential.https://github.com.helper"], cwd=tmp, timeout=args.timeout)
            run([git, "config", "--local", "--add", "credential.https://github.com.helper", ""], cwd=tmp, timeout=args.timeout)
            run([git, "config", "--local", "--add", "credential.https://github.com.helper", helper], cwd=tmp, timeout=args.timeout)

        code, output = run(
            [git, "-c", "http.lowSpeedLimit=1", "-c", "http.lowSpeedTime=30", "push", "-u", "origin", f"HEAD:refs/heads/{branch}"],
            cwd=tmp,
            timeout=max(args.timeout, 90),
        )
        add(results, "HTTPS git push", code == 0, branch if code == 0 else output)


def release_probe(args: argparse.Namespace, results: list[dict[str, object]]) -> None:
    if not args.repo:
        add(results, "Release asset upload", False, "--repo is required")
        return
    stamp = time.strftime("%Y%m%d-%H%M%S")
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".txt") as handle:
        handle.write(f"release asset upload ok {stamp}\n")
        asset = handle.name
    try:
        code, output = run(
            gh_args(
                args,
                [
                    "release",
                    "create",
                    f"probe-{stamp}",
                    asset,
                    "--repo",
                    args.repo,
                    "--title",
                    f"Probe {stamp}",
                    "--notes",
                    "Temporary release asset upload probe.",
                    "--latest=false",
                ],
            ),
            timeout=max(args.timeout, 120),
        )
        add(results, "Release asset upload", code == 0, output)
    finally:
        Path(asset).unlink(missing_ok=True)


def ssh_probe(args: argparse.Namespace, results: list[dict[str, object]]) -> None:
    for host, port, label in (("github.com", 22, "SSH port 22"), ("ssh.github.com", 443, "SSH over 443")):
        ok, detail = tcp_plain(host, port, timeout=10)
        add(results, label, ok, detail)

    ssh = shutil.which("ssh")
    if not ssh:
        add(results, "SSH auth", False, "ssh command is missing")
        return
    code, output = run(
        [ssh, "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=10", "git@github.com"],
        timeout=20,
    )
    authenticated = "successfully authenticated" in output.lower()
    add(results, "SSH auth", authenticated, output or f"exit {code}")


def recommendation(results: list[dict[str, object]]) -> str:
    if has_ok(results, "HTTPS git push"):
        return "Use normal HTTPS git push for source publishing."
    if has_ok(results, "Contents API upload"):
        return "Use GitHub API fallback for uploads; Contents API writes are confirmed."
    if has_ok(results, "Release asset upload"):
        return "Use GitHub Releases for binary/package uploads; release asset upload is confirmed."
    if not has_ok(results, "network api.github.com:443"):
        return "GitHub API connectivity is not healthy. Fix connectivity or proxy before retrying API-based GitHub operations."
    if not has_ok(results, "gh auth"):
        return "GitHub CLI authentication is not ready. Run gh auth login or use the account router if available."
    if not has_ok(results, "network github.com:443") and has_ok(results, "network api.github.com:443"):
        return "GitHub API works but github.com web/git connectivity looks unstable. Prefer gh/API fallback before retrying git push."
    if has_ok(results, "repo view") or has_ok(results, "repo create"):
        return "Repository API access works. Use gh/API for repo management and diagnose git push separately."
    return "Authentication or repository access is incomplete. Verify owner, repo name, and token permissions."


def has_usable_path(args: argparse.Namespace, results: list[dict[str, object]]) -> bool:
    if not has_ok(results, "gh auth"):
        return False
    if args.repo and not (has_ok(results, "repo view") or has_ok(results, "repo create")):
        return False
    if args.write_probe and not has_ok(results, "Contents API upload"):
        return False
    if args.git_push_probe and not has_ok(results, "HTTPS git push"):
        return False
    if args.release_probe and not has_ok(results, "Release asset upload"):
        return False
    return has_ok(results, "network api.github.com:443") or has_ok(results, "network github.com:443")


def format_markdown(results: list[dict[str, object]]) -> str:
    lines = ["# GitHub Probe Result", "", "| Check | Result | Detail |", "| --- | --- | --- |"]
    for item in results:
        status = "PASS" if item["ok"] else "FAIL"
        detail = str(item.get("detail", "")).replace("\n", "<br>")
        lines.append(f"| {item['method']} | {status} | {detail} |")
    lines.extend(["", f"Recommendation: {recommendation(results)}"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Optional OWNER/REPO to test")
    parser.add_argument("--create-private", action="store_true", help="Create --repo as private if missing")
    parser.add_argument("--write-probe", action="store_true", help="Write a small probe file through Contents API")
    parser.add_argument("--git-push-probe", action="store_true", help="Push a temporary probe branch to --repo")
    parser.add_argument("--release-probe", action="store_true", help="Create a temporary probe release with one asset")
    parser.add_argument("--ssh-check", action="store_true", help="Check SSH reachability and GitHub SSH auth")
    parser.add_argument("--router", help="Optional gh-account-router.py path")
    parser.add_argument("--account", help="Account alias for --router, such as harzva or saihao")
    parser.add_argument("--timeout", type=int, default=60, help="Command timeout in seconds")
    parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Output format")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any individual check fails")
    args = parser.parse_args()

    results: list[dict[str, object]] = []

    add(results, "python", True, sys.version.split()[0])
    add(results, "git command", shutil.which("git") is not None, shutil.which("git") or "missing")
    add(results, "gh command", shutil.which("gh") is not None or bool(args.router), shutil.which("gh") or args.router or "missing")

    for host in ("github.com", "api.github.com"):
        ok, detail = tcp_tls(host)
        add(results, f"network {host}:443", ok, detail)

    code, output = run(gh_args(args, ["api", "user", "--jq", ".login"]), timeout=args.timeout)
    add(results, "gh auth", code == 0, output)

    if args.repo:
        code, output = run(gh_args(args, ["repo", "view", args.repo, "--json", "nameWithOwner,url,visibility"]), timeout=args.timeout)
        if code == 0:
            add(results, "repo view", True, output)
        elif args.create_private:
            code, output = run(
                gh_args(args, ["repo", "create", args.repo, "--private", "--description", "Probe repository for GitHub upload method testing"]),
                timeout=max(args.timeout, 120),
            )
            add(results, "repo create", code == 0, output)
        else:
            add(results, "repo view", False, output)

    if args.write_probe:
        contents_probe(args, results)
    if args.git_push_probe:
        git_push_probe(args, results)
    if args.release_probe:
        release_probe(args, results)
    if args.ssh_check:
        ssh_probe(args, results)

    payload = {"results": results, "recommendation": recommendation(results)}
    if args.format == "markdown":
        print(format_markdown(results))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    if args.strict:
        required = [item for item in results if item["method"] not in {"repo view"}]
        return 0 if all(bool(item["ok"]) for item in required) else 1
    return 0 if has_usable_path(args, results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
