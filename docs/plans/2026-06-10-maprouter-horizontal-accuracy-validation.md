# MapRouter Horizontal Accuracy Validation

Status: Completed

## Goal

Avoid forwarding a current-location route when Core Location has explicitly
marked the latitude and longitude as invalid.

## Scope

- Reject any `CLLocation` with negative `horizontalAccuracy` before converting
  it into a route endpoint.
- Treat negative-accuracy live updates like missing or invalid coordinates.
- Clear the pending route before a rejected live update can be stored.
- Enforce both conversion-time and update-time guards in portable contracts.

## Verification

- `make check`
- Mutation check: removing the live-update accuracy condition causes the
  contract checker to fail.
- Xcode build skipped locally because `xcodebuild` is unavailable; hosted
  Linux verification intentionally exercises the portable contracts.

## Outcome

Numerically plausible coordinates are no longer accepted when Core Location's
accuracy metadata says they are invalid. Pending state is cleared instead of
forwarding an untrustworthy source or destination to Google Maps.
