"""Tests for GloBird sensor helpers."""

from __future__ import annotations

import asyncio
import importlib
import json
import sys
import types
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

COMPONENT_PATH = Path(__file__).parents[1] / "custom_components"
INTEGRATION_PATH = COMPONENT_PATH / "globird"
GAS_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "globird_gas_responses.json"

custom_components = types.ModuleType("custom_components")
custom_components.__path__ = [str(COMPONENT_PATH)]  # type: ignore[attr-defined]
globird_package = types.ModuleType("custom_components.globird")
globird_package.__path__ = [str(INTEGRATION_PATH)]  # type: ignore[attr-defined]
sys.modules["custom_components"] = custom_components
sys.modules["custom_components.globird"] = globird_package

homeassistant = types.ModuleType("homeassistant")
components = types.ModuleType("homeassistant.components")
sensor_component = types.ModuleType("homeassistant.components.sensor")
config_entries = types.ModuleType("homeassistant.config_entries")
const = types.ModuleType("homeassistant.const")
core = types.ModuleType("homeassistant.core")
recorder = types.ModuleType("homeassistant.components.recorder")
recorder_models = types.ModuleType("homeassistant.components.recorder.models")
helpers = types.ModuleType("homeassistant.helpers")
entity_platform = types.ModuleType("homeassistant.helpers.entity_platform")
event = types.ModuleType("homeassistant.helpers.event")
storage = types.ModuleType("homeassistant.helpers.storage")
update_coordinator = types.ModuleType("homeassistant.helpers.update_coordinator")
util = types.ModuleType("homeassistant.util")
dt = types.ModuleType("homeassistant.util.dt")
util_logging = types.ModuleType("homeassistant.util.logging")
unit_conversion = types.ModuleType("homeassistant.util.unit_conversion")


class SensorDeviceClass:
    """Minimal sensor device classes used by the integration."""

    ENERGY = "energy"
    ENUM = "enum"
    GAS = "gas"
    MONETARY = "monetary"
    TEMPERATURE = "temperature"
    TIMESTAMP = "timestamp"


class SensorEntity:
    """Minimal stand-in for Home Assistant's SensorEntity."""


class SensorStateClass:
    """Minimal sensor state classes used by the integration."""

    MEASUREMENT = "measurement"
    TOTAL = "total"
    TOTAL_INCREASING = "total_increasing"


class CoordinatorEntity:
    """Minimal stand-in for Home Assistant's CoordinatorEntity."""

    def __class_getitem__(cls, _item: Any) -> type[CoordinatorEntity]:
        return cls

    def __init__(self, coordinator: Any) -> None:
        self.coordinator = coordinator
        self.hass = object()
        self._remove_callbacks: list[Any] = []
        self._write_count = 0

    async def async_added_to_hass(self) -> None:
        return None

    def async_on_remove(self, callback: Any) -> None:
        self._remove_callbacks.append(callback)

    def async_write_ha_state(self) -> None:
        self._write_count += 1

    def _handle_coordinator_update(self) -> None:
        return None


class DataUpdateCoordinator:
    """Minimal stand-in for Home Assistant's DataUpdateCoordinator."""

    def __class_getitem__(cls, _item: Any) -> type[DataUpdateCoordinator]:
        return cls

    def __init__(
        self,
        *_args: Any,
        update_interval: timedelta | None = None,
        **_kwargs: Any,
    ) -> None:
        self.update_interval = update_interval


class Store:
    """Minimal stand-in for Home Assistant storage."""

    def __class_getitem__(cls, _item: Any) -> type[Store]:
        return cls

    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        return None


class UpdateFailed(Exception):
    """Minimal stand-in for Home Assistant's update failure."""


class StatisticMeanType:
    """Minimal recorder mean type enum stub."""

    NONE = 0


def async_track_point_in_time(*_args: Any, **_kwargs: Any) -> Any:
    """Return an unsubscribe callback."""
    return lambda: None


