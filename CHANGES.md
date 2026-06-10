# Changes

## 2026-06-10

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
- Added `make check` as the local verification entry point for this Objective-C iOS sample.
