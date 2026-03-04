---
applyTo: "src/unifi_official_api/auth.py, src/unifi_official_api/base.py, src/unifi_official_api/const.py, src/unifi_official_api/network/client.py, src/unifi_official_api/protect/client.py"
---

# Config Flow Instructions

In this repository, "config flow" maps to client configuration inputs (auth, connection mode, URL, console/site identifiers, timeout settings).

## Input Handling Rules

- Keep constructor parameters explicit and typed.
- Validate required combinations early (for example, options required only for remote mode).
- Keep defaults backward-compatible unless a breaking change is intentional.

## Behavior Rules

- Configuration should affect transport/auth behavior predictably.
- Avoid hidden side effects when setting config options.
- Prefer clear exception messages when configuration is invalid.

## Change Checklist

- Update affected client signatures.
- Update constants/defaults where needed.
- Add tests for valid and invalid configuration combinations.
- Update README examples when user-facing behavior changes.
