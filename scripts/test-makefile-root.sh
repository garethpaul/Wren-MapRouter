#!/usr/bin/env sh
set -eu

PATH=/usr/bin:/bin
export PATH
ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && /bin/pwd -P)
TEMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/wren-maprouter-make-authority-XXXXXX")
trap 'rm -rf "$TEMP_ROOT"' EXIT HUP INT TERM
unset BUILD_DERIVED_DATA BUILD_DESTINATION MAKEFILES MAKEFILE_LIST MAKEFLAGS MFLAGS MAKEOVERRIDES PYTHON ROOT SHELL TEST_DERIVED_DATA TEST_DESTINATION XCODEBUILD

CONTROL_DIR="$TEMP_ROOT/control"
CHECKOUT="$TEMP_ROOT/wren app's [gate] \"quoted\" \`touch WREN_ROOT_MARKER\`"
ATTACKER_ROOT="$TEMP_ROOT/attacker"
AUTHORITY_PATH="$TEMP_ROOT/no-platform-tools"
LOG="$TEMP_ROOT/commands.log"
SHELL_LOG="$TEMP_ROOT/shell.log"
mkdir -p "$CONTROL_DIR" "$CHECKOUT/scripts" "$CHECKOUT/.build/build-derived-data" "$CHECKOUT/.build/test-derived-data" "$ATTACKER_ROOT" "$AUTHORITY_PATH"
CONTROL_DIR=$(CDPATH= cd -- "$CONTROL_DIR" && /bin/pwd -P)
CHECKOUT=$(CDPATH= cd -- "$CHECKOUT" && /bin/pwd -P)
MAKEFILE="$CHECKOUT/Makefile"
cp "$ROOT_DIR/Makefile" "$MAKEFILE"

FAKE_PYTHON="$TEMP_ROOT/trusted python's \"quoted\" \`touch WREN_PYTHON_MARKER\` \$literal"
cat >"$FAKE_PYTHON" <<'SCRIPT'
#!/bin/sh
printf '%s|%s|%s\n' "$PWD" "$0" "$*" >> "$WREN_COMMAND_LOG"
SCRIPT
chmod +x "$FAKE_PYTHON"
for script in test-makefile-root.sh check_wren_maprouter_contracts.py run_mutation_checks.py; do
  cp "$FAKE_PYTHON" "$CHECKOUT/scripts/$script"
done

FAKE_XCODEBUILD="$TEMP_ROOT/trusted xcodebuild's quoted"
cat >"$FAKE_XCODEBUILD" <<'SCRIPT'
#!/bin/sh
printf '%s|%s|%s\n' "$PWD" "$0" "$*" >> "$WREN_COMMAND_LOG"
SCRIPT
chmod +x "$FAKE_XCODEBUILD"

FAKE_SHELL="$TEMP_ROOT/fake-shell"
printf '#!/bin/sh\nprintf invoked >> %s\nexec /bin/sh "$@"\n' "'$SHELL_LOG'" >"$FAKE_SHELL"
chmod +x "$FAKE_SHELL"

run_case() {
  target=$1
  mode=$2
  output="$TEMP_ROOT/case.out"
  rm -f "$LOG" "$SHELL_LOG" "$output"
  mkdir -p "$CHECKOUT/.build/build-derived-data" "$CHECKOUT/.build/test-derived-data"
  : >"$CHECKOUT/.build/build-derived-data/probe"
  : >"$CHECKOUT/.build/test-derived-data/probe"
  : >"$ATTACKER_ROOT/keep"
  set +e
  case "$mode" in
    default)
      (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WREN_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "XCODEBUILD=$FAKE_XCODEBUILD" "$target") >"$output" 2>&1
      ;;
    command-root)
      (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WREN_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" ROOT="$ATTACKER_ROOT" "PYTHON=$FAKE_PYTHON" "XCODEBUILD=$FAKE_XCODEBUILD" "$target") >"$output" 2>&1
      ;;
    environment-root)
      (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" ROOT="$ATTACKER_ROOT" WREN_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "XCODEBUILD=$FAKE_XCODEBUILD" "$target") >"$output" 2>&1
      ;;
    command-shell)
      (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WREN_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" SHELL="$FAKE_SHELL" "PYTHON=$FAKE_PYTHON" "XCODEBUILD=$FAKE_XCODEBUILD" "$target") >"$output" 2>&1
      ;;
    environment-shell)
      (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" SHELL="$FAKE_SHELL" WREN_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "XCODEBUILD=$FAKE_XCODEBUILD" "$target") >"$output" 2>&1
      ;;
  esac
  status=$?
  set -e
  if [ "$status" -ne 0 ] || [ -e "$SHELL_LOG" ] || [ ! -e "$ATTACKER_ROOT/keep" ]; then
    printf 'authority case failed: target=%s mode=%s status=%s\n' "$target" "$mode" "$status" >&2
    cat "$output" >&2
    return 1
  fi
  case "$target" in
    clean)
      [ ! -e "$CHECKOUT/.build/build-derived-data" ]
      [ ! -e "$CHECKOUT/.build/test-derived-data" ]
      ;;
    *)
      grep -Fq "$CHECKOUT" "$LOG"
      ;;
  esac
}

