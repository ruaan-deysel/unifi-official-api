---
applyTo: "src/unifi_official_api/base.py, src/unifi_official_api/exceptions.py, tests/**/*.py"
---

# Diagnostics Instructions

## Logging and Error Context

- Keep diagnostics actionable and concise.
- Never log API keys, tokens, or sensitive identifiers.
- Include key context (endpoint path/status) without exposing secrets.

## Exceptions

- Preserve the original error chain.
- Use package exception classes for consistent caller behavior.
- Include retry metadata when available (rate-limit scenarios).

## Debugging Changes

When adding diagnostics behavior, include tests for:

- exception mapping
- redaction/sensitive data handling
- edge cases with partial or malformed payloads
