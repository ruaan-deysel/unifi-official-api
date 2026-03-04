---
applyTo: "src/unifi_official_api/base.py, src/unifi_official_api/auth.py, src/unifi_official_api/exceptions.py, src/unifi_official_api/network/**/*.py, src/unifi_official_api/protect/**/*.py"
---

# API and Client Instructions

**Applies to:** core client transport/auth, endpoint modules, API models, and websocket handling.

## Client Layering

Use this layering consistently:

- `BaseUniFiClient` for HTTP/session/error translation
- API-specific client (`UniFiNetworkClient` / `UniFiProtectClient`) for endpoint composition
- Endpoint classes for resource-specific behavior
- Pydantic models for typed response parsing

Endpoint classes should not create sessions or implement transport primitives.

## Endpoint Method Pattern

Each endpoint method should:

1. Build request path/params/payload.
2. Call a client helper (`_get`, `_post`, `_put`, `_delete`).
3. Parse API response shape (`{"data": ...}` and raw payloads).
4. Return typed model instance(s) or documented primitive values.

Prefer explicit parsing helpers over repeating response-shape handling in every method.

## Response Parsing Rules

UniFi APIs may return inconsistent envelopes. Validate both common forms:

- Envelope: `{"data": [...]} / {"data": {...}}`
- Direct payload: `[...] / {...}`

Be defensive against missing keys and unexpected nulls where API behavior is known to vary.

## Error Translation

Raise package exceptions from `src/unifi_official_api/exceptions.py`.

- 401/403 -> authentication errors
- 404 -> not-found errors
- 429 -> rate-limit errors (include retry metadata when available)
- timeout/network failures -> timeout/connection errors
- other HTTP failures -> response errors with status/body context

Do not swallow exceptions silently.

## Auth and Security

- Keep credentials out of logs and exception messages.
- Respect local-vs-remote connection differences.
- Preserve `LocalAuth.verify_ssl` behavior for self-signed local deployments.

## Session Ownership

- If a client receives an external `aiohttp.ClientSession`, do not close it.
- If a client creates its own session, close it in `close()` and context manager exit.
- Avoid session churn per request; reuse one session per client lifecycle.

## WebSocket (Protect)

For websocket code:

- keep reconnect/backoff behavior explicit
- isolate event parsing from transport loop control
- surface failures with actionable exception context
- avoid blocking operations in receive loops

## Public API Stability

Treat public client and endpoint method signatures as stable by default.

If a breaking change is unavoidable, update docs/changelog and call it out in the PR summary.
