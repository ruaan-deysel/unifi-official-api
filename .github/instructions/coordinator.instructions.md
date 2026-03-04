---
applyTo: "src/unifi_official_api/base.py, src/unifi_official_api/network/client.py, src/unifi_official_api/protect/client.py, src/unifi_official_api/protect/websocket.py"
---

# Coordinator Instructions

In this repository, "coordinator" maps to orchestration logic in clients/base transport (request flow, retries, refresh-like calls, websocket event handling).

## Orchestration Rules

- Keep request orchestration centralized in client/base layers.
- Keep endpoint methods focused on resource operations.
- Use consistent timeout/retry behavior across clients.

## Failure Handling

- Map transport failures to package exceptions.
- Preserve failure context (`raise ... from err`).
- Avoid duplicate or noisy logging of expected exception paths.

## Update/Data Flow

- Keep data-fetch/update orchestration explicit.
- For websocket updates, separate transport loop logic from payload interpretation.
- Ensure reconnection behavior is deterministic and testable.
