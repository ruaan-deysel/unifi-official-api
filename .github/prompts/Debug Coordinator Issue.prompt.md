---
agent: "agent"
tools: ["search/codebase", "search", "problems"]
description: "Diagnose and fix client orchestration issues (auth, transport, stale parsing)"
---

# Debug Coordinator Issue

In this repository, interpret "coordinator" as client transport/update orchestration (base client + endpoint interaction).

Your goal is to diagnose and fix data/update issues in the client stack.

## Investigation Checklist

- Reproduce with focused tests (`pytest -k ...`).
- Inspect URL/path/params/body construction.
- Verify response parsing assumptions (`{"data": ...}` vs raw payload).
- Check exception mapping in `base.py` and endpoint code.
- Confirm auth mode handling (local vs remote).

## Common Failures

- Auth errors mapped to wrong exception type
- Rate-limit handling missing retry metadata
- Incorrect host/site identifiers passed to endpoints
- Partial payloads causing model validation failures
- Session lifecycle issues (leaks/double-close)

## Fix Requirements

- Add regression tests for the scenario.
- Keep fix scoped to root cause.
- Validate with `pytest`, `mypy`, and `ruff`.
