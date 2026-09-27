"""Tests for GloBird coordinator scheduling helpers."""

from __future__ import annotations

import asyncio
import importlib
import sys
import types
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

COMPONENT_PATH = Path(__file__).parents[1] / "custom_components"
INTEGRATION_PATH = COMPONENT_PATH / "globird"

custom_components = types.ModuleType("custom_components")
custom_components.__path__ = [str(COMPONENT_PATH)]  # type: ignore[attr-defined]
globird_package = types.ModuleType("custom_components.globird")
globird_package.__path__ = [str(INTEGRATION_PATH)]  # type: ignore[attr-defined]
sys.modules["custom_components"] = custom_components
sys.modules["custom_components.globird"] = globird_package

homeassistant = types.ModuleType("homeassistant")
config_entries = types.ModuleType("homeassistant.config_entries")
core = types.ModuleType("homeassistant.core")
helpers = types.ModuleType("homeassistant.helpers")
storage = types.ModuleType("homeassistant.helpers.storage")
update_coordinator = types.ModuleType("homeassistant.helpers.update_coordinator")
util = types.ModuleType("homeassistant.util")
dt = types.ModuleType("homeassistant.util.dt")
util_logging = types.ModuleType("homeassistant.util.logging")


class DataUpdateCoordinator:
    """Minimal stand-in for Home Assistant's coordinator base."""

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
        pass


class UpdateFailed(Exception):
    """Minimal stand-in for Home Assistant's update failure."""


exceptions = types.ModuleType("homeassistant.exceptions")