sensor_component.SensorDeviceClass = SensorDeviceClass
sensor_component.SensorEntity = SensorEntity
sensor_component.SensorStateClass = SensorStateClass
config_entries.ConfigEntry = object
const.EntityCategory = types.SimpleNamespace(DIAGNOSTIC="diagnostic")
const.UnitOfEnergy = types.SimpleNamespace(KILO_WATT_HOUR="kWh")
const.UnitOfTemperature = types.SimpleNamespace(CELSIUS="C")
const.UnitOfVolume = types.SimpleNamespace(CUBIC_METERS="m3")
core.HomeAssistant = object
core.callback = lambda func: func
entity_platform.AddEntitiesCallback = object
event.async_track_point_in_time = async_track_point_in_time
storage.Store = Store
update_coordinator.CoordinatorEntity = CoordinatorEntity
update_coordinator.DataUpdateCoordinator = DataUpdateCoordinator
update_coordinator.UpdateFailed = UpdateFailed
recorder_models.StatisticMeanType = StatisticMeanType
recorder_models.StatisticData = lambda **kwargs: dict(kwargs)
recorder_models.StatisticMetaData = lambda **kwargs: dict(kwargs)
unit_conversion.VolumeConverter = types.SimpleNamespace(UNIT_CLASS="volume")
unit_conversion.EnergyConverter = types.SimpleNamespace(UNIT_CLASS="energy")
dt.now = lambda: datetime.now(UTC)
util.dt = dt
util_logging.log_exception = lambda *_args, **_kwargs: None
util.logging = util_logging
util.unit_conversion = unit_conversion

components.sensor = sensor_component
components.recorder = recorder
helpers.entity_platform = entity_platform
helpers.event = event
helpers.storage = storage
helpers.update_coordinator = update_coordinator
homeassistant.components = components
homeassistant.config_entries = config_entries
homeassistant.const = const
homeassistant.core = core
homeassistant.helpers = helpers
homeassistant.util = util

sys.modules["homeassistant"] = homeassistant
sys.modules["homeassistant.components"] = components
sys.modules["homeassistant.components.recorder"] = recorder
sys.modules["homeassistant.components.recorder.models"] = recorder_models
sys.modules["homeassistant.components.sensor"] = sensor_component
sys.modules["homeassistant.config_entries"] = config_entries
sys.modules["homeassistant.const"] = const
sys.modules["homeassistant.core"] = core
sys.modules["homeassistant.helpers"] = helpers
sys.modules["homeassistant.helpers.entity_platform"] = entity_platform
sys.modules["homeassistant.helpers.event"] = event
sys.modules["homeassistant.helpers.storage"] = storage
sys.modules["homeassistant.helpers.update_coordinator"] = update_coordinator
sys.modules["homeassistant.util"] = util
sys.modules["homeassistant.util.dt"] = dt
sys.modules["homeassistant.util.logging"] = util_logging
sys.modules["homeassistant.util.unit_conversion"] = unit_conversion

sensor = importlib.import_module("custom_components.globird.sensor")


def load_gas_fixtures() -> dict[str, Any]:
    """Load dedicated gas fixture payloads."""
    return json.loads(GAS_FIXTURE_PATH.read_text())


def test_expected_monthly_cost_uses_existing_mdi_icon() -> None:
    """Expected Monthly Cost should not point at a non-existent MDI icon."""
    assert sensor.GloBirdExpectedMonthlyCostSensor.sensor_icon == "mdi:cash-clock"


def test_billing_period_days_uses_home_assistant_local_date(monkeypatch: Any) -> None:
    """Billing Period Days should follow the configured HA timezone."""
    data = {
        "dashboard": {
            "data": {
                "lastestInvoice": {
                    "issuedDate": "2026-07-02T00:00:00",
                },
            },
        },
    }
    local_tz = timezone(timedelta(hours=10))
    monkeypatch.setattr(
        sensor.dt_util,
        "now",
        lambda: datetime(2026, 7, 2, 0, 30, tzinfo=local_tz),
    )

    assert sensor._billing_period_completed_days(data) == 0

    monkeypatch.setattr(
        sensor.dt_util,
        "now",
        lambda: datetime(2026, 7, 3, 0, 30, tzinfo=local_tz),
    )

    assert sensor._billing_period_completed_days(data) == 1


def test_zerohero_status_reports_latest_complete_result() -> None:
    """Achieved/missed should follow the latest complete portal result."""
    local_tz = timezone(timedelta(hours=10))
    yesterday_summary = {
        "latest_day": "2026/07/01",
        "latest_day_zerohero_credit": 0.0,
        "latest_day_zerohero_achieved": False,
    }

    assert (
        sensor._zerohero_status(
            yesterday_summary,
            datetime(2026, 7, 2, 20, 59, tzinfo=local_tz),
        )
        == "missed"
    )
    assert (
        sensor._zerohero_status(
            yesterday_summary,
            datetime(2026, 7, 2, 21, 0, tzinfo=local_tz),
        )
        == "missed"
    )

    today_summary = {
        "latest_day": "2026/07/02",
        "latest_day_zerohero_credit": 0.0,
        "latest_day_zerohero_achieved": False,
    }

    assert (
        sensor._zerohero_status(
            today_summary,
            datetime(2026, 7, 2, 21, 30, tzinfo=local_tz),
        )
        == "missed"
    )

    today_summary["latest_day_zerohero_credit"] = -0.3
    today_summary["latest_day_zerohero_achieved"] = True

    assert (
        sensor._zerohero_status(
            today_summary,
            datetime(2026, 7, 2, 21, 30, tzinfo=local_tz),
        )
        == "achieved"
    )


