---
agent: "agent"
tools: ["search/codebase", "search", "edit"]
description: "Create a phased implementation plan for features or refactors"
---

# Create Implementation Plan

Your goal is to create a phased plan for a new feature or refactor.

## Output Location

Create plan in `.ai-scratch/plan-<topic>.md`.

## Plan Structure

1. Goal and scope
2. Relevant architecture map
3. Phased implementation steps
4. Validation plan (tests/lint/type-check)
5. Risks and rollback considerations

## Guidelines

- Keep phases independently testable.
- Include concrete file paths expected to change.
- Highlight breaking-change risk explicitly.
