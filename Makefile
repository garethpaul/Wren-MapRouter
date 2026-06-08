.PHONY: lint test build verify check

PYTHON ?= python3

lint:
	$(PYTHON) -m py_compile scripts/check_wren_maprouter_contracts.py

test:
	$(PYTHON) scripts/check_wren_maprouter_contracts.py

build:
	@if command -v xcodebuild >/dev/null 2>&1; then \
		xcodebuild -project GoogleTransit.xcodeproj -target GoogleTransit -sdk iphonesimulator CODE_SIGNING_ALLOWED=NO build; \
	else \
		echo "xcodebuild unavailable; skipping legacy iOS build"; \
	fi

verify: lint test build

check: verify
