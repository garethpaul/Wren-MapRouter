## Wren MapRouter Vision

Wren MapRouter is an Objective-C iOS route-handler sample that accepts MapKit
directions URLs, resolves current-location coordinates, and forwards the route
to Google Maps transit directions.

The repository is useful as a historical routing experiment with MapKit URL
handling, CoreLocation updates, screenshots, and a simple GeoJSON artifact.

The goal is to preserve the route-forwarding sample while making location,
URL-handling, and external-map assumptions explicit.

The current focus is:

Priority:

- Preserve MapKit directions URL detection and forwarding behavior
- Keep current-location use visible and permission-aware
- Treat Google Maps URL parameters as legacy assumptions
- Restrict external forwarding to the documented Google Maps endpoint
- Restrict external forwarding to the expected Google Maps route path
- Reject empty route endpoints before external forwarding
- Reject whitespace-only route endpoints before external forwarding
- Encode route endpoints before external URL forwarding
- Escape route query delimiters in encoded endpoints
- Clear pending route state when endpoint encoding fails
- Clear incomplete non-location routes before external URL construction
- Clear pending routes when CoreLocation updates are missing or invalid
- Avoid storing route or location history
- Keep portable location and external-forwarding contracts running in hosted CI

Next priorities:

- Add README setup notes and expected route behavior
- Document location permission requirements
- Decide whether the sample is archived or should target modern Maps APIs

Contribution rules:

- One PR = one focused routing, location, URL, project, or documentation change.
- Do not commit user route or location data.
- Keep external map destinations explicit.
- Keep route endpoint normalization explicit before external forwarding.
- Include simulator/device notes for route handling changes.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Routes and locations are sensitive. The app should avoid retaining route
history, should make external URL forwarding clear, and should keep location
permissions explicit.

## What We Will Not Merge (For Now)

- Hidden route storage
- Silent forwarding to unexpected services
- Location upload behavior
- Modernization that changes routing semantics without documentation

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
