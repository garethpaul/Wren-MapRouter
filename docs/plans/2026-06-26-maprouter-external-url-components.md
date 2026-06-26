# MapRouter External URL Component Boundary

## Status: Completed

## Context

The existing external forwarding helper allowed HTTPS `maps.google.com/maps`
URLs, but did not reject user information, explicit ports, or fragments. Apple
Foundation exposes each as a separate URL component, so the allowlist should
make the exact authority and fragment boundary explicit.

## Requirements

- Preserve the canonical Google Maps transit handoff and query parameters.
- Keep exact HTTPS scheme, `maps.google.com` host, and `/maps` path checks.
- Reject user names, passwords, any explicit port including 443, and fragments.
- Keep route cleanup, endpoint encoding, current-location behavior, and privacy
  disclosures unchanged.
- Exercise the policy through native XCTest and fail-closed portable contracts.

## Verification Plan

- Add native tests before implementation and observe the portable contract gate
  fail because the policy and project source registration do not exist.
- Add the smallest Foundation-only policy and delegate AppDelegate admission.
- Mutate explicit-port rejection and require the mutation suite to fail closed.
- Run `make check`, hosted Xcode build/XCTest, CodeQL, and `git diff --check`.

## Work Completed

- Added a pure external URL policy and canonical/hostile native tests.
- Registered policy and test sources in the legacy Xcode project.
- Replaced AppDelegate's private inline allowlist with policy delegation.
- Updated maintained routing, security, roadmap, and change guidance.

## Verification

- The red-first static gate reported every missing implementation and project
  contract before production code was added.
- The portable `make check` gate passed after implementation.
- Checkout-local and external-directory gates passed 45 Make authority cases,
  static contracts, and all eight hostile mutations.
- Xcode project inspection found no duplicate PBX object IDs, and
  `git diff --check` passed.
- Exact-head review, hosted Xcode/XCTest, and CodeQL evidence remain the final
  pre-merge actions.
