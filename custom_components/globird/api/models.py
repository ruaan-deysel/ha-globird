"""Pydantic v2 models for validated GloBird API summaries."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

type UsageDirection = Literal["import", "export"]
type DataReadinessStatus = Literal[
    "ready",
    "waiting_for_cost",
    "waiting_for_usage",
    "no_data",
]
type RefreshStatus = Literal["ok", "error"]


def _coerce_optional_float(value: object) -> float | None:
    """Coerce numeric values to float or return None."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return float(stripped)
        except ValueError:
            return None
    return None


class ApiModel(BaseModel):
    """Base model following Pydantic v2 best practices for integration payloads."""

    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
        populate_by_name=True,
        validate_default=True,
    )


class UsageDailyRow(ApiModel):
    """Single daily usage summary row."""

    readDate: str | None = None
    usage: float | None = None
    meterStatus: str | None = None
    minQualityMethod: str | None = None

    @field_validator("usage", mode="before")
    @classmethod
    def _validate_usage(cls, value: object) -> float | None:
        return _coerce_optional_float(value)


class UsageRegisterSummary(ApiModel):
    """Per-register (e.g. E1 import or B1 solar export) usage summary."""

    key: str = "unknown"
    suffix: str | None = None
    chargeType: str | None = None
    chargeCategoryCode: str | None = None
    direction: UsageDirection = "import"
    days: int = Field(default=0, ge=0)
    total: float | None = None
    latest_day: str | None = None
    latest_day_usage: float | None = None

    @field_validator("total", "latest_day_usage", mode="before")
    @classmethod
    def _validate_floats(cls, value: object) -> float | None:
        return _coerce_optional_float(value)


class UsageSummary(ApiModel):
    """Validated electricity usage summary across import and export registers."""

    days: int = Field(default=0, ge=0)
    total_usage: float | None = None
    latest_day: str | None = None
    latest_day_usage: float | None = None
    daily: list[UsageDailyRow] = Field(default_factory=list)
    latest_intervals: list[float | int | None] = Field(default_factory=list)
    total_export: float | None = None
    latest_day_export: float | None = None
    export_daily: list[UsageDailyRow] = Field(default_factory=list)
    registers: list[UsageRegisterSummary] = Field(default_factory=list)

    @field_validator(
        "total_usage",
        "latest_day_usage",
        "total_export",
        "latest_day_export",
        mode="before",
    )
    @classmethod
    def _validate_floats(cls, value: object) -> float | None:
        return _coerce_optional_float(value)


class GasReadingHistoryRow(ApiModel):
    """Single historical gas meter index reading."""

    date: str
    read_index: float
    source: str | None = None
    serial: str | None = None
    quality_method: str | None = None


class GasReadingSummary(ApiModel):
    """Validated gas basic meter index reading summary."""

    latest_reading: float | None = None
    latest_reading_date: str | None = None
    latest_reading_source: str | None = None
    latest_reading_serial: str | None = None
    latest_reading_quality_method: str | None = None
    history: list[GasReadingHistoryRow] = Field(default_factory=list)
    history_recent: list[GasReadingHistoryRow] = Field(default_factory=list)
    history_count: int = Field(default=0, ge=0)
    history_truncated: bool = False

    @field_validator("latest_reading", mode="before")
    @classmethod
    def _validate_latest_reading(cls, value: object) -> float | None:
        return _coerce_optional_float(value)


class CostDailyRow(ApiModel):
    """Single daily cost line item."""

    date: str | None = None
    amount: float | None = None
    quantity: float | None = None
    chargeCategory: str | None = None
    chargeType: str | None = None
    complete: bool | None = None

    @field_validator("amount", "quantity", mode="before")
    @classmethod
    def _validate_floats(cls, value: object) -> float | None:
        return _coerce_optional_float(value)


class CostDailyTotalRow(ApiModel):
    """Aggregated daily cost total for a specific date."""

    date: str
    amount: float


