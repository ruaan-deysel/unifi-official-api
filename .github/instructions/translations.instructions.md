---
applyTo: "README.md, CHANGELOG.md, docs/**/*.md"
---

# Translations Instructions

This library does not currently maintain Home Assistant translation bundles.

Treat "translations" as consistency of user-facing wording in docs/examples.

## Wording Rules

- Keep terminology consistent: `Network`, `Protect`, `LOCAL`, `REMOTE`.
- Keep code identifiers unchanged when explaining examples.
- Keep error descriptions user-actionable.

## Sync Rules

When behavior changes:

- update README examples
- update changelog wording for user-visible impact
- avoid claiming unsupported features
