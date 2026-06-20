# Wren MapRouter Deep Review

Status: Completed

## Scope

Reviewed dependent PRs #2 through #7 and the archived Objective-C route flow from
MapKit URL intake through Core Location validation and Google Maps forwarding.

## Findings

- The iOS 6 deployment target no longer linked with Xcode 26 because the SDK no
  longer ships the required ARC compatibility library.
- A current iOS launch aborted because the application window had no root view
  controller.
- The location callback trusted only the final sample in a batch, so an invalid
  trailing sample could hide an earlier valid sample.
- NaN accuracy and age values passed comparison-only validation, and arbitrarily
  inaccurate coordinates could be forwarded.
- A callback arriving after route cancellation could retain a coordinate even
  though no route still owned location work.

## Fix Shape

`LocationSamplePolicy` now owns coordinate, accuracy, and freshness validation.
The delegate accepts the newest usable sample only while a pending route still
requires Current Location. Route replacement first cancels previous state.
Authorization and URL opening use current APIs, while transient
`kCLErrorLocationUnknown` behavior remains unchanged.

The project now targets iOS 13, launches with a root view controller, and has a
native XCTest target. Hosted CI retains pinned, credential-free checkout and
adds a macOS build/XCTest gate.

## Provenance

The original route callback and iOS 6 project settings were introduced in
commit `11039c8` on 2012-09-20. Later hardening fixed individual validation
cases but carried forward implicit callback ownership and comparison-only
finite-value checks.

## Verification

- `make check`
- `make -f ../repo/Makefile check` from an external directory
- Seven native XCTest cases on an iPhone 16 Pro simulator
- Seven hostile static mutations rejected
- Current-tree and full-history Gitleaks scans with zero findings
- GitHub CodeQL, secret-scanning, and Dependabot alert counts all zero before
  consolidation
