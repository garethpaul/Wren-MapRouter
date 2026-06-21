# Changes

## 2026-06-21

- Isolated repository verification from later single-colon recipe replacement,
  unsafe modes, unsafe Make syntax, and caller-selected cleanup paths while
  documenting target-specific override shells, startup parse-time code, and
  default PATH-selected Python as caller authority.
- Contained Xcode derived-data cleanup beneath the checkout and added a
  regression harness proving hostile caller paths are never removed.
- Aligned local and hosted verification on the trusted `/usr/bin/make`
  authority while preserving the native simulator destination override.

## 2026-06-19

- Added native XCTest coverage for finite, fresh, bounded-accuracy location
  selection and for mixed valid/invalid callback batches.
- Prevented late callbacks from retaining a coordinate after route cancellation,
  reset previous location work before route replacement, and adopted modern
  authorization and URL-opening APIs.
- Raised the archived project to iOS 13, restored current-Xcode launch/build
  compatibility, and documented Google Maps route-coordinate disclosure.

## 2026-06-13

- Preserved pending Current Location routes when Core Location emits a missing,
  invalid-coordinate, or negative-accuracy sample while awaiting later data.

## 2026-06-12

- Disabled persisted checkout credentials and enforced the sole pinned
  credential-free workflow boundary.

## 2026-06-10

- Rejected Core Location objects with negative horizontal accuracy before
  route endpoint conversion or live-location storage, with cleanup and static
  regression coverage.
- Added immutable, read-only GitHub Actions verification on Python 3.10, 3.12,
  and 3.14 for location, route normalization, and external forwarding
  contracts, with manual dispatch for maintenance runs.
- Added static protection for workflow permissions, action revisions, matrix
  versions, timeout, and the `make check` entry point.
- Documented that hosted Linux checks intentionally skip the legacy Xcode build.
- Rejected future-dated and older-than-60-second CoreLocation samples before
  using current location in an external route.
- Pinned hosted verification to Ubuntu 24.04 with superseded-run cancellation
  and made static and optional Xcode checks root-independent.

## 2026-06-09

- Trimmed route endpoints before empty checks and percent encoding so
  whitespace-only values cannot be forwarded.
- Added static checker coverage for endpoint whitespace normalization.
- Rejected empty route endpoints before percent encoding and external Google
  Maps URL construction.
- Added static checker coverage for empty route endpoint rejection.
- Cleared pending route state when CoreLocation returns no location or an
  invalid coordinate update.
- Added static checker coverage for location update validation.
- Cleared pending route state when a non-location directions request is missing
  either endpoint.
- Added static checker coverage for incomplete route cleanup before external
  URL construction.
- Escaped URL query delimiters when encoding route endpoints for Google Maps
  forwarding.
- Added static checker coverage for delimiter-safe route endpoint encoding.
- Cleared pending route state when route endpoint encoding fails before
  external forwarding.
- Added static checker coverage for encoding-failure cleanup.
- Restricted external Google Maps forwarding to the expected `/maps` route
  path in addition to HTTPS host allowlisting.
- Added static checker coverage for the external URL path allowlist.
- Encoded route source and destination endpoint strings before formatting the
  Google Maps forwarding URL.
- Added static checker coverage for route endpoint URL encoding.

## 2026-06-08

- Restricted external forwarding to HTTPS Google Maps URLs before calling
  `openURL`.
- Limited declared Maps directions modes to transit-compatible route types.
- Added docs-plan coverage to the static MapRouter contract checker.
- Added static contracts for the legacy MapKit directions handler, location permission metadata, and bundled GeoJSON artifact.
- Hardened current-location route handling so unresolved or denied location access clears pending route state.
- Preserved pending Current Location routes during temporary inactive states
  while retaining cleanup when the app enters the background.
- Added `make check` as the local verification entry point for this Objective-C iOS sample.
