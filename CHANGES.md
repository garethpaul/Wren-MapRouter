# Changes

## 2026-06-26 13:55 PDT - P2 - Enforce exact Google Maps URL components

### Summary

Extracted external directions admission into a Foundation-only policy and
closed authority-component gaps beyond the existing scheme, host, and path
allowlist.

### Work completed

- Added `ExternalDirectionsURLPolicy` and made `AppDelegate` use it before
  `canOpenURL:` or external forwarding.
- Preserved exact HTTPS, `maps.google.com`, and `/maps` checks.
- Rejected URL user names, passwords, all explicit ports, and fragments.
- Added native XCTest cases for the canonical handoff and hostile URL variants.
- Added static project/source/test contracts and a hostile mutation that
  removes explicit-port rejection.
- External URL admission rejects credentials, explicit ports, and fragments.

### Threads

- Started: none — the bounded routing change was completed directly.
- Continued: none.
- Stopped: none.

### Files changed

- `GoogleTransit/ExternalDirectionsURLPolicy.h` and
  `GoogleTransit/ExternalDirectionsURLPolicy.m` — define exact URL admission.
- `GoogleTransit/AppDelegate.m` — delegates external admission to the policy.
- `GoogleTransitTests/ExternalDirectionsURLPolicyTests.m` and
  `GoogleTransit.xcodeproj/project.pbxproj` — add native tests and target files.
- `scripts/check_wren_maprouter_contracts.py` and
  `scripts/run_mutation_checks.py` — bind the implementation, tests, project,
  documentation, and hostile mutation.
- `README.md`, `SECURITY.md`, `VISION.md`, and
  `docs/plans/2026-06-26-maprouter-external-url-components.md` — record scope
  and evidence.

### Validation

- Red-first static gate — failed on the missing policy, AppDelegate delegation,
  component checks, and Xcode project source registration.
- Green portable gate — 45 Make authority cases, static contracts, and all
  eight registered hostile mutations passed from both the checkout and an
  external working directory.
- Xcode project inspection found no duplicate 24-character PBX object IDs, and
  `git diff --check` passed.
- Hosted static-contract jobs passed on Python 3.10, 3.12, and 3.14.
- Hosted native Xcode build and XCTest passed, and CodeQL Actions and Python
  analysis passed.
- The immutable PR head `5f63671901e67b6cd7391175798207d12c594a74`
  matched the locally reviewed head and merged as
  `3b04b1dceec474329104851589cef37742f88244`.
- Manual exact-head review found no actionable issue.

### Bugs / findings

- P2: the old host/path allowlist still admitted decorated Google Maps URLs
  containing credentials, an explicit port, or a fragment.

### Review limitations

- `$codex-review` was attempted against `origin/master`, but the helper stopped
  before analysis with OpenAI HTTP 401 authentication failure. No review
  finding was suppressed; the exact diff received an immutable manual review.
- `xcodebuild` is unavailable on the Linux host, so the passing hosted native
  job is the authoritative compilation and XCTest evidence.

### Next action

- Continue repository maintenance from the merged, fully green master head.

## 2026-06-26

- Priority P2 cycle: completed the README setup, route-behavior, and location
  permission roadmap gaps without changing the archived application or Xcode
  project.
- Documented the Apple Maps-to-Google Maps transit handoff, supported transit
  modes, route-provider invocation, current-location admission policy, terminal
  cleanup behavior, external coordinate disclosure, and privacy-safe manual
  verification.
- Replaced stale generated inventory with the actual routing, permission,
  coverage, native test, and verification surfaces and added fail-closed static
  documentation contracts.
- Portable checkout-local and external-directory gates passed 45 Make authority
  cases, seven existing source/workflow mutations, static contracts, and syntax
  checks. Fifteen hostile setup, route, permission, privacy, roadmap, history,
  and plan mutations were rejected; native build/XCTest remains hosted-macOS
  evidence.
