# UniFi Official API

[![PyPI version](https://badge.fury.io/py/unifi-official-api.svg)](https://badge.fury.io/py/unifi-official-api)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Async Python library for the official UniFi Network and Protect APIs.

## Features

- **Async-first**: Built with `aiohttp` for efficient async operations
- **Type-safe**: Full type hints and Pydantic models for all API responses
- **Official API**: Uses the official UniFi developer API (not web scraping)
- **Comprehensive**: Supports both UniFi Network and UniFi Protect
- **Home Assistant ready**: Designed for integration with Home Assistant and other automation platforms

## Requirements

> **Python 3.11 or higher is required.**

- Python 3.11, 3.12, or 3.13
- UniFi API Key from [developer.ui.com](https://developer.ui.com)

## Installation

```bash
pip install unifi-official-api
```

### Optional Dependencies

Install with optional dependency groups for development:

```bash
# Install with test dependencies
pip install unifi-official-api[test]

# Install with linting/type checking tools
pip install unifi-official-api[lint]

# Install with documentation tools
pip install unifi-official-api[docs]

# Install all development dependencies
pip install unifi-official-api[dev]
```

## Quick Start

### UniFi Network API

```python
import asyncio
from unifi_official_api import ApiKeyAuth
from unifi_official_api.network import UniFiNetworkClient

async def main():
    async with UniFiNetworkClient(
        auth=ApiKeyAuth(api_key="your-api-key"),
    ) as client:
        # Get available hosts
        hosts = await client.get_hosts()
        host_id = hosts[0]["id"]

        # List all sites
        sites = await client.sites.list(host_id)

        # List all devices
        devices = await client.devices.list(host_id)
        for device in devices:
            print(f"Device: {device.name} ({device.mac})")

        # List connected clients
        clients = await client.clients.list(host_id)
        for client_info in clients:
            print(f"Client: {client_info.display_name} - {client_info.ip}")

asyncio.run(main())
```

### UniFi Protect API

```python
import asyncio
from unifi_official_api import ApiKeyAuth
from unifi_official_api.protect import UniFiProtectClient

async def main():
    async with UniFiProtectClient(
        auth=ApiKeyAuth(api_key="your-api-key"),
    ) as client:
        # Get available hosts
        hosts = await client.get_hosts()
        host_id = hosts[0]["id"]
        site_id = "your-site-id"

        # List all cameras
        cameras = await client.cameras.list(host_id, site_id)
        for camera in cameras:
            print(f"Camera: {camera.name} - Recording: {camera.is_recording}")

        # Get a camera snapshot
        if cameras:
            snapshot = await client.cameras.get_snapshot(
                host_id, site_id, cameras[0].id
            )
            with open("snapshot.jpg", "wb") as f:
                f.write(snapshot)

        # List recent motion events
        events = await client.events.list_motion_events(
            host_id, site_id, limit=10
        )

asyncio.run(main())
```

## API Coverage

### UniFi Network API

| Endpoint | Methods |
|----------|---------|
| Sites | list, get |
| Devices | list, get, restart, adopt, forget |
| Clients | list, get, block, unblock, reconnect |
| Networks | list, get, create, update, delete |
| WiFi | list, get, create, update, delete |
| Firewall | list_zones, list_rules, get_rule, create_rule, update_rule, delete_rule |

### UniFi Protect API

| Endpoint | Methods |
|----------|---------|
| Cameras | list, get, update, set_recording_mode, get_snapshot, restart, ptz_move |
| Sensors | list, get, update, set_status_led, set_motion_sensitivity |
| Lights | list, get, update, turn_on, turn_off, set_mode, set_brightness |
| Chimes | list, get, update, set_volume, play |
| NVR | get, update, restart, set_recording_retention |
| Live Views | list, get, create, update, delete |
| Events | list, get, get_thumbnail, get_heatmap, list_motion_events, list_smart_detect_events |

## Error Handling

The library provides specific exceptions for different error types:

```python
from unifi_official_api import (
    UniFiError,
    UniFiAuthenticationError,
    UniFiConnectionError,
    UniFiNotFoundError,
    UniFiRateLimitError,
    UniFiTimeoutError,
)

try:
    devices = await client.devices.list(host_id)
except UniFiAuthenticationError:
    print("Invalid API key")
except UniFiConnectionError:
    print("Failed to connect to API")
except UniFiRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except UniFiNotFoundError:
    print("Resource not found")
except UniFiError as e:
    print(f"API error: {e.message}")
```

## Configuration Options

Both clients accept the following configuration options:

```python
from unifi_official_api import ApiKeyAuth
from unifi_official_api.network import UniFiNetworkClient

client = UniFiNetworkClient(
    auth=ApiKeyAuth(api_key="your-api-key"),
    base_url="https://api.ui.com",  # Default
    timeout=30,  # Request timeout in seconds
    connect_timeout=10,  # Connection timeout in seconds
    session=None,  # Optional: reuse an existing aiohttp session
)
```

### Local Protect Installation

For connecting directly to a local UniFi Protect installation:

```python
from unifi_official_api import LocalAuth
from unifi_official_api.protect import UniFiProtectClient

client = UniFiProtectClient(
    auth=LocalAuth(
        api_key="local-api-key",
        verify_ssl=False,  # Disable SSL verification for self-signed certs
    ),
    base_url="https://192.168.1.1:7443",
)
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/ruaan-deysel/unifi-official-api.git
cd unifi-official-api

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src tests

# Run type checking
mypy src
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=unifi_official_api --cov-report=html

# Run specific test file
pytest tests/network/test_client.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial library. UniFi is a trademark of Ubiquiti Inc. This project is not affiliated with, endorsed by, or sponsored by Ubiquiti Inc.

## Related Projects

- [Home Assistant](https://www.home-assistant.io/) - Open source home automation
- [UniFi Developer Documentation](https://developer.ui.com/) - Official API documentation
