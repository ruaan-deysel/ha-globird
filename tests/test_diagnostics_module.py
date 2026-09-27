"""Tests for diagnostics payload redaction."""

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
sys.modules.setdefault("custom_components", custom_components)
sys.modules.setdefault("custom_components.globird", globird_package)

homeassistant = types.ModuleType("homeassistant")
config_entries = types.ModuleType("homeassistant.config_entries")
core = types.ModuleType("homeassistant.core")
util = types.ModuleType("homeassistant.util")
util_logging = types.ModuleType("homeassistant.util.logging")
config_entries.ConfigEntry = object
core.HomeAssistant = object
util_logging.log_exception = lambda *_args, **_kwargs: None
util.logging = util_logging
homeassistant.config_entries = config_entries
homeassistant.core = core
homeassistant.util = util
sys.modules.setdefault("homeassistant", homeassistant)
sys.modules.setdefault("homeassistant.config_entries", config_entries)
sys.modules.setdefault("homeassistant.core", core)
sys.modules.setdefault("homeassistant.util", util)
sys.modules.setdefault("homeassistant.util.logging", util_logging)

diagnostics = importlib.import_module("custom_components.globird.diagnostics")


class FakeCoordinator:
    def __init__(self) -> None:
        self.data = {
            "accounts": [{"accountNumber": "123"}],
            "password": "hidden",
        }


class FakeHass:
    def __init__(self) -> None:
        self.data = {
            diagnostics.DOMAIN: {
                "entry-1": FakeCoordinator(),
            }
        }


class FakeEntry:
    def __init__(self, data: dict[str, Any] | None = None) -> None:
        self.entry_id = "entry-1"
        self.data = (
            data
            if data is not None
            else {
                "email": "user@example.test",
                "password": "secret",
            }
        )


def test_async_get_config_entry_diagnostics_redacts_sensitive_values() -> None:
    """Diagnostics should redact credentials and sensitive payload keys."""
    payload = asyncio.run(
        diagnostics.async_get_config_entry_diagnostics(FakeHass(), FakeEntry())
    )

    assert payload["entry"]["password"] == "**REDACTED**"
    assert payload["data"]["accounts"][0]["accountNumber"] == "**REDACTED**"


def test_async_get_config_entry_diagnostics_without_password_key() -> None:
    """Diagnostics should succeed when password key is absent from entry data."""
    payload = asyncio.run(
        diagnostics.async_get_config_entry_diagnostics(
            FakeHass(), FakeEntry(data={"email": "user@example.test"})
        )
    )
    assert payload["entry"]["email"] == "**REDACTED**"
