# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.4.0] - 2026-08-26

### Added

#### Full Official UniFi API Coverage (6 Suites)

- **UniFi Network API**:
  - **Switching**: Complete switching management (`client.switching`)
    - `get_lags()` / `get_lag()`: List and retrieve Link Aggregation Groups (LAGs)
    - `get_mc_lag_domains()` / `get_mc_lag_domain()`: List and retrieve Multi-Chassis LAG (MC-LAG) domains
    - `get_switch_stacks()` / `get_switch_stack()`: List and retrieve Switch Stacks and member units
    - Models: `Lag`, `LagMember`, `LagType`, `LagPage`, `McLagDomain`, `McLagPeer`, `McLagDomainPage`, `SwitchStack`, `SwitchStackMember`, `SwitchStackPage`

- **UniFi Protect API**:
  - **Sirens**: `client.sirens` for managing siren devices (`get_all`, `get`, `update`, `play`, `stop`, `test_sound`)
  - **Key Fobs**: `client.fobs` for managing key fobs (`get_all`, `get`, `update`)
  - **Relays**: `client.relays` for managing relay devices and output activation (`get_all`, `get`, `update`, `activate_output`)
  - **Speakers**: `client.speakers` for managing Protect speakers and test sounds (`get_all`, `get`, `update`, `test_sound`)
  - **Bridges & Link Stations**: `client.bridges` and `client.link_stations` for managing bridges and link stations
  - **Alarm Hubs & Alarm Manager**: `client.alarm_hubs` for alarm hub devices and output triggers, and `client.alarm_manager` for alarm manager webhook dispatch
  - **Arm Profiles**: `client.arm_profiles` for arm profile lifecycle, global arm settings, enable, and disable
  - **Users**: `client.users` for local Protect users and UniFi Identity (ULP) users (`get_users`, `get_user`, `get_ulp_users`, `get_ulp_user`)
  - **Point of Sale (POS)**: `client.pos` for ingesting POS transactions overlaid onto camera footage (`ingest_transaction`)
  - Models: `Siren`, `Fob`, `Relay`, `Speaker`, `Bridge`, `LinkStation`, `AlarmHub`, `ArmProfile`, `ArmProfileSettings`, `ProtectUser`, `ULPUser`, `POSTransactionRequest`, `POSLineItem`, `POSLocation`

- **UniFi InnerSpace API (`UniFiInnerSpaceClient`)**:
  - New dedicated client supporting direct `LOCAL` and cloud `REMOTE` connections
  - **Project**: `client.project.get()` for full RF geometry, wall types, and attenuation shapes
  - **Floor Plans**: `client.floor_plans.get_all()` for floor plan definitions and scale
  - **Placed APs & Switches**: `client.access_points.get_all()` and `client.switches.get_all()` for placed network hardware coordinates
  - **Inventory**: `client.inventory.get_all()` for unplaced hardware devices
  - **Blueprint Assets**: `client.assets.download()` for downloading floor plan raster blueprint images
  - Models: `ProjectData`, `ProjectMeta`, `FloorPlan`, `InnerSpaceAccessPoint`, `InnerSpaceMountType`, `InnerSpaceSwitch`, `InventoryDevice`

- **UniFi Site Manager API (`UniFiSiteManagerClient`)**:
  - New dedicated client for cloud-level console management via `https://api.ui.com`
  - **Hosts**: `client.hosts.get_all()`, `client.hosts.get()` for registered console hosts
  - **Sites**: `client.sites.get_all()` for cross-console site aggregation
  - **Devices**: `client.devices.get_all()` for cross-console device inventories
  - **ISP Metrics**: `client.isp_metrics.get_metrics()`, `client.isp_metrics.query()` for WAN performance telemetry
  - **SD-WAN**: `client.sd_wan.get_configs()`, `client.sd_wan.get_config()`, `client.sd_wan.get_status()` for SD-WAN topologies and tunnel health
  - **Cloud Connector**: `client.connector.proxy()` for proxying arbitrary HTTP requests to remote consoles
  - Models: `Host`, `HostUserData`, `HostReportedState`, `HostListResponse`, `SiteManagerSite`, `SiteListResponse`, `SiteManagerDevice`, `SiteManagerHostDevices`, `DeviceListResponse`, `ISPMetric`, `ISPMetricQuery`, `ISPMetricQueryResult`, `SDWanConfig`, `SDWanConfigDetail`, `SDWanStatus`

