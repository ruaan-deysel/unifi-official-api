---
agent: "agent"
tools: ["search/codebase", "edit"]
description: "Create an Architecture Decision Record for major design choices"
---

# Create ADR

Your goal is to create a concise ADR for an architectural decision.

If missing, ask for:

- Decision to document
- Alternatives considered
- Tradeoffs and impact

## Output Location

- Prefer `docs/development/adr/NNNN-title.md` if docs are requested.
- If docs location is not approved yet, draft in `.ai-scratch/` first and ask before moving.

## ADR Sections

- Context
- Decision drivers
- Options considered
- Decision and rationale
- Consequences (positive/negative)
- Rollout or migration notes
