"""Statistical anomaly detection utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd

from utils.data_processing import engineer_features


def detect_zscore_anomalies(df: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
    """Detect anomalies per device using Z-score."""
    data = engineer_features(df)
    grouped = data.groupby("device_id")["power_consumption_kwh"]
    mean = grouped.transform("mean")
    std = grouped.transform("std").replace(0, np.nan)
    data["z_score"] = ((data["power_consumption_kwh"] - mean) / std).fillna(0)
    data["zscore_anomaly"] = data["z_score"].abs() > threshold
    return data


def detect_iqr_anomalies(df: pd.DataFrame, multiplier: float = 1.5) -> pd.DataFrame:
    """Detect anomalies per device using IQR fences."""
    data = engineer_features(df)
    q1 = data.groupby("device_id")["power_consumption_kwh"].transform(lambda values: values.quantile(0.25))
    q3 = data.groupby("device_id")["power_consumption_kwh"].transform(lambda values: values.quantile(0.75))
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    data["iqr_lower"] = lower
    data["iqr_upper"] = upper
    data["iqr_anomaly"] = (data["power_consumption_kwh"] < lower) | (data["power_consumption_kwh"] > upper)
    return data


def detect_threshold_anomalies(df: pd.DataFrame, percentile: float = 0.98) -> pd.DataFrame:
    """Detect high-consumption outliers above a device-specific percentile."""
    data = engineer_features(df)
    thresholds = data.groupby("device_id")["power_consumption_kwh"].transform(lambda values: values.quantile(percentile))
    data["threshold_kwh"] = thresholds
    data["threshold_anomaly"] = data["power_consumption_kwh"] > thresholds
    return data


def combined_anomaly_detection(df: pd.DataFrame) -> pd.DataFrame:
    """Combine generated flags with Z-score, IQR, and threshold rules."""
    z = detect_zscore_anomalies(df)
    iqr = detect_iqr_anomalies(z)
    threshold = detect_threshold_anomalies(iqr)
    threshold["detected_anomaly"] = (
        (threshold["anomaly_flag"] == 1)
        | threshold["zscore_anomaly"]
        | threshold["iqr_anomaly"]
        | threshold["threshold_anomaly"]
    )
    threshold["severity"] = np.select(
        [
            threshold["z_score"].abs() >= 4,
            threshold["z_score"].abs().between(3, 4, inclusive="left"),
            threshold["detected_anomaly"],
        ],
        ["High", "Medium", "Low"],
        default="Normal",
    )
    return threshold


def anomaly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize anomaly counts by device."""
    anomalies = combined_anomaly_detection(df)
    return (
        anomalies[anomalies["detected_anomaly"]]
        .groupby(["device_id", "device_name", "device_category"], as_index=False)
        .agg(
            anomaly_count=("detected_anomaly", "sum"),
            max_kwh=("power_consumption_kwh", "max"),
            avg_z_score=("z_score", "mean"),
            latest_anomaly=("timestamp", "max"),
        )
        .sort_values("anomaly_count", ascending=False)
    )
