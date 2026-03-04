---
applyTo: "**/services.yaml"
---

# Services YAML Instructions

This repository does not currently use `services.yaml` for runtime behavior.

If introduced for tooling/docs/examples:

- keep structure documented and minimal
- ensure values match implemented Python behavior
- avoid embedding secrets

Primary source of behavior remains typed Python code in `src/unifi_official_api/`.