- **UniFi Mobility API (`UniFiMobilityClient`)**:
  - New dedicated client for UMR cellular gateway router fleets via `https://api.ui.com`
  - **Workspaces & Admins**: `client.workspaces.get_all()`, `client.workspaces.get_admins()`
  - **Device Gateways**: `client.devices.get_all()`, `client.devices.get()`, `client.devices.update_name()` with GPS location coordinates
  - **Connected Clients**: `client.clients.get_all()` for connected wireless and wired client monitoring
  - **Remote Network & Wireless**: `client.network.update()` for LAN/DHCP settings and `client.wireless.update()` for WiFi SSIDs/passwords
  - Models: `WorkspaceSummary`, `AdminSummary`, `AdminPermission`, `MobilityDeviceSummary`, `MobilityDeviceDetail`, `DeviceLocation`, `MobilityDeviceClient`, `UpdateDeviceNameReq`, `UpdateNetworkReq`, `UpdateWirelessReq`

- **UniFi Carrier Fabric API (`UniFiCarrierFabricClient`)**:
  - New dedicated client for ISP subscriber provisioning via `https://api.ui.com`
  - **Subscribers**: `client.subscribers.get_all()`, `create()`, `get()`, `update()`, `attach_host()`, `detach_host()`, `assign_plan()`, `suspend()`, `resume()`
  - **Service Plans**: `client.service_plans.get_all()`, `get()` for bandwidth and QoS plans
  - Models: `Subscriber`, `SubscriberCreate`, `SubscriberPatch`, `HostLinkResponse`, `SubscriberListResponse`, `ServicePlan`, `ServicePlanListResponse`, `Meta`

### Changed

- Update repository URLs and documentation references to tinkerologie organization.

- Modernized `(str, Enum)` definitions across all network and protect models to standard Python 3.11+ `StrEnum`
- Exported all 6 official clients (`UniFiNetworkClient`, `UniFiProtectClient`, `UniFiInnerSpaceClient`, `UniFiSiteManagerClient`, `UniFiMobilityClient`, `UniFiCarrierFabricClient`) from root `unifi_official_api` package
- Updated `pyproject.toml` dependency constraint `aiohttp>=3.9.0,<3.14.0` for `aioresponses` mock compatibility
- Expanded unit test suite to 657 tests with 96% overall code coverage

## [1.3.0] - 2026-03-30

### Added

#### Network API

- **Sites**: `get_legacy_all()` method for retrieving raw legacy site dictionaries from `/self/sites`
- **Auto-pagination**: `clients.get_all()` and `firewall.list_rules()` now automatically paginate to retrieve all results when called without explicit `offset`/`limit` parameters
- **Device model**: Added `DeviceState.GETTING_READY` state and flexible `state`/`type` fields accepting raw strings for forward compatibility with new device states

### Changed

- Update repository URLs and documentation references to tinkerologie organization.

#### Network API

- **REMOTE URL paths**: Removed `/proxy/` prefix from REMOTE connector URLs — the connector now adds this during forwarding
- **Lazy console_id validation**: Network client no longer raises at `__init__` when `console_id` is missing for REMOTE connections; validation deferred to when API paths are built, allowing `get_hosts()` without a console_id
- **`firewall.update_rule()`**: Changed from PATCH to GET+PUT pattern for compatibility with current UniFi controller versions
- **`firewall.patch_rule()`**: **Breaking behavioral change** — no longer performs an HTTP PATCH / partial update. `patch_rule()` now delegates to `update_rule()`, which fetches the full rule via GET and writes it back via PUT. Fields not included in the call may be overwritten with server defaults. Callers relying on partial-update semantics should switch to `update_rule()` with all desired fields, or implement a custom read-modify-write workflow
- **`wifi.update()`**: Changed from PATCH to GET+PUT pattern for compatibility with current UniFi controller versions
- **PoE port metrics**: `get_port_metrics()` now requires `port_poe` flag on port data before including PoE metrics

#### Protect API

- **REMOTE URL paths**: Removed `/proxy/` prefix from REMOTE connector URLs
- **REMOTE site paths**: REMOTE Protect API paths no longer include `/sites/{site_id}/` segments; all Protect endpoints now use site-agnostic paths

### Removed

- **`devices.execute_port_action()`**: Removed non-functional method

## [1.2.0] - 2026-02-17

### Added

#### Network API

- **DNS Policies**: DNS policy management
  - `get_all()`: List all DNS policies with pagination and filtering
  - `get()`: Get specific DNS policy
  - `create()`: Create DNS record (A, AAAA, CNAME, MX, TXT, SRV, forward domain)
  - `update()`: Update existing DNS policy
  - `delete()`: Remove DNS policy

