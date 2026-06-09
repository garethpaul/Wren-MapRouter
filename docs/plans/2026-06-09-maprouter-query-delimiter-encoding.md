# MapRouter Query Delimiter Encoding

## Status: Completed

## Context

The route handler encoded endpoint strings before formatting the Google Maps
forwarding URL, but the legacy `stringByAddingPercentEscapesUsingEncoding` call
did not make the set of escaped query delimiters explicit. Route endpoints are
currently coordinate strings, yet the helper is the boundary that protects
future endpoint changes from injecting additional query parameters.

## Objectives

- Preserve the iOS 6 deployment target and existing Google Maps forwarding URL.
- Escape URL query delimiters before inserting endpoint values into the query
  string.
- Keep the endpoint-encoding failure cleanup behavior intact.
- Keep ARC ownership explicit for the CoreFoundation encoding result.
- Extend static checker coverage for the delimiter-safe encoding contract.

## Work Completed

- Replaced the endpoint encoder with `CFURLCreateStringByAddingPercentEscapes`.
- Added the reserved URL delimiter set to the encoder so query separators are
  escaped before external forwarding.
- Returned the encoded CoreFoundation string with `CFBridgingRelease`.
- Extended `scripts/check_wren_maprouter_contracts.py`.
- Updated README, VISION, and CHANGES.

## Verification

- Negative check: `python3 scripts/check_wren_maprouter_contracts.py` failed
  before the delimiter-safe encoder was added.
- `python3 scripts/check_wren_maprouter_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add simulator notes for Maps directions handoff behavior.
- Decide whether the sample is archived or should target modern Maps APIs.
