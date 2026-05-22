"""FastAPI REST API for the Smart Energy Optimization Platform."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from database.db_manager import (
    create_reading,
    create_tables,
    delete_reading,
    fetch_energy_data,
    load_csv_to_database,
    update_reading,
)
from models.anomaly_detection import combined_anomaly_detection
from models.forecasting import combined_forecast
from models.optimization import generate_recommendations
from utils.config import DATA_PATH, DB_PATH
from utils.data_generator import generate_energy_dataset
from utils.data_processing import device_analytics


app = FastAPI(
    title="Smart Energy Optimization API",
    description="REST API for energy data, device analytics, forecasts, anomalies, and recommendations.",
    version="1.0.0",
)


class ReadingCreate(BaseModel):
    device_id: str
    timestamp: str
    power_consumption_kwh: float = Field(ge=0)
    voltage: float = Field(gt=0)
    current: float = Field(ge=0)
    temperature: float
    energy_cost: float = Field(ge=0)
    status: str = Field(pattern="^(ON|OFF)$")
    anomaly_flag: int = Field(default=0, ge=0, le=1)


class ReadingUpdate(BaseModel):
    power_consumption_kwh: float | None = Field(default=None, ge=0)
    voltage: float | None = Field(default=None, gt=0)
    current: float | None = Field(default=None, ge=0)
    temperature: float | None = None
    energy_cost: float | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, pattern="^(ON|OFF)$")
    anomaly_flag: int | None = Field(default=None, ge=0, le=1)


def ensure_api_data() -> None:
    csv_path = Path(DATA_PATH)
    db_path = Path(DB_PATH)
    if not csv_path.exists():
        generate_energy_dataset(csv_path, days=150)
    if not db_path.exists():
        create_tables(db_path)
        load_csv_to_database(csv_path, db_path, replace=True)


def records(df: pd.DataFrame) -> list[dict[str, Any]]:
    clean = df.copy()
    for column in clean.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns:
        clean[column] = clean[column].astype(str)
    return clean.replace({pd.NA: None}).to_dict(orient="records")


@app.on_event("startup")
def startup() -> None:
    ensure_api_data()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "smart-energy-api"}


@app.get("/energy")
def get_energy_data(
    limit: int = Query(500, ge=1, le=10000),
    device_id: str | None = None,
    category: str | None = None,
) -> dict[str, Any]:
    df = fetch_energy_data(DB_PATH, limit=None)
    if device_id:
        df = df[df["device_id"] == device_id]
    if category:
        df = df[df["device_category"] == category]
    return {"count": int(min(len(df), limit)), "data": records(df.head(limit))}


@app.get("/devices/analytics")
def get_device_analytics() -> dict[str, Any]:
    df = fetch_energy_data(DB_PATH)
    analytics = device_analytics(df)
    return {"count": len(analytics), "data": records(analytics)}


@app.get("/forecast")
def get_forecast() -> dict[str, Any]:
    df = fetch_energy_data(DB_PATH)
    forecast = combined_forecast(df)
    return {name: records(result) for name, result in forecast.items()}


@app.get("/anomalies")
def get_anomalies(limit: int = Query(100, ge=1, le=5000)) -> dict[str, Any]:
    df = fetch_energy_data(DB_PATH)
    anomalies = combined_anomaly_detection(df)
    detected = anomalies[anomalies["detected_anomaly"]].sort_values("timestamp", ascending=False).head(limit)
    return {"count": len(detected), "data": records(detected)}


@app.get("/recommendations")
def get_recommendations() -> dict[str, Any]:
    df = fetch_energy_data(DB_PATH)
    recommendations = generate_recommendations(df)
    return {"count": len(recommendations), "data": records(recommendations)}


@app.post("/readings", status_code=201)
def post_reading(reading: ReadingCreate) -> dict[str, int]:
    try:
        reading_id = create_reading(reading.model_dump(), DB_PATH)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"reading_id": reading_id}


@app.patch("/readings/{reading_id}")
def patch_reading(reading_id: int, updates: ReadingUpdate) -> dict[str, str]:
    update_data = updates.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No update fields provided")
    update_reading(reading_id, update_data, DB_PATH)
    return {"status": "updated"}


@app.delete("/readings/{reading_id}")
def remove_reading(reading_id: int) -> dict[str, str]:
    delete_reading(reading_id, DB_PATH)
    return {"status": "deleted"}
