# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Network API
- **Vouchers**: Hotspot voucher management
  - `get_all()`: List vouchers with pagination and filtering
  - `get()`: Get specific voucher details
  - `create()`: Generate new vouchers with rate limits and time restrictions
  - `delete()`: Delete single voucher
  - `delete_multiple()`: Bulk delete vouchers

- **ACL Rules**: Access control list management
  - `get_all()`: List ACL rules
  - `get()`: Get specific rule
  - `create()`: Create new rule with source/destination filters
  - `update()`: Modify existing rule
  - `delete()`: Remove rule

- **Traffic Matching**: Traffic matching lists and DPI
  - `get_all_lists()`: List traffic matching lists
  - `get_list()`: Get specific list details
  - `create_list()`: Create IP/port/domain lists
  - `update_list()`: Modify list entries
  - `delete_list()`: Remove list
  - `get_dpi_categories()`: Get DPI categories
  - `get_dpi_applications()`: Get DPI applications
  - `get_countries()`: Get countries for geo-blocking

- **Resources**: Supporting network resources
  - `get_wan_interfaces()`: List WAN interfaces
  - `get_vpn_tunnels()`: List site-to-site VPN tunnels
  - `get_vpn_servers()`: List VPN servers (WireGuard, OpenVPN, L2TP)
  - `get_radius_profiles()`: List RADIUS profiles
  - `get_device_tags()`: List device tags

- **Device Actions**: Device management operations
  - `execute_port_action()`: Control device ports (enable/disable PoE, speed)
  - `execute_action()`: Device actions (restart, locate, adopt, forget)
  - `get_pending_adoption()`: List devices pending adoption
  - `get_statistics()`: Get device statistics

- **Client Actions**: Client management operations
  - `execute_action()`: Client actions (block, unblock, reconnect, forget)

- **Application Info**: `get_application_info()` method on client

#### Protect API
- **Viewers**: Viewport device management
  - `get_all()`: List all viewers
  - `get()`: Get specific viewer
  - `update()`: Modify viewer settings
  - `set_liveview()`: Set viewer's current liveview

- **Application**: System management
  - `get_info()`: Get Protect application info
  - `get_files()`: List device asset files
  - `upload_file()`: Upload animation/asset files
  - `trigger_alarm_webhook()`: Trigger alarm manager webhook

- **Camera Enhancements**:
  - `ptz_patrol_start()`: Start PTZ patrol on slot
  - `ptz_patrol_stop()`: Stop PTZ patrol
  - `ptz_goto_preset()`: Move camera to PTZ preset position
  - `create_rtsps_stream()`: Create RTSPS stream for camera
  - `get_rtsps_stream()`: Get existing RTSPS stream info
  - `delete_rtsps_stream()`: Remove RTSPS stream
  - `create_talkback_session()`: Create two-way audio session
  - `disable_mic_permanently()`: Permanently disable camera microphone
  - `set_hdr_mode()`: Set HDR mode (off, auto, always)
  - `set_video_mode()`: Set video mode (default, highFps, sport)
  - `get_snapshot()`: Retrieve camera snapshot image

- **WebSocket Subscriptions**: Real-time event streaming
  - `subscribe_devices()`: Subscribe to device state updates
  - `subscribe_events()`: Subscribe to Protect events

### Changed
- Renamed `list()` methods to `get_all()` to avoid shadowing Python built-in

## [0.1.0] - 2024-01-17

### Added
- Initial release with async Python library for UniFi APIs
- UniFi Network API support:
  - Hosts management
  - Sites management
  - Devices (list, get, update, restart)
  - Clients (list, get)
  - Networks (CRUD)
  - WiFi/WLAN (CRUD)
  - Firewall rules (CRUD)
- UniFi Protect API support:
  - Cameras (list, get, update, PTZ control)
  - Lights (list, get, update)
  - Sensors (list, get, update)
  - Chimes (list, get, update)
  - Liveviews (CRUD)
  - Events (list, get, download)
  - NVR (get, update)
- API Key authentication
- Pydantic v2 models for all API responses
- Full type annotations with strict mypy compliance
- Comprehensive test suite with 95%+ coverage
- Modern Python packaging with pyproject.toml