class ConfigEntryAuthFailed(Exception):
    """Minimal stand-in for Home Assistant's ConfigEntryAuthFailed."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args)
        self.kwargs = kwargs


exceptions.ConfigEntryAuthFailed = ConfigEntryAuthFailed
config_entries.ConfigEntry = object
core.HomeAssistant = object
storage.Store = Store
update_coordinator.DataUpdateCoordinator = DataUpdateCoordinator
update_coordinator.UpdateFailed = UpdateFailed
dt.now = lambda: datetime.now(UTC)
util.dt = dt
util_logging.log_exception = lambda *_args, **_kwargs: None
util.logging = util_logging
helpers.storage = storage
helpers.update_coordinator = update_coordinator
homeassistant.config_entries = config_entries
homeassistant.core = core
homeassistant.exceptions = exceptions
homeassistant.helpers = helpers
homeassistant.util = util

sys.modules["homeassistant"] = homeassistant
sys.modules["homeassistant.config_entries"] = config_entries
sys.modules["homeassistant.core"] = core
sys.modules["homeassistant.exceptions"] = exceptions
sys.modules["homeassistant.helpers"] = helpers
sys.modules["homeassistant.helpers.storage"] = storage
sys.modules["homeassistant.helpers.update_coordinator"] = update_coordinator
sys.modules["homeassistant.util"] = util
sys.modules["homeassistant.util.dt"] = dt
sys.modules["homeassistant.util.logging"] = util_logging

coordinator = importlib.import_module("custom_components.globird.coordinator")


def test_next_ready_poll_interval_targets_configured_daily_start() -> None:
    """Ready data should schedule the next automatic check for the next day."""
    now = datetime(2026, 6, 29, 10, 30, tzinfo=UTC)

    assert coordinator._next_ready_poll_interval(now) == timedelta(
        hours=13,
        minutes=35,
    )
    assert coordinator._next_ready_poll_interval(
        now,
        coordinator._parse_daily_poll_start_time("03:00"),
    ) == timedelta(hours=16, minutes=30)


def test_invalid_daily_poll_start_time_falls_back_to_default() -> None:
    """Invalid stored options should keep the midnight-plus-default behavior."""
    now = datetime(2026, 6, 29, 10, 30, tzinfo=UTC)

    assert coordinator._parse_daily_poll_start_time("25:99").isoformat() == "00:05:00"
    assert coordinator._next_ready_poll_interval(
        now,
        coordinator._parse_daily_poll_start_time("25:99"),
    ) == timedelta(hours=13, minutes=35)


def test_update_interval_slows_only_when_daily_data_is_ready(monkeypatch: Any) -> None:
    """Coordinator returns to normal polling until the latest daily data is ready."""
    now = datetime(2026, 6, 29, 10, 30, tzinfo=UTC)
    monkeypatch.setattr(coordinator.dt_util, "now", lambda: now)

    instance = object.__new__(coordinator.GloBirdCoordinator)
    instance.update_interval = coordinator.ACCOUNT_UPDATE_INTERVAL
    instance.entry = types.SimpleNamespace(options={})

    instance._set_update_interval_for_data(
        {
            "service_data": {
                "svc-1": {
                    "latest_data_status": {
                        "status": "ready",
                        "latest_ready_day": "2026/06/28",
                    },
                },
            },
        }
    )

    assert instance.update_interval == timedelta(hours=13, minutes=35)

    instance._set_update_interval_for_data(
        {
            "service_data": {
                "svc-1": {
                    "latest_data_status": {
                        "status": "waiting_for_cost",
                        "latest_ready_day": "2026/06/27",
                    },
                },
            },
        }
    )

    assert instance.update_interval == coordinator.ACCOUNT_UPDATE_INTERVAL


def test_update_interval_ignores_gas_readiness(monkeypatch: Any) -> None:
    """Gas reads are not daily electricity data and must not prevent slow polling."""
    now = datetime(2026, 6, 29, 10, 30, tzinfo=UTC)
    monkeypatch.setattr(coordinator.dt_util, "now", lambda: now)

    instance = object.__new__(coordinator.GloBirdCoordinator)
    instance.update_interval = coordinator.ACCOUNT_UPDATE_INTERVAL
    instance.entry = types.SimpleNamespace(
        options={coordinator.CONF_DAILY_POLL_START_TIME: "03:00"}
    )
    instance._set_update_interval_for_data(
        {
            "service_data": {
                "power": {
                    "service": {"serviceType": "Power"},
                    "latest_data_status": {
                        "status": "ready",
                        "latest_ready_day": "2026/06/28",
                    },
                },
                "gas": {
                    "service": {"serviceType": "Gas"},
                    "latest_data_status": {
                        "status": "no_data",
                        "latest_ready_day": None,
                    },
                },
            }
        }
    )

    assert instance.update_interval == timedelta(hours=16, minutes=30)

    instance.update_interval = coordinator.ACCOUNT_UPDATE_INTERVAL
    instance._set_update_interval_for_data(
        {
            "service_data": {
                "gas": {
                    "service": {"serviceType": "Gas"},
                    "latest_data_status": {
                        "status": "no_data",
                        "latest_ready_day": None,
                    },
                }
            }
        }
    )

    assert instance.update_interval == timedelta(hours=16, minutes=30)


def test_gas_service_fetches_its_own_meter_and_forces_basic_endpoint() -> None:
    """Mixed accounts must not reuse the primary electricity service's meter."""

    class FakeClient:
        def __init__(self) -> None:
            self.read_meter_ids: list[int] = []
            self.usage_calls: list[dict[str, Any]] = []

        async def get_read_meters(self, *, account_service_id: int) -> dict[str, Any]:
            self.read_meter_ids.append(account_service_id)
            return {
                "data": [
                    {
                        "siteIdentifier": "MIRN-GAS",
                        "serialNumber": "gas-meter",
                        "meterReadType": "BASIC",
                        "serialStatus": "Active",
                    }
                ]
            }

        async def get_usage(self, **kwargs: Any) -> dict[str, Any]:
            self.usage_calls.append(kwargs)
            return {"data": {}, "success": True}

        async def get_cost_detail(self, **_kwargs: Any) -> dict[str, Any]:
            return {"data": [], "success": True}

    instance = object.__new__(coordinator.GloBirdCoordinator)
    instance.client = FakeClient()
    result = asyncio.run(
        instance._fetch_service_detail(
            {
                "accountServiceId": 11,
                "siteIdentifier": "MIRN-GAS",
                "serviceType": "Gas",
            },
            {
                "data": [
                    {
                        "siteIdentifier": "NMI-POWER",
                        "serialNumber": "power-meter",
                        "meterReadType": "SMART",
                        "serialStatus": "Active",
                    }
                ]
            },
            None,
            {},
        )
    )

    assert instance.client.read_meter_ids == [11]
    assert instance.client.usage_calls[0]["serial_number"] == "gas-meter"
    assert instance.client.usage_calls[0]["is_smart"] is False
    assert result["meter"]["serialNumber"] == "gas-meter"


