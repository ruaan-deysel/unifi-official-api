---
agent: "agent"
tools: ["search/codebase", "edit", "search"]
description: "Add a new API resource surface (endpoint module + client wiring)"
---

# Add Entity Platform

In this repository, treat "entity platform" as a new API resource surface.

Your goal is to add a new endpoint module (or resource group) to the Network or Protect client.

If not provided, ask for:

- API family (`network` or `protect`)
- Resource name
- Initial read/write methods
- Response example payloads

## Implementation Steps

1. Create endpoint module in `src/unifi_official_api/{network|protect}/endpoints/`.
2. Add/extend models in matching `models/` package.
3. Wire endpoint property/accessor in client class.
4. Export symbols in relevant `__init__.py` files.
5. Add tests under `tests/{network|protect}/`.
6. Run validation commands (`pytest`, `mypy`, `ruff`).

## Requirements

- Keep one resource concern per endpoint module.
- Reuse shared parsing helpers where possible.
- Maintain existing naming and file organization conventions.
