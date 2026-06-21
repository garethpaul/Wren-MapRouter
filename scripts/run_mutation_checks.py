#!/usr/bin/env python3
"""Verify that critical static contracts reject hostile source mutations."""

from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]

MUTATIONS = {
    "route ownership guard": (
        "GoogleTransit/AppDelegate.m",
        "- (void)locationManager:(CLLocationManager *)manager\n"
        "\t didUpdateLocations:(NSArray *)locations\n"
        "{\n\tif (![self routeNeedsCurrentLocation]){\n\t\treturn;\n\t}\n",
        "- (void)locationManager:(CLLocationManager *)manager\n"
        "\t didUpdateLocations:(NSArray *)locations\n{\n",
    ),
    "bounded horizontal accuracy": (
        "GoogleTransit/LocationSamplePolicy.m",
        "LocationSampleMaximumHorizontalAccuracy = 1000",
        "LocationSampleMaximumHorizontalAccuracy = INFINITY",
    ),
    "finite sample age": (
        "GoogleTransit/LocationSamplePolicy.m",
        "!isfinite(locationAge) ||\n        ",
        "",
    ),
    "newest-first sample selection": (
        "GoogleTransit/LocationSamplePolicy.m",
        "[locations reverseObjectEnumerator]",
        "locations",
    ),
    "launch root controller": (
        "GoogleTransit/AppDelegate.m",
        "    self.window.rootViewController = [[UIViewController alloc] init];\n",
        "",
    ),
    "Make derived-data protection": (
        "Makefile",
        "override BUILD_DERIVED_DATA :=",
        "BUILD_DERIVED_DATA ?=",
    ),
    "checkout credential isolation": (
        ".github/workflows/check.yml",
        "persist-credentials: false",
        "persist-credentials: true",
    ),
}


def copy_repository(destination):
    shutil.copytree(
        ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", ".build", "build", "__pycache__", "*.pyc"),
    )


def apply_mutation(root, relative_path, original, replacement):
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    if original not in text:
        raise RuntimeError(f"mutation target is missing: {relative_path}: {original!r}")
    path.write_text(text.replace(original, replacement, 1), encoding="utf-8")


def main():
    for name, mutation in MUTATIONS.items():
        with tempfile.TemporaryDirectory(prefix="wren-maprouter-mutation-") as temporary_directory:
            mutated_root = Path(temporary_directory) / "repo"
            copy_repository(mutated_root)
            apply_mutation(mutated_root, *mutation)
            result = subprocess.run(
                ["python3", "scripts/check_wren_maprouter_contracts.py"],
                cwd=mutated_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                print(f"Mutation survived: {name}")
                return 1
            print(f"Mutation killed: {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
