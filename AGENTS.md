# AI Agent Instructions

This document is the primary instruction set for AI coding agents working in this repository.

## Project Overview

This repository is an async Python library for the official UniFi APIs:

- UniFi Network API
- UniFi Protect API

Core package:

- `src/unifi_official_api/`

Key characteristics:

- Async-first (`aiohttp`)
- Strong typing and strict static analysis (`mypy --strict`)
- Pydantic v2 models for API responses
- Supports local and cloud connection modes

## Project Identity

- Package name: `unifi-official-api`
- Import root: `unifi_official_api`
- Minimum Python version: `3.11`
- Main branch: `main`

## Codebase Map

- `src/unifi_official_api/auth.py` - auth strategies (`ApiKeyAuth`, `LocalAuth`)
- `src/unifi_official_api/base.py` - shared HTTP behavior, session lifecycle
- `src/unifi_official_api/const.py` - constants, URLs, defaults
- `src/unifi_official_api/exceptions.py` - exception hierarchy
- `src/unifi_official_api/network/` - Network client, endpoints, models
- `src/unifi_official_api/protect/` - Protect client, endpoints, models, websocket
- `tests/` - pytest suite with `aioresponses` mocks

## Development Commands

Use these commands when validating changes:

```bash
pip install -e ".[dev]"
pytest
pytest tests/network/ -v
pytest tests/protect/ -v
pytest -k "pattern"
mypy src/ --strict
ruff check src/ tests/
ruff format src/ tests/
pre-commit run --all-files
```

## Architecture Rules

### Client Structure

- `BaseUniFiClient` contains shared HTTP/session/error behavior.
- `UniFiNetworkClient` and `UniFiProtectClient` compose endpoint classes.
- Endpoints should delegate HTTP calls through client helper methods.

### Endpoint Pattern

- One resource per endpoint module under `network/endpoints/` or `protect/endpoints/`.
- Endpoint methods should:
  - build path/params
  - call client transport helpers
  - parse response shape (`{"data": ...}` vs raw list/object)
  - return typed model objects

### Model Pattern

- Keep models in `network/models/` or `protect/models/`.
- Use Pydantic aliases for API camelCase keys.
- Allow compatible forward fields with `extra="allow"` where needed.

### Error Handling

- Raise package exceptions from `exceptions.py`.
- Do not silently swallow HTTP/auth/timeout errors.
- Preserve context (`raise ... from err`) when translating exceptions.

## Implementation Guidance

### Adding Endpoints

1. Add endpoint class/module.
2. Add/extend corresponding models.
3. Wire endpoint into client accessor/property.
4. Export via package `__init__.py` where relevant.
5. Add/update tests with mocked HTTP responses.
6. Run lint, type-check, and tests.

### Changing Shared Transport/Auth

- Validate both Network and Protect clients.
- Check local and remote flows when behavior is connection-type specific.
- Prefer backward-compatible signatures for public APIs.

### WebSocket Changes (Protect)

- Keep reconnect/error handling explicit.
- Avoid blocking operations in subscription paths.
- Preserve public callback/event contracts.

## Testing Rules

- Use `aioresponses` or existing fixtures for HTTP mocking.
- Keep tests deterministic and isolated (no real network calls).
- Mirror package structure in tests where possible.
- Cover both success and failure paths for new behavior.

## Documentation and Scratch Notes

- Use `.ai-scratch/` for temporary plans/notes.
- `.ai-scratch/` contents are not intended to be committed.
- Do not create new permanent docs unless requested.
- Prefer updating existing docs (`README.md`, `CHANGELOG.md`) when needed.

## Working With Developers

If developer instructions conflict with this file:

1. Confirm intent and constraints.
2. Follow explicit developer direction.
3. Suggest updating this file if the new approach is intended to persist.

## Path-Specific Instruction Files

Additional guidance is in `.github/instructions/*.instructions.md`.
Use the file that matches the path you are editing.

- `api.instructions.md` - API/client/endpoint/model architecture details
- `config_flow.instructions.md` - client configuration input and validation patterns
- `configuration_yaml.instructions.md` - guidance for optional YAML config examples
- `coordinator.instructions.md` - client orchestration and update flow guidance
- `diagnostics.instructions.md` - logging/redaction/diagnostic error context rules
- `entities.instructions.md` - endpoint-model resource mapping conventions
- `python.instructions.md` - Python style and async coding conventions
- `repairs.instructions.md` - compatibility-safe fixes and repair patterns
- `service_actions.instructions.md` - mutating endpoint method guidance
- `services_yaml.instructions.md` - optional `services.yaml` documentation guidance
- `tests.instructions.md` - testing and fixture patterns
- `translations.instructions.md` - user-facing wording consistency guidance
- `manifest.instructions.md` - packaging/version metadata (`pyproject.toml`)
- `json.instructions.md` - JSON formatting rules
- `yaml.instructions.md` - YAML formatting rules
- `markdown.instructions.md` - markdown content conventions