- **Firewall Policy**: Advanced firewall policy operations
  - `patch_rule()`: Partial update of firewall policy fields
  - `get_policy_ordering()`: Get user-defined policy ordering for zone pair
  - `update_policy_ordering()`: Reorder policies (before/after system-defined)

- **ACL Rule Ordering**: ACL rule priority management
  - `get_ordering()`: Get current ACL rule order
  - `update_ordering()`: Reorder user-defined ACL rules

### Changed

- Update repository URLs and documentation references to tinkerologie organization.

- `FirewallRule.action` now accepts both dict format (`{"type": "ALLOW", "allowReturnTraffic": true}`) and legacy string format for API v10+ compatibility
- Added `FirewallActionConfig` model to parse structured firewall action responses from newer API versions

### Fixed

- **Protect API**: Fixed `Sensor.battery_status` field type - now correctly parses as `BatteryStatus` model with `percentage` and `is_low` fields instead of string
- **Network API**: Added missing `params` parameter support to `_put()` method in base client (required for firewall policy ordering endpoints)
- DNS endpoint now properly handles both `DNSRecordType` enum and string values for `record_type` parameter

## [1.1.0] - 2025-01-22

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
  - `get_wan_interfaces()`: List WAN interfaces with filter support
  - `get_vpn_tunnels()`: List site-to-site VPN tunnels with filter support
  - `get_vpn_servers()`: List VPN servers (WireGuard, OpenVPN, L2TP) with filter support
  - `get_radius_profiles()`: List RADIUS profiles with filter support
  - `get_device_tags()`: List device tags with filter support

- **Firewall Enhancements**:
  - `get_zone()`: Get specific firewall zone
  - `create_zone()`: Create custom firewall zone
  - `update_zone()`: Update firewall zone
  - `delete_zone()`: Delete custom firewall zone
  - Added pagination and filter support to `list_zones()` and `list_rules()`

- **Networks Enhancements**:
  - `get_references()`: Get references to a network (what uses a network)

- **Device Actions**: Device management operations
  - `execute_port_action()`: Control device ports (enable/disable PoE, speed)
  - `execute_action()`: Device actions (restart, locate, adopt, forget)
  - `get_pending_adoption()`: List devices pending adoption
  - `get_statistics()`: Get device statistics

- **Client Actions**: Client management operations
  - `execute_action()`: Client actions (block, unblock, reconnect, forget)

- **Application Info**: `get_application_info()` method on client

- **Filter Query Support**: All list endpoints now support the UniFi filter query syntax
  - Property expressions: `id.eq(123)`, `name.like('guest*')`
  - Compound expressions: `and(name.isNull(), createdAt.gt(2025-01-01))`
  - Negation expressions: `not(name.like('guest*'))`

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
  - `create_rtsps_stream()`: Create RTSPS stream for camera (requires `qualities` parameter)
  - `get_rtsps_stream()`: Get existing RTSPS stream info
  - `delete_rtsps_stream()`: Remove RTSPS stream
  - `create_talkback_session()`: Create two-way audio session
  - `disable_mic_permanently()`: Permanently disable camera microphone
  - `set_hdr_mode()`: Set HDR mode (off, auto, always)
  - `set_video_mode()`: Set video mode (default, highFps, sport)
  - `get_snapshot()`: Retrieve camera snapshot image
  - `construct_rtsp_url()`: Helper method to construct RTSP URLs for cameras

- **WebSocket Subscriptions**: Real-time event streaming
  - `subscribe_devices()`: Subscribe to device state updates
  - `subscribe_events()`: Subscribe to Protect events
  - `get_host_id()`: Helper method to get host ID for WebSocket subscriptions

### Changed

- Update repository URLs and documentation references to tinkerologie organization.

- Renamed `list()` methods to `get_all()` to avoid shadowing Python built-in
- Standardized filter parameter naming to `filter_str` across all endpoints
- Fixed `create_rtsps_stream()` to require `qualities` parameter per API spec
- Fixed `delete_rtsps_stream()` to pass qualities as query parameters
- Fixed WAN interfaces endpoint path from `/wan` to `/wans`
- Fixed `ClientType` enum serialization to return string values instead of enum objects
- Made WAN/VPN model fields optional for better API compatibility

### Fixed

- RTSPS stream creation now properly sends `qualities` in request body
- Client type field now returns string ("WIRED"/"WIRELESS") instead of enum object
- WAN interfaces API now uses correct endpoint path

## [1.0.0] - 2025-01-17

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
