---
agent: "agent"
tools: ["search/codebase", "search"]
description: "Review library quality, regressions, and architecture conformance"
---

# Review Integration

In this repository, "integration" refers to the UniFi API Python library.

Your goal is to perform a focused technical review.

## Review Steps

1. Static checks:

```bash
mypy src/ --strict
ruff check src/ tests/
```

1. Test execution:

```bash
pytest
```

1. Review findings in these areas:

- API compatibility and method signature stability
- exception mapping correctness
- response-shape parsing robustness
- async/session lifecycle correctness
- model typing and alias fidelity

## Output Expectations

- List findings by severity.
- Include exact file paths and line references.
- Call out residual risk where coverage is missing.
