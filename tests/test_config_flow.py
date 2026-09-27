"""Tests for GloBird config flow helpers."""

from __future__ import annotations

import asyncio
import importlib
import sys
import types
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

voluptuous = types.ModuleType("voluptuous")
homeassistant = types.ModuleType("homeassistant")
config_entries = types.ModuleType("homeassistant.config_entries")
data_entry_flow = types.ModuleType("homeassistant.data_entry_flow")
helpers = types.ModuleType("homeassistant.helpers")
selector = types.ModuleType("homeassistant.helpers.selector")
util = types.ModuleType("homeassistant.util")
util_logging = types.ModuleType("homeassistant.util.logging")


class Schema(dict):
    """Minimal schema object that preserves field keys for assertions."""


class Required:
    """Minimal required field marker."""

    def __init__(self, key: str, default: Any | None = None) -> None:
        self.key = key
        self.default = default

    def __repr__(self) -> str:
        return self.key

    def __hash__(self) -> int:
        return hash((self.key, self.default))


class ConfigFlow:
    """Minimal stand-in for Home Assistant's config flow base."""

    def __init_subclass__(cls, **_kwargs: Any) -> None:
        return None

    async def async_set_unique_id(self, _unique_id: str) -> None:
        return None

    def _abort_if_unique_id_configured(self) -> None:
        return None

    def async_create_entry(self, **kwargs: Any) -> dict[str, Any]:
        return {"type": "create_entry", **kwargs}

    def async_show_form(self, **kwargs: Any) -> dict[str, Any]:
        return {"type": "form", **kwargs}


class OptionsFlow:
    """Minimal stand-in that mirrors HA-owned config_entry access."""

    def async_create_entry(self, **kwargs: Any) -> dict[str, Any]:
        return {"type": "create_entry", **kwargs}

    def async_show_form(self, **kwargs: Any) -> dict[str, Any]:
        return {"type": "form", **kwargs}


class ConfigEntry:
    """Minimal config entry carrying options for the options flow."""

    def __init__(self, options: dict[str, Any] | None = None) -> None:
        self.options = options or {}


class TextSelector:
    """Minimal text selector."""

    def __init__(self, _config: Any) -> None:
        return None


class TimeSelector:
    """Minimal time selector."""


config_entries.ConfigEntry = ConfigEntry
config_entries.ConfigFlow = ConfigFlow
config_entries.OptionsFlow = OptionsFlow
data_entry_flow.FlowResult = dict[str, Any]
voluptuous.Required = Required
voluptuous.Schema = Schema
selector.TextSelector = TextSelector
selector.TextSelectorConfig = lambda **kwargs: kwargs
selector.TextSelectorType = types.SimpleNamespace(PASSWORD="password")
selector.TimeSelector = TimeSelector
helpers.selector = selector
util_logging.log_exception = lambda *_args, **_kwargs: None
util.logging = util_logging
homeassistant.config_entries = config_entries
homeassistant.data_entry_flow = data_entry_flow
homeassistant.helpers = helpers
homeassistant.util = util

sys.modules["homeassistant"] = homeassistant
sys.modules["voluptuous"] = voluptuous
sys.modules["homeassistant.config_entries"] = config_entries
sys.modules["homeassistant.data_entry_flow"] = data_entry_flow
sys.modules["homeassistant.helpers"] = helpers
sys.modules["homeassistant.helpers.selector"] = selector
sys.modules["homeassistant.util"] = util
sys.modules["homeassistant.util.logging"] = util_logging

config_flow = importlib.import_module("custom_components.globird.config_flow")


def test_options_flow_is_created_without_manual_config_entry_assignment() -> None:
    """Home Assistant owns config_entry on options flows in current core."""
    flow = config_flow.GloBirdConfigFlow.async_get_options_flow(ConfigEntry())

    assert isinstance(flow, config_flow.GloBirdOptionsFlow)
    assert not hasattr(flow, "config_entry")


def test_options_flow_uses_ha_attached_config_entry_for_current_value() -> None:
    """Opening options should render the daily polling start time field."""
    flow = config_flow.GloBirdOptionsFlow()
    flow.config_entry = ConfigEntry({"daily_poll_start_time": "03:00"})

    result = asyncio.run(flow.async_step_init())

    assert result["type"] == "form"
    assert result["step_id"] == "init"
    assert "daily_poll_start_time" in str(result["data_schema"])


def test_options_flow_saves_daily_poll_start_time() -> None:
    """Submitting options should store the selected daily polling start time."""
    flow = config_flow.GloBirdOptionsFlow()

    result = asyncio.run(flow.async_step_init({"daily_poll_start_time": "03:00"}))

    assert result == {
        "type": "create_entry",
        "title": "",
        "data": {"daily_poll_start_time": "03:00"},
    }


def test_user_step_creates_entry_on_valid_auth(monkeypatch: Any) -> None:
    """Valid credentials should create a config entry."""

    class FakeClient:
        async def authenticate(self, _email: str, _password: str) -> dict[str, Any]:
            return {"success": True}

        async def close(self) -> None:
            return None

    monkeypatch.setattr(config_flow, "GloBirdClient", lambda: FakeClient())

    flow = config_flow.GloBirdConfigFlow()
    result = asyncio.run(
        flow.async_step_user(
            {
                "email": "user@example.test",
                "password": "secret",
            }
        )
    )

    assert result["type"] == "create_entry"
    assert result["title"] == "user@example.test"
    assert result["data"]["email"] == "user@example.test"


def test_user_step_maps_captcha_error(monkeypatch: Any) -> None:
    """Captcha-required auth failures should map to the expected flow error."""

    class FakeClient:
        async def authenticate(self, _email: str, _password: str) -> dict[str, Any]:
            raise config_flow.GloBirdCaptchaRequired()

        async def close(self) -> None:
            return None

    monkeypatch.setattr(config_flow, "GloBirdClient", lambda: FakeClient())

    flow = config_flow.GloBirdConfigFlow()
    result = asyncio.run(flow.async_step_user({"email": "a@b", "password": "x"}))

    assert result["type"] == "form"
    assert result["errors"]["base"] == "captcha_required"


def test_user_step_maps_invalid_auth_error(monkeypatch: Any) -> None:
    """Invalid credentials should map to invalid_auth."""

    class FakeClient:
        async def authenticate(self, _email: str, _password: str) -> dict[str, Any]:
            raise config_flow.GloBirdAuthError()

        async def close(self) -> None:
            return None

    monkeypatch.setattr(config_flow, "GloBirdClient", lambda: FakeClient())

    flow = config_flow.GloBirdConfigFlow()
    result = asyncio.run(flow.async_step_user({"email": "a@b", "password": "x"}))

    assert result["type"] == "form"
    assert result["errors"]["base"] == "invalid_auth"


def test_user_step_maps_unknown_error_to_cannot_connect(monkeypatch: Any) -> None:
    """Unexpected failures should map to cannot_connect."""

    class FakeClient:
        async def authenticate(self, _email: str, _password: str) -> dict[str, Any]:
            raise RuntimeError("boom")

        async def close(self) -> None:
            return None

    monkeypatch.setattr(config_flow, "GloBirdClient", lambda: FakeClient())

    flow = config_flow.GloBirdConfigFlow()
    result = asyncio.run(flow.async_step_user({"email": "a@b", "password": "x"}))

    assert result["type"] == "form"
    assert result["errors"]["base"] == "cannot_connect"
