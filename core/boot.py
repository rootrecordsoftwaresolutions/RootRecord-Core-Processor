#!/usr/bin/env python3
"""Self-checking RootRecord Processor bootstrap.

OS packages are installed by install.sh; this entrypoint verifies persistent
paths and installs application dependencies when manifests change.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"
LOG_DIR = RUNTIME / "logs"
LOG_FILE = LOG_DIR / "boot.log"


def log(message: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = f"[RootRecord Processor] {message}"
    print(line, flush=True)
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def run(command: list[str]) -> None:
    log("RUN " + " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def fingerprint(*paths: Path) -> str:
    digest = hashlib.sha256()
    for path in paths:
        if path.is_file():
            digest.update(str(path.relative_to(ROOT)).encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def ensure_dependencies() -> None:
    for command in ("git", "ffmpeg", "sqlite3"):
        if not shutil.which(command):
            log(f"WARNING missing dependency: {command}; run install.sh")
    pyproject = ROOT / "pyproject.toml"
    if pyproject.is_file():
        python = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        if not python.exists():
            log("Creating Python virtual environment")
            run([sys.executable, "-m", "venv", str(python.parent.parent)])
        marker = RUNTIME / "python-dependencies.sha256"
        current = fingerprint(pyproject)
        needs_install = not marker.exists() or marker.read_text().strip() != current
        if needs_install:
            run([str(python), "-m", "pip", "install", "--upgrade", "pip", "wheel"])
            run([str(python), "-m", "pip", "install", "-e", str(ROOT)])
            marker.write_text(current, encoding="utf-8")


def main() -> int:
    log("BOOT_START")
    for directory in (RUNTIME, RUNTIME / "data", RUNTIME / "data/db", RUNTIME / "config", RUNTIME / "logs", RUNTIME / "secrets", ROOT / "media"):
        directory.mkdir(parents=True, exist_ok=True)
        log(f"READY {directory.relative_to(ROOT)}")
    ensure_dependencies()
    log("BOOT_COMPLETE")
    log(f"Log file: {LOG_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