def test_expected_optional_fetch_failure_classification() -> None:
    """Known AccountServiceStatus endpoint failures should be treated as expected."""
    assert (
        coordinator._is_expected_optional_fetch_failure(
            "service_status",
            RuntimeError("Unable to get AccountServiceStatus."),
        )
        is True
    )

    assert (
        coordinator._is_expected_optional_fetch_failure(
            "service_status",
            RuntimeError("temporary timeout"),
        )
        is False
    )

    assert (
        coordinator._is_expected_optional_fetch_failure(
            "balance",
            RuntimeError("Unable to get AccountServiceStatus."),
        )
        is False
    )


def test_async_initialize_restores_cache_and_cookies() -> None:
    """Initialization should load cache and restore persisted cookies once."""

    class FakeStore:
        def __init__(self, payload: Any) -> None:
            self._payload = payload

        async def async_load(self) -> Any:
            return self._payload

    class FakeClient:
        def __init__(self) -> None:
            self.imported = None
            self.restored = None

        def import_session_cookies(self, cookies: list[dict[str, Any]]) -> None:
            self.imported = cookies

        async def restore_session(self, email: str, password: str) -> dict[str, Any]:
            self.restored = (email, password)
            return {"ok": True}

    instance = object.__new__(coordinator.GloBirdCoordinator)
    instance._initialized = False
    instance._cache = None
    instance.email = "user@example.test"
    instance.password = "secret"
    instance.client = FakeClient()
    instance._cache_store = FakeStore({"cached": True})
    instance._cookie_store = FakeStore(
        {"cookies": [{"name": "ARRAffinity", "value": "abc"}]}
    )

    asyncio.run(instance._async_initialize())

    assert instance._initialized is True
    assert instance._cache == {"cached": True}
    assert instance.client.imported == [{"name": "ARRAffinity", "value": "abc"}]
    assert instance.client.restored == ("user@example.test", "secret")


def test_fetch_optional_uses_cache_when_callback_fails() -> None:
    """Optional fetch failures should return cached payloads when available."""
    instance = object.__new__(coordinator.GloBirdCoordinator)

    async def boom() -> dict[str, Any]:
        raise RuntimeError("timeout")

    result = asyncio.run(
        instance._fetch_optional(
            "balance",
            boom,
            {"balance": {"cached": 1}},
            _errors={},
        )
    )

    assert result == {"cached": 1}


def test_async_update_data_returns_stale_cache_on_failure() -> None:
    """When update fails and cache exists, stale cache should be returned."""

    class FakeClient:
        is_authenticated = False

        async def authenticate(self, _email: str, _password: str) -> dict[str, Any]:
            raise RuntimeError("cannot connect")

    instance = object.__new__(coordinator.GloBirdCoordinator)
    instance.email = "user@example.test"
    instance.password = "secret"
    instance.client = FakeClient()
    instance._initialized = True
    instance._cache = {"service_data": {}, "last_update": 1}
    instance.update_interval = coordinator.ACCOUNT_UPDATE_INTERVAL

    result = asyncio.run(instance._async_update_data())

    assert result["service_data"] == {}
    assert "refresh_error" in result
    assert "last_failed_update" in result


