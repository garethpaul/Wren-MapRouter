# Wren-MapRouter

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Device Preview

<!-- DEVICE-PREVIEW-IMAGE -->
![Device preview](docs/device-preview.svg)

## Overview

`garethpaul/Wren-MapRouter` is a legacy Objective-C iOS directions-provider
sample. It accepts a transit request from Apple Maps and forwards the resolved
route to the reviewed Google Maps web endpoint.

This is a directions handoff sample, not a standalone map or route-planning UI.
The app itself presents only a blank host window while it resolves and forwards
an incoming route.

## Repository Contents

- `GoogleTransit/AppDelegate.m` - directions-request parsing, location
  permission, route normalization, cleanup, and external handoff
- `GoogleTransit/LocationSamplePolicy.m` - finite, fresh, bounded-accuracy
  current-location selection
- `GoogleTransit/GoogleTransit-Info.plist` - Maps directions registration,
  transit modes, and when-in-use permission text
- `GoogleTransit/Directions.geojson` - worldwide directions-provider coverage
- `GoogleTransitTests/LocationSamplePolicyTests.m` - native location-policy
  regression tests
- `scripts/` and `Makefile` - portable contracts, hostile mutations, Make
  authority checks, and optional Xcode build/XCTest gates

## Getting Started

### Prerequisites

- Git
- macOS with a current Xcode capable of building an iOS 13 or newer target
- An iOS simulator or device for manual Apple Maps handoff verification
- No package manager, third-party dependency install, account, API key, or
  credential file is required

### Setup

```bash
git clone https://github.com/garethpaul/Wren-MapRouter.git
cd Wren-MapRouter
open GoogleTransit.xcodeproj
```

In Xcode, select the `GoogleTransit` scheme and an iOS 13 or newer simulator or
device. Code signing is not required for the repository build gate; a physical
device run may require your own development team.

## Running or Using the Project

### Expected Route Behavior

The app registers for Apple Maps directions requests covering bus, ferry,
streetcar, subway, or train routes. On a simulator or device where Maps exposes
registered directions providers:

1. Install and launch the `GoogleTransit` target once.
2. In Apple Maps, create a route and choose Transit.
3. Select the displayed **Google Directions** provider when Maps offers it.
4. The provider parses the Apple Maps directions request, resolves both route
   endpoints, percent-encodes them, and opens
   `https://maps.google.com/maps` with transit routing selected.

Routes with two concrete endpoints forward immediately. When In Use location
permission is requested only when the source or destination is **Current
Location**. The provider waits for the newest valid sample that is no more than
60 seconds old and no worse than 1,000 meters horizontal accuracy. Missing,
future-dated, stale, invalid-coordinate, and negative-accuracy samples are
ignored while a pending current-location route waits for a later usable sample.

If location services are disabled, permission is denied or restricted, the app
enters the background, endpoint encoding fails, or Core Location reports a
terminal error, the provider cancels and clears pending route state. A transient
`kCLErrorLocationUnknown` keeps the request pending. The app retains no route
history and clears source, destination, and resolved location after forwarding
or cancellation.

The forwarded Google Maps URL contains the source, destination, and any
resolved current-location coordinate. Use synthetic routes during verification;
do not include private home, work, or travel locations in screenshots or logs.

## Testing and Verification

- `/usr/bin/make check` - runs dependency-free static contracts, Make authority regression tests, focused mutations, and optional Xcode build/XCTest gates when `/usr/bin/xcodebuild` is available
- `open GoogleTransit.xcodeproj` - opens the project for simulator/device route
  handoff verification with the `GoogleTransit` scheme
- `/usr/bin/make build` - builds the iOS 13+ app without code signing when
  `xcodebuild` is available
- `/usr/bin/make xctest TEST_DESTINATION="platform=iOS Simulator,id=<UDID>"` -
  runs the native `GoogleTransitTests` location-policy suite
- GitHub Actions runs the portable gate on Python 3.10, 3.12, and 3.14 with
  fixed Ubuntu 24.04 runners, read-only permissions, superseded-run
  cancellation, and manual dispatch. A macOS gate also builds the iOS 13+
  target and runs the native XCTest policy suite on an available simulator.
  Checkout credentials are not persisted after source retrieval.
- `/usr/bin/make verify` - checks Maps directions registration, location permission
  metadata, GeoJSON validity, route parsing guards, transit modes, and external
  URL forwarding host/path allowlists, route endpoint encoding, query delimiter
  escaping, cleanup on encoding failure, and incomplete non-location route
  cleanup, empty and whitespace-only endpoint rejection, plus transient invalid
  location-sample rejection, negative horizontal-accuracy rejection, and
  cached-location freshness rejection, and transient Core Location error
  preservation
- Completed maintenance plans live under `docs/plans` and are checked by
  `/usr/bin/make check`.
