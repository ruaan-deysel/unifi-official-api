# AI Coding Agent Instructions for UniFi Official API

## Project Overview

This is an async Python library for the official UniFi Network and Protect APIs. The codebase is structured as two parallel client implementations with shared authentication and base infrastructure, supporting both cloud-hosted and local on-premise deployments.

## Architecture

### Core Concepts

- **Two distinct APIs**: `network/` (devices, clients, networks, WiFi, firewall) and `protect/` (cameras, sensors, lights, NVR)
- **Endpoint pattern**: Each API has an endpoint class per resource (e.g., `DevicesEndpoint`, `CamerasEndpoint`)
- **Model pattern**: Each endpoint has corresponding Pydantic models in `models/` subdirectories
- **Async-first**: All I/O operations use `aiohttp` and must be `async`
- **Context managers**: Both clients use `async with` patterns for session lifecycle management

### Client Hierarchy

```
BaseUniFiClient (base.py)
├── UniFiNetworkClient (network/client.py) - inherits, adds Network endpoints
└── UniFiProtectClient (protect/client.py) - inherits, adds Protect endpoints
```

### Authentication

- `ApiKeyAuth`: API key for cloud-hosted APIs (both Network and Protect)
- `LocalAuth`: Alternative for on-premise Protect deployments
- Keys are passed via `X-API-Key` header; never hardcode or log them

## Key Patterns

### Endpoint Implementation

Each endpoint class:

- Accepts the client instance in `__init__` to access `self._client._get()`, `self._client._post()`, etc.
- Methods typically fetch data via `await self._client._get(path, params=params)`
- Returns Pydantic model instances or lists thereof
- Handles response parsing (responses may be `{"data": [...]}` or raw lists)

Example structure ([src/unifi_official_api/network/endpoints/devices.py](../src/unifi_official_api/network/endpoints/devices.py)):

```python
class DevicesEndpoint:
    def __init__(self, client: UniFiNetworkClient) -> None:
        self._client = client

    async def get_all(self, host_id: str) -> list[Device]:
        response = await self._client._get(f"/ea/hosts/{host_id}/devices")
        # Parse response and return Device models
```

### Model Patterns

Models use Pydantic v2 with:

- `Field(alias="...")` for camelCase API responses → snake_case Python
- `model_config = {"populate_by_name": True, "extra": "allow"}` for flexible parsing
- Enums for typed constants (e.g., `DeviceType`, `DeviceState`)

Example ([src/unifi_official_api/network/models/device.py](../src/unifi_official_api/network/models/device.py)):

```python
class Device(BaseModel):
    id: str
    mac: str
    model_config = {"populate_by_name": True, "extra": "allow"}
```

### HTTP Method Delegation

The base client provides:

- `await self._client._get(path, params=params)` - GET requests
- `await self._client._post(path, json=payload)` - POST requests
- `await self._client._put(path, json=payload)` - PUT requests
- `await self._client._delete(path)` - DELETE requests

All methods automatically:

- Add authentication headers
- Handle SSL context (cloud vs. local)
- Raise appropriate `UniFiError` subclasses on failure

### Error Handling

All error scenarios raise exceptions from [src/unifi_official_api/exceptions.py](../src/unifi_official_api/exceptions.py):

- `UniFiAuthenticationError` - auth failed
- `UniFiRateLimitError` - 429 response (includes `retry_after`)
- `UniFiNotFoundError` - 404 response
- `UniFiTimeoutError` - request timeout
- `UniFiConnectionError` - connection failure
- `UniFiResponseError` - other HTTP errors (includes `status_code`, `response_body`)

Do **not** swallow exceptions; let them propagate unless there's explicit handling logic.

## Development Workflows

### Running Tests

```bash
pytest tests/ -v                    # All tests
pytest tests/network/ -v            # Network API tests only
pytest tests/protect/ -v            # Protect API tests only
pytest tests/ -k "test_devices"     # Specific test
pytest tests/ --cov=src            # With coverage
```

### Type Checking

