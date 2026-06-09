# Changes

## 2026-06-09

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