- Xcode's test action or `xcodebuild test` with the appropriate scheme and destination
- See `docs/plans/2026-06-26-wren-readme-routing-guide.md` for the completed
  setup, route-handoff, permission, privacy, and verification documentation
  plan.

Repository verification intentionally uses `/usr/bin/make`, anchors default
tools to literal values, and freezes tool/destination selections before later
makefiles can replace them. Its checked-in recipes keep root, recipe
replacement, execution-mode, and derived-data cleanup under the repository
boundary, so build and test cleanup stays contained under `.build/` and
caller-provided derived-data paths are ignored.

That boundary is not a sandbox for caller-supplied Make programs. Target-
specific `override SHELL`/`.SHELLFLAGS`, startup parse-time code from
`MAKEFILES` or extra `-f` inputs, and the default `PYTHON=python3` lookup
through caller `PATH` remain caller authority. Use a trusted `PATH` or an
explicit literal `PYTHON=/path/to/python3` for local verification. Once
selected, Python verification runs with `-I -B`, so caller `PYTHONPATH`, user
site packages, and bytecode output cannot replace the checked-in checkers.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- The app uses current location only to resolve a Maps directions endpoint that explicitly uses Current Location. Do not add route or location persistence without a privacy plan.
- Source, destination, and any resolved current-location coordinate are sent to
  `https://maps.google.com/maps` when the app forwards the transit route. The
  app does not retain those values after forwarding or cancellation.
- Future-dated and older-than-60-second cached locations are ignored while the
  router waits for a fresh coordinate.
- Missing, invalid-coordinate, and negative-accuracy samples are ignored
  without abandoning the pending route or stopping location updates.
- `kCLErrorLocationUnknown` keeps the pending Current Location route active so
  Core Location can deliver a later coordinate; other delegate failures clear
  route state and stop updates.
- Route endpoints are trimmed before encoding so whitespace-only endpoints are
  not forwarded to external maps.

## Security and Privacy Notes

- Review changes touching network requests, sockets, or service endpoints; examples from the scan include GoogleTransit/AppDelegate.m, GoogleTransit/GoogleTransit-Info.plist.
- Review changes touching mobile permissions or privacy-sensitive device data; examples from the scan include GoogleTransit/AppDelegate.m.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include GoogleTransit/GoogleTransit-Info.plist.

## Maintenance Notes

- This looks like an Apple platform project or sample. Xcode, Swift, CocoaPods, and deployment target versions may need to match the original project era.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-maprouter-location-url-contracts.md` for the
  current location and URL-routing baseline.
- See `docs/plans/2026-06-08-maprouter-transit-mode-scope.md` for the declared
  transit-mode scope.
- See `docs/plans/2026-06-08-maprouter-external-url-allowlist.md` for the
  Google Maps forwarding allowlist.
- See `docs/plans/2026-06-09-maprouter-route-endpoint-encoding.md` for route
  endpoint encoding before external forwarding.
- See `docs/plans/2026-06-09-maprouter-empty-endpoint-guard.md` for empty route
  endpoint rejection before external forwarding.
- See `docs/plans/2026-06-09-maprouter-query-delimiter-encoding.md` for
  delimiter-safe query encoding of route endpoints.
- See `docs/plans/2026-06-09-maprouter-external-path-allowlist.md` for the
  Google Maps `/maps` path allowlist.
- See `docs/plans/2026-06-09-maprouter-encoding-failure-cleanup.md` for route
  cleanup when endpoint encoding fails.
- See `docs/plans/2026-06-09-maprouter-incomplete-route-cleanup.md` for route
  cleanup when a non-location route cannot resolve both endpoints.
- See `docs/plans/2026-06-09-maprouter-location-update-validation.md` for
  the original no-location and invalid-coordinate validation boundary.
- See `docs/plans/2026-06-09-maprouter-whitespace-endpoint-guard.md` for
  trimming route endpoints before empty checks and external URL forwarding.
- See `docs/plans/2026-06-10-maprouter-hosted-static-verification.md` for the
  pinned, least-privilege hosted contract baseline.
- See `docs/plans/2026-06-10-maprouter-location-freshness.md` for cached
  location rejection and root-independent verification.
- See `docs/plans/2026-06-10-maprouter-horizontal-accuracy-validation.md` for
  rejecting Core Location samples whose coordinates are marked invalid.
- See `docs/plans/2026-06-13-maprouter-transient-location-errors.md` for
  preserving pending routes across temporary location acquisition failures.
- See `docs/plans/2026-06-13-maprouter-background-route-cleanup.md` for
  preserving routes during temporary inactive states and clearing on
  background entry.
- See `docs/plans/2026-06-13-maprouter-transient-location-samples.md` for
  preserving pending routes while Core Location emits unusable samples.
- See `docs/plans/2026-06-21-maprouter-make-authority-isolation.md` for the
  trusted Make boundary and derived-data cleanup containment.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
