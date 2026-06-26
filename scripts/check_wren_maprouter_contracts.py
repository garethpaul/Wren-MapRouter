#!/usr/bin/env python3
"""Static contracts for the Wren MapRouter legacy iOS sample."""

from pathlib import Path
import json
import plistlib
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
DOCS_PLANS = ROOT / "docs/plans"
CANONICAL_PLANS = [
    DOCS_PLANS / "2026-06-08-maprouter-location-url-contracts.md",
    DOCS_PLANS / "2026-06-08-maprouter-transit-mode-scope.md",
    DOCS_PLANS / "2026-06-08-maprouter-external-url-allowlist.md",
    DOCS_PLANS / "2026-06-09-maprouter-route-endpoint-encoding.md",
    DOCS_PLANS / "2026-06-09-maprouter-query-delimiter-encoding.md",
    DOCS_PLANS / "2026-06-09-maprouter-external-path-allowlist.md",
    DOCS_PLANS / "2026-06-09-maprouter-encoding-failure-cleanup.md",
    DOCS_PLANS / "2026-06-09-maprouter-incomplete-route-cleanup.md",
    DOCS_PLANS / "2026-06-09-maprouter-location-update-validation.md",
    DOCS_PLANS / "2026-06-09-maprouter-empty-endpoint-guard.md",
    DOCS_PLANS / "2026-06-09-maprouter-whitespace-endpoint-guard.md",
    DOCS_PLANS / "2026-06-10-maprouter-hosted-static-verification.md",
    DOCS_PLANS / "2026-06-10-maprouter-location-freshness.md",
    DOCS_PLANS / "2026-06-10-maprouter-horizontal-accuracy-validation.md",
    DOCS_PLANS / "2026-06-12-checkout-credential-boundary.md",
    DOCS_PLANS / "2026-06-13-maprouter-transient-location-errors.md",
    DOCS_PLANS / "2026-06-13-maprouter-background-route-cleanup.md",
    DOCS_PLANS / "2026-06-13-maprouter-transient-location-samples.md",
    DOCS_PLANS / "2026-06-14-maprouter-make-root-override-protection.md",
    DOCS_PLANS / "2026-06-21-maprouter-make-authority-isolation.md",
    DOCS_PLANS / "2026-06-26-wren-readme-routing-guide.md",
    DOCS_PLANS / "2026-06-26-maprouter-external-url-components.md",
]
WORKFLOW = ROOT / ".github/workflows/check.yml"
MAKEFILE = ROOT / "Makefile"
MAKE_AUTHORITY_SCRIPT = ROOT / "scripts/test-makefile-root.sh"
TRANSIT_MODES = {
    "MKDirectionsModeBus",
    "MKDirectionsModeFerry",
    "MKDirectionsModeStreetcar",
    "MKDirectionsModeSubway",
    "MKDirectionsModeTrain",
}


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def read_plist(relative_path, failures):
    try:
        with (ROOT / relative_path).open("rb") as plist_file:
            return plistlib.load(plist_file)
    except Exception as exc:
        failures.append(f"{relative_path} is not readable as a plist: {exc}")
        return {}


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def application_did_become_active_body(source):
    match = re.search(
        r"- \(void\) applicationDidBecomeActive:\(UIApplication \*\)application\s*\{(?P<body>.*?)\n\}",
        source,
        re.S,
    )
    return match.group("body") if match else ""


