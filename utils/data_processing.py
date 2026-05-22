"""Data cleaning, aggregation, and analytics utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd


def clean_energy_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw energy data and normalize expected types."""
    cleaned = df.copy()
    cleaned["timestamp"] = pd.to_datetime(cleaned["timestamp"], errors="coerce")
    cleaned = cleaned.dropna(subset=["device_id", "timestamp"])
    numeric_columns = ["power_consumption_kwh", "voltage", "current", "temperature", "energy_cost"]
    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
        cleaned[column] = cleaned[column].fillna(cleaned[column].median())
    cleaned["status"] = cleaned["status"].fillna("OFF").str.upper()
    cleaned["anomaly_flag"] = cleaned["anomaly_flag"].fillna(0).astype(int)
    cleaned = cleaned.sort_values("timestamp").reset_index(drop=True)
    return cleaned


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add time, cost, and behavioral features."""
    featured = clean_energy_data(df)
    featured["hour"] = featured["timestamp"].dt.hour
    featured["date"] = featured["timestamp"].dt.date
    featured["day_name"] = featured["timestamp"].dt.day_name()
    featured["month"] = featured["timestamp"].dt.to_period("M").astype(str)
    featured["is_weekend"] = featured["timestamp"].dt.weekday >= 5
    featured["is_peak_hour"] = featured["hour"].between(18, 22)
    featured["cost_per_kwh"] = np.where(
        featured["power_consumption_kwh"] > 0,
        featured["energy_cost"] / featured["power_consumption_kwh"],
        0,
    )
    return featured


def calculate_kpis(df: pd.DataFrame) -> dict[str, float | int]:
    """Calculate high-level dashboard metrics."""
    data = engineer_features(df)
    latest_month = data["month"].max()
    monthly = data[data["month"] == latest_month]
    return {
        "total_energy_kwh": round(float(data["power_consumption_kwh"].sum()), 2),
        "monthly_cost": round(float(monthly["energy_cost"].sum()), 2),
        "active_devices": int(data.loc[data["status"] == "ON", "device_id"].nunique()),
        "peak_alerts": int(data.loc[(data["is_peak_hour"]) & (data["anomaly_flag"] == 1)].shape[0]),
    }


def daily_aggregation(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate readings by day."""
    data = engineer_features(df)
    return (
        data.groupby("date", as_index=False)
        .agg(
            power_consumption_kwh=("power_consumption_kwh", "sum"),
            energy_cost=("energy_cost", "sum"),
            anomaly_count=("anomaly_flag", "sum"),
            avg_temperature=("temperature", "mean"),
        )
        .rename(columns={"date": "timestamp"})
    )


def monthly_aggregation(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate readings by month."""
    data = engineer_features(df)
    return (
        data.groupby("month", as_index=False)
        .agg(
            power_consumption_kwh=("power_consumption_kwh", "sum"),
            energy_cost=("energy_cost", "sum"),
            anomaly_count=("anomaly_flag", "sum"),
            avg_temperature=("temperature", "mean"),
        )
        .sort_values("month")
    )


def device_analytics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate device-level energy and cost analytics."""
    data = engineer_features(df)
    analytics = (
        data.groupby(["device_id", "device_name", "device_category", "room_location"], as_index=False)
        .agg(
            total_kwh=("power_consumption_kwh", "sum"),
            avg_kwh=("power_consumption_kwh", "mean"),
            max_kwh=("power_consumption_kwh", "max"),
            total_cost=("energy_cost", "sum"),
            anomaly_count=("anomaly_flag", "sum"),
            on_hours=("status", lambda values: int((values == "ON").sum())),
        )
        .sort_values("total_kwh", ascending=False)
    )
    analytics["efficiency_score"] = calculate_efficiency_scores(analytics)
    return analytics


def calculate_efficiency_scores(device_df: pd.DataFrame) -> pd.Series:
    """Score each device from 0 to 100 using energy, anomalies, and cost."""
    total_norm = device_df["total_kwh"] / max(device_df["total_kwh"].max(), 1)
    anomaly_norm = device_df["anomaly_count"] / max(device_df["anomaly_count"].max(), 1)
    cost_norm = device_df["total_cost"] / max(device_df["total_cost"].max(), 1)
    score = 100 - (55 * total_norm + 25 * anomaly_norm + 20 * cost_norm)
    return score.clip(0, 100).round(1)


def peak_usage_by_hour(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate energy by hour of day."""
    data = engineer_features(df)
    return (
        data.groupby("hour", as_index=False)
        .agg(power_consumption_kwh=("power_consumption_kwh", "sum"), energy_cost=("energy_cost", "sum"))
        .sort_values("hour")
    )


def category_cost_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate cost by device category."""
    data = engineer_features(df)
    return (
        data.groupby("device_category", as_index=False)
        .agg(power_consumption_kwh=("power_consumption_kwh", "sum"), energy_cost=("energy_cost", "sum"))
        .sort_values("energy_cost", ascending=False)
    )
