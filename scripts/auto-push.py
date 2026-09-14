#!/usr/bin/env python3
"""Opt-in safe GitHub auto-push for Processor development checkouts."""
from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / ".runtime" / "logs" / "auto-push.log"
LOCK = ROOT / ".runtime" / "auto-push.lock"
DENY = (".env", "credentials", ".runtime/", "data/", "logs/", "secrets/", ".venv/", "node_modules/", "media/")


def log(message: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"{datetime.now(timezone.utc).isoformat()} {message}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)


def allowed(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    return not any(normalized == item or normalized.startswith(item) or item in normalized for item in DENY)


def main() -> int:
    if os.getenv("ROOTRECORD_AUTO_PUSH", "0").lower() not in {"1", "true", "yes", "on"}:
        log("disabled; set ROOTRECORD_AUTO_PUSH=1 to enable")
        return 0
    if LOCK.exists():
        log("busy lock; skipping")
        return 0
    LOCK.write_text(str(os.getpid()), encoding="ascii")
    try:
        status = git("status", "--porcelain")
        if status.returncode:
            return 1
        git("add", "-u")
        for line in status.stdout.splitlines():
            if len(line) >= 3 and line[:2] == "??" and allowed(line[3:].strip()):
                git("add", "--", line[3:].strip())
        names = git("diff", "--cached", "--name-only").stdout.splitlines()
        denied = [x for x in names if not allowed(x)]
        if denied:
            git("restore", "--staged", "--", *denied)
        if git("diff", "--cached", "--quiet").returncode == 0:
            log("clean")
            return 0
        env = os.environ.copy()
        env.update({"GIT_AUTHOR_NAME": "Ava-Core-Dev", "GIT_AUTHOR_EMAIL": "ava-core-dev@users.noreply.github.com", "GIT_COMMITTER_NAME": "Ava-Core-Dev", "GIT_COMMITTER_EMAIL": "ava-core-dev@users.noreply.github.com"})
        commit = subprocess.run(["git", "commit", "-m", f"auto: sync {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}"], cwd=ROOT, env=env, text=True, capture_output=True)
        if commit.returncode:
            log("commit failed")
            return commit.returncode
        push = git("push", "origin", "HEAD")
        log("pushed" if push.returncode == 0 else "push failed")
        return push.returncode
    finally:
        LOCK.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
