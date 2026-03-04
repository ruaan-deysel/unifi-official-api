---
agent: "agent"
tools: ["search/codebase", "edit", "search"]
description: "Add a new client action/mutation method to a UniFi endpoint"
---

# Add Action

Your goal is to add a new write/action method to an existing Network or Protect endpoint.

If not provided, ask for:

- Target endpoint/resource
- HTTP method and path
- Required parameters/body fields
- Expected response payload
- Error behavior expectations

## Implementation Steps

1. Add endpoint method in `src/unifi_official_api/{network|protect}/endpoints/`.
2. Add/update request and response models if needed.
3. Keep method naming consistent with existing endpoint patterns.
4. Ensure proper exception translation from transport errors.
5. Add/extend tests under `tests/{network|protect}/`.
6. Validate with:
   - `pytest`
   - `mypy src/ --strict`
   - `ruff check src/ tests/`

## Requirements

- Keep async behavior end-to-end.
- Handle both `{"data": ...}` and raw payload responses where applicable.
- Preserve backward-compatible signatures unless a breaking change is explicitly requested.
