---
agent: "agent"
tools: ["search/codebase", "search"]
description: "Review unifi-official-api code quality, regressions, and API design"
---

# Review Python Library

Your goal is to perform a focused technical review of the `unifi-official-api` codebase.

## Scope

Prioritize findings that affect correctness, API stability, runtime behavior, and maintainability.

Key areas:

- `src/unifi_official_api/base.py` transport/session behavior
- `src/unifi_official_api/network/` endpoint and model changes
- `src/unifi_official_api/protect/` endpoint/model/websocket changes
- `src/unifi_official_api/auth.py` and `exceptions.py` behavior
- tests under `tests/`

## Review Process

1. Run static checks:

```bash
mypy src/ --strict
ruff check src/ tests/
```

1. Run tests (full or targeted):

```bash
pytest
pytest tests/network/ -v
pytest tests/protect/ -v
```

1. Review for high-value issues:

- exception mapping correctness (401/403/404/429/timeout/network)
- response parsing robustness (`{"data": ...}` vs raw payloads)
- async/session lifecycle correctness (ownership, close behavior)
- public API compatibility (method signatures and return contracts)
- model alias/type accuracy and optional field handling
- regressions from refactors or endpoint additions

## Output Requirements

- List findings first, ordered by severity.
- Include exact file paths and line references.
- Explain user/runtime impact for each finding.
- Call out missing tests or residual risk explicitly.

If no findings are discovered, state that clearly and list any coverage gaps.
