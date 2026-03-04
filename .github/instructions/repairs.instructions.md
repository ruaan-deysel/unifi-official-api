---
applyTo: "src/unifi_official_api/**/*.py, README.md, CHANGELOG.md"
---

# Repairs Instructions

In this repository, "repairs" maps to corrective maintenance: deprecations, bug fixes, compatibility patches, and migration-safe updates.

## Repair Strategy

- Fix root cause before adding workarounds.
- Keep patches minimal and scoped.
- Add regression tests for repaired behavior.

## Compatibility Rules

- Prefer non-breaking repairs.
- If breaking behavior is unavoidable, document clearly in `CHANGELOG.md` and affected docs.
- Keep exception behavior stable for callers unless intentionally changed.

## Validation

After repair work, run relevant tests plus static checks (`pytest`, `mypy`, `ruff`).
