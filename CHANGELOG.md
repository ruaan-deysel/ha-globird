# Changelog

All notable changes to this project are documented in this file.

This project uses Home Assistant's calendar versioning scheme (`YYYY.M.P`, for example `2026.10.0`).

## [2026.10.0] - 2026-09-28

### Added
- **Home Assistant Energy Dashboard Support**:
  - Enabled `SensorStateClass.TOTAL` and `last_reset` tracking across electricity and gas cost sensors (`Recent Cost Total`, `Latest Daily Cost`, `Billing Period Cost`) so they can be selected directly in the Energy Dashboard under *Use an entity tracking the total costs*.
  - Added `Recent Solar Export Credit Total` and `Latest Daily Solar Export Credit` (`AUD`, `SensorDeviceClass.MONETARY`, `SensorStateClass.TOTAL`) to track solar feed-in compensation in the Energy Dashboard under *Return to grid*.
  - Added `last_reset` support on `Latest Day Usage` and `Latest Day Solar Export` sensors so daily meter cycles reset cleanly at midnight in Home Assistant's Recorder.
  - Added full cost and readiness sensor coverage (`Recent Cost Total`, `Latest Daily Cost`, `Billing Period Cost`, `Expected Monthly Cost`, `Billing Period Days`, `Latest Data Date`, `Latest Data Status`) for Gas services in addition to Electricity services.
  - Added automatic Recorder long-term external statistics (`globird:*`) backfilling for daily electricity consumption (`kWh`), solar export (`kWh`), net cost (`AUD`), and solar export credits (`AUD`) alongside serial-aware gas meter statistics (`m³`).
- **Home Assistant Integration Quality Scale (Platinum)**:
  - Implemented `ConfigEntry.runtime_data` (`GloBirdConfigEntry`) for typed coordinator storage (`runtime-data`).
  - Added UI Re-authentication (`async_step_reauth` / `async_step_reauth_confirm`) and UI Reconfiguration (`async_step_reconfigure`) flows (`reauthentication-flow`, `reconfiguration-flow`).
  - Raised `ConfigEntryAuthFailed` with translatable exception keys on authentication failures (`test-before-setup`, `exception-translations`).
  - Added `icons.json` for entity and state icon translations (`icon-translations`), `EntityCategory.DIAGNOSTIC` classifications (`entity-category`), `PARALLEL_UPDATES = 0` (`parallel-updates`), and `quality_scale.yaml`.
- **Automated Release Workflow**:
  - Added `.github/workflows/release.yaml` to monitor `custom_components/globird/manifest.json` and `CHANGELOG.md`, validate Home Assistant versioning (`YYYY.M.P`), and automatically publish GitHub Releases with extracted changelog notes.

### Changed
- **Client Architecture & Pydantic v2**:
  - Renamed `custom_components/globird/api/api.py` to `custom_components/globird/api/client.py` and exposed `custom_components/globird/client.py`.
  - Upgraded `custom_components/globird/api/models.py` to use Pydantic v2 (`ConfigDict`, `@field_validator`, `Literal` types, `CostDailyTotalRow`, `BillingPeriodProjection`, and import/export cost breakdown fields).
  - Updated `./script/query-api` to automatically resolve `accountId` from `current_user` for account-scoped endpoints (`dashboard`, `balance`, `signup_info`) and handle newly transferring accounts without active meter data gracefully.

### Fixed
- Resolved all strict `pyright` type-checking diagnostics across `config_flow.py` and `sensor.py` (`0 errors, 0 warnings`).
