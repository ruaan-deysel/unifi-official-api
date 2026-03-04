---
applyTo: "tests/**/*.py"
---

# Test Instructions

**Applies to:** all tests in `tests/`.

## Testing Framework

- Use `pytest` with async test support already configured in `pyproject.toml`.
- Use fixtures from `tests/conftest.py` where available.
- Keep tests deterministic and network-isolated.

## HTTP Mocking

- Use `aioresponses` for HTTP mocks.
- Match exact request URLs/methods when possible.
- Cover envelope and raw-response shapes when endpoint parsing must handle both.

## What to Validate

For endpoint/client additions, include tests for:

- success path with expected model mapping
- error translation (auth/not-found/rate-limit/timeout as applicable)
- edge response shapes (missing keys, empty arrays, nulls)

## Session and Cleanup

- Ensure clients are properly closed in tests.
- Prefer `async with` client usage or fixture-managed cleanup.

## Test Naming

- Name tests by behavior, not implementation detail.
- Keep one behavioral assertion theme per test.

## Useful Commands

```bash
pytest
pytest tests/network/ -v
pytest tests/protect/ -v
pytest -k "pattern"
```