```bash
mypy src/ --strict                  # Type validation
```

### Linting

```bash
ruff check src/ tests/              # Linting
ruff format src/ tests/             # Auto-format
```

### Test Fixtures

[tests/conftest.py](../tests/conftest.py) provides:

- `@pytest.fixture auth` - test API key auth
- `@pytest.fixture network_client` - async Network client
- `@pytest.fixture protect_client` - async Protect client
- `@pytest.fixture mock_aioresponse` - mocks HTTP responses
- `@pytest.fixture sample_device`, `sample_client`, `sample_camera` - test data

### Testing Pattern

Tests use `aioresponses` to mock HTTP calls:

```python
async def test_example(self, mock_aioresponse, network_client):
    mock_aioresponse.get(
        "https://api.ui.com/ea/hosts/test-host-id/devices",
        payload=[{"id": "device-123", "name": "Test"}]
    )
    devices = await network_client.devices.get_all("test-host-id")
```

## Project-Specific Conventions

### Import Organization

- Use absolute imports from `unifi_official_api` root
- Avoid circular imports by using `TYPE_CHECKING` blocks for type hints
- All module docstrings include purpose and example usage

### Naming

- Files/modules: snake_case (e.g., `devices.py`, `device.py`)
- Classes: PascalCase (e.g., `DevicesEndpoint`, `Device`)
- Constants: UPPER_SNAKE_CASE (defined in [src/unifi_official_api/const.py](../src/unifi_official_api/const.py))

### Required Python Version

- Minimum: **Python 3.11**
- Uses `from __future__ import annotations` in all modules for forward references

### Dependencies

- **Core**: `aiohttp>=3.9.0`, `pydantic>=2.0.0`, `yarl>=1.9.0`
- **Testing**: `pytest`, `pytest-asyncio`, `aioresponses`
- **Linting**: `mypy`, `ruff`

### Documentation

All public classes/methods require docstrings with:

- Summary line
- Args section (with types)
- Returns section
- Optional Raises section

## Adding New Endpoints

1. Create endpoint class in `network/endpoints/{resource}.py` or `protect/endpoints/{resource}.py`
2. Create model class(es) in parallel `models/` subdirectory with Pydantic definitions
3. Add `__{resource}` property to client class to expose endpoint
4. Add tests in `tests/{network|protect}/test_endpoints.py` using `mock_aioresponse`
5. Update client `__all__` exports in respective `endpoints/__init__.py`

## Integration Points

### Session Management

- Both clients accept optional `session: aiohttp.ClientSession | None`
- If not provided, client creates its own (and owns cleanup responsibility)
- Always use `async with client:` context manager or call `await client.close()`

### WebSocket Support

`UniFiProtectClient` includes `websocket` module for real-time event subscriptions. Separate from REST endpoints but shares authentication and base URL logic.

### Multi-Host Architecture

Both APIs require `host_id` as a parameter (obtain via `await client.get_hosts()`). Some operations also need `site_id`. This enables managing multiple UniFi instances from one client.

## Critical Files

- [src/unifi_official_api/base.py](../src/unifi_official_api/base.py) - HTTP request dispatch logic
- [src/unifi_official_api/auth.py](../src/unifi_official_api/auth.py) - authentication handling
- [src/unifi_official_api/const.py](../src/unifi_official_api/const.py) - API URLs, timeouts, constants
- [src/unifi_official_api/exceptions.py](../src/unifi_official_api/exceptions.py) - error types
- [pyproject.toml](../pyproject.toml) - dependencies, build config, test commands
- [tests/conftest.py](../tests/conftest.py) - shared test fixtures

## Common Pitfalls

- **Forgetting async/await**: All HTTP operations must use `await`
- **Response parsing**: APIs return inconsistent shapes; check for both `{"data": [...]}` and raw lists
- **SSL verification**: `LocalAuth` has `verify_ssl` flag; respect user configuration
- **Model aliases**: Use `Field(alias="camelCase")` to match API response keys
- **Test isolation**: Always close clients in test teardown (fixtures handle this)
