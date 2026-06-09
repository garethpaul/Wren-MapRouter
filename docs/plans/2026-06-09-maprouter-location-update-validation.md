# MapRouter Location Update Validation

## Status: Completed

## Context

The route handler waits for CoreLocation updates when a directions endpoint uses
Current Location. `didUpdateLocations` stored the latest location without first
checking whether the callback supplied a location or a valid coordinate. If the
latest update was missing or invalid, pending route state could remain active
until another lifecycle or location event cleared it.

## Objectives

- Preserve current-location route forwarding for valid updates.
- Reject empty or invalid CoreLocation updates before storing them.
- Clear pending route and location state when an update cannot satisfy the
  current route.
- Extend static checker coverage for location update validation.

## Work Completed

- Added a guarded `latestLocation` local in `didUpdateLocations`.
- Cleared pending route state and returned when no location or invalid
  coordinates are supplied.
- Stored the latest location only after validation.
- Extended `scripts/check_wren_maprouter_contracts.py`.
- Updated README, VISION, and CHANGES.

## Verification

- Pre-change inspection found direct storage of `[locations lastObject]`.
- `python3 scripts/check_wren_maprouter_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add simulator/device notes for invalid-location and location-denied paths.
- Decide whether the sample is archived or should target modern Maps APIs.