- No delegated threads were needed. The next recommended action is to decide
  whether the sample remains archived or receives a dedicated modern Maps API
  migration plan.

## 2026-06-21

- Isolated repository verification from later single-colon recipe replacement,
  unsafe modes, unsafe Make syntax, and caller-selected cleanup paths while
  documenting target-specific override shells, startup parse-time code, and
  default PATH-selected Python as caller authority.
- Isolated the selected Python runtime from `PYTHONPATH`, user-site imports,
  and bytecode output for every repository checker.
- Contained Xcode derived-data cleanup beneath the checkout and added a
  regression harness proving hostile caller paths are never removed.
- Aligned local and hosted verification on the trusted `/usr/bin/make`
  authority while preserving the native simulator destination override.

## 2026-06-19

- Added native XCTest coverage for finite, fresh, bounded-accuracy location
  selection and for mixed valid/invalid callback batches.
- Prevented late callbacks from retaining a coordinate after route cancellation,
  reset previous location work before route replacement, and adopted modern
  authorization and URL-opening APIs.
- Raised the archived project to iOS 13, restored current-Xcode launch/build
  compatibility, and documented Google Maps route-coordinate disclosure.

## 2026-06-13

- Preserved pending Current Location routes when Core Location emits a missing,
  invalid-coordinate, or negative-accuracy sample while awaiting later data.

## 2026-06-12

- Disabled persisted checkout credentials and enforced the sole pinned
  credential-free workflow boundary.

## 2026-06-10

- Rejected Core Location objects with negative horizontal accuracy before
  route endpoint conversion or live-location storage, with cleanup and static
  regression coverage.
- Added immutable, read-only GitHub Actions verification on Python 3.10, 3.12,
  and 3.14 for location, route normalization, and external forwarding
  contracts, with manual dispatch for maintenance runs.
- Added static protection for workflow permissions, action revisions, matrix
  versions, timeout, and the `make check` entry point.
- Documented that hosted Linux checks intentionally skip the legacy Xcode build.
- Rejected future-dated and older-than-60-second CoreLocation samples before
  using current location in an external route.
- Pinned hosted verification to Ubuntu 24.04 with superseded-run cancellation
  and made static and optional Xcode checks root-independent.

## 2026-06-09

- Trimmed route endpoints before empty checks and percent encoding so
  whitespace-only values cannot be forwarded.
- Added static checker coverage for endpoint whitespace normalization.
- Rejected empty route endpoints before percent encoding and external Google
  Maps URL construction.
- Added static checker coverage for empty route endpoint rejection.
- Cleared pending route state when CoreLocation returns no location or an
  invalid coordinate update.
- Added static checker coverage for location update validation.
- Cleared pending route state when a non-location directions request is missing
  either endpoint.
- Added static checker coverage for incomplete route cleanup before external
  URL construction.
- Escaped URL query delimiters when encoding route endpoints for Google Maps
  forwarding.
- Added static checker coverage for delimiter-safe route endpoint encoding.
- Cleared pending route state when route endpoint encoding fails before
  external forwarding.
- Added static checker coverage for encoding-failure cleanup.
- Restricted external Google Maps forwarding to the expected `/maps` route
  path in addition to HTTPS host allowlisting.
- Added static checker coverage for the external URL path allowlist.
- Encoded route source and destination endpoint strings before formatting the
  Google Maps forwarding URL.
- Added static checker coverage for route endpoint URL encoding.

## 2026-06-08

- Restricted external forwarding to HTTPS Google Maps URLs before calling
  `openURL`.
- Limited declared Maps directions modes to transit-compatible route types.
- Added docs-plan coverage to the static MapRouter contract checker.
- Added static contracts for the legacy MapKit directions handler, location permission metadata, and bundled GeoJSON artifact.
- Hardened current-location route handling so unresolved or denied location access clears pending route state.
- Preserved pending Current Location routes during temporary inactive states
  while retaining cleanup when the app enters the background.
- Added `make check` as the local verification entry point for this Objective-C iOS sample.