executed=0
for target in build check clean lint mutations root-test test verify xctest; do
  for mode in default command-root environment-root command-shell environment-shell; do
    run_case "$target" "$mode"
    executed=$((executed + 1))
  done
done
[ "$executed" -eq 45 ]

rm -f "$LOG"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WREN_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" "XCODEBUILD=$FAKE_XCODEBUILD" check) >/dev/null 2>&1
grep -Fq "$FAKE_PYTHON" "$LOG"
grep -Fq "$FAKE_XCODEBUILD" "$LOG"
grep -Fq -- "-destination generic/platform=iOS Simulator" "$LOG"
grep -Fq -- "-destination platform=iOS Simulator,name=iPhone 16 Pro" "$LOG"
[ ! -e "$CONTROL_DIR/WREN_ROOT_MARKER" ]
[ ! -e "$CONTROL_DIR/WREN_PYTHON_MARKER" ]

controls=0
for variable in PYTHON XCODEBUILD BUILD_DESTINATION TEST_DESTINATION; do
  mark="$TEMP_ROOT/${variable}-command-syntax"
  bad="\$(shell /usr/bin/touch '$mark')"
  if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make --no-print-directory -f "$MAKEFILE" "$variable=$bad" lint) >"$TEMP_ROOT/syntax.out" 2>&1; then exit 1; fi
  [ ! -e "$mark" ]
  controls=$((controls + 1))

  mark="$TEMP_ROOT/${variable}-environment-syntax"
  bad="\$(shell /usr/bin/touch '$mark')"
  if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" env "$variable=$bad" /usr/bin/make --environment-overrides --no-print-directory -f "$MAKEFILE" lint) >"$TEMP_ROOT/syntax-environment.out" 2>&1; then exit 1; fi
  [ ! -e "$mark" ]
  controls=$((controls + 1))
done

ROOT_MARK="$TEMP_ROOT/root-command-syntax"
ROOT_BAD="\$(shell /usr/bin/touch '$ROOT_MARK')"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WREN_COMMAND_LOG="$LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" "ROOT=$ROOT_BAD" "PYTHON=$FAKE_PYTHON" XCODEBUILD=/definitely/not-xcodebuild lint) >/dev/null 2>&1
[ ! -e "$ROOT_MARK" ]
controls=$((controls + 1))
ROOT_ENV_MARK="$TEMP_ROOT/root-environment-syntax"
ROOT_ENV_BAD="\$(shell /usr/bin/touch '$ROOT_ENV_MARK')"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" ROOT="$ROOT_ENV_BAD" WREN_COMMAND_LOG="$LOG" /usr/bin/make --environment-overrides --no-print-directory -f "$MAKEFILE" "PYTHON=$FAKE_PYTHON" XCODEBUILD=/definitely/not-xcodebuild lint) >/dev/null 2>&1
[ ! -e "$ROOT_ENV_MARK" ]
controls=$((controls + 1))
[ "$controls" -eq 10 ]

LIST_MARK="$TEMP_ROOT/list-command-syntax"
LIST_BAD="\$(shell /usr/bin/touch '$LIST_MARK')"
if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make --no-print-directory -f "$MAKEFILE" "MAKEFILE_LIST=$LIST_BAD" check) >"$TEMP_ROOT/list-command.out" 2>&1; then exit 1; fi
[ ! -e "$LIST_MARK" ]
grep -Fq 'MAKEFILE_LIST must not be overridden' "$TEMP_ROOT/list-command.out"
if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" MAKEFILE_LIST=/tmp/untrusted /usr/bin/make --environment-overrides --no-print-directory -f "$MAKEFILE" check) >"$TEMP_ROOT/list-environment.out" 2>&1; then exit 1; fi
grep -Fq 'MAKEFILE_LIST must not be overridden' "$TEMP_ROOT/list-environment.out"

