.PHONY: lint test build verify check

PYTHON ?= python3
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
CHECK_SCRIPT := $(ROOT)/scripts/check_wren_maprouter_contracts.py
PROJECT := $(ROOT)/GoogleTransit.xcodeproj

lint:
	$(PYTHON) -m py_compile "$(CHECK_SCRIPT)"

test:
	$(PYTHON) "$(CHECK_SCRIPT)"

build:
	@if command -v xcodebuild >/dev/null 2>&1; then \
		xcodebuild -project "$(PROJECT)" -target GoogleTransit -sdk iphonesimulator CODE_SIGNING_ALLOWED=NO build; \
	else \
		echo "xcodebuild unavailable; skipping legacy iOS build"; \
	fi

verify: lint test build

check: verify
