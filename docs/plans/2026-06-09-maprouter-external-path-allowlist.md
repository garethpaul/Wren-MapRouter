# MapRouter External Path Allowlist

## Status: Completed

## Context

External forwarding was restricted to HTTPS `maps.google.com` URLs before
calling `openURL`, but the allowlist did not check the URL path. The app only
constructs Google Maps route URLs under `/maps`, so the allowlist should encode
that routing assumption explicitly.

## Objectives

- Preserve the existing Google Maps transit route forwarding behavior.
- Keep HTTPS and host allowlisting intact.
- Restrict forwarded URLs to the expected `/maps` path.
- Extend static checks for the path allowlist.

## Work Completed

- Added a `/maps` path check to `isAllowedExternalURL`.
- Kept the existing HTTPS scheme and `maps.google.com` host checks.
- Added static checker and completed-plan coverage for the stricter allowlist.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_wren_maprouter_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Clear pending route state if endpoint encoding fails.
- Modernize route URL encoding with a newer percent-encoding API in a
  compatibility pass.
