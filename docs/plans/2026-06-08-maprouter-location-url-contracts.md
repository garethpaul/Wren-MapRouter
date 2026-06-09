---
title: Wren MapRouter Location And URL Contracts
status: completed
date: 2026-06-08
origin: user-requested continuous engineering quality loop
execution: code
---

# Wren MapRouter Location And URL Contracts

Status: Completed

## Problem Frame

The sample starts CoreLocation updates whenever the app becomes active, but its
plist does not include modern location permission copy. The directions URL
handler also assumes every non-current MapKit endpoint has a placemark location
before forwarding to Google Maps.

## Scope Boundaries

- Preserve the legacy MapKit directions request entry point.
- Preserve Google Maps transit forwarding semantics.
- Do not store route or location history.
- Do not modernize the whole Objective-C project in this pass.

## Implementation Units

### U1: Add Static Contracts

Files:

- Create `scripts/check_wren_maprouter_contracts.py`
- Create `Makefile`
- Create `CHANGES.md`

Approach:

- Add dependency-free checks for Maps document-type registration, location
  usage metadata, supported mode uniqueness, GeoJSON validity, guarded
  direction endpoint parsing, and explicit external URL forwarding checks.

### U2: Harden Location And Route Handling

Files:

- Modify `GoogleTransit/AppDelegate.m`
- Modify `GoogleTransit/GoogleTransit-Info.plist`

Approach:

- Request when-in-use location authorization only when a directions request
  actually depends on current location.
- Avoid unconditional location updates on app activation.
- Guard placemark and coordinate extraction before constructing the Google Maps
  URL.
- Clear pending route state after forwarding.

## Verification

- `make check`
- `git diff --check`
