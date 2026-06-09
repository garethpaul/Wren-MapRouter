# MapRouter Route Endpoint Encoding

## Status: Completed

## Context

The route handler already validates current-location coordinates and restricts
external forwarding to HTTPS Google Maps URLs. The Google Maps query string was
still formatted directly from route endpoint strings, leaving URL encoding as an
implicit assumption.

## Objectives

- Preserve MapKit directions URL handling and Google Maps forwarding.
- Encode route endpoint values before inserting them into the external URL.
- Avoid forwarding when an endpoint cannot be encoded.
- Keep route cleanup and external URL allowlist behavior intact.
- Extend static checks for the encoding contract.

## Work Completed

- Added `encodedRouteEndpoint:` for route query values.
- Encoded current source and destination before formatting the Google Maps URL.
- Returned before forwarding when endpoint encoding fails.
- Added static checker coverage for encoded route URL construction.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_wren_maprouter_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add README setup notes and expected route behavior.
- Decide whether the sample is archived or should target modern Maps APIs.
