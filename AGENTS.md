# Repository Guidance: RootRecord Core Processor

This repository is the RootRecord hosted processor. It has no license and is public for transparency only.

## Scope

- Put hosted FastAPI services, schedulers, ingestion, AI/API integrations, media processing, radio encoding, installers, and systemd units here.
- GitHub is the source of deployable code; the server pulls read-only and fast-forward-only.
- Runtime data, credentials, logs, and media remain outside the Git checkout.

## Boundaries

- RootMC development belongs only in `RootRecord-RootMC`.
- Self-hostable public software belongs in `RootRecord-Core-Node`.
- Laptop controls, OBS operation, and local backup/restore belong in `RootRecord-Core-Ops`.

## Safety

Never commit secrets, private keys, database files, runtime media, or production dumps. Do not make deployment pullers push, stash, reset, or overwrite dirty state.
