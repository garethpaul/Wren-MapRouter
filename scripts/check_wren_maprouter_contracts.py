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
]
WORKFLOW = ROOT / ".github/workflows/check.yml"
MAKEFILE = ROOT / "Makefile"
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
    plist = read_plist("GoogleTransit/GoogleTransit-Info.plist", failures)
    workflow = read_text(".github/workflows/check.yml") if WORKFLOW.is_file() else ""
    plans = sorted(DOCS_PLANS.glob("*.md")) if DOCS_PLANS.is_dir() else []

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
        "isAllowedExternalURL" in app
        and 'isEqualToString:@"https"' in app
        and 'isEqualToString:@"maps.google.com"' in app,
        "external URL forwarding must be restricted to HTTPS Google Maps URLs",
        failures,
    )
    require(
        '[[url path] isEqualToString:@"/maps"]' in app,
        "external URL forwarding must be restricted to the Google Maps route path",
        failures,
    )
    require(
        "[self isAllowedExternalURL:url]" in app
        and app.index("[self isAllowedExternalURL:url]") < app.index("canOpenURL:url"),
        "external URL allowlist must be checked before canOpenURL/openURL",
        failures,
    )
    require(
        "openTransitDirections" in app and "clearPendingRoute" in app,
        "route state must be cleared after forwarding or cancellation",
        failures,
    )
    require(
        "encodedRouteEndpoint" in app
        and "CFURLCreateStringByAddingPercentEscapes" in app
        and ":/?#[]@!$&'()*+,;=" in app
        and "stringByAddingPercentEscapesUsingEncoding" not in app,
        "route endpoints must escape URL query delimiters before external forwarding",
        failures,
    )
    trim_endpoint_index = app.find(
        "NSString *trimmedEndpoint = [endpoint stringByTrimmingCharactersInSet:"
    )
    empty_endpoint_index = app.find("if ([trimmedEndpoint length] == 0)", trim_endpoint_index)
    encoding_call_index = app.find("CFURLCreateStringByAddingPercentEscapes")
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
        and "(__bridge CFStringRef)trimmedEndpoint" in app
        and "(__bridge CFStringRef)endpoint" not in app
        and trim_endpoint_index < empty_endpoint_index < encoding_call_index,
        "route endpoint encoder must trim whitespace before empty checks and percent encoding",
        failures,
    )
    require(
        "CFBridgingRelease(encodedEndpoint)" in app,
        "route endpoint encoder must transfer its CoreFoundation string under ARC",
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
    coordinate_accuracy_index = app.find("if (location.horizontalAccuracy < 0)", coordinate_method_index)
    coordinate_value_index = app.find("CLLocationCoordinate2D coordinate = location.coordinate;", coordinate_method_index)
    require(
        coordinate_method_index != -1
        and coordinate_accuracy_index != -1
        and coordinate_value_index != -1
        and coordinate_method_index < coordinate_accuracy_index < coordinate_value_index,
        "route endpoint conversion must reject locations with invalid horizontal accuracy",
        failures,
    )
    latest_location_index = app.find("CLLocation *latestLocation = [locations lastObject];", location_update_index)
    invalid_location_index = app.find("if (!latestLocation", latest_location_index)
    invalid_coordinate_index = app.find(
        "!CLLocationCoordinate2DIsValid(latestLocation.coordinate)", invalid_location_index
    )
    update_accuracy_index = app.find("latestLocation.horizontalAccuracy < 0", invalid_location_index)
    invalid_return_index = app.find("return;", invalid_location_index)
    location_age_index = app.find("NSTimeInterval locationAge", invalid_return_index)
    assign_location_index = app.find("self.currentLocation = latestLocation;", invalid_return_index)
    require(
        latest_location_index != -1
        and invalid_location_index != -1
        and invalid_coordinate_index != -1
        and invalid_return_index != -1
        and location_age_index != -1
        and assign_location_index != -1
        and latest_location_index
        < invalid_location_index
        < invalid_coordinate_index
        < invalid_return_index
        < location_age_index
        < assign_location_index,
        "unusable location samples must return before freshness checks and storage",
        failures,
    )
    require(
        update_accuracy_index != -1
        and invalid_coordinate_index < update_accuracy_index < invalid_return_index,
        "location updates must reject negative horizontal accuracy before returning",
        failures,
    )
    invalid_sample_body = app[invalid_location_index:invalid_return_index]
    require(
        "clearPendingRoute" not in invalid_sample_body,
        "transient unusable samples must preserve the pending route and active updates",
        failures,
    )
    require(
        "if (!latestLocation ||\n"
        "\t\t!CLLocationCoordinate2DIsValid(latestLocation.coordinate) ||\n"
        "\t\tlatestLocation.horizontalAccuracy < 0){\n"
        "\t\treturn;\n"
        "\t}" in app,
        "unusable location samples must use an unconditional early return",
        failures,
    )
    require(
        "self.currentLocation = [locations lastObject]" not in app,
        "location updates must not store unvalidated latest locations",
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
    freshness_index = app.find("NSTimeInterval locationAge = -[latestLocation.timestamp timeIntervalSinceNow];")
    stale_guard_index = app.find("if (locationAge < 0 || locationAge > 60)", freshness_index)
    stale_return_index = app.find("return;", stale_guard_index)
    require(
        freshness_index != -1
        and stale_guard_index != -1
        and stale_return_index != -1
        and assign_location_index != -1
        and freshness_index < stale_guard_index < stale_return_index < assign_location_index,
        "location updates must ignore future-dated and stale cached coordinates before storing them",
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
    require("run: make check" in workflow, "hosted verification must run make check", failures)
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
        workflow.count("actions/checkout@") == 1 and checkout_step in workflow,
        "hosted verification must use one pinned credential-free checkout",
        failures,
    )
    require(
        workflow.count("persist-credentials:") == 1
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
    makefile = MAKEFILE.read_text(encoding="utf-8")
    makefile_lines = set(makefile.splitlines())
    require(
        "override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))" in makefile_lines,
        "Makefile must protect the repository root",
        failures,
    )
    require("PYTHON ?= python3" in makefile_lines, "Makefile must preserve the Python command override", failures)
    require(
        "CHECK_SCRIPT := $(ROOT)/scripts/check_wren_maprouter_contracts.py" in makefile,
        "Makefile must use the rooted checker path",
        failures,
    )
    require(
        "PROJECT := $(ROOT)/GoogleTransit.xcodeproj" in makefile
        and '-project "$(PROJECT)"' in makefile,
        "optional Xcode build must use the rooted project path",
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
