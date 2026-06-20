# MapRouter Transient Location Errors

Status: Completed

## Context

The route handler clears all pending route and location state whenever Core
Location calls `locationManager:didFailWithError:`. Apple documents
`kCLErrorLocationUnknown` as a temporary inability to produce a location and
states that Core Location keeps trying. Clearing the route for that error
silently abandons an otherwise valid Current Location directions request before
a later coordinate can complete it.

## Requirements

- **R1:** Preserve the pending route and active location update session when
  the delegate receives `kCLErrorLocationUnknown`.
- **R2:** Continue clearing pending route, cached location, and active updates
  for terminal or unsupported Core Location errors.
- **R3:** Keep denied and restricted authorization cleanup unchanged.
- **R4:** Preserve existing valid-coordinate, freshness, accuracy, route
  encoding, and external URL allowlist behavior.
- **R5:** Make the transient-error ordering and completed verification part of
  the dependency-free repository contract.

## Implementation Units

### U1: Classify Delegate Failures

**Files:** `GoogleTransit/AppDelegate.m`

Add an explicit `kCLErrorLocationUnknown` branch before route cleanup. The
branch returns without changing route endpoints, current-location dependency
flags, cached location, or the running location manager. All other errors keep
the existing cleanup path.

### U2: Enforce The Reliability Contract

**Files:** `scripts/check_wren_maprouter_contracts.py`

Require the transient error check and verify its return occurs before
`clearPendingRoute`. Require the terminal cleanup to remain reachable after
that branch. Add the plan to the canonical completed-plan inventory.

### U3: Document And Verify The Boundary

**Files:** `README.md`, `docs/plans/2026-06-13-maprouter-transient-location-errors.md`

Document that temporary location acquisition failures keep waiting while other
delegate failures cancel the pending route. Record focused mutation evidence,
the full portable gate, and the unavailable Xcode boundary after execution.

## Test Scenarios

- Removing the `kCLErrorLocationUnknown` check fails the static contract.
- Moving cleanup before the transient-error return fails the ordering contract.
- Returning for every Core Location error fails the terminal-cleanup contract.
- Removing the plan from the canonical inventory fails the plan contract.
- `make check` continues to pass all existing route, location, workflow, and
  documentation contracts.

## Scope Boundaries

- Do not persist location or route data.
- Do not change authorization prompts, route formats, Google Maps endpoints,
  deployment targets, or Xcode project settings.
- Do not claim simulator or device behavior was exercised without a compatible
  macOS/Xcode environment.

## Verification

- `make check` passed the full portable contract suite and truthfully reported
  that `xcodebuild` is unavailable on this Linux host.
- External-directory `make -f <repo>/Makefile check` passed, proving the rooted
  checker and optional project paths remain caller-directory independent.
- Four hostile mutations were rejected: removing the transient branch,
  cleaning up before its return, ignoring non-transient errors, and removing
  the canonical completed plan.
- Python compilation, workflow YAML parsing, focused source-order assertions,
  and `git diff --check` passed.
- Simulator and device behavior still requires a compatible macOS/Xcode
  environment and was not claimed here.

## Source

- Apple, `locationManager:didFailWithError:`:
  https://developer.apple.com/documentation/corelocation/cllocationmanagerdelegate/locationmanager%28_%3Adidfailwitherror%3A%29?language=objc
