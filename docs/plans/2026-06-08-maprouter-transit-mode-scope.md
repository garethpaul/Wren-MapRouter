---
title: Wren MapRouter Transit Mode Scope
status: completed
date: 2026-06-08
origin: user-requested continuous engineering quality loop
execution: code
---

# Wren MapRouter Transit Mode Scope

Status: Completed

## Problem Frame

The app forwards every accepted Maps directions request to Google Maps with the
transit routing flag, but the plist advertised non-transit modes including car,
walking, bike, taxi, plane, and other. That can cause Maps to route unsupported
requests into a transit-only handler.

## Scope Boundaries

- Preserve the existing Google Maps transit forwarding URL.
- Do not add alternate routing behavior for non-transit modes.
- Keep the current directions document type registration.

## Implementation

- Limit `MKDirectionsApplicationSupportedModes` to bus, ferry, streetcar,
  subway, and train.
- Extend the dependency-free contract checker to reject non-transit mode claims.

## Verification

- `python3 scripts/check_wren_maprouter_contracts.py`
- `make check`
- `git diff --check`
