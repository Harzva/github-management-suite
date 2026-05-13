#!/usr/bin/env python3
"""Cross-platform GitHub upload probe.

Checks network reachability, gh authentication, optional repository access,
and optional Contents API upload. It never prints token values.
"""

from __future__ import annotations

import argparse
import base64
import json
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def run(cmd: list[str], timeout: int = 60) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout.strip()


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


def add(results: list[dict[str, object]], method: str, ok: bool, detail: str = "") -> None:
    results.append({"method": method, "ok": ok, "detail": detail})


def write_json_temp(payload: dict[str, object]) -> str:
    handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".json")
    with handle:
        json.dump(payload, handle, separators=(",", ":"))
    return handle.name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Optional OWNER/REPO to test")
    parser.add_argument("--create-private", action="store_true", help="Create --repo as private if missing")
    parser.add_argument("--write-probe", action="store_true", help="Write a small probe file through Contents API")
    parser.add_argument("--router", help="Optional gh-account-router.py path")
    parser.add_argument("--account", help="Account alias for --router, such as harzva or saihao")
    args = parser.parse_args()

    results: list[dict[str, object]] = []

    add(results, "python", True, sys.version.split()[0])
    add(results, "git command", shutil.which("git") is not None, shutil.which("git") or "missing")
    add(results, "gh command", shutil.which("gh") is not None or bool(args.router), shutil.which("gh") or args.router or "missing")

    for host in ("github.com", "api.github.com"):
        ok, detail = tcp_tls(host)
        add(results, f"network {host}:443", ok, detail)

    code, output = run(gh_args(args, ["api", "user", "--jq", ".login"]))
    add(results, "gh auth", code == 0, output)

    if args.repo:
        code, output = run(gh_args(args, ["repo", "view", args.repo, "--json", "nameWithOwner,url,visibility"]))
        if code == 0:
            add(results, "repo view", True, output)
        elif args.create_private:
            code, output = run(
                gh_args(
                    args,
                    [
                        "repo",
                        "create",
                        args.repo,
                        "--private",
                        "--description",
                        "Probe repository for GitHub upload method testing",
                    ],
                ),
                timeout=120,
            )
            add(results, "repo create", code == 0, output)
        else:
            add(results, "repo view", False, output)

        if args.write_probe:
            stamp = time.strftime("%Y%m%d-%H%M%S")
            content = base64.b64encode(f"contents api ok {stamp}\n".encode("utf-8")).decode("ascii")
            body_path = write_json_temp(
                {
                    "message": f"Probe Contents API {stamp}",
                    "content": content,
                }
            )
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
                    timeout=120,
                )
                add(results, "Contents API upload", code == 0, f"probes/contents-api-{stamp}.txt" if code == 0 else output)
            finally:
                Path(body_path).unlink(missing_ok=True)

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if all(item["ok"] for item in results if item["method"] != "repo view") else 1


if __name__ == "__main__":
    raise SystemExit(main())