def test_zerohero_status_is_unknown_without_usable_cost_summary() -> None:
    """Missing latest complete cost data should remain unknown."""
    assert sensor._zerohero_status({}) == "unknown"


def test_is_gas_service_matches_service_type() -> None:
    """Gas services should be detected from serviceType."""
    assert sensor._is_gas_service({"serviceType": "Gas"}) is True
    assert sensor._is_gas_service({"serviceType": "POWER"}) is False


def test_non_gas_service_sensor_name_uses_original_title() -> None:
    """Non-gas service sensors should keep the original title-only naming."""

    class FakeCoordinator:
        data = {}

    entity = sensor.GloBirdBillingPeriodCostSensor(
        FakeCoordinator(),
        types.SimpleNamespace(entry_id="entry-1"),
        {
            "accountServiceId": 810965,
            "serviceType": "Power",
            "siteIdentifier": "NMI00000001",
        },
    )

    assert entity._attr_name == "Billing Period Cost"


def test_gas_service_sensor_name_includes_site_suffix() -> None:
    """Gas service sensors should include identifiers to avoid ambiguous names."""

    class FakeCoordinator:
        data = {
            "service_data": {
                "123456": {
                    "service": {
                        "accountServiceId": 123456,
                        "siteIdentifier": "55104217567",
                        "serviceType": "Gas",
                    },
                    "gas_reading_summary": {},
                }
            }
        }

    reading = sensor.GloBirdLatestGasReadingSensor(
        FakeCoordinator(),
        types.SimpleNamespace(entry_id="entry-1"),
        {
            "accountServiceId": 123456,
            "serviceType": "Gas",
            "siteIdentifier": "55104217567",
        },
    )
    reading_date = sensor.GloBirdLatestGasReadingDateSensor(
        FakeCoordinator(),
        types.SimpleNamespace(entry_id="entry-1"),
        {
            "accountServiceId": 123456,
            "serviceType": "Gas",
            "siteIdentifier": "55104217567",
        },
    )

    assert reading._attr_name == "Latest Gas Reading (55104217567)"
    assert reading_date._attr_name == "Latest Gas Reading Date (55104217567)"


def test_gas_shared_service_sensors_include_site_suffix() -> None:
    """Shared service sensors should also include suffixes when the service is gas."""

    class FakeCoordinator:
        data = {
            "service_data": {
                "123456": {
                    "service": {
                        "accountServiceId": 123456,
                        "siteIdentifier": "55104217567",
                        "serviceType": "Gas",
                    }
                }
            }
        }

    status = sensor.GloBirdServiceStatusSensor(
        FakeCoordinator(),
        types.SimpleNamespace(entry_id="entry-1"),
        {
            "accountServiceId": 123456,
            "serviceType": "Gas",
            "siteIdentifier": "55104217567",
        },
    )
    meter = sensor.GloBirdMeterInfoSensor(
        FakeCoordinator(),
        types.SimpleNamespace(entry_id="entry-1"),
        {
            "accountServiceId": 123456,
            "serviceType": "Gas",
            "siteIdentifier": "55104217567",
        },
    )

    assert status._attr_name == "Service Status (55104217567)"
    assert meter._attr_name == "Meter Info (55104217567)"


def test_safe_statistic_id_sanitizes_for_recorder() -> None:
    """Recorder statistic IDs must contain only supported characters."""
    assert (
        sensor._safe_statistic_id(
            "01ABC-service 123/latest-gas-reading",
            fallback="service-1",
        )
        == "svc_01abc_service_123_latest_gas_reading"
    )
    assert sensor._safe_statistic_id("a---b___c", fallback="x") == "a_b_c"


def test_statistic_id_uses_recorder_domain_prefix() -> None:
    """Statistic IDs should use recorder's <domain>:<slug> format."""
    suffix = sensor._safe_statistic_id("entry-1_service_123_latest_gas_reading", "x")
    statistic_id = f"{sensor.DOMAIN}:{suffix}"
    assert statistic_id.startswith(f"{sensor.DOMAIN}:")
    assert "__" not in statistic_id


