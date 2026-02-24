# UniFi Official API

[![PyPI version](https://badge.fury.io/py/unifi-official-api.svg)](https://badge.fury.io/py/unifi-official-api)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/ruaan-deysel/unifi-official-api/branch/main/graph/badge.svg)](https://codecov.io/gh/ruaan-deysel/unifi-official-api)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/ruaan-deysel/unifi-official-api)

Async Python library for the official UniFi Network and Protect APIs.

## Features

- **Async-first**: Built with `aiohttp` for efficient async operations
- **Type-safe**: Full type hints and Pydantic models for all API responses
- **Official API**: Uses the official UniFi developer API endpoints
- **Comprehensive**: Supports both UniFi Network and UniFi Protect
- **Dual Connection Support**: Works with both LOCAL (direct to device) and REMOTE (cloud) connections
- **Home Assistant ready**: Designed for integration with Home Assistant and other automation platforms

## Requirements

> **Python 3.11 or higher is required.**

- Python 3.11, 3.12, or 3.13
- UniFi API Key from [developer.ui.com](https://developer.ui.com) or generated locally on your device

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

## Connection Types

This library supports two connection types:

| Connection Type | Use Case | Base URL | API Key Source |
|-----------------|----------|----------|----------------|
| **LOCAL** | Direct connection to your UniFi device (UDM, UDM-Pro, etc.) | Your device IP (e.g., `https://192.168.1.1`) | Generated on device under Settings → Admins & Users → API Keys |
| **REMOTE** | Cloud connection via Ubiquiti's API | `https://api.ui.com` (default) | Generated at [account.ui.com](https://account.ui.com) |

## Quick Start

### Local Connection (Direct to Device)

For direct connection to your UniFi device on your local network:

```python
import asyncio
from unifi_official_api import LocalAuth, ConnectionType
from unifi_official_api.network import UniFiNetworkClient

async def main():
    async with UniFiNetworkClient(
        auth=LocalAuth(
            api_key="your-local-api-key",
            verify_ssl=False,  # Disable SSL verification for self-signed certs
        ),
        base_url="https://192.168.1.1",  # Your device IP
        connection_type=ConnectionType.LOCAL,
    ) as client:
        # List all sites
        sites = await client.sites.get_all()
        site_id = sites[0].id  # Use the actual site ID

        # List all devices
        devices = await client.devices.get_all(site_id)
        for device in devices:
            print(f"Device: {device.name} ({device.mac})")

        # List connected clients
        clients = await client.clients.get_all(site_id)
        for client_info in clients:
            print(f"Client: {client_info.display_name} - {client_info.ip}")

asyncio.run(main())
```

### Remote Connection (Cloud API)

For cloud connection via Ubiquiti's API:

```python
import asyncio
from unifi_official_api import ApiKeyAuth, ConnectionType
from unifi_official_api.network import UniFiNetworkClient

async def main():
    async with UniFiNetworkClient(
        auth=ApiKeyAuth(api_key="your-cloud-api-key"),
        connection_type=ConnectionType.REMOTE,
        console_id="your-console-id",  # Required for REMOTE
    ) as client:
        # List all sites
        sites = await client.sites.get_all()
        site_id = sites[0].id

        # List all devices
        devices = await client.devices.get_all(site_id)
        for device in devices:
            print(f"Device: {device.name} ({device.mac})")

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
        cameras = await client.cameras.get_all(host_id, site_id)
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
| Devices | list, get, restart, adopt, forget, locate, get_statistics, execute_port_action |
| Clients | list, get, block, unblock, reconnect, forget, execute_action |
| Networks | list, get, create, update, delete, get_references |
| WiFi | list, get, create, update, delete |
| Firewall | list_zones, get_zone, create_zone, update_zone, delete_zone, list_rules, get_rule, create_rule, update_rule, delete_rule |
| Vouchers | list, get, create, delete, delete_multiple |
| ACL | list, get, create, update, delete |
| Traffic | list_matching_lists, create_list, update_list, delete_list, get_dpi_categories, get_dpi_applications, get_countries |
| Resources | get_wan_interfaces, get_vpn_tunnels, get_vpn_servers, get_radius_profiles, get_device_tags |

### UniFi Protect API

| Endpoint | Methods |
|----------|---------|
| Cameras | list, get, update, get_snapshot, ptz_patrol_start, ptz_patrol_stop, ptz_goto_preset, create_rtsps_stream, delete_rtsps_stream, create_talkback_session |
| Sensors | list, get, update |
| Lights | list, get, update |
| Chimes | list, get, update |
| NVR | get, update |
| Live Views | list, get, create, update, delete |
| Viewers | list, get, update, set_liveview |
| Events | list, get, get_thumbnail, get_heatmap, list_motion_events, list_smart_detect_events |
| Application | get_info, get_files, upload_file, trigger_alarm_webhook |
| WebSocket | subscribe_devices, subscribe_events |

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
    devices = await client.devices.get_all(host_id)
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
from unifi_official_api import LocalAuth, ConnectionType
from unifi_official_api.network import UniFiNetworkClient

# Local connection
client = UniFiNetworkClient(
    auth=LocalAuth(
        api_key="your-local-api-key",
        verify_ssl=False,  # For self-signed certificates
    ),
    base_url="https://192.168.1.1",  # Your device IP
    connection_type=ConnectionType.LOCAL,
    timeout=30,  # Request timeout in seconds
    connect_timeout=10,  # Connection timeout in seconds
)

# Remote/Cloud connection
from unifi_official_api import ApiKeyAuth

client = UniFiNetworkClient(
    auth=ApiKeyAuth(api_key="your-cloud-api-key"),
    connection_type=ConnectionType.REMOTE,
    console_id="your-console-id",  # Required for REMOTE connections
    timeout=30,
    connect_timeout=10,
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

# Install pre-commit hooks (recommended)
pre-commit install

# Run tests
pytest

# Run linting
ruff check src tests

# Run type checking
mypy src
```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality before commits. The hooks automatically run:

- **Ruff** - Linting and formatting
- **Mypy** - Static type checking
- **Bandit** - Security vulnerability scanning
- **Markdownlint** - Markdown file linting
- **Codespell** - Spell checking
- **Pyupgrade** - Python syntax modernization
- **File checks** - YAML, TOML, JSON validation, trailing whitespace, etc.

To set up pre-commit hooks:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# (Optional) Run against all files
pre-commit run --all-files
```

Once installed, the hooks will automatically run on every commit. If any check fails, the commit will be blocked until you fix the issues.

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
