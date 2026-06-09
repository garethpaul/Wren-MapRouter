# MapRouter Empty Endpoint Guard

## Status: Completed

## Context

Route endpoint encoding rejected nil endpoints and escaped query delimiters, but
it still allowed empty strings through percent encoding. An empty source or
destination can produce a malformed Google Maps forwarding URL, so empty
endpoints should fail the same way as missing endpoints.

## Objectives

- Preserve existing route endpoint encoding behavior for non-empty endpoints.
- Reject nil and empty route endpoint strings before URL construction.
- Keep route cleanup on endpoint encoding failure.
- Cover the guard in dependency-free static checks.

## Work Completed

- Added an empty-string guard to `encodedRouteEndpoint`.
- Extended the static checker to require empty endpoint rejection before percent
  encoding.
- Updated README, SECURITY, VISION, and CHANGES.

## Verification

- `python3 scripts/check_wren_maprouter_contracts.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
