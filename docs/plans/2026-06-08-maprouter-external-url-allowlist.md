# MapRouter External URL Allowlist

## Status: Completed

## Context

The route forwarding path builds a Google Maps transit URL, but the shared
`openURL:` helper accepted any URL object it was passed. Keeping an explicit
allowlist in the helper makes future routing changes preserve the intended
external destination boundary.

## Objectives

- Preserve the existing Google Maps transit forwarding behavior.
- Reject non-HTTPS and non-Google Maps URLs before calling `canOpenURL`.
- Keep route-state cleanup behavior unchanged.
- Cover the URL allowlist in `make check`.

## Work Completed

- Added `isAllowedExternalURL:` for `https://maps.google.com`.
- Checked the allowlist before `canOpenURL:` and `openURL:`.
- Extended `scripts/check_wren_maprouter_contracts.py` with URL allowlist
  assertions.
- Updated README, VISION, and CHANGES with the new guardrail.

## Verification

- `python3 scripts/check_wren_maprouter_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add route URL encoding tests around source and destination query values.
- Add simulator notes for Maps directions handoff behavior.
