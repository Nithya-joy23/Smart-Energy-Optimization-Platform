"""Energy optimization recommendation engine."""

from __future__ import annotations

import pandas as pd

from utils.data_processing import device_analytics, engineer_features, peak_usage_by_hour


def generate_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    """Generate device-specific energy optimization recommendations."""
    data = engineer_features(df)
    devices = device_analytics(data)
    recommendations: list[dict[str, object]] = []

    peak = data[data["is_peak_hour"]]
    peak_by_device = (
        peak.groupby("device_id", as_index=False)
        .agg(peak_kwh=("power_consumption_kwh", "sum"), peak_cost=("energy_cost", "sum"))
    )
    devices = devices.merge(peak_by_device, on="device_id", how="left").fillna({"peak_kwh": 0, "peak_cost": 0})

    for _, row in devices.iterrows():
        recs: list[str] = []
        savings = 0.0
        if row["peak_kwh"] / max(row["total_kwh"], 1) > 0.34:
            recs.append("Shift high-load usage from 6 PM-10 PM to off-peak hours.")
            savings += 8.0
        if row["efficiency_score"] < 45:
            recs.append("Inspect maintenance, calibration, or replacement options for this inefficient device.")
            savings += 10.0
        if row["anomaly_count"] > 8:
            recs.append("Investigate repeated consumption spikes and configure automated alerts.")
            savings += 6.0
        if row["device_category"] == "HVAC":
            recs.append("Raise cooling setpoint by 1-2 degrees during peak windows.")
            savings += 7.0
        if row["device_category"] in {"Kitchen", "Industrial", "Charging", "Appliances"}:
            recs.append("Schedule batch operation during lower-tariff periods.")
            savings += 5.0

        if not recs:
            recs.append("Usage pattern is stable. Continue monitoring for drift.")
            savings += 2.0

        recommendations.append(
            {
                "device_id": row["device_id"],
                "device_name": row["device_name"],
                "device_category": row["device_category"],
                "room_location": row["room_location"],
                "recommendation": " ".join(recs),
                "estimated_savings_percent": round(min(savings, 28.0), 1),
                "estimated_monthly_savings": round((row["total_cost"] / 5) * min(savings, 28.0) / 100, 2),
                "priority": "High" if savings >= 18 else "Medium" if savings >= 10 else "Low",
            }
        )

    result = pd.DataFrame(recommendations)
    priority_rank = {"High": 0, "Medium": 1, "Low": 2}
    result["_priority_rank"] = result["priority"].map(priority_rank)
    return (
        result.sort_values(["_priority_rank", "estimated_monthly_savings"], ascending=[True, False])
        .drop(columns="_priority_rank")
        .reset_index(drop=True)
    )


def savings_summary(df: pd.DataFrame) -> dict[str, float]:
    """Summarize optimization potential."""
    recommendations = generate_recommendations(df)
    hourly = peak_usage_by_hour(df)
    peak_hour = int(hourly.sort_values("power_consumption_kwh", ascending=False).iloc[0]["hour"])
    return {
        "total_estimated_monthly_savings": round(float(recommendations["estimated_monthly_savings"].sum()), 2),
        "average_savings_percent": round(float(recommendations["estimated_savings_percent"].mean()), 2),
        "high_priority_actions": int((recommendations["priority"] == "High").sum()),
        "highest_usage_hour": peak_hour,
    }
