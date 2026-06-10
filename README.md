# Wren-MapRouter

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/Wren-MapRouter` is an Apple platform application or Objective-C/Swift sample. Steve Wren's Map Router

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Objective-C (2), C/C++ headers (1).

## Repository Contents

- `README.md` - project overview and local usage notes
- `GoogleTransit` - source or example code
- `GoogleTransit.xcodeproj` - Xcode project file
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: GoogleTransit
- Dependency and build manifests: none detected
- Entry points or build surfaces: GoogleTransit.xcodeproj
- Test-looking files: no obvious test files detected

## Getting Started

### Prerequisites

- Git
- macOS with Xcode for building Apple platform projects

### Setup

```bash
git clone https://github.com/garethpaul/Wren-MapRouter.git
cd Wren-MapRouter
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Open `GoogleTransit.xcodeproj` in Xcode, choose the app or sample scheme, and run it on the matching simulator/device.

## Testing and Verification

- `make check` - runs dependency-free static contracts and attempts an Xcode build only when `xcodebuild` is available
- GitHub Actions runs the portable gate on Python 3.10, 3.12, and 3.14 with
  read-only permissions and manual dispatch; Linux runners intentionally skip
  the Xcode build pending the Objective-C and deployment-target migration.
- `make verify` - checks Maps directions registration, location permission
  metadata, GeoJSON validity, route parsing guards, transit modes, and external
  URL forwarding host/path allowlists, route endpoint encoding, query delimiter
  escaping, cleanup on encoding failure, and incomplete non-location route
  cleanup, empty and whitespace-only endpoint rejection, plus invalid
  location-update cleanup
- Completed maintenance plans live under `docs/plans` and are checked by
  `make check`.
- Xcode's test action or `xcodebuild test` with the appropriate scheme and destination

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- The app uses current location only to resolve a Maps directions endpoint that explicitly uses Current Location. Do not add route or location persistence without a privacy plan.
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
  cleanup when CoreLocation returns no location or an invalid coordinate.
- See `docs/plans/2026-06-09-maprouter-whitespace-endpoint-guard.md` for
  trimming route endpoints before empty checks and external URL forwarding.
- See `docs/plans/2026-06-10-maprouter-hosted-static-verification.md` for the
  pinned, least-privilege hosted contract baseline.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
