---
agent: "agent"
tools: ["edit", "search"]
description: "Update user-facing wording in docs, examples, and API text"
---

# Update Translations

This library does not have Home Assistant translation bundles. Treat this task as updating user-facing text consistency.

## Targets

- `README.md`
- `CHANGELOG.md`
- public docstrings/examples where wording appears to users

## Requirements

- Keep terminology consistent (`Network`, `Protect`, `LOCAL`, `REMOTE`).
- Ensure examples reflect current method signatures and parameters.
- Keep changes scoped to wording/labels unless code changes are explicitly requested.
- Avoid introducing behavior claims not implemented in code.
