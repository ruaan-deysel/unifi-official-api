---
applyTo: "src/unifi_official_api/network/endpoints/**/*.py, src/unifi_official_api/protect/endpoints/**/*.py"
---

# Service Actions Instructions

In this repository, "service actions" maps to mutating endpoint methods (create/update/delete/execute operations).

## Method Design

- Use clear verb-based names (`create_*`, `update_*`, `delete_*`, `execute_*`).
- Keep request payload typing explicit.
- Return typed output or documented status structures.

## Safety and Validation

- Validate caller inputs before issuing API requests where practical.
- Handle partial success and API error payloads explicitly.
- Keep idempotency considerations in mind for repeated calls.

## Testing

Include tests for:

- successful mutation path
- expected error mapping
- payload shape and serialization edge cases