def test_async_update_data_success_persists_cache_and_cookies(monkeypatch: Any) -> None:
    """Successful updates should persist refreshed cache and cookies."""

    class FakeStore:
        def __init__(self) -> None:
            self.saved = None

        async def async_save(self, payload: Any) -> None:
            self.saved = payload

        async def async_load(self) -> Any:
            return None

    class FakeClient:
        is_authenticated = False

        def disable_reauth(self) -> None:
            return None

        def enable_reauth(self) -> None:
            return None

        async def authenticate(self, _email: str, _password: str) -> dict[str, Any]:
            return {
                "data": {
                    "accounts": [
                        {
                            "accountId": 1,
                            "accountNumber": "A1",
                            "accountAddress": "Street",
                            "services": [
                                {
                                    "accountServiceId": 10,
                                    "siteIdentifier": "NMI-1",
                                    "serviceType": "Power",
                                    "status": "Switched",
                                }
                            ],
                        }
                    ]
                },
                "success": True,
            }

        async def get_dashboard(self, **_kwargs: Any) -> dict[str, Any]:
            return {"data": {}, "success": True}

        async def get_balance(self, **_kwargs: Any) -> dict[str, Any]:
            return {"data": {"balance": 1}, "success": True}

        async def get_signup_info(self, **_kwargs: Any) -> dict[str, Any]:
            return {"data": [], "success": True}

        async def get_account_service_status(self) -> dict[str, Any]:
            return {"data": {"10": {"status": "Active"}}, "success": True}

        async def get_power_meter_types(self, **_kwargs: Any) -> dict[str, Any]:
            return {"data": [], "success": True}

        async def get_read_meters(self, **_kwargs: Any) -> dict[str, Any]:
            return {
                "data": [
                    {
                        "siteIdentifier": "NMI-1",
                        "serialNumber": "meter-1",
                        "meterReadType": "SMART",
                        "serialStatus": "Active",
                    }
                ],
                "success": True,
            }

        async def get_weather_impacted_days(self, **_kwargs: Any) -> dict[str, Any]:
            return {"data": [], "success": True}

        async def get_usage(self, **_kwargs: Any) -> dict[str, Any]:
            return {"data": [], "success": True}

        async def get_cost_detail(self, **_kwargs: Any) -> dict[str, Any]:
            return {"data": [], "success": True}

        async def get_weather_data(self, **_kwargs: Any) -> dict[str, Any]:
            return {"data": [], "success": True}

        def export_session_cookies(self) -> list[dict[str, str]]:
            return [{"name": "ARRAffinity", "value": "abc"}]

    now = datetime(2026, 6, 29, 10, 30, tzinfo=UTC)
    monkeypatch.setattr(coordinator.dt_util, "now", lambda: now)

    instance = object.__new__(coordinator.GloBirdCoordinator)
    instance._initialized = True
    instance._cache = None
    instance.email = "user@example.test"
    instance.password = "secret"
    instance.client = FakeClient()
    instance._cache_store = FakeStore()
    instance._cookie_store = FakeStore()
    instance.entry = types.SimpleNamespace(options={})
    instance.update_interval = coordinator.ACCOUNT_UPDATE_INTERVAL

    result = asyncio.run(instance._async_update_data())

    assert "service_data" in result
    assert instance._cache_store.saved is not None
    assert instance._cookie_store.saved == {
        "cookies": [{"name": "ARRAffinity", "value": "abc"}]
    }


