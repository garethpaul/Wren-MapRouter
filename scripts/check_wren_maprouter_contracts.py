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
]
WORKFLOW = ROOT / ".github/workflows/check.yml"
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
    latest_location_index = app.find("CLLocation *latestLocation = [locations lastObject];", location_update_index)
    invalid_location_index = app.find(
        "if (!latestLocation || !CLLocationCoordinate2DIsValid(latestLocation.coordinate))",
        latest_location_index,
    )
    invalid_cleanup_index = app.find("[self clearPendingRoute];", invalid_location_index)
    invalid_return_index = app.find("return;", invalid_cleanup_index)
    assign_location_index = app.find("self.currentLocation = latestLocation;", invalid_return_index)
    require(
        latest_location_index != -1
        and invalid_location_index != -1
        and invalid_cleanup_index != -1
        and invalid_return_index != -1
        and assign_location_index != -1
        and latest_location_index < invalid_location_index < invalid_cleanup_index < invalid_return_index < assign_location_index,
        "location updates must clear pending routes before storing missing or invalid coordinates",
        failures,
    )
    require(
        "self.currentLocation = [locations lastObject]" not in app,
        "location updates must not store unvalidated latest locations",
        failures,
    )
    require(WORKFLOW.is_file(), "hosted verification workflow must exist", failures)
    require(
        "permissions:\n  contents: read" in workflow,
        "hosted verification permissions must be read-only",
        failures,
    )
    require(
        "python-version: ['3.10', '3.12']" in workflow,
        "hosted verification must cover Python 3.10 and 3.12",
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
