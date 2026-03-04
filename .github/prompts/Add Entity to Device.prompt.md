---
agent: "agent"
tools: ["search/codebase", "edit", "search"]
description: "Add new fields or behaviors to existing device-oriented models/endpoints"
---

# Add Entity to Device

In this repository, treat "entity" as a new typed field/capability on an existing device/resource model.

Your goal is to extend an existing model + endpoint flow without breaking compatibility.

If not provided, ask for:

- Target model and endpoint
- New field names/types
- Required vs optional semantics
- Example API payload including new fields

## Implementation Steps

1. Update model in `src/unifi_official_api/{network|protect}/models/`.
2. Update endpoint parsing/mapping logic if needed.
3. Ensure aliases match API field names.
4. Add tests for presence/absence of new fields.
5. Validate with `pytest`, `mypy`, and `ruff`.

## Requirements

- Keep existing model fields stable.
- Use optional types when API rollout is partial.
- Do not silently coerce incompatible types without justification.
