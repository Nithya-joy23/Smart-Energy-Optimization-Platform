"""Lightweight forecasting models for energy usage."""

from __future__ import annotations

import numpy as np
import pandas as pd

from utils.data_processing import daily_aggregation, engineer_features


def moving_average_forecast(df: pd.DataFrame, periods: int = 7, window: int = 7) -> pd.DataFrame:
    """Forecast daily energy with a rolling moving average."""
    daily = daily_aggregation(df)
    daily["timestamp"] = pd.to_datetime(daily["timestamp"])
    average = daily["power_consumption_kwh"].rolling(window=window, min_periods=1).mean().iloc[-1]
    last_date = daily["timestamp"].max()
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=periods, freq="D")
    return pd.DataFrame(
        {
            "timestamp": future_dates,
            "forecast_kwh": np.repeat(round(float(average), 2), periods),
            "model": f"{window}-day moving average",
        }
    )


def linear_regression_forecast(df: pd.DataFrame, periods: int = 30) -> pd.DataFrame:
    """Forecast daily energy with a simple NumPy linear regression trend."""
    daily = daily_aggregation(df)
    daily["timestamp"] = pd.to_datetime(daily["timestamp"])
    y = daily["power_consumption_kwh"].to_numpy()
    x = np.arange(len(y))
    slope, intercept = np.polyfit(x, y, 1)
    future_x = np.arange(len(y), len(y) + periods)
    predictions = np.maximum(slope * future_x + intercept, 0)
    future_dates = pd.date_range(daily["timestamp"].max() + pd.Timedelta(days=1), periods=periods, freq="D")
    return pd.DataFrame(
        {
            "timestamp": future_dates,
            "forecast_kwh": predictions.round(2),
            "model": "linear regression trend",
        }
    )


def hourly_profile_forecast(df: pd.DataFrame, days: int = 1) -> pd.DataFrame:
    """Forecast hourly demand using recent same-hour averages."""
    data = engineer_features(df)
    profile = data.groupby("hour")["power_consumption_kwh"].mean()
    last_timestamp = data["timestamp"].max().floor("h")
    future = pd.date_range(last_timestamp + pd.Timedelta(hours=1), periods=days * 24, freq="h")
    forecast = [profile.loc[hour] for hour in future.hour]
    return pd.DataFrame(
        {
            "timestamp": future,
            "forecast_kwh": np.round(forecast, 2),
            "model": "hourly profile",
        }
    )


def combined_forecast(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Return next-day, weekly, and monthly forecasts."""
    return {
        "next_day": hourly_profile_forecast(df, days=1),
        "weekly": moving_average_forecast(df, periods=7, window=7),
        "monthly": linear_regression_forecast(df, periods=30),
    }
