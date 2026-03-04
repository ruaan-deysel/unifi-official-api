---
applyTo: "src/unifi_official_api/network/endpoints/**/*.py, src/unifi_official_api/protect/endpoints/**/*.py, src/unifi_official_api/network/models/**/*.py, src/unifi_official_api/protect/models/**/*.py"
---

# Entities Instructions

In this repository, "entities" maps to API resources represented by endpoint methods and model classes.

## Resource Modeling Rules

- Keep one resource concern per endpoint module where practical.
- Keep model names aligned with API resource semantics.
- Use aliases for camelCase API keys.

## Endpoint-to-Model Contract

- Endpoint methods should return typed models or documented primitives.
- Keep response normalization near the endpoint boundary.
- Handle empty/partial payloads safely.

## Compatibility

- Avoid renaming/removing model fields without migration notes.
- Add optional fields when API rollouts are staged/inconsistent.
