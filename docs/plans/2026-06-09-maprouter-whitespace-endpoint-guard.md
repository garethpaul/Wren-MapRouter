# MapRouter Whitespace Endpoint Guard

## Status: Completed

## Context

Route endpoint encoding rejected nil and empty strings before building the
Google Maps forwarding URL, but a whitespace-only endpoint still had a nonzero
length and could be percent encoded. That would create an external route URL
with an endpoint that carried no useful coordinate or route value.

## Objectives

- Preserve existing route parsing and Google Maps forwarding behavior.
- Trim whitespace and newlines from route endpoints before validation.
- Reject whitespace-only endpoints before percent encoding.
- Percent encode the trimmed endpoint value.
- Cover endpoint normalization in dependency-free static checks.

## Work Completed

- Added whitespace/newline trimming inside `encodedRouteEndpoint:`.
- Updated the empty endpoint guard to validate the trimmed endpoint.
- Updated percent encoding to use the trimmed endpoint value.
- Added static checker coverage for route endpoint normalization.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_wren_maprouter_contracts.py`
- `make check`
- `git diff --check`
