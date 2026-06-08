#!/usr/bin/env python3
"""Static contracts for the Wren MapRouter legacy iOS sample."""

from pathlib import Path
import json
import plistlib
import re
import sys


ROOT = Path(__file__).resolve().parents[1]


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
        "openTransitDirections" in app and "clearPendingRoute" in app,
        "route state must be cleared after forwarding or cancellation",
        failures,
    )

    if failures:
        print("Wren MapRouter contract check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wren MapRouter contract check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
