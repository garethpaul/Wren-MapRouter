# MapRouter Encoding Failure Cleanup

## Status: Completed

## Context

Route endpoint values are encoded before formatting the external Google Maps
URL. If encoding returned `nil`, `openTransitDirections` returned immediately
without clearing pending route or current-location state, leaving stale route
data in memory until another lifecycle event cleared it.

## Objectives

- Preserve the existing MapKit directions parsing and forwarding behavior.
- Continue returning before forwarding when endpoint encoding fails.
- Clear pending route and current-location state on encoding failure.
- Keep external URL allowlist and route endpoint encoding checks intact.

## Work Completed

- Added `clearPendingRoute` before returning from the endpoint-encoding failure
  path.
- Extended the static contract checker to require cleanup on encoding failure.
- Added completed-plan coverage for the cleanup contract.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_wren_maprouter_contracts.py`
- `python3 -m py_compile scripts/check_wren_maprouter_contracts.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `make verify`
- `git diff --check`

On this workspace, `make build`, `make check`, and `make verify` reported
`xcodebuild unavailable; skipping legacy iOS build`.

## Follow-Up Candidates

- Add README setup notes and expected route behavior.
- Decide whether the sample is archived or should target modern Maps APIs.
