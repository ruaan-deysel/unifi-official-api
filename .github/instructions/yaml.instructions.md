---
applyTo: "**/*.yaml, **/*.yml"
---

# YAML Instructions

**Applies to:** all YAML files.

## Formatting

- 2-space indentation
- no tabs
- no trailing whitespace
- single newline at EOF

## Structure

- Keep sections logically grouped.
- Prefer readable, minimal nesting.
- Avoid mixing formatting changes with functional changes when possible.

## Validation

If a YAML file feeds tooling/CI, validate with the project command that consumes it.
