---
applyTo: "pyproject.toml, src/unifi_official_api/_version.py"
---

# Packaging and Version Instructions

**Applies to:** package metadata and version files.

## `pyproject.toml` Changes

When editing project metadata:

- Keep dependency groups aligned with real usage (`test`, `lint`, `docs`, `dev`).
- Preserve strict lint/type settings unless intentionally changed.
- Keep Python version constraints consistent with CI and code usage.

## Versioning

- Use semantic versioning intent for release changes.
- Ensure `src/unifi_official_api/_version.py` and release workflow expectations stay aligned.

## Metadata Consistency

If package behavior changes significantly, verify related fields:

- `description`
- `keywords`
- classifiers
- project URLs

## Validation

After metadata changes, run at least:

```bash
pytest
mypy src/ --strict
ruff check src/ tests/
```