def test_gas_statistics_continue_across_meter_replacement() -> None:
    """A lower replacement-meter index should continue the cumulative sum."""
    local_tz = timezone(timedelta(hours=10))
    statistics = sensor._build_gas_statistics(
        [
            {"date": "2026-01-01", "read_index": 100.0, "serial": "old"},
            {"date": "2026-02-01", "read_index": 110.0, "serial": "old"},
            {"date": "2026-03-01", "read_index": 5.0, "serial": "new"},
            {"date": "2026-04-01", "read_index": 12.0, "serial": "new"},
        ],
        tzinfo=local_tz,
    )

    assert [row["state"] for row in statistics] == [100.0, 110.0, 5.0, 12.0]
    assert [row["sum"] for row in statistics] == [100.0, 110.0, 110.0, 117.0]
    assert statistics[0]["start"].utcoffset() == timedelta(hours=10)


def test_gas_statistics_ignore_downward_correction_without_double_counting() -> None:
    """A corrected lower read must not be counted again when the index recovers."""
    statistics = sensor._build_gas_statistics(
        [
            {"date": "2026-01-01", "read_index": 100.0, "serial": "meter"},
            {"date": "2026-02-01", "read_index": 95.0, "serial": "meter"},
            {"date": "2026-03-01", "read_index": 102.0, "serial": "meter"},
        ],
        tzinfo=UTC,
    )

    assert [row["sum"] for row in statistics] == [100.0, 100.0, 102.0]


def test_latest_gas_reading_sensor_exposes_reading_summary() -> None:
    """Latest Gas Reading sensor should surface parsed basic meter data."""
    gas_fixture = load_gas_fixtures()["gas_service_data"]

    class FakeCoordinator:
        data = {
            "service_data": {
                "123456": gas_fixture,
            }
        }

    sensor_entity = sensor.GloBirdLatestGasReadingSensor(
        FakeCoordinator(),
        types.SimpleNamespace(entry_id="entry-1"),
        {"accountServiceId": 123456, "serviceType": "Gas"},
    )

    assert sensor_entity.native_value == 3050.0
    assert sensor_entity.extra_state_attributes["latest_reading_date"] == "2026-07-12"
    assert sensor_entity.extra_state_attributes["history_count"] == 1


def test_global_sensors_return_values_and_attributes() -> None:
    """Global sensor descriptors should map coordinator data into state values."""

    class FakeCoordinator:
        data = {
            "dashboard": {
                "data": {
                    "currentBalance": 42.2,
                    "accountId": 1,
                    "accountNumber": "A1",
                    "lastestCorrespondence": {"id": 1},
                    "lastestInvoice": {"amount": 12.34},
                    "recentAccountTransactions": [{"id": "t1"}],
                }
            },
            "balance": {
                "data": {
                    "balance": 55.0,
                    "maxRefundableAmount": 10.0,
                    "showRefundableAmount": True,
                }
            },
            "signup_info": {"data": [1, 2, 3]},
            "last_update": 1700000000,
            "_fetch_errors": {},
        }

    entities = [
        sensor.GloBirdGlobalSensor(
            FakeCoordinator(),
            types.SimpleNamespace(entry_id="entry-1"),
            description,
        )
        for description in sensor.GLOBAL_SENSORS
    ]

    assert len(entities) == len(sensor.GLOBAL_SENSORS)
    values = {entity._description.key: entity.native_value for entity in entities}
    assert values["balance"] == -55.0
    assert values["dashboard_balance"] == -42.2
    assert values["latest_invoice"] == 12.34
    assert values["signup_services"] == 3
    assert values["refresh_status"] == "ok"

    attrs = {
        entity._description.key: entity.extra_state_attributes for entity in entities
    }
    assert attrs["balance"]["max_refundable_amount"] == 10.0
    assert attrs["dashboard_balance"]["account_number"] == "A1"


