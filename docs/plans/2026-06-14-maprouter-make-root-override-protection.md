# MapRouter Make Root Override Protection

Status: Completed

## Problem

The Makefile-derived repository root anchors the portable checker and legacy
Xcode project, but an ordinary assignment can be replaced from the command
line and redirect verification away from the checkout.

## Requirements

1. Protect the derived root with GNU Make's `override` directive.
2. Preserve the configurable Python command and existing targets.
3. Require exact protected-root, Python-override, checker, project, and Xcode
   path contracts.
4. Pass local, external-directory, and hostile-root full gates.
5. Reject focused root, tool, path, and plan-status mutations.

## Verification

- Compile and run the portable checker.
- Run bounded local, external-directory, and hostile `ROOT` `make check`.
- Run focused mutations and plist/JSON/XML/workflow audits.
- Audit exact paths, artifacts, whitespace, and changed-line credentials.
- Record the unavailable Linux `xcodebuild` boundary truthfully.

## Scope Boundaries

- Do not change Objective-C behavior, project metadata, workflows, assets, or
  deployment configuration.
- Do not merge or close any pull request without explicit owner authorization.

## Work Completed

- Protected the Makefile-derived root while preserving the Python override and
  existing targets.
- Added exact portable contracts for protected derivation, checker/project
  paths, Python override semantics, and this completed plan.

## Verification Results

- Python compilation and the portable checker passed.
- Local, external-directory, and hostile `ROOT` full `make check` gates passed;
  each truthfully skipped the unavailable Linux `xcodebuild`.
- Eight focused root, tool, path, and plan-status mutations were rejected.
- Plist/JSON/XML/workflow, whitespace, explicit-artifact, and changed-line
  credential audits passed before shipment.
