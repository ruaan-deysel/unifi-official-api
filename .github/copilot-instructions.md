# GitHub Copilot Instructions

> Full instructions: See [`AGENTS.md`](../AGENTS.md).
>
> This file is a compact Copilot-facing guide. Detailed architecture rules live in `AGENTS.md` and `.github/instructions/*.instructions.md`.

## Project Identity

- Package: `unifi-official-api`
- Import root: `unifi_official_api`
- Main code: `src/unifi_official_api/`
- Tests: `tests/`

## Quality Baseline

- Python 3.11+
- Async I/O with `aiohttp`
- Strict typing (`mypy src/ --strict`)
- Ruff lint/format for style consistency
- Pydantic v2 models for response parsing

Before considering a task complete, run:

```bash
pytest
mypy src/ --strict
ruff check src/ tests/
```

Use `ruff format src/ tests/` when formatting is needed.

## Architecture Quick Reference

- Shared transport/session logic in `BaseUniFiClient`.
- Network and Protect clients compose endpoint classes.
- Endpoint methods call client HTTP helpers and return typed models.
- Exceptions should map to package-defined error classes.

## Workflow Rules

1. Keep changes scoped to the request.
2. Implement complete feature slices (code + wiring + tests when requested).
3. Avoid breaking public API signatures unless explicitly asked.
4. Prefer updating existing docs over creating new docs.
5. Use `.ai-scratch/` for temporary planning notes.

## Path-Specific Instructions

Consult `.github/instructions/*.instructions.md` for path-level rules:

- `api.instructions.md`
- `config_flow.instructions.md`
- `configuration_yaml.instructions.md`
- `coordinator.instructions.md`
- `diagnostics.instructions.md`
- `entities.instructions.md`
- `python.instructions.md`
- `repairs.instructions.md`
- `service_actions.instructions.md`
- `services_yaml.instructions.md`
- `tests.instructions.md`
- `translations.instructions.md`
- `manifest.instructions.md`
- `json.instructions.md`
- `yaml.instructions.md`
- `markdown.instructions.md`