def test_service_sensors_return_expected_values() -> None:
    """Service-level sensors should read from service_data generated by API summaries."""

    service = {
        "accountServiceId": 810965,
        "siteIdentifier": "NMI-1",
        "siteAddress": "Street",
        "postCode": "3000",
        "serviceType": "Power",
        "accountId": 1,
        "accountNumber": "A1",
    }
    detail = {
        "service": service,
        "status": {"status": "Switched"},
        "meter": {"meterReadType": "SMART", "serialStatus": "Active"},
        "usage_summary": {
            "total_usage": 10.5,
            "latest_day_usage": 1.2,
            "total_export": 3.4,
            "latest_day_export": 0.3,
            "daily": [{"readDate": "2026-07-01", "usage": 1.2}],
            "export_daily": [{"readDate": "2026-07-01", "usage": 0.3}],
            "latest_intervals": [0.4, 0.8],
            "registers": [],
        },
        "cost_summary": {
            "total_amount": 12.5,
            "latest_day_amount": 1.1,
            "latest_day": "2026/07/01",
            "latest_available_day": "2026/07/01",
            "latest_available_day_complete": True,
            "latest_day_zerohero_credit": -0.2,
            "latest_day_zerohero_achieved": True,
            "daily": [],
            "daily_totals": [{"date": "2026/07/01", "amount": 1.1}],
            "available_daily": [],
            "categories": [],
        },
        "latest_data_status": {
            "status": "ready",
            "latest_ready_day": "2026/07/01",
            "latest_usage_day": "2026/07/01",
            "latest_cost_day": "2026/07/01",
            "latest_available_cost_day": "2026/07/01",
            "latest_available_cost_day_complete": True,
            "incomplete_cost_days": [],
        },
        "weather_summary": {
            "days": 1,
            "latest_date": "2026-07-01",
            "latest_min_temp": 12,
            "latest_max_temp": 27,
            "daily": [{"dateAsDate": "2026-07-01", "obMinTemp": 12, "obMaxTemp": 27}],
        },
    }

    class FakeCoordinator:
        data = {
            "service_data": {"810965": detail},
            "dashboard": {
                "data": {"lastestInvoice": {"issuedDate": "2026-07-01T00:00:00"}}
            },
            "last_update": 1700000000,
        }

    entry = types.SimpleNamespace(entry_id="entry-1")
    created = [
        sensor.GloBirdServiceStatusSensor(FakeCoordinator(), entry, service),
        sensor.GloBirdMeterInfoSensor(FakeCoordinator(), entry, service),
        sensor.GloBirdLatestDataDateSensor(FakeCoordinator(), entry, service),
        sensor.GloBirdLatestDataStatusSensor(FakeCoordinator(), entry, service),
        sensor.GloBirdUsageTotalSensor(FakeCoordinator(), entry, service),
        sensor.GloBirdLatestDayUsageSensor(FakeCoordinator(), entry, service),
        sensor.GloBirdSolarExportTotalSensor(FakeCoordinator(), entry, service),
        sensor.GloBirdLatestDaySolarExportSensor(FakeCoordinator(), entry, service),
        sensor.GloBirdCostTotalSensor(FakeCoordinator(), entry, service),
        sensor.GloBirdLatestDayCostSensor(FakeCoordinator(), entry, service),
        sensor.GloBirdZeroHeroStatusSensor(FakeCoordinator(), entry, service),
        sensor.GloBirdExpectedMonthlyCostSensor(FakeCoordinator(), entry, service),
        sensor.GloBirdBillingPeriodDaysSensor(FakeCoordinator(), entry, service),
        sensor.GloBirdBillingPeriodCostSensor(FakeCoordinator(), entry, service),
        sensor.GloBirdWeatherSummarySensor(FakeCoordinator(), entry, service),
    ]

    values = [entity.native_value for entity in created]
    assert "Switched" in values
    assert "SMART" in values
    assert "2026/07/01" in values
    assert "ready" in values
    assert 10.5 in values
    assert 1.2 in values
    assert 3.4 in values
    assert 0.3 in values
    assert 12.5 in values
    assert 1.1 in values
    assert "achieved" in values
    assert 27 in values

    # Touch attributes for branch coverage across sensor classes.
    for entity in created:
        attrs = entity.extra_state_attributes
        assert "service_type" in attrs


def test_async_setup_entry_adds_global_account_and_service_entities() -> None:
    """Setup should create entity instances for global, account, and service sensors."""

    class FakeCoordinator:
        data = {
            "accounts": [
                {
                    "accountId": 1,
                    "accountNumber": "A1",
                    "service_count": 1,
                }
            ],
            "services": [
                {
                    "accountServiceId": 810965,
                    "serviceType": "Power",
                    "siteIdentifier": "NMI-1",
                }
            ],
            "service_data": {
                "810965": {
                    "service": {
                        "accountServiceId": 810965,
                        "serviceType": "Power",
                        "siteIdentifier": "NMI-1",
                    },
                    "usage_summary": {},
                    "cost_summary": {},
                    "latest_data_status": {},
                    "weather_summary": {},
                }
            },
        }

    hass = {
        sensor.DOMAIN: {
            "entry-1": FakeCoordinator(),
        }
    }

    captured: list[Any] = []

    def add_entities(entities: list[Any]) -> None:
        captured.extend(entities)

    asyncio.run(
        sensor.async_setup_entry(
            types.SimpleNamespace(data=hass),
            types.SimpleNamespace(entry_id="entry-1"),
            add_entities,
        )
    )

    assert captured
    assert any(isinstance(entity, sensor.GloBirdGlobalSensor) for entity in captured)
    assert any(
        isinstance(entity, sensor.GloBirdAccountSummarySensor) for entity in captured
    )


