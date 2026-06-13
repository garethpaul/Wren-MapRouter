# MapRouter Background Route Cleanup

Status: Planned

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

## Verification Plan

- Run the portable checker and `make check` from the repository and an external
  working directory.
- Compile the Python checker and run `git diff --check`.
- Reject mutations that restore resign-active cleanup, remove background
  cleanup, misorder the lifecycle methods, omit the canonical plan, or leave
  stale plan status.
- Audit the exact diff for generated artifacts, vendored/project/workflow
  changes, and credential-like additions.
- Do not claim simulator, device, or current-SDK behavior when `xcodebuild` is
  unavailable.
