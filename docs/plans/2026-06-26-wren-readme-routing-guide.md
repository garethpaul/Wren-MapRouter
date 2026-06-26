# Wren MapRouter README Routing Guide

Status: Completed

## Context

The app, static contracts, and native tests already defined a precise Maps
directions-provider boundary, but the README still described a generic Apple
sample and did not explain how routes enter the app, when location permission
is requested, what leaves the device, or how to verify the handoff.

## Objectives

- Document the current Xcode project setup and iOS 13+ target without inventing
  a dependency installation step.
- Explain that the app is a directions handoff provider rather than a standalone
  map or route-planning interface.
- Describe Apple Maps invocation, supported transit modes, endpoint resolution,
  Google Maps forwarding, and route-state cleanup.
- Make when-in-use permission conditional on a Current Location endpoint and
  document the 60-second and 1,000-meter sample policy.
- State the coordinate disclosure and privacy-safe manual verification boundary.
- Replace stale generated inventory with the actual source, metadata, coverage,
  tests, and verification surfaces.

## Verification

- Focused README route and permission contracts fail before documentation is
  aligned and pass afterward.
- Hostile setup, route, mode, permission, freshness, accuracy, destination,
  cleanup, privacy, roadmap, history, and plan-status mutations
  fail closed.
- `python3 scripts/check_wren_maprouter_contracts.py`
- `python3 scripts/run_mutation_checks.py`
- `/usr/bin/make check` from the checkout and through an absolute Makefile path
  from an external working directory.
- Native iOS build and XCTest results are recorded by the hosted macOS gate.
- `git diff --check`

## Scope Boundary

- Do not change Objective-C behavior, project settings, deployment target,
  directions coverage, tests, workflows, or external destinations.
- Do not claim that the blank host window is a standalone navigation UI.
- Do not use or retain private route or location data during verification.

## Work Completed

- Added copyable project setup, build, test, and manual handoff guidance.
- Documented exact route-provider behavior, conditional permission requests,
  usable-location bounds, cleanup outcomes, and Google Maps coordinate sharing.
- Registered executable documentation and completed-plan contracts.

## Results

- Checkout-local and external-directory `/usr/bin/make check` passed 45 Make
  authority cases, seven existing source/workflow mutations, static contracts,
  and Python syntax checks.
- Fifteen hostile setup, route, permission, location-policy, destination,
  privacy, roadmap, history, and plan mutations failed closed.
- Native iOS build and XCTest verification is intentionally left to the hosted
  macOS gate because this Linux environment has no `xcodebuild`.