def test_global_helper_fallback_branches_without_global_summary() -> None:
    """Helper fallbacks should work when API global summary is unavailable."""
    data = {
        "dashboard": {
            "data": {
                "currentBalance": 2.5,
                "accountId": 1,
                "accountNumber": "A1",
                "lastestCorrespondence": {"id": 1},
                "lastestInvoice": {"amount": 5.5},
                "recentAccountTransactions": [{"id": "t1"}],
            }
        },
        "balance": {
            "data": {
                "balance": 3.1,
                "maxRefundableAmount": 1,
                "showRefundableAmount": True,
            }
        },
        "signup_info": {"data": [1]},
        "last_update": 1700000000,
    }

    assert sensor._balance_value(data) == -3.1
    assert sensor._dashboard_balance_value(data) == -2.5
    assert sensor._latest_invoice_value(data) == 5.5
    assert sensor._signup_services_value(data) == 1
    assert sensor._refresh_status_value(data) == "ok"
    assert sensor._dashboard_attrs(data)["account_number"] == "A1"
    assert sensor._latest_invoice_attrs(data)["amount"] == 5.5


def test_account_summary_returns_empty_when_account_missing() -> None:
    """Account summary entity should gracefully handle missing account rows."""

    class FakeCoordinator:
        data = {"accounts": []}

    entity = sensor.GloBirdAccountSummarySensor(
        FakeCoordinator(),
        types.SimpleNamespace(entry_id="entry-1"),
        {"accountId": 123, "accountNumber": "A123"},
    )
    assert entity.native_value is None
    assert entity.extra_state_attributes == {}


def test_zerohero_boundary_scheduling_and_callbacks(monkeypatch: Any) -> None:
    """ZeroHero sensor should schedule and cancel boundary callbacks."""

    scheduled = {}

    def fake_track(_hass: Any, callback: Any, when: Any) -> Any:
        scheduled["callback"] = callback
        scheduled["when"] = when

        def unsub() -> None:
            scheduled["unsub_called"] = True

        return unsub

    monkeypatch.setattr(sensor, "async_track_point_in_time", fake_track)

    class FakeCoordinator:
        data = {
            "service_data": {
                "1": {"service": {"accountServiceId": 1}, "cost_summary": {}}
            }
        }

    entity = sensor.GloBirdZeroHeroStatusSensor(
        FakeCoordinator(),
        types.SimpleNamespace(entry_id="entry-1"),
        {"accountServiceId": 1, "serviceType": "Power"},
    )
    entity.hass = types.SimpleNamespace()

    asyncio.run(entity.async_added_to_hass())
    assert "when" in scheduled

    entity._handle_zerohero_boundary_update(datetime.now(UTC))
    entity._cancel_zerohero_boundary_update()
    assert scheduled.get("unsub_called") is True


def test_gas_statistics_import_paths(monkeypatch: Any) -> None:
    """Gas statistics uploader should handle success and add failures safely."""

    class FakeCoordinator:
        data = {
            "service_data": {
                "123": {
                    "service": {"accountServiceId": 123, "serviceType": "Gas"},
                    "gas_reading_summary": {
                        "history": [
                            {"date": "2026-01-01", "read_index": 100.0, "serial": "x"},
                            {"date": "2026-01-02", "read_index": 101.0, "serial": "x"},
                        ],
                        "latest_reading": 101.0,
                    },
                }
            }
        }

    entity = sensor.GloBirdLatestGasReadingSensor(
        FakeCoordinator(),
        types.SimpleNamespace(entry_id="entry-1"),
        {"accountServiceId": 123, "serviceType": "Gas"},
    )
    entity.hass = types.SimpleNamespace(async_create_task=lambda _coro: None)

    recorder_statistics = types.ModuleType(
        "homeassistant.components.recorder.statistics"
    )

    class StatisticData(dict):
        def __init__(self, **kwargs: Any) -> None:
            super().__init__(**kwargs)

    class StatisticMetaData(dict):
        def __init__(self, **kwargs: Any) -> None:
            super().__init__(**kwargs)

    async def add_ok(_hass: Any, _meta: Any, _stats: Any) -> None:
        return None

    recorder_statistics.StatisticData = StatisticData
    recorder_statistics.StatisticMetaData = StatisticMetaData
    recorder_statistics.async_add_external_statistics = add_ok
    sys.modules["homeassistant.components.recorder.statistics"] = recorder_statistics

    asyncio.run(entity._async_upload_historical_statistics())

    async def add_fail(_hass: Any, _meta: Any, _stats: Any) -> None:
        raise RuntimeError("fail")

    recorder_statistics.async_add_external_statistics = add_fail
    asyncio.run(entity._async_upload_historical_statistics())


