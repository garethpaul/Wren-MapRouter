# MapRouter Transient Location Samples

Status: Completed

## Problem

`didUpdateLocations:` already ignores stale or future-dated samples while
waiting for a usable Current Location coordinate. Missing samples, invalid
coordinates, and negative horizontal accuracy instead clear the pending route
and stop updates immediately. Those sample-level failures are transient in the
same way as stale data: a later delegate update can still complete the route.

## Requirements

1. Ignore missing, invalid-coordinate, and negative-accuracy location samples
   without clearing route endpoints or stopping location updates.
2. Continue ignoring stale and future-dated samples under the existing
   sixty-second freshness boundary.
3. Keep terminal cleanup for denied/restricted authorization, non-transient
   delegate errors, background entry, encoding failures, and incomplete routes.
4. Preserve coordinate validation before assignment and route forwarding.
5. Add portable ordering contracts and hostile mutations for transient sample
   handling and retained terminal cleanup.

## Verification

- Run focused transient-sample contracts and hostile mutations.
- Run local and external-working-directory `make check` under explicit timeouts.
- Compile the Python checker and inspect exact paths, artifacts, credentials,
  conflict markers, and whitespace.
- Record the unavailable Linux `xcodebuild` boundary without claiming simulator
  or physical-device validation.

## Scope Boundaries

- Do not persist route/location data, change freshness or accuracy thresholds,
  alter authorization prompts, or modify Google Maps URL construction.
- Do not merge or close any pull request without explicit owner authorization.

## Verification Results

- Before this status update, the dependency-free checker passed all source and
  documentation contracts and stopped only at the plan-completion requirement.
- Local and external-working-directory `timeout 180s make check` passed the
  portable contracts and explicitly skipped unavailable `xcodebuild`.
- Eight isolated hostile mutations were rejected for premature cleanup,
  missing or late return, missing coordinate or accuracy validation, removed
  background or terminal delegate cleanup, and stale plan status.
