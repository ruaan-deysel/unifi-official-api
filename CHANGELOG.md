# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

- `FirewallRule.action` now accepts both dict format (`{"type": "ALLOW", "allowReturnTraffic": true}`) and legacy string format for API v10+ compatibility
- Added `FirewallActionConfig` model to parse structured firewall action responses from newer API versions

### Fixed

- **Protect API**: Fixed `Sensor.battery_status` field type - now correctly parses as `BatteryStatus` model with `percentage` and `is_low` fields instead of string
- **Network API**: Added missing `params` parameter support to `_put()` method in base client (required for firewall policy ordering endpoints)
- DNS endpoint now properly handles both `DNSRecordType` enum and string values for `record_type` parameter

## [1.0.0] - 2024-01-17

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
