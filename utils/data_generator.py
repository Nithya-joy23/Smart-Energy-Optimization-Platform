"""Synthetic energy dataset generator."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from utils.config import DEFAULT_ENERGY_RATE


@dataclass(frozen=True)
class DeviceProfile:
    device_id: str
    device_name: str
    device_category: str
    room_location: str
    base_kwh: float
    peak_multiplier: float
    weather_sensitivity: float


DEVICE_PROFILES = [
    DeviceProfile("DEV001", "Central AC", "HVAC", "Building A - Floor 1", 2.8, 1.8, 0.075),
    DeviceProfile("DEV002", "Conference AC", "HVAC", "Building A - Floor 2", 2.1, 1.7, 0.068),
    DeviceProfile("DEV003", "Lobby Lighting", "Lighting", "Building A - Lobby", 0.45, 1.5, 0.005),
    DeviceProfile("DEV004", "Office Lighting", "Lighting", "Building A - Floor 1", 0.75, 1.4, 0.004),
    DeviceProfile("DEV005", "Server Rack", "IT Equipment", "Building A - Server Room", 3.2, 1.1, 0.018),
    DeviceProfile("DEV006", "Desktop Cluster", "IT Equipment", "Building A - Floor 2", 1.6, 1.45, 0.01),
    DeviceProfile("DEV007", "Elevator Motor", "Motors", "Building A - Core", 1.2, 1.9, 0.002),
    DeviceProfile("DEV008", "Water Pump", "Pumps", "Building B - Utility", 1.85, 1.5, 0.006),
    DeviceProfile("DEV009", "Refrigerator", "Kitchen", "Building A - Cafeteria", 0.62, 1.2, 0.025),
    DeviceProfile("DEV010", "Coffee Machine", "Kitchen", "Building A - Pantry", 0.38, 2.2, 0.0),
    DeviceProfile("DEV011", "Microwave", "Kitchen", "Building A - Cafeteria", 0.55, 2.6, 0.0),
    DeviceProfile("DEV012", "EV Charger", "Charging", "Building B - Parking", 4.2, 1.9, 0.0),
    DeviceProfile("DEV013", "Solar Inverter Load", "Renewables", "Building B - Roof", 0.35, 0.8, -0.015),
    DeviceProfile("DEV014", "Security Cameras", "Security", "Building A - Exterior", 0.28, 1.05, 0.002),
    DeviceProfile("DEV015", "Access Control", "Security", "Building A - Lobby", 0.18, 1.05, 0.001),
    DeviceProfile("DEV016", "Air Compressor", "Industrial", "Building B - Workshop", 2.4, 1.7, 0.005),
    DeviceProfile("DEV017", "CNC Machine", "Industrial", "Building B - Workshop", 3.8, 1.65, 0.004),
    DeviceProfile("DEV018", "Projector", "AV Equipment", "Building A - Conference Room", 0.42, 1.8, 0.0),
    DeviceProfile("DEV019", "Smart Plugs", "Plug Load", "Building A - Floor 1", 0.35, 1.4, 0.002),
    DeviceProfile("DEV020", "Washing Machine", "Appliances", "Building B - Maintenance", 0.95, 1.8, 0.0),
    DeviceProfile("DEV021", "Ventilation Fan", "Ventilation", "Building A - Basement", 0.82, 1.35, 0.025),
    DeviceProfile("DEV022", "Battery Storage", "Storage", "Building B - Energy Room", 0.7, 1.15, -0.004),
    DeviceProfile("DEV023", "Printers", "Office Equipment", "Building A - Floor 2", 0.32, 1.7, 0.0),
    DeviceProfile("DEV024", "Lab Instruments", "Lab Equipment", "Building B - Lab", 1.35, 1.55, 0.006),
]


def _temperature_for_timestamp(timestamp: pd.Timestamp, rng: np.random.Generator) -> float:
    seasonal = 7 * np.sin(2 * np.pi * timestamp.dayofyear / 365)
    daily = 5 * np.sin(2 * np.pi * (timestamp.hour - 8) / 24)
    noise = rng.normal(0, 1.8)
    return round(24 + seasonal + daily + noise, 2)


def _status_probability(timestamp: pd.Timestamp, profile: DeviceProfile) -> float:
    hour = timestamp.hour
    weekday = timestamp.weekday() < 5
    always_on = {"Server Rack", "Security Cameras", "Access Control", "Refrigerator", "Battery Storage"}
    if profile.device_name in always_on:
        return 0.98
    if profile.device_category in {"Industrial", "Lab Equipment"}:
        return 0.86 if weekday and 8 <= hour <= 19 else 0.18
    if profile.device_category in {"Lighting", "IT Equipment", "Office Equipment", "AV Equipment", "Plug Load"}:
        return 0.9 if weekday and 7 <= hour <= 20 else 0.25
    if profile.device_category == "Charging":
        return 0.65 if hour in list(range(18, 24)) + list(range(0, 6)) else 0.2
    if profile.device_category == "Kitchen":
        return 0.8 if hour in [7, 8, 9, 12, 13, 17, 18] else 0.25
    return 0.72 if 7 <= hour <= 22 else 0.32


def _peak_factor(timestamp: pd.Timestamp, profile: DeviceProfile) -> float:
    hour = timestamp.hour
    business_peak = 9 <= hour <= 18 and timestamp.weekday() < 5
    evening_peak = 18 <= hour <= 22
    night_charging = profile.device_category == "Charging" and (hour >= 20 or hour <= 5)
    if business_peak or evening_peak or night_charging:
        return profile.peak_multiplier
    if 0 <= hour <= 5:
        return 0.58
    return 1.0


def generate_energy_dataset(
    output_path: str | Path,
    days: int = 150,
    seed: int = 42,
    start_date: str = "2025-10-01",
    energy_rate: float = DEFAULT_ENERGY_RATE,
) -> pd.DataFrame:
    """Generate hourly energy readings and save them to CSV."""
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range(start=start_date, periods=days * 24, freq="h")
    rows: list[dict[str, object]] = []

    for timestamp in timestamps:
        temperature = _temperature_for_timestamp(timestamp, rng)
        for profile in DEVICE_PROFILES:
            status = "ON" if rng.random() < _status_probability(timestamp, profile) else "OFF"
            anomaly = rng.random() < 0.012
            base = profile.base_kwh if status == "ON" else profile.base_kwh * rng.uniform(0.01, 0.07)
            weather_adjustment = max(0.4, 1 + (temperature - 24) * profile.weather_sensitivity)
            consumption = base * _peak_factor(timestamp, profile) * weather_adjustment
            consumption *= rng.normal(1.0, 0.08)

            if anomaly:
                consumption *= rng.uniform(2.4, 5.5)

            consumption = max(consumption, 0.01)
            voltage = rng.normal(230, 4.5)
            current = (consumption * 1000) / voltage
            cost_multiplier = 1.35 if 18 <= timestamp.hour <= 22 else 1.0
            energy_cost = consumption * energy_rate * cost_multiplier

            rows.append(
                {
                    "device_id": profile.device_id,
                    "device_name": profile.device_name,
                    "device_category": profile.device_category,
                    "room_location": profile.room_location,
                    "timestamp": timestamp,
                    "power_consumption_kwh": round(float(consumption), 4),
                    "voltage": round(float(voltage), 2),
                    "current": round(float(current), 3),
                    "temperature": temperature,
                    "energy_cost": round(float(energy_cost), 4),
                    "status": status,
                    "anomaly_flag": int(anomaly),
                }
            )

    df = pd.DataFrame(rows)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df
