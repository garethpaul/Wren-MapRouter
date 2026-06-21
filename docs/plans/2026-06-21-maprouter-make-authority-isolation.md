# MapRouter Make Authority Isolation

Status: Completed

## Problem

The verification Makefile accepted caller-controlled tools, shell behavior,
startup files, recipes, execution modes, and Xcode derived-data paths. Because
the build targets delete derived data before invoking Xcode, a hostile or
accidental command-line override could redirect cleanup outside the checkout.

## Requirements

1. Resolve default verification tools from literal paths, freeze any explicit
   literal tool selection, and keep the repository root under repository
   control for checked-in recipes.
2. Reject injected Make syntax, detect startup files before repository recipes
   execute, reject replacement recipes, and reject modes that skip or ignore
   verification work.
3. Keep build and XCTest derived-data cleanup beneath `.build/` regardless of
   caller-provided variables.
4. Preserve the explicit native simulator destination override used by CI.
5. Add deterministic regression coverage for every authority boundary.

## Work Completed

- Froze literal Python/Xcode selections plus repository-controlled root and
  derived-data values before defining public recipes.
- Rejected hostile `MAKEFLAGS`, `MAKEFILES`, `MAKEFILE_LIST`, recipe, mode,
  path, and raw Make-syntax inputs.
- Added a root-independent shell harness that proves cleanup containment and
  trusted tool execution across every public target.
- Documented the caller boundary for target-specific override shell settings,
  startup parse-time code, and default PATH-selected Python.
- Isolated each selected Python invocation with `-I -B` so `PYTHONPATH`, user
  site packages, and bytecode output cannot replace repository checkers.
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
- Target-specific `override SHELL`/`.SHELLFLAGS`, startup parse-time code from
  caller Makefiles, and default `PYTHON=python3` lookup through caller `PATH`
  are caller authority, not repository-controlled sandbox behavior.
