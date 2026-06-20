# MapRouter Background Route Cleanup

Status: Completed

## Context

`applicationWillResignActive:` currently clears pending Current Location route
state for every temporary inactive transition. Interruptions that do not move
the app into the background can therefore abandon a valid route while Core
Location is still resolving it.

## Requirements

- Preserve pending route and location-update state when the app only resigns
  active.
- Clear pending route state when the app actually enters the background.
- Keep launch, activation, authorization, location validation, route encoding,
  external URL allowlisting, and terminal cleanup behavior unchanged.
- Add lifecycle-scoped static ordering contracts and hostile mutation coverage.

## Verification Completed

- The portable checker and repository-local and external-directory
  `make check` invocations passed.
- Python checker compilation and `git diff --check` passed.
- Six isolated hostile mutations were rejected: restored resign-active cleanup,
  missing or duplicate background cleanup, late background cleanup, missing
  canonical plan, and stale plan status.
- Exact-base path, generated-artifact, and added-line secret-pattern scans
  passed without vendored, project, lockfile, or workflow changes.
- Both Make runs reported `xcodebuild` unavailable on this Linux host, so no
  simulator, device, or current-SDK behavior is claimed.