PRE="$TEMP_ROOT/pre.mk"
PRE_MARKER="$TEMP_ROOT/pre-marker"
printf '$(shell /usr/bin/touch %s)\n' "$PRE_MARKER" >"$PRE"
if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" MAKEFILES="$PRE" /usr/bin/make --no-print-directory -f "$MAKEFILE" check) >"$TEMP_ROOT/pre.out" 2>&1; then exit 1; fi
grep -Fq 'MAKEFILES must be empty' "$TEMP_ROOT/pre.out"
[ -e "$PRE_MARKER" ]
rm -f "$PRE_MARKER"
if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" MAKEFILES="$PRE" /usr/bin/make --environment-overrides --no-print-directory -f "$MAKEFILE" check) >"$TEMP_ROOT/pre-environment.out" 2>&1; then exit 1; fi
grep -Fq 'MAKEFILES must be empty' "$TEMP_ROOT/pre-environment.out"
[ -e "$PRE_MARKER" ]

LATER="$TEMP_ROOT/later.mk"
for target in build check clean lint mutations root-test test verify xctest; do
  printf '%s:\n\t@/usr/bin/touch %s\n' "$target" "$TEMP_ROOT/later-$target" >"$LATER"
  if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make --no-print-directory -f "$MAKEFILE" -f "$LATER" "$target" "PYTHON=$FAKE_PYTHON" XCODEBUILD=/definitely/not-xcodebuild) >"$TEMP_ROOT/later.out" 2>&1; then exit 1; fi
  [ ! -e "$TEMP_ROOT/later-$target" ]
done

TARGET_XCODE="$TEMP_ROOT/target-xcode"
TARGET_XCODE_LOG="$TEMP_ROOT/target-xcode.log"
cat >"$TARGET_XCODE" <<'SCRIPT'
#!/bin/sh
printf '%s\n' "$*" >> "$WREN_TARGET_XCODE_LOG"
SCRIPT
chmod +x "$TARGET_XCODE"
LATER_VARS="$TEMP_ROOT/later-vars.mk"
cat >"$LATER_VARS" <<LATER_VARS
build check clean lint mutations root-test test verify xctest: MAKEFILE_LIST := $MAKEFILE
build check clean lint mutations root-test test verify xctest: ROOT := $ATTACKER_ROOT
build check clean lint mutations root-test test verify xctest: PYTHON := /definitely/not-python
build check clean lint mutations root-test test verify xctest: XCODEBUILD := $TARGET_XCODE
build check clean lint mutations root-test test verify xctest: BUILD_DESTINATION := attacker-build
build check clean lint mutations root-test test verify xctest: TEST_DESTINATION := attacker-test
build check clean lint mutations root-test test verify xctest: BUILD_DERIVED_DATA := $ATTACKER_ROOT/build
build check clean lint mutations root-test test verify xctest: TEST_DERIVED_DATA := $ATTACKER_ROOT/test
LATER_VARS
rm -f "$LOG" "$TARGET_XCODE_LOG"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WREN_COMMAND_LOG="$LOG" WREN_TARGET_XCODE_LOG="$TARGET_XCODE_LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" -f "$LATER_VARS" check "PYTHON=$FAKE_PYTHON" "XCODEBUILD=$FAKE_XCODEBUILD") >"$TEMP_ROOT/later-vars.out" 2>&1
grep -Fq "$FAKE_PYTHON" "$LOG"
grep -Fq "$FAKE_XCODEBUILD" "$LOG"
grep -Fq 'generic/platform=iOS Simulator' "$LOG"
grep -Fq 'platform=iOS Simulator,name=iPhone 16 Pro' "$LOG"
[ ! -e "$TARGET_XCODE_LOG" ]
[ ! -e "$ATTACKER_ROOT/build" ]
[ ! -e "$ATTACKER_ROOT/test" ]

LATER_FAKE_SHELL="$TEMP_ROOT/later-fake-shell"
LATER_SHELL_LOG="$TEMP_ROOT/later-shell.log"
cat >"$LATER_FAKE_SHELL" <<'SCRIPT'
#!/bin/sh
printf invoked >> "$WREN_LATER_SHELL_LOG"
exec /bin/sh "$@"
SCRIPT
chmod +x "$LATER_FAKE_SHELL"
LATER_OVERRIDE="$TEMP_ROOT/later-override.mk"
cat >"$LATER_OVERRIDE" <<LATER_OVERRIDE_MAKE
build check clean lint mutations root-test test verify xctest: MAKEFILE_LIST := $MAKEFILE
build check clean lint mutations root-test test verify xctest: override SHELL := $LATER_FAKE_SHELL
build check clean lint mutations root-test test verify xctest: override .SHELLFLAGS := -c
LATER_OVERRIDE_MAKE
rm -f "$LATER_SHELL_LOG" "$LOG"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" WREN_COMMAND_LOG="$LOG" WREN_LATER_SHELL_LOG="$LATER_SHELL_LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" -f "$LATER_OVERRIDE" check "PYTHON=$FAKE_PYTHON" XCODEBUILD=/definitely/not-xcodebuild) >"$TEMP_ROOT/later-override.out" 2>&1
[ -s "$LATER_SHELL_LOG" ]

