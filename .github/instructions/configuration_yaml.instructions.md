---
applyTo: "**/configuration.yaml"
---

# Configuration YAML Instructions

This repository does not use Home Assistant `configuration.yaml` files in normal operation.

If a `configuration.yaml` file is introduced for demos, tooling, or examples:

- keep it minimal and example-focused
- never store secrets in plaintext
- document how it is used in `README.md`

Prefer Python configuration objects and typed constructor parameters for runtime behavior.
