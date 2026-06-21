# AGENTS.md

## Repository purpose

`garethpaul/Wren-MapRouter` is an Apple platform application or Objective-C/Swift sample. Steve Wren's Map Router

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `GoogleTransit.xcodeproj` - Xcode project
- `GoogleTransit` - repository source or sample assets

## Development commands

- Install dependencies: no repository-specific install command is documented.
- Full baseline: `/usr/bin/make check`
- Combined verification: `/usr/bin/make verify`
- Lint/static checks: `/usr/bin/make lint`
- Tests: `/usr/bin/make test`
- Build: `/usr/bin/make build`
- Local Apple development: `open GoogleTransit.xcodeproj`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: Objective-C (2), C/C++ headers (1).
- Preserve legacy Xcode project settings and signing assumptions unless the change is explicitly about modernization.

## Testing guidance

- Treat `/usr/bin/make check` as the minimum portable baseline; native XCTest also runs when Xcode is available.
- Start with the narrowest relevant test or Make target, then run `/usr/bin/make check` before handing off if the change is not documentation-only.
- Keep the system Make entry point, repository-derived root, checked-in recipes, and derived-data paths under repository authority; explicit literal Python/Xcode selections may be frozen, but do not weaken the containment harness to permit caller-controlled cleanup paths.
- Treat target-specific override shell settings, startup parse-time code from caller Makefiles, and default PATH-selected Python as caller authority outside the local Make boundary.
- Keep repository Python checker invocations isolated with `-I -B`; do not reintroduce `PYTHONPATH` or user-site import authority.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- The app uses current location only to resolve a Maps directions endpoint that explicitly uses Current Location. Do not add route or location persistence without a privacy plan.
- This looks like an Apple platform project or sample. Xcode, Swift, CocoaPods, and deployment target versions may need to match the original project era.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-maprouter-location-url-contracts.md` for the current location and URL-routing baseline.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `/usr/bin/make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