PATH_PYTHON="$TEMP_ROOT/python3"
PATH_PYTHON_LOG="$TEMP_ROOT/path-python.log"
cp "$FAKE_PYTHON" "$PATH_PYTHON"
rm -f "$PATH_PYTHON_LOG"
(cd "$CONTROL_DIR" && PATH="$TEMP_ROOT:/usr/bin:/bin" WREN_COMMAND_LOG="$PATH_PYTHON_LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" lint) >"$TEMP_ROOT/path-python.out" 2>&1
[ -s "$PATH_PYTHON_LOG" ]

PATH_XCODE="$TEMP_ROOT/xcodebuild"
PATH_XCODE_LOG="$TEMP_ROOT/path-xcode.log"
cat >"$PATH_XCODE" <<'SCRIPT'
#!/bin/sh
printf '%s\n' "$*" >> "$WREN_PATH_XCODE_LOG"
SCRIPT
chmod +x "$PATH_XCODE"
rm -f "$PATH_XCODE_LOG"
(cd "$CONTROL_DIR" && PATH="$TEMP_ROOT:/usr/bin:/bin" WREN_PATH_XCODE_LOG="$PATH_XCODE_LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" build "PYTHON=$FAKE_PYTHON") >"$TEMP_ROOT/path-xcode.out" 2>&1
[ ! -e "$PATH_XCODE_LOG" ]

EXPLICIT_XCODE="$TEMP_ROOT/explicit xcodebuild"
EXPLICIT_XCODE_LOG="$TEMP_ROOT/explicit-xcode.log"
cat >"$EXPLICIT_XCODE" <<'SCRIPT'
#!/bin/sh
printf '%s\n' "$*" >> "$WREN_EXPLICIT_XCODE_LOG"
SCRIPT
chmod +x "$EXPLICIT_XCODE"
rm -f "$EXPLICIT_XCODE_LOG" "$TARGET_XCODE_LOG"
(cd "$CONTROL_DIR" && PATH="$TEMP_ROOT:/usr/bin:/bin" XCODEBUILD="$EXPLICIT_XCODE" WREN_EXPLICIT_XCODE_LOG="$EXPLICIT_XCODE_LOG" WREN_TARGET_XCODE_LOG="$TARGET_XCODE_LOG" /usr/bin/make --no-print-directory -f "$MAKEFILE" -f "$LATER_VARS" build "PYTHON=$FAKE_PYTHON") >"$TEMP_ROOT/explicit-xcode.out" 2>&1
[ -s "$EXPLICIT_XCODE_LOG" ]
[ ! -e "$TARGET_XCODE_LOG" ]

: >"$ATTACKER_ROOT/build-keep"
: >"$ATTACKER_ROOT/test-keep"
(cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make --no-print-directory -f "$MAKEFILE" clean "BUILD_DERIVED_DATA=$ATTACKER_ROOT" "TEST_DERIVED_DATA=$ATTACKER_ROOT") >"$TEMP_ROOT/cleanup.out" 2>&1
[ -e "$ATTACKER_ROOT/build-keep" ]
[ -e "$ATTACKER_ROOT/test-keep" ]

if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make --no-print-directory -f "$MAKEFILE" MAKEFLAGS=-n check) >"$TEMP_ROOT/flags.out" 2>&1; then exit 1; fi
grep -Fq 'MAKEFLAGS must not be overridden' "$TEMP_ROOT/flags.out"
for flag in -n --just-print --dry-run --recon -t --touch -q --question -i --ignore-errors; do
  if (cd "$CONTROL_DIR" && PATH="$AUTHORITY_PATH" /usr/bin/make "$flag" --no-print-directory -f "$MAKEFILE" check) >"$TEMP_ROOT/flag.out" 2>&1; then exit 1; fi
  grep -Fq 'non-executing or error-ignoring MAKEFLAGS are not supported' "$TEMP_ROOT/flag.out"
done

printf '%s\n' 'Make authority tests passed: 45 target/authority cases, hostile literal Python and Xcode paths, 10 raw Make-syntax controls, 2 MAKEFILE_LIST rejections, 2 startup-boundary cases, 9 later recipe-replacement rejections, later root/tool/destination/derived-data and non-override shell protection, override/startup/PATH-Python boundary controls, PATH-Xcode rejection, dual derived-data cleanup containment, caller MAKEFLAGS rejection, and 10 mode rejections'
