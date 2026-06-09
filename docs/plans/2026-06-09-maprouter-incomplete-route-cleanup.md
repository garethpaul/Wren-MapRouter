# MapRouter Incomplete Route Cleanup

status: completed

## Context

Directions requests can fail to produce a source or destination coordinate even
when neither endpoint is waiting for Current Location. In that case there is no
future location callback that can complete the route, so keeping partial route
state around risks stale forwarding behavior on later lifecycle events.

## Completed Scope

- Added an early incomplete-route branch before endpoint encoding.
- Preserved pending routes that still depend on Current Location callbacks.
- Cleared pending route state when a non-location route is incomplete.
- Extended the static contract checker to keep this cleanup before external
  URL construction.
- Updated README, VISION, and CHANGES with the cleanup guardrail.

## Verification

- `make check`
- `git diff --check`
