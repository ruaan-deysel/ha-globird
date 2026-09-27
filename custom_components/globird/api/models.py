"""Pydantic models for validated API summaries."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    """Base model with strict-enough defaults for integration payloads."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


class UsageDailyRow(ApiModel):
    readDate: str | None = None
    usage: float | None = None
    meterStatus: str | None = None
    minQualityMethod: str | None = None


class UsageRegisterSummary(ApiModel):
    key: str = "unknown"
    suffix: str | None = None
    chargeType: str | None = None
    chargeCategoryCode: str | None = None
    direction: str = "import"
    days: int = 0
    total: float | None = None
    latest_day: str | None = None
    latest_day_usage: float | None = None


class UsageSummary(ApiModel):
    days: int = 0
    total_usage: float | None = None
    latest_day: str | None = None
    latest_day_usage: float | None = None
    daily: list[UsageDailyRow] = Field(default_factory=list)
    latest_intervals: list[float | int | None] = Field(default_factory=list)
    total_export: float | None = None
    latest_day_export: float | None = None
    export_daily: list[UsageDailyRow] = Field(default_factory=list)
    registers: list[UsageRegisterSummary] = Field(default_factory=list)


class GasReadingHistoryRow(ApiModel):
    date: str
    read_index: float
    source: str | None = None
    serial: str | None = None
    quality_method: str | None = None


class GasReadingSummary(ApiModel):
    latest_reading: float | None = None
    latest_reading_date: str | None = None
    latest_reading_source: str | None = None
    latest_reading_serial: str | None = None
    latest_reading_quality_method: str | None = None
    history: list[GasReadingHistoryRow] = Field(default_factory=list)
    history_recent: list[GasReadingHistoryRow] = Field(default_factory=list)
    history_count: int = 0
    history_truncated: bool = False


class CostDailyRow(ApiModel):
    date: str | None = None
    amount: float | None = None
    quantity: float | None = None
    chargeCategory: str | None = None
    chargeType: str | None = None
    complete: bool | None = None


class CostCategorySummary(ApiModel):
    chargeCategory: str | None = None
    amount: float | None = None
    quantity: float | None = None


class CostProjectionSummary(ApiModel):
    month: str | None = None
    cost_to_date: float | None = None
    projected_cost: float | None = None
    completed_days: int = 0
    days_in_month: int = 0
    latest_day: str | None = None


class CostSummary(ApiModel):
    days: int = 0
    total_amount: float | None = None
    total_quantity: float | None = None
    latest_day: str | None = None
    latest_day_amount: float | None = None
    latest_available_day: str | None = None
    latest_available_day_complete: bool | None = None
    latest_day_zerohero_credit: float | None = None
    latest_day_zerohero_achieved: bool = False
    daily: list[CostDailyRow] = Field(default_factory=list)
    daily_totals: list[dict[str, Any]] = Field(default_factory=list)
    available_daily: list[CostDailyRow] = Field(default_factory=list)
    incomplete_days: list[str] = Field(default_factory=list)
    projected_month: CostProjectionSummary = Field(
        default_factory=CostProjectionSummary
    )
    categories: list[CostCategorySummary] = Field(default_factory=list)


class LatestDataStatus(ApiModel):
    status: str = "no_data"
    latest_ready_day: str | None = None
    latest_usage_day: str | None = None
    latest_cost_day: str | None = None
    latest_available_cost_day: str | None = None
    latest_available_cost_day_complete: bool | None = None
    incomplete_cost_days: list[str] = Field(default_factory=list)


class WeatherDailyRow(ApiModel):
    dateAsDate: str | None = None
    obMinTemp: float | int | None = None
    obMaxTemp: float | int | None = None
    distanceMeters: float | int | None = None


class WeatherSummary(ApiModel):
    days: int = 0
    latest_date: str | None = None
    latest_min_temp: float | int | None = None
    latest_max_temp: float | int | None = None
    daily: list[WeatherDailyRow] = Field(default_factory=list)
