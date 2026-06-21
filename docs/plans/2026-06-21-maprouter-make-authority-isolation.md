# MapRouter Make Authority Isolation

Status: Completed

## Problem

The verification Makefile accepted caller-controlled tools, shell behavior,
startup files, recipes, execution modes, and Xcode derived-data paths. Because
the build targets delete derived data before invoking Xcode, a hostile or
accidental command-line override could redirect cleanup outside the checkout.

## Requirements

1. Resolve verification tools, shell behavior, and the repository root from
   trusted literal values.
2. Reject injected Make syntax, startup files, replacement recipes, and modes
   that skip or ignore verification work.
3. Keep build and XCTest derived-data cleanup beneath `.build/` regardless of
   caller-provided variables.
4. Preserve the explicit native simulator destination override used by CI.
5. Add deterministic regression coverage for every authority boundary.

## Work Completed

- Froze Python, Xcode, shell, root, and derived-data values before defining
  public recipes.
- Rejected hostile `MAKEFLAGS`, `MAKEFILES`, `MAKEFILE_LIST`, recipe, mode,
  path, and raw Make-syntax inputs.
- Added a root-independent shell harness that proves cleanup containment and
  trusted tool execution across every public target.
- Updated hosted verification and contributor commands to invoke
  `/usr/bin/make` explicitly.

## Verification

- Run `/usr/bin/make check` from the repository root.
- Run `/usr/bin/make check` from an unrelated working directory.
- Run the Make authority harness directly with `/bin/sh`.
- On macOS, run the native build and XCTest gates with Xcode.

## Scope Boundaries

- Do not change Objective-C application behavior or routing policy.
- Do not change project signing, deployment, or release settings.
- Keep the simulator destination as the only supported caller override needed
  by hosted native verification.
