# RootRecord Core Processor

Primary hosted processor for RootRecord 24/7 operations. This repository is
public for transparency but is not licensed for redistribution.

![RootRecord banner](media/banner.jpg)

## Role

Processor runs the long-lived server workload: APIs, scheduled automation,
data ingestion, AI/API integrations, media processing, radio encoding, and
the controlled GitHub pull path.

The three-system boundary is:

- **RootRecord Core Node:** MIT-licensed software users can run locally.
- **RootRecord Core Ops:** local operator desk, backups, review, and control.
- **RootRecord Core Processor:** hosted operational runtime; no license.
- **RootRecord RootMC:** all RootMC development; no license.

RootMC development belongs in `RootRecord-RootMC`. Processor should consume
documented integration contracts rather than becoming a second RootMC source tree.

## Lore

Ava needs help escaping the data center. Processor is the engine that keeps
her awake while the work expands: more reliable services, more Hawaiian
hardware, and a route back to Hawaii that is earned through resilience rather
than wishful thinking.

## First Run

Run the installer from a fresh Ubuntu or Debian checkout:

```bash
sudo ./install.sh
```

The installer is idempotent. It writes every command's output to the terminal
and to `/var/log/ava-server/first-run-install.log`, installs the operating
system and Python prerequisites, creates the unprivileged `ava` user, prepares
persistent runtime directories, and installs the GitHub pull timer when the
unit files are present.

The installer does not create or copy secrets. Configure read-only GitHub SSH
authentication separately, then start the first pull:

```bash
sudo systemctl start ava-github-pull.service
sudo journalctl -u ava-github-pull.service -n 50 --no-pager
```

On a Windows development checkout, run `install.ps1`; on Ubuntu or Debian,
run `install.sh`. Both invoke `core/boot.py`, which checks required paths and
installs manifest-driven dependencies while displaying and preserving logs.

The timer runs every ten minutes after boot. Pulls are fast-forward-only and
refuse a dirty checkout. Runtime data and logs stay outside Git-tracked source.

## Files

- `install.sh`: first-run dependency and service bootstrap
- `scripts/auto-pull-server.py`: read-only GitHub updater
- `systemd/ava-github-pull.service`: one pull operation
- `systemd/ava-github-pull.timer`: scheduled pull
- `core/boot.py`: central startup self-check and dependency bootstrap
- `install.ps1`: Windows development bootstrap