def main():
    failures = []

    app = read_text("GoogleTransit/AppDelegate.m")
    location_policy = read_text("GoogleTransit/LocationSamplePolicy.m") if (ROOT / "GoogleTransit/LocationSamplePolicy.m").is_file() else ""
    external_url_policy = read_text("GoogleTransit/ExternalDirectionsURLPolicy.m") if (ROOT / "GoogleTransit/ExternalDirectionsURLPolicy.m").is_file() else ""
    external_url_tests = read_text("GoogleTransitTests/ExternalDirectionsURLPolicyTests.m") if (ROOT / "GoogleTransitTests/ExternalDirectionsURLPolicyTests.m").is_file() else ""
    project = read_text("GoogleTransit.xcodeproj/project.pbxproj")
    plist = read_plist("GoogleTransit/GoogleTransit-Info.plist", failures)
    workflow = read_text(".github/workflows/check.yml") if WORKFLOW.is_file() else ""
    plans = sorted(DOCS_PLANS.glob("*.md")) if DOCS_PLANS.is_dir() else []
    readme = " ".join(read_text("README.md").split())
    vision = " ".join(read_text("VISION.md").split())
    changes = " ".join(read_text("CHANGES.md").split())

    for contract in (
        "This is a directions handoff sample, not a standalone map or route-planning UI.",
        "iOS 13 or newer",
        "`GoogleTransit` scheme",
        "Apple Maps directions request",
        "bus, ferry, streetcar, subway, or train",
        "When In Use location permission is requested only when",
        "permission is denied or restricted",
        "no more than 60 seconds old",
        "no worse than 1,000 meters horizontal accuracy",
        "`https://maps.google.com/maps`",
        "source, destination, and any resolved current-location coordinate",
        "clears pending route state",
        "rejects URL credentials, explicit ports, and fragments",
    ):
        require(contract in readme, "README routing guidance must include {0}".format(contract), failures)
    require(
        "Keep README setup, route handoff, and location permission behavior aligned with the app" in vision,
        "VISION must preserve setup, routing, and permission guidance",
        failures,
    )
    require(
        "Reject external URL credentials, explicit ports, and fragments" in vision,
        "VISION must preserve the exact external URL component boundary",
        failures,
    )
    require(
        "Apple Maps-to-Google Maps transit handoff" in changes,
        "CHANGES must record the documented route handoff",
        failures,
    )
    require(
        "External URL admission rejects credentials, explicit ports, and fragments." in changes,
        "CHANGES must record the exact external URL component boundary",
        failures,
    )

    try:
        geojson = json.loads(read_text("GoogleTransit/Directions.geojson"))
    except Exception as exc:
        failures.append(f"GoogleTransit/Directions.geojson is not valid JSON: {exc}")
        geojson = {}

    modes = plist.get("MKDirectionsApplicationSupportedModes", [])
    document_types = plist.get("CFBundleDocumentTypes", [])
    content_types = [
        item
        for document_type in document_types
        for item in document_type.get("LSItemContentTypes", [])
    ]

    require(
        "com.apple.maps.directionsrequest" in content_types,
        "Info.plist must register the Maps directions request document type",
        failures,
    )
    require(
        plist.get("NSLocationWhenInUseUsageDescription"),
        "Info.plist must include a when-in-use location usage description",
        failures,
    )
    require(
        len(modes) == len(set(modes)),
        "Info.plist must not duplicate MKDirections supported modes",
        failures,
    )
    non_transit_modes = sorted(set(modes) - TRANSIT_MODES)
    require(
        not non_transit_modes,
        "Info.plist must only advertise transit-compatible modes: " + ", ".join(non_transit_modes),
        failures,
    )
    require(
        geojson.get("type") == "MultiPolygon",
        "Directions.geojson must remain a MultiPolygon coverage artifact",
        failures,
    )
    require(
        "coordinates" in geojson,
        "Directions.geojson must include coordinates",
        failures,
    )

    active_body = application_did_become_active_body(app)
    require(
        "startUpdatingLocation" not in active_body,
        "applicationDidBecomeActive must not start location updates unconditionally",
        failures,
    )
    require(
        "requestWhenInUseAuthorization" in app
        and "authorizationStatus" in app
        and "locationServicesEnabled" in app,
        "location updates must check services, authorization, and request when-in-use access",
        failures,
    )
    require(
        "kCLAuthorizationStatusDenied" in app
        and "kCLAuthorizationStatusRestricted" in app
        and "clearPendingRoute" in app,
        "denied or restricted location access must clear pending route state",
        failures,
    )
    require(
        "currentSourceNeedsLocation" in app and "currentDestinationNeedsLocation" in app,
        "directions requests must remember which endpoint depends on current location",
        failures,
    )
    require(
        "CLLocationCoordinate2DIsValid" in app,
        "route endpoint formatting must reject invalid coordinates",
        failures,
    )
    require(
        "directionsRequest.source.placemark.location.coordinate" not in app
        and "directionsRequest.destination.placemark.location.coordinate" not in app,
        "directions parsing must not dereference placemark locations without guards",
        failures,
    )
    require(
        "canOpenURL:url" in app,
        "external map forwarding must check canOpenURL before opening",
        failures,
    )
    require(
        "ExternalDirectionsURLPolicy" in app
        and "[ExternalDirectionsURLPolicy isAllowedURL:url]" in app,
        "AppDelegate must delegate external URL admission to the tested policy",
        failures,
    )
    for contract in (
        '[[url scheme] isEqualToString:@"https"]',
        '[[url host] isEqualToString:@"maps.google.com"]',
        '[[url path] isEqualToString:@"/maps"]',
        "[url user] == nil",
        "[url password] == nil",
        "[url port] == nil",
        "[url fragment] == nil",
    ):
        require(
            contract in external_url_policy,
            "external URL policy must preserve component contract {0}".format(contract),
            failures,
        )
    for test_contract in (
        "testAllowsCanonicalGoogleMapsDirectionsURL",
        "testRejectsAuthorityDecorationsAndFragments",
        "https://user@maps.google.com/maps",
        "https://maps.google.com:443/maps",
        "https://maps.google.com:444/maps",
        "#fragment",
    ):
        require(
            test_contract in external_url_tests,
            "native tests must preserve external URL contract {0}".format(test_contract),
            failures,
        )
    require(
        "[ExternalDirectionsURLPolicy isAllowedURL:url]" in app
        and app.index("[ExternalDirectionsURLPolicy isAllowedURL:url]") < app.index("canOpenURL:url"),
        "external URL allowlist must be checked before canOpenURL/openURL",
        failures,
    )
    for project_contract in (
        "ExternalDirectionsURLPolicy.h",
        "ExternalDirectionsURLPolicy.m",
        "ExternalDirectionsURLPolicy.m in Sources",
        "ExternalDirectionsURLPolicyTests.m",
        "ExternalDirectionsURLPolicyTests.m in Sources",
    ):
        require(
            project_contract in project,
            "Xcode project must include {0}".format(project_contract),
            failures,
        )
    require(
        "openTransitDirections" in app and "clearPendingRoute" in app,
        "route state must be cleared after forwarding or cancellation",
        failures,
    )
    require(
        "encodedRouteEndpoint" in app
        and "stringByAddingPercentEncodingWithAllowedCharacters" in app
        and '[allowedCharacters addCharactersInString:@"-._~"]' in app
        and "URLQueryAllowedCharacterSet" not in app,
        "route endpoints must escape URL query delimiters before external forwarding",
        failures,
    )
    trim_endpoint_index = app.find(
        "NSString *trimmedEndpoint = [endpoint stringByTrimmingCharactersInSet:"
    )
    empty_endpoint_index = app.find("if ([trimmedEndpoint length] == 0)", trim_endpoint_index)
    encoding_call_index = app.find("stringByAddingPercentEncodingWithAllowedCharacters")
    require(
        empty_endpoint_index != -1
        and encoding_call_index != -1
        and app.find("return nil;", empty_endpoint_index) < encoding_call_index
        and empty_endpoint_index < encoding_call_index,
        "route endpoint encoder must reject empty strings before percent encoding",
        failures,
    )
    require(
        trim_endpoint_index != -1
        and "whitespaceAndNewlineCharacterSet" in app
        and trim_endpoint_index < empty_endpoint_index < encoding_call_index,
        "route endpoint encoder must trim whitespace before empty checks and percent encoding",
        failures,
    )
    require(
        "NSString *source = [self encodedRouteEndpoint:self.currentSource]" in app
        and "NSString *destination = [self encodedRouteEndpoint:self.currentDestination]" in app
        and "source, destination" in app,
        "Google Maps URL construction must use encoded route endpoints",
        failures,
    )
    encoding_failure_index = app.find("if (!source || !destination)")
    encoding_cleanup_index = app.find("[self clearPendingRoute];", encoding_failure_index)
    encoding_return_index = app.find("return;", encoding_cleanup_index)
    url_string_index = app.find("NSString *directionsURLString", encoding_return_index)
    require(
        encoding_failure_index != -1
        and encoding_cleanup_index != -1
        and encoding_return_index != -1
        and url_string_index != -1
        and encoding_failure_index < encoding_cleanup_index < encoding_return_index < url_string_index,
        "route state must be cleared when endpoint encoding fails",
        failures,
    )
    incomplete_route_index = app.find("if (!self.currentSource || !self.currentDestination)")
    wait_for_location_index = app.find("if (![self routeNeedsCurrentLocation])", incomplete_route_index)
    incomplete_cleanup_index = app.find("[self clearPendingRoute];", wait_for_location_index)
    incomplete_return_index = app.find("return;", incomplete_cleanup_index)
    encode_source_index = app.find("NSString *source = [self encodedRouteEndpoint:self.currentSource]")
    require(
        incomplete_route_index != -1
        and wait_for_location_index != -1
        and incomplete_cleanup_index != -1
        and incomplete_return_index != -1
        and incomplete_route_index < wait_for_location_index < incomplete_cleanup_index < incomplete_return_index < encode_source_index,
        "incomplete non-location routes must clear pending state before endpoint encoding",
        failures,
    )
    location_update_index = app.find("didUpdateLocations")
    coordinate_method_index = app.find("- (NSString *) coordinateStringForLocation:(CLLocation *)location")
    coordinate_accuracy_index = app.find("!isfinite(location.horizontalAccuracy)", coordinate_method_index)
    coordinate_value_index = app.find("CLLocationCoordinate2D coordinate = location.coordinate;", coordinate_method_index)
    require(
        coordinate_method_index != -1
        and coordinate_accuracy_index != -1
        and coordinate_value_index != -1
        and coordinate_method_index < coordinate_accuracy_index < coordinate_value_index,
        "route endpoint conversion must reject locations with invalid horizontal accuracy",
        failures,
    )
    route_guard_index = app.find("if (![self routeNeedsCurrentLocation])", location_update_index)
    sample_selection_index = app.find("newestUsableLocationFromLocations:locations", route_guard_index)
    invalid_location_index = app.find("if (!latestLocation)", sample_selection_index)
    invalid_return_index = app.find("return;", invalid_location_index)
    assign_location_index = app.find("self.currentLocation = latestLocation;", invalid_return_index)
    require(
        "self.currentLocation = [locations lastObject]" not in app,
        "location updates must not store unvalidated latest locations",
        failures,
    )
    require(
        route_guard_index != -1
        and sample_selection_index != -1
        and invalid_location_index != -1
        and invalid_return_index != -1
        and assign_location_index != -1
        and route_guard_index < sample_selection_index < invalid_location_index < invalid_return_index < assign_location_index,
        "late location callbacks must not retain coordinates after route cancellation",
        failures,
    )
    require(
        "newestUsableLocationFromLocations:locations" in app,
        "location updates must select the newest usable sample instead of trusting the final sample",
        failures,
    )
    require(
        "isfinite(location.horizontalAccuracy)" in location_policy
        and "LocationSampleMaximumHorizontalAccuracy = 1000" in location_policy
        and "location.horizontalAccuracy > LocationSampleMaximumHorizontalAccuracy" in location_policy,
        "location policy must reject non-finite and excessively inaccurate samples",
        failures,
    )
    require(
        "isfinite(locationAge)" in location_policy,
        "location policy must reject non-finite sample ages",
        failures,
    )
    require(
        "[locations reverseObjectEnumerator]" in location_policy,
        "location policy must inspect callback batches from newest to oldest",
        failures,
    )
    require(
        "self.window.rootViewController = [[UIViewController alloc] init];" in app,
        "current iOS launches require a root view controller",
        failures,
    )
    require(
        project.count("IPHONEOS_DEPLOYMENT_TARGET = 13.0;") >= 4,
        "Xcode project must use a deployment target supported by the current SDK",
        failures,
    )
    require(
        "GoogleTransitTests" in project and "com.apple.product-type.bundle.unit-test" in project,
        "Xcode project must include the native XCTest target",
        failures,
    )
    resign_match = re.search(
        r"- \(void\) applicationWillResignActive:\(UIApplication \*\)application"
        r"\s*\{(?P<body>.*?)\n\}",
        app,
        re.S,
    )
    resign_body = resign_match.group("body") if resign_match else ""
    background_match = re.search(
        r"- \(void\) applicationDidEnterBackground:\(UIApplication \*\)application"
        r"\s*\{(?P<body>.*?)\n\}",
        app,
        re.S,
    )
    background_body = background_match.group("body") if background_match else ""
    background_method_index = app.find("applicationDidEnterBackground")
    route_handler_index = app.find("application:(UIApplication *)application openURL:")
    require(
        "[self clearPendingRoute];" not in resign_body,
        "temporary resign-active transitions must preserve pending routes",
        failures,
    )
    require(
        background_match is not None
        and background_body.count("[self clearPendingRoute];") == 1
        and background_method_index < route_handler_index,
        "background entry must clear pending routes before later route handling",
        failures,
    )
    location_failure_match = re.search(
        r"- \(void\)locationManager:\(CLLocationManager \*\)manager "
        r"didFailWithError:\(NSError \*\)error\s*\{(?P<body>.*?)\n\}",
        app,
        re.S,
    )
    location_failure_body = location_failure_match.group("body") if location_failure_match else ""
    transient_domain_index = location_failure_body.find(
        "[[error domain] isEqualToString:kCLErrorDomain]"
    )
    transient_code_index = location_failure_body.find(
        "[error code] == kCLErrorLocationUnknown", transient_domain_index
    )
    transient_return_index = location_failure_body.find("return;", transient_code_index)
    terminal_cleanup_index = location_failure_body.find(
        "[self clearPendingRoute];", transient_return_index
    )
    require(
        location_failure_match is not None
        and transient_domain_index != -1
        and transient_code_index != -1
        and transient_return_index != -1
        and terminal_cleanup_index != -1
        and location_failure_body.count("[self clearPendingRoute];") == 1
        and transient_domain_index
        < transient_code_index
        < transient_return_index
        < terminal_cleanup_index,
        "transient Core Location failures must preserve pending routes before terminal cleanup",
        failures,
    )
    require(WORKFLOW.is_file(), "hosted verification workflow must exist", failures)
    require(
        "permissions:\n  contents: read" in workflow,
        "hosted verification permissions must be read-only",
        failures,
    )
    require(
        "python-version: ['3.10', '3.12', '3.14']" in workflow,
        "hosted verification must cover Python 3.10, 3.12, and 3.14",
        failures,
    )
    require(
        "workflow_dispatch:" in workflow,
        "hosted verification must support manual dispatch",
        failures,
    )
    require(
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10" in workflow,
        "checkout must use an immutable revision",
        failures,
    )
    require(
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405" in workflow,
        "setup-python must use an immutable revision",
        failures,
    )
    require("timeout-minutes: 5" in workflow, "hosted verification must have a timeout", failures)
    require(
        "run: /usr/bin/make check" in workflow,
        "hosted verification must run the trusted system Make authority",
        failures,
    )
    require(
        "run: /usr/bin/make build" in workflow
        and '/usr/bin/make xctest TEST_DESTINATION="platform=iOS Simulator,id=${device_id}"' in workflow,
        "native verification must use the trusted system Make authority",
        failures,
    )
    require("concurrency:" in workflow, "hosted verification must define concurrency", failures)
    require(
        "cancel-in-progress: true" in workflow,
        "hosted verification must cancel superseded runs",
        failures,
    )
    require(
        "runs-on: ubuntu-24.04" in workflow,
        "hosted verification must use a fixed Ubuntu runner",
        failures,
    )
    require("ubuntu-latest" not in workflow, "hosted verification must not use a floating runner", failures)
    workflow_files = sorted(
        path.relative_to(ROOT).as_posix()
        for path in WORKFLOW.parent.iterdir()
        if path.is_file()
    )
    checkout_step = (
        "      - name: Check out repository\n"
        "        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3\n"
        "        with:\n"
        "          persist-credentials: false"
    )
    require(
        workflow_files == [".github/workflows/check.yml"],
        "workflow inventory must contain only .github/workflows/check.yml",
        failures,
    )
    require(
        workflow.count("actions/checkout@") == 2
        and workflow.count(checkout_step) == 2,
        "hosted verification must use pinned credential-free checkout steps",
        failures,
    )
    require(
        workflow.count("persist-credentials:") == 2
        and workflow.count("persist-credentials: false") == 2
        and "persist-credentials: true" not in workflow,
        "hosted verification must not persist checkout credentials",
        failures,
    )
    checkout_plan = read_text("docs/plans/2026-06-12-checkout-credential-boundary.md")
    require(
        "status: completed" in checkout_plan.lower()
        and "persist-credentials: false" in checkout_plan
        and "hostile mutations rejected" in checkout_plan,
        "checkout credential plan must record completed verification",
        failures,
    )
    guidance = " ".join(
        "\n".join(read_text(path) for path in ["README.md", "SECURITY.md", "VISION.md", "CHANGES.md"]).split()
    ).lower()
    require(
        "checkout credentials are not persisted" in guidance
        and "credential-free checkout" in guidance,
        "repository guidance must document the credential-free checkout boundary",
        failures,
    )
    for boundary in (
        "target-specific override shell",
        "startup parse-time code",
        "default path-selected python",
        "caller authority",
    ):
        require(
            boundary in guidance,
            "repository guidance must document caller Make boundary {0!r}".format(boundary),
            failures,
        )
    makefile = MAKEFILE.read_text(encoding="utf-8")
    makefile_lines = set(makefile.splitlines())
    for contract in (
        ".DEFAULT_GOAL := check",
        ".SECONDEXPANSION:",
        "PYTHON ?= python3",
        "override PYTHON := $(value PYTHON)",
        "XCODEBUILD ?= /usr/bin/xcodebuild",
        "override XCODEBUILD := $(value XCODEBUILD)",
        "override BUILD_DESTINATION := $(value BUILD_DESTINATION)",
        "override TEST_DESTINATION := $(value TEST_DESTINATION)",
        "override BUILD_DERIVED_DATA := $(ROOT)/.build/build-derived-data",
        "override TEST_DERIVED_DATA := $(ROOT)/.build/test-derived-data",
        "override SHELL := /bin/sh",
        "override .SHELLFLAGS := -c",
        "override MAKEFILES :=",
        "ifneq ($(origin MAKEFILE_LIST),file)",
        "export ROOT",
        "root-test::",
        "\t/bin/sh '$(REPOSITORY_ROOT_LITERAL)/scripts/test-makefile-root.sh'",
        "verify:: root-test lint test mutations build xctest",
    ):
        require(
            contract in makefile_lines,
            "Makefile authority contract is missing {0!r}".format(contract),
            failures,
        )
    require("MAKEFLAGS must not be overridden" in makefile, "Makefile must reject caller MAKEFLAGS", failures)
    require("MAKEFILES must be empty" in makefile, "Makefile must reject startup files", failures)
    require("MAKEFILE_LIST must not be overridden" in makefile, "Makefile must reject Makefile-list replacement", failures)
    require(
        "$(error $(1) must be a literal value, not Make syntax)" in makefile
        and "$(foreach variable,PYTHON XCODEBUILD BUILD_DESTINATION TEST_DESTINATION,$(eval $(call REPOSITORY_REJECT_MAKE_SYNTAX,$(variable))))"
        in makefile,
        "Makefile must reject Make syntax in tool and destination values",
        failures,
    )
    require(
        "'$(REPOSITORY_ROOT_LITERAL)/scripts/check_wren_maprouter_contracts.py'" in makefile
        and "'$(REPOSITORY_ROOT_LITERAL)/scripts/run_mutation_checks.py'" in makefile,
        "Makefile must use rooted checker and mutation paths",
        failures,
    )
    for python_contract in (
        "'$(REPOSITORY_PYTHON_LITERAL)' -I -B -m py_compile",
        "'$(REPOSITORY_PYTHON_LITERAL)' -I -B '$(REPOSITORY_ROOT_LITERAL)/scripts/check_wren_maprouter_contracts.py'",
        "'$(REPOSITORY_PYTHON_LITERAL)' -I -B '$(REPOSITORY_ROOT_LITERAL)/scripts/run_mutation_checks.py'",
    ):
        require(
            python_contract in makefile,
            "Python verification must remain isolated from PYTHONPATH and user site state",
            failures,
        )
    require(
        "'$(REPOSITORY_ROOT_LITERAL)/GoogleTransit.xcodeproj'" in makefile
        and "-derivedDataPath '$(REPOSITORY_BUILD_DERIVED_DATA_LITERAL)'" in makefile
        and "-derivedDataPath '$(REPOSITORY_TEST_DERIVED_DATA_LITERAL)'" in makefile
        and "/bin/rm -rf '$(REPOSITORY_BUILD_DERIVED_DATA_LITERAL)'" in makefile
        and "'$(REPOSITORY_TEST_DERIVED_DATA_LITERAL)'" in makefile,
        "optional Xcode build and test must use rooted project and derived-data paths",
        failures,
    )
    require(
        MAKE_AUTHORITY_SCRIPT.is_file() and MAKE_AUTHORITY_SCRIPT.stat().st_mode & 0o111,
        "Make authority harness must exist and be executable",
        failures,
    )
    authority_source = MAKE_AUTHORITY_SCRIPT.read_text(encoding="utf-8")
    for contract in (
        "45 target/authority cases",
        "10 raw Make-syntax controls",
        "2 MAKEFILE_LIST rejections",
        "2 startup-boundary cases",
        "9 later recipe-replacement rejections",
        "PYTHONPATH isolation",
        "PATH-Xcode rejection",
        "xcodebuild unavailable; skipping legacy iOS build",
        "dual derived-data cleanup containment",
        "10 mode rejections",
    ):
        require(
            contract in authority_source,
            "Make authority harness must retain {0}".format(contract),
            failures,
        )
    require(DOCS_PLANS.is_dir(), "docs/plans must exist", failures)
    for plan in CANONICAL_PLANS:
        require(plan in plans, f"{plan.relative_to(ROOT)} must be present", failures)
    for plan in plans:
        text = plan.read_text(encoding="utf-8")
        require(
            "status: completed" in text.lower() or "Status: Completed" in text,
            f"{plan.relative_to(ROOT)} must be completed",
            failures,
        )
        require("make check" in text, f"{plan.relative_to(ROOT)} must document make check verification", failures)

    if failures:
        print("Wren MapRouter contract check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wren MapRouter contract check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