def test_coordinator_constructor_and_shutdown(monkeypatch: Any) -> None:
    """Constructor should set stores and shutdown should close the client."""

    class FakeStore:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            return None

    class FakeClient:
        def __init__(self) -> None:
            self.closed = False

        async def close(self) -> None:
            self.closed = True

    monkeypatch.setattr(coordinator, "Store", FakeStore)
    monkeypatch.setattr(coordinator, "GloBirdClient", FakeClient)

    entry = types.SimpleNamespace(
        data={coordinator.CONF_EMAIL: "u", coordinator.CONF_PASSWORD: "p"},
        entry_id="entry-1",
        options={},
    )
    instance = coordinator.GloBirdCoordinator(object(), entry)
    assert instance.email == "u"
    asyncio.run(instance.async_shutdown())
    assert instance.client.closed is True


def test_async_initialize_returns_early_when_already_initialized() -> None:
    """Initialization should no-op once already initialized."""
    instance = object.__new__(coordinator.GloBirdCoordinator)
    instance._initialized = True
    instance._cache_store = None
    instance._cookie_store = None
    asyncio.run(instance._async_initialize())


def test_async_update_data_raises_update_failed_without_cache() -> None:
    """Failed refresh without cache should raise UpdateFailed."""

    class FakeClient:
        is_authenticated = False

        async def authenticate(self, _email: str, _password: str) -> dict[str, Any]:
            raise RuntimeError("offline")

    instance = object.__new__(coordinator.GloBirdCoordinator)
    instance.email = "u"
    instance.password = "p"
    instance.client = FakeClient()
    instance._initialized = True
    instance._cache = None
    instance.update_interval = coordinator.ACCOUNT_UPDATE_INTERVAL

    try:
        asyncio.run(instance._async_update_data())
    except coordinator.UpdateFailed:
        pass
    else:
        raise AssertionError("Expected UpdateFailed")


def test_async_update_data_raises_config_entry_auth_failed_on_auth_error() -> None:
    """Authentication errors during update should raise ConfigEntryAuthFailed."""

    class FakeClient:
        is_authenticated = True

        async def get_current_user(self) -> dict[str, Any]:
            raise coordinator.GloBirdAuthError("bad password")

    instance = object.__new__(coordinator.GloBirdCoordinator)
    instance.email = "u"
    instance.password = "p"
    instance.client = FakeClient()
    instance._initialized = True
    instance._cache = {"service_data": {}}
    instance.update_interval = coordinator.ACCOUNT_UPDATE_INTERVAL

    try:
        asyncio.run(instance._async_update_data())
    except coordinator.ConfigEntryAuthFailed:
        pass
    else:
        raise AssertionError("Expected ConfigEntryAuthFailed")


def test_parse_daily_poll_start_time_and_weather_fetch() -> None:
    """Malformed time falls back to default and weather fetch runs when postCode is set."""
    assert (
        coordinator._parse_daily_poll_start_time("bad:time").isoformat() == "00:05:00"
    )

    class FakeClient:
        async def get_read_meters(self, **_kwargs: Any) -> Any:
            return None

        async def get_usage(self, **_kwargs: Any) -> dict[str, Any]:
            return {"data": [], "success": True}

        async def get_cost_detail(self, **_kwargs: Any) -> dict[str, Any]:
            return {"data": [], "success": True}

        async def get_weather_data(self, **_kwargs: Any) -> dict[str, Any]:
            return {
                "data": [
                    {"dateAsDate": "2026-06-28", "obMinTemp": 10, "obMaxTemp": 20}
                ],
                "success": True,
            }

    instance = object.__new__(coordinator.GloBirdCoordinator)
    instance.client = FakeClient()
    detail = asyncio.run(
        instance._fetch_service_detail(
            {
                "accountServiceId": 10,
                "siteIdentifier": "NMI-1",
                "serviceType": "Power",
                "postCode": "3000",
            },
            {
                "data": [
                    {
                        "siteIdentifier": "NMI-1",
                        "serialNumber": "m1",
                        "meterReadType": "SMART",
                        "serialStatus": "Active",
                    }
                ]
            },
            None,
            {},
        )
    )
    assert detail["weather_summary"]["latest_max_temp"] == 20
