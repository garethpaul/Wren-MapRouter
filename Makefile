.DEFAULT_GOAL := check
.PHONY: __repository-make-authority build check clean lint mutations root-test test verify xctest
.SECONDEXPANSION:

PYTHON ?= python3
override PYTHON := $(value PYTHON)
export PYTHON
XCODEBUILD ?= /usr/bin/xcodebuild
override XCODEBUILD := $(value XCODEBUILD)
export XCODEBUILD
BUILD_DESTINATION ?= generic/platform=iOS Simulator
override BUILD_DESTINATION := $(value BUILD_DESTINATION)
export BUILD_DESTINATION
TEST_DESTINATION ?= platform=iOS Simulator,name=iPhone 16 Pro
override TEST_DESTINATION := $(value TEST_DESTINATION)
export TEST_DESTINATION
override REPOSITORY_MAKE_DOLLAR := $$
override REPOSITORY_MAKE_OPEN := (
override REPOSITORY_MAKE_OPEN_BRACE := {
define REPOSITORY_REJECT_MAKE_SYNTAX
ifneq ($$(findstring $$(REPOSITORY_MAKE_DOLLAR)$$(REPOSITORY_MAKE_OPEN),$$(value $(1))),)
$$(error $(1) must be a literal value, not Make syntax)
endif
ifneq ($$(findstring $$(REPOSITORY_MAKE_DOLLAR)$$(REPOSITORY_MAKE_OPEN_BRACE),$$(value $(1))),)
$$(error $(1) must be a literal value, not Make syntax)
endif
endef
$(foreach variable,PYTHON XCODEBUILD BUILD_DESTINATION TEST_DESTINATION,$(eval $(call REPOSITORY_REJECT_MAKE_SYNTAX,$(variable))))

override SHELL := /bin/sh
override .SHELLFLAGS := -c
build check clean lint mutations root-test test verify xctest __repository-make-authority: override SHELL := /bin/sh
build check clean lint mutations root-test test verify xctest __repository-make-authority: override .SHELLFLAGS := -c

ifneq ($(filter command line,$(origin MAKEFLAGS)),)
$(error MAKEFLAGS must not be overridden for repository verification)
endif
override REPOSITORY_MAKE_FIRST_FLAGS := $(firstword $(MAKEFLAGS))
ifneq ($(filter -%,$(REPOSITORY_MAKE_FIRST_FLAGS)),)
override REPOSITORY_MAKE_FIRST_FLAGS :=
endif
override REPOSITORY_MAKE_SHORT_FLAGS := $(REPOSITORY_MAKE_FIRST_FLAGS) $(filter-out --%,$(filter -%,$(MAKEFLAGS)))
ifneq ($(findstring n,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring t,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring q,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring i,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(filter --just-print --dry-run --recon --touch --question --ignore-errors,$(MAKEFLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(strip $(MAKEFILES)),)
$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)
endif
override MAKEFILES :=
ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(value MAKEFILE_LIST))'; path=$$(printf '%s' "$$path" | /usr/bin/sed 's/^ //'); [ -f "$$path" ] || exit 1; directory=$$(/usr/bin/dirname -- "$$path"); CDPATH= cd -- "$$directory" && /bin/pwd -P)
export ROOT
ifeq ($(strip $(ROOT)),)
$(error repository Makefile path could not be resolved)
endif
override BUILD_DERIVED_DATA := $(ROOT)/.build/build-derived-data
override TEST_DERIVED_DATA := $(ROOT)/.build/test-derived-data
override REPOSITORY_SHELL_LITERAL = $(subst $$,$$$$,$(subst ','"'"',$1))
override REPOSITORY_ROOT_LITERAL := $(call REPOSITORY_SHELL_LITERAL,$(ROOT))
override REPOSITORY_PYTHON_LITERAL := $(call REPOSITORY_SHELL_LITERAL,$(PYTHON))
override REPOSITORY_XCODEBUILD_LITERAL := $(call REPOSITORY_SHELL_LITERAL,$(XCODEBUILD))
override REPOSITORY_BUILD_DESTINATION_LITERAL := $(call REPOSITORY_SHELL_LITERAL,$(BUILD_DESTINATION))
override REPOSITORY_TEST_DESTINATION_LITERAL := $(call REPOSITORY_SHELL_LITERAL,$(TEST_DESTINATION))
override REPOSITORY_BUILD_DERIVED_DATA_LITERAL := $(call REPOSITORY_SHELL_LITERAL,$(BUILD_DERIVED_DATA))
override REPOSITORY_TEST_DERIVED_DATA_LITERAL := $(call REPOSITORY_SHELL_LITERAL,$(TEST_DERIVED_DATA))

build check clean lint mutations root-test test verify xctest:: $$(if $$(filter file,$$(origin MAKEFILE_LIST)),,$$(error MAKEFILE_LIST must not be overridden))
build check clean lint mutations root-test test verify xctest:: $$(if $$(shell path=$$$$(/usr/bin/printf '%s' '$$(subst ','"'"',$$(MAKEFILE_LIST))' | /usr/bin/sed 's/^ //') && [ -f "$$$$path" ] && /usr/bin/printf '%s' ok),,$$(error repository Makefile must be loaded alone))
build check clean lint mutations root-test test verify xctest:: __repository-make-authority

__repository-make-authority::
	@:

define REPOSITORY_PUBLIC_RECIPES
clean::
	/bin/rm -rf '$(REPOSITORY_BUILD_DERIVED_DATA_LITERAL)' '$(REPOSITORY_TEST_DERIVED_DATA_LITERAL)'
	/usr/bin/find '$(REPOSITORY_ROOT_LITERAL)' -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	/usr/bin/find '$(REPOSITORY_ROOT_LITERAL)' -type d -name '__pycache__' -prune -exec /bin/rm -rf {} +

lint::
	'$(REPOSITORY_PYTHON_LITERAL)' -I -B -m py_compile '$(REPOSITORY_ROOT_LITERAL)/scripts/check_wren_maprouter_contracts.py' '$(REPOSITORY_ROOT_LITERAL)/scripts/run_mutation_checks.py'

test::
	'$(REPOSITORY_PYTHON_LITERAL)' -I -B '$(REPOSITORY_ROOT_LITERAL)/scripts/check_wren_maprouter_contracts.py'

mutations::
	'$(REPOSITORY_PYTHON_LITERAL)' -I -B '$(REPOSITORY_ROOT_LITERAL)/scripts/run_mutation_checks.py'

build::
	@if [ -x '$(REPOSITORY_XCODEBUILD_LITERAL)' ]; then \
		/bin/rm -rf '$(REPOSITORY_BUILD_DERIVED_DATA_LITERAL)'; \
		'$(REPOSITORY_XCODEBUILD_LITERAL)' -project '$(REPOSITORY_ROOT_LITERAL)/GoogleTransit.xcodeproj' -scheme GoogleTransit -destination '$(REPOSITORY_BUILD_DESTINATION_LITERAL)' -derivedDataPath '$(REPOSITORY_BUILD_DERIVED_DATA_LITERAL)' CODE_SIGNING_ALLOWED=NO build; \
	else \
		/usr/bin/printf '%s\n' 'xcodebuild unavailable; skipping legacy iOS build'; \
	fi

xctest::
	@if [ -x '$(REPOSITORY_XCODEBUILD_LITERAL)' ]; then \
		/bin/rm -rf '$(REPOSITORY_TEST_DERIVED_DATA_LITERAL)'; \
		'$(REPOSITORY_XCODEBUILD_LITERAL)' -project '$(REPOSITORY_ROOT_LITERAL)/GoogleTransit.xcodeproj' -scheme GoogleTransitTests -destination '$(REPOSITORY_TEST_DESTINATION_LITERAL)' -derivedDataPath '$(REPOSITORY_TEST_DERIVED_DATA_LITERAL)' CODE_SIGNING_ALLOWED=NO test; \
	else \
		/usr/bin/printf '%s\n' 'xcodebuild unavailable; skipping native XCTest'; \
	fi

root-test::
	/bin/sh '$(REPOSITORY_ROOT_LITERAL)/scripts/test-makefile-root.sh'

verify:: root-test lint test mutations build xctest

check:: clean verify
	/usr/bin/find '$(REPOSITORY_ROOT_LITERAL)' -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	/usr/bin/find '$(REPOSITORY_ROOT_LITERAL)' -type d -name '__pycache__' -prune -exec /bin/rm -rf {} +
endef

$(eval $(REPOSITORY_PUBLIC_RECIPES))
