.PHONY: lint test mutations build xctest verify check

PYTHON ?= python3
override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
CHECK_SCRIPT := $(ROOT)/scripts/check_wren_maprouter_contracts.py
PROJECT := $(ROOT)/GoogleTransit.xcodeproj
BUILD_DESTINATION ?= generic/platform=iOS Simulator
TEST_DESTINATION ?= platform=iOS Simulator,name=iPhone 16 Pro
BUILD_DERIVED_DATA ?= $(ROOT)/.build/build-derived-data
TEST_DERIVED_DATA ?= $(ROOT)/.build/test-derived-data

lint:
	$(PYTHON) -m py_compile "$(CHECK_SCRIPT)"

test:
	$(PYTHON) "$(CHECK_SCRIPT)"

mutations:
	$(PYTHON) "$(ROOT)/scripts/run_mutation_checks.py"

build:
	@if command -v xcodebuild >/dev/null 2>&1; then \
		rm -rf "$(BUILD_DERIVED_DATA)"; \
		xcodebuild -project "$(PROJECT)" -scheme GoogleTransit -destination "$(BUILD_DESTINATION)" -derivedDataPath "$(BUILD_DERIVED_DATA)" CODE_SIGNING_ALLOWED=NO build; \
	else \
		echo "xcodebuild unavailable; skipping legacy iOS build"; \
	fi

xctest:
	@if command -v xcodebuild >/dev/null 2>&1; then \
		rm -rf "$(TEST_DERIVED_DATA)"; \
		xcodebuild -project "$(PROJECT)" -scheme GoogleTransitTests -destination "$(TEST_DESTINATION)" -derivedDataPath "$(TEST_DERIVED_DATA)" CODE_SIGNING_ALLOWED=NO test; \
	else \
		echo "xcodebuild unavailable; skipping native XCTest"; \
	fi

verify: lint test mutations build xctest

check: verify
