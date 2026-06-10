# MapRouter Location Freshness

Status: Completed

## Context

CoreLocation may deliver a cached coordinate immediately after location updates
start. The router accepted the first valid coordinate without checking its
timestamp, so an old location could be forwarded as the route endpoint.

## Changes

- Ignore future-dated location samples.
- Ignore cached samples older than 60 seconds while waiting for a fresh update.
- Keep pending route state active until a fresh coordinate arrives or location
  delivery fails.
- Pin hosted verification to Ubuntu 24.04 with superseded-run cancellation.
- Make static checks and the optional Xcode project build root-independent.

## Verification

- `make check`
- Root-independent `make test`
- Mutation checks for freshness, CI, project paths, and plan completion
- `git diff --check`
