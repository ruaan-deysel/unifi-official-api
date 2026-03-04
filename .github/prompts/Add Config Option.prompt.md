---
agent: "agent"
tools: ["search/codebase", "edit", "search"]
description: "Add a new client configuration option across auth/client layers"
---

# Add Config Option

Your goal is to add a new configurable option to one or more UniFi clients.

If not provided, ask for:

- Option name and type
- Which client(s) it applies to (Network, Protect, or both)
- Default value
- Validation constraints
- Whether it affects transport, auth, retries, or parsing behavior

## Implementation Steps

1. Add/update constants in `src/unifi_official_api/const.py` if needed.
2. Update constructor signatures in affected client classes.
3. Propagate option through transport/auth layers as appropriate.
4. Document behavior in docstrings and `README.md` if user-facing.
5. Add tests for default and non-default behavior.
6. Validate with `pytest`, `mypy`, and `ruff` checks.

## Requirements

- Keep existing defaults backward-compatible by default.
- Validate invalid inputs with clear errors.
- Avoid leaking sensitive option values in logs/exceptions.
