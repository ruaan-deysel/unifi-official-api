# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Async Python library (Python 3.11+) for the official UniFi Network and Protect APIs. Supports both LOCAL (direct device) and REMOTE (cloud) connections.

## Commands

```bash
# Install for development
pip install -e ".[dev]"

# Run tests
pytest                                    # All tests
pytest tests/network/ -v                  # Network API only
pytest tests/protect/ -v                  # Protect API only
pytest -k "test_devices"                  # Specific test pattern
pytest --cov=unifi_official_api           # With coverage

# Type checking
mypy src/ --strict

# Linting & formatting
ruff check src/ tests/                    # Lint
ruff format src/ tests/                   # Format

# Pre-commit (runs ruff, mypy, bandit, codespell, pyupgrade)
pre-commit install                        # Setup hooks
pre-commit run --all-files                # Run all checks
```

## Architecture

### Client Hierarchy

```
BaseUniFiClient (base.py)
├── UniFiNetworkClient (network/client.py) - 10 endpoints
└── UniFiProtectClient (protect/client.py) - 12 endpoints + WebSocket
```

### Directory Structure

```
src/unifi_official_api/
├── auth.py           # ApiKeyAuth, LocalAuth classes
├── base.py           # BaseUniFiClient - HTTP dispatch, session management
├── const.py          # ConnectionType enum, API paths, timeouts
├── exceptions.py     # UniFiError subclasses
├── network/
│   ├── client.py     # UniFiNetworkClient
│   ├── endpoints/    # DevicesEndpoint, ClientsEndpoint, etc.
│   └── models/       # Pydantic models for Network API
└── protect/
    ├── client.py     # UniFiProtectClient
    ├── endpoints/    # CamerasEndpoint, SensorsEndpoint, etc.
    ├── models/       # Pydantic models for Protect API
    └── websocket.py  # Real-time event subscriptions
```

### Key Patterns

**Endpoint Pattern**: Each endpoint class receives the client in `__init__` and delegates HTTP via `self._client._get()`, `_post()`, `_put()`, `_delete()`. Returns Pydantic model instances.

**Model Pattern**: Pydantic v2 with `Field(alias="camelCase")` for API response mapping and `model_config = {"populate_by_name": True, "extra": "allow"}` for flexible parsing.

**Response Handling**: APIs return inconsistent shapes - check for both `{"data": [...]}` and raw lists.

**Session Management**: Use `async with client:` context manager or call `await client.close()`.

### Connection Types

- **LOCAL**: Direct to device IP (e.g., `https://192.168.1.1`), uses `LocalAuth` with optional `verify_ssl=False`
- **REMOTE**: Via cloud (`https://api.ui.com`), uses `ApiKeyAuth`, requires `console_id`

## Testing

Tests use `aioresponses` for HTTP mocking. Key fixtures in `tests/conftest.py`:

- `network_client`, `protect_client` - async client fixtures
- `mock_aioresponse` - HTTP mock context manager
- `sample_device`, `sample_camera`, etc. - test data fixtures

```python
async def test_example(self, mock_aioresponse, network_client):
    mock_aioresponse.get(
        "https://api.ui.com/ea/hosts/test-host-id/devices",
        payload=[{"id": "device-123", "name": "Test"}]
    )
    devices = await network_client.devices.get_all("test-host-id")
```

## Adding New Endpoints

1. Create endpoint class in `{network|protect}/endpoints/{resource}.py`
2. Create Pydantic models in parallel `models/` subdirectory
3. Add `__{resource}` property to client class to expose endpoint
4. Add tests using `mock_aioresponse`
5. Update `__all__` exports in `endpoints/__init__.py`

## Critical Notes

- All HTTP operations must use `await` - async-first design
- Use `TYPE_CHECKING` blocks for circular import avoidance
- Exceptions should propagate - don't swallow them unless there's explicit handling logic
- `LocalAuth` has `verify_ssl` flag - respect user configuration for self-signed certs