class CostCategorySummary(ApiModel):
    """Aggregated cost and quantity for a charge category."""

    chargeCategory: str | None = None
    amount: float | None = None
    quantity: float | None = None

    @field_validator("amount", "quantity", mode="before")
    @classmethod
    def _validate_floats(cls, value: object) -> float | None:
        return _coerce_optional_float(value)


class CostProjectionSummary(ApiModel):
    """Calendar-month cost projection summary."""

    month: str | None = None
    cost_to_date: float | None = None
    projected_cost: float | None = None
    completed_days: int = Field(default=0, ge=0)
    days_in_month: int = Field(default=0, ge=0)
    latest_day: str | None = None

    @field_validator("cost_to_date", "projected_cost", mode="before")
    @classmethod
    def _validate_floats(cls, value: object) -> float | None:
        return _coerce_optional_float(value)


class BillingPeriodProjection(ApiModel):
    """Billing-period cost projection summary."""

    billing_period_start: str | None = None
    cost_to_date: float | None = None
    projected_cost: float | None = None
    completed_days: int = Field(default=0, ge=0)
    period_days: int = Field(default=30, ge=0)
    latest_day: str | None = None

    @field_validator("cost_to_date", "projected_cost", mode="before")
    @classmethod
    def _validate_floats(cls, value: object) -> float | None:
        return _coerce_optional_float(value)


class CostSummary(ApiModel):
    """Validated service cost summary including grid import and solar export splits."""

    days: int = Field(default=0, ge=0)
    total_amount: float | None = None
    total_quantity: float | None = None
    total_import_cost: float | None = None
    total_export_credit: float | None = None
    latest_day: str | None = None
    latest_day_amount: float | None = None
    latest_day_import_cost: float | None = None
    latest_day_export_credit: float | None = None
    latest_available_day: str | None = None
    latest_available_day_complete: bool | None = None
    latest_day_zerohero_credit: float | None = None
    latest_day_zerohero_achieved: bool = False
    daily: list[CostDailyRow] = Field(default_factory=list)
    daily_totals: list[CostDailyTotalRow] = Field(default_factory=list)
    daily_import_totals: list[CostDailyTotalRow] = Field(default_factory=list)
    daily_export_credit_totals: list[CostDailyTotalRow] = Field(default_factory=list)
    available_daily: list[CostDailyRow] = Field(default_factory=list)
    incomplete_days: list[str] = Field(default_factory=list)
    projected_month: CostProjectionSummary = Field(
        default_factory=CostProjectionSummary
    )
    categories: list[CostCategorySummary] = Field(default_factory=list)

    @field_validator(
        "total_amount",
        "total_quantity",
        "total_import_cost",
        "total_export_credit",
        "latest_day_amount",
        "latest_day_import_cost",
        "latest_day_export_credit",
        "latest_day_zerohero_credit",
        mode="before",
    )
    @classmethod
    def _validate_floats(cls, value: object) -> float | None:
        return _coerce_optional_float(value)


class LatestDataStatus(ApiModel):
    """Readiness status for a service's daily usage and cost data."""

    status: DataReadinessStatus = "no_data"
    latest_ready_day: str | None = None
    latest_usage_day: str | None = None
    latest_cost_day: str | None = None
    latest_available_cost_day: str | None = None
    latest_available_cost_day_complete: bool | None = None
    incomplete_cost_days: list[str] = Field(default_factory=list)


class WeatherDailyRow(ApiModel):
    """Single daily weather observation row."""

    dateAsDate: str | None = None
    obMinTemp: float | int | None = None
    obMaxTemp: float | int | None = None
    distanceMeters: float | int | None = None


class WeatherSummary(ApiModel):
    """Validated service weather summary."""

    days: int = Field(default=0, ge=0)
    latest_date: str | None = None
    latest_min_temp: float | int | None = None
    latest_max_temp: float | int | None = None
    daily: list[WeatherDailyRow] = Field(default_factory=list)