def test_latest_data_status_fallback_and_billing_start_invalid() -> None:
    """Fallback status and invalid billing date should be handled gracefully."""
    status = sensor._latest_data_status({"usage_summary": {}, "cost_summary": {}})
    assert status["status"] == "no_data"
    assert (
        sensor._billing_period_start(
            {"dashboard": {"data": {"lastestInvoice": {"issuedDate": "bad"}}}}
        )
        is None
    )


def test_billing_period_cost_sensor_fallbacks() -> None:
    """Billing period cost sensor should return fallback totals when no start date."""

    service = {"accountServiceId": 1, "serviceType": "Power", "siteIdentifier": "NMI"}

    class FakeCoordinator:
        data = {
            "dashboard": {"data": {"lastestInvoice": {}}},
            "service_data": {
                "1": {
                    "service": service,
                    "cost_summary": {
                        "total_amount": 4.2,
                        "daily_totals": [{"date": "2026/01/01", "amount": 4.2}],
                    },
                }
            },
        }

    entity = sensor.GloBirdBillingPeriodCostSensor(
        FakeCoordinator(),
        types.SimpleNamespace(entry_id="entry-1"),
        service,
    )
    assert entity.native_value == 4.2
    assert entity.last_reset is None


def test_energy_dashboard_sensors_and_external_statistics() -> None:
    """Test Energy Dashboard usage, solar export, cost, and solar credit sensors and external stats."""
    service = {"accountServiceId": 1, "serviceType": "Power", "siteIdentifier": "NMI-1"}
    gas_service = {
        "accountServiceId": 2,
        "serviceType": "Gas",
        "siteIdentifier": "MIRN-1",
    }

    class FakeCoordinator:
        data = {
            "last_update": 1700000000.0,
            "dashboard": {
                "data": {"lastestInvoice": {"issuedDate": "2026-09-01T00:00:00"}}
            },
            "accounts": [
                {"accountId": 10, "accountNumber": "ACC-10", "service_count": 2}
            ],
            "services": [service, gas_service],
            "service_data": {
                "1": {
                    "service": service,
                    "usage_summary": {
                        "total_usage": 120.5,
                        "latest_day": "2026-09-27",
                        "latest_day_usage": 14.2,
                        "daily": [{"readDate": "2026-09-27", "usage": 14.2}],
                        "total_export": 45.0,
                        "latest_day_export": 6.5,
                        "export_daily": [{"readDate": "2026-09-27", "usage": 6.5}],
                        "registers": [],
                    },
                    "cost_summary": {
                        "total_amount": 32.10,
                        "total_import_cost": 36.10,
                        "total_export_credit": 4.00,
                        "latest_day": "2026-09-27",
                        "latest_day_amount": 3.50,
                        "latest_day_import_cost": 4.00,
                        "latest_day_export_credit": 0.50,
                        "daily_totals": [{"date": "2026-09-27", "amount": 3.50}],
                        "daily_export_credit_totals": [
                            {"date": "2026-09-27", "amount": 0.50}
                        ],
                    },
                },
                "2": {
                    "service": gas_service,
                    "gas_reading_summary": {
                        "latest_reading": 250.0,
                        "latest_reading_date": "2026-09-26",
                        "latest_reading_source": "Basic",
                        "latest_reading_serial": "G1",
                        "latest_reading_quality_method": "Actual",
                        "history": [],
                    },
                    "cost_summary": {
                        "total_amount": 18.00,
                        "latest_day": "2026-09-26",
                        "latest_day_amount": 1.20,
                        "daily_totals": [{"date": "2026-09-26", "amount": 1.20}],
                    },
                },
            },
        }

    recorder_statistics = types.ModuleType(
        "homeassistant.components.recorder.statistics"
    )
    uploaded: list[tuple[Any, Any]] = []

    async def add_ok(_hass: Any, meta: Any, stats: Any) -> None:
        uploaded.append((meta, stats))

    recorder_statistics.async_add_external_statistics = add_ok
    sys.modules["homeassistant.components.recorder.statistics"] = recorder_statistics

    entry = types.SimpleNamespace(entry_id="entry-1", runtime_data=FakeCoordinator())
    added_entities: list[Any] = []
    asyncio.run(
        sensor.async_setup_entry(
            types.SimpleNamespace(data={sensor.DOMAIN: {"entry-1": FakeCoordinator()}}),
            entry,
            added_entities.extend,
        )
    )
    assert len(added_entities) >= 25

    for ent in added_entities:
        ent.hass = types.SimpleNamespace(
            async_create_task=lambda coro: asyncio.run(coro)
        )
        _ = ent.native_value
        _ = ent.extra_state_attributes
        if hasattr(ent, "last_reset"):
            _ = ent.last_reset
        asyncio.run(ent.async_added_to_hass())
        ent._handle_coordinator_update()

    assert len(uploaded) >= 4

    # Test external statistics error handling and empty/invalid rows
    assert (
        sensor._build_daily_cumulative_statistics(
            ["not-a-dict", {"date": "invalid", "amount": 1.0}],
            date_key="date",
            value_key="amount",
            tzinfo=UTC,
        )
        == []
    )

    async def add_err(_hass: Any, _meta: Any, _stats: Any) -> None:
        raise RuntimeError("db error")

    recorder_statistics.async_add_external_statistics = add_err
    usage_sensor = sensor.GloBirdUsageTotalSensor(FakeCoordinator(), entry, service)
    usage_sensor.hass = types.SimpleNamespace()
    asyncio.run(usage_sensor._async_upload_statistics())

    # Test global summary vs raw fallback functions
    raw_data = {
        "balance": {
            "data": {
                "balance": 10.0,
                "maxRefundableAmount": 5.0,
                "showRefundableAmount": True,
            }
        },
        "dashboard": {
            "data": {
                "currentBalance": 20.0,
                "accountId": 1,
                "accountNumber": "A1",
                "lastestInvoice": {"amount": 50.0},
                "recentAccountTransactions": [{"id": 1}],
            }
        },
        "signup_info": {"data": [{"id": 1}]},
        "last_update": "bad-timestamp",
    }
    assert sensor._balance_value(raw_data) == -10.0
    assert sensor._balance_attrs(raw_data)["max_refundable_amount"] == 5.0
    assert sensor._dashboard_balance_value(raw_data) == -20.0
    assert sensor._dashboard_attrs(raw_data)["account_id"] == 1
    assert sensor._latest_invoice_value(raw_data) == 50.0
    assert sensor._latest_invoice_attrs(raw_data)["amount"] == 50.0
    assert sensor._signup_services_value(raw_data) == 1
    assert len(sensor._signup_services_attrs(raw_data)["signup_info"]) == 1
    assert sensor._timestamp_value("bad-timestamp") is None
    assert sensor._refresh_status_value({"refresh_error": "boom"}) == "error"
    assert (
        sensor._refresh_status_attrs({"refresh_error": "boom"})["refresh_error"]
        == "boom"
    )

    summary_data = {
        "global_summary": {
            "balance": -12.3,
            "max_refundable_amount": 3.0,
            "show_refundable_amount": False,
            "dashboard_balance": -4.5,
            "dashboard": {"account_id": 99},
            "latest_invoice_amount": 88.0,
            "latest_invoice": {"amount": 88.0},
            "signup_services": 2,
            "signup_info": [{"id": 1}, {"id": 2}],
            "refresh_status": "ok",
            "last_successful_refresh": 1700000000.0,
            "last_failed_refresh": None,
            "refresh_error": None,
            "fetch_errors": {},
        }
    }
    assert sensor._balance_value(summary_data) == -12.3
    assert sensor._balance_attrs(summary_data)["max_refundable_amount"] == 3.0
    assert sensor._dashboard_balance_value(summary_data) == -4.5
    assert sensor._dashboard_attrs(summary_data)["account_id"] == 99
    assert sensor._latest_invoice_value(summary_data) == 88.0
    assert sensor._latest_invoice_attrs(summary_data)["amount"] == 88.0
    assert sensor._signup_services_value(summary_data) == 2
    assert len(sensor._signup_services_attrs(summary_data)["signup_info"]) == 2
    assert sensor._refresh_status_value(summary_data) == "ok"
    assert sensor._refresh_status_attrs(summary_data)["refresh_error"] is None
    assert sensor._parse_portal_day("   ") is None
    assert sensor._day_reset_timestamp(None) is None
    assert sensor._billing_period_completed_days({}) is None
    assert sensor._service_name_suffix({}) == "unknown"
    assert sensor._safe_statistic_id("!!!", "!!!") == "service"
    assert sensor._safe_statistic_id("", "123") == "svc_123"
    assert sensor._build_gas_statistics([], tzinfo=UTC) == []
