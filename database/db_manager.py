"""SQLite database access and CRUD helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

from utils.config import DB_PATH
from utils.logger import get_logger

logger = get_logger(__name__)


def get_connection(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    """Create a SQLite connection with dictionary-like row access."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables(db_path: str | Path = DB_PATH) -> None:
    """Create database tables."""
    with get_connection(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS devices (
                device_id TEXT PRIMARY KEY,
                device_name TEXT NOT NULL,
                device_category TEXT NOT NULL,
                room_location TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS energy_readings (
                reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                power_consumption_kwh REAL NOT NULL,
                voltage REAL NOT NULL,
                current REAL NOT NULL,
                temperature REAL NOT NULL,
                energy_cost REAL NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('ON', 'OFF')),
                anomaly_flag INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(device_id) REFERENCES devices(device_id)
            );

            CREATE INDEX IF NOT EXISTS idx_energy_timestamp ON energy_readings(timestamp);
            CREATE INDEX IF NOT EXISTS idx_energy_device_timestamp ON energy_readings(device_id, timestamp);
            """
        )


def load_csv_to_database(csv_path: str | Path, db_path: str | Path = DB_PATH, replace: bool = False) -> None:
    """Load generated CSV data into normalized SQLite tables."""
    df = pd.read_csv(csv_path)
    required = {
        "device_id",
        "device_name",
        "device_category",
        "room_location",
        "timestamp",
        "power_consumption_kwh",
        "voltage",
        "current",
        "temperature",
        "energy_cost",
        "status",
        "anomaly_flag",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {sorted(missing)}")

    devices = df[["device_id", "device_name", "device_category", "room_location"]].drop_duplicates()
    readings = df[
        [
            "device_id",
            "timestamp",
            "power_consumption_kwh",
            "voltage",
            "current",
            "temperature",
            "energy_cost",
            "status",
            "anomaly_flag",
        ]
    ].copy()
    readings["timestamp"] = pd.to_datetime(readings["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")

    with get_connection(db_path) as conn:
        if replace:
            conn.execute("DELETE FROM energy_readings")
            conn.execute("DELETE FROM devices")
        devices.to_sql("devices", conn, if_exists="append", index=False)
        readings.to_sql("energy_readings", conn, if_exists="append", index=False)
    logger.info("Loaded %s readings into %s", len(readings), db_path)


def fetch_energy_data(db_path: str | Path = DB_PATH, limit: int | None = None) -> pd.DataFrame:
    """Return joined energy readings for analysis."""
    query = """
        SELECT
            r.reading_id,
            d.device_id,
            d.device_name,
            d.device_category,
            d.room_location,
            r.timestamp,
            r.power_consumption_kwh,
            r.voltage,
            r.current,
            r.temperature,
            r.energy_cost,
            r.status,
            r.anomaly_flag
        FROM energy_readings r
        JOIN devices d ON d.device_id = r.device_id
        ORDER BY r.timestamp
    """
    if limit:
        query += f" LIMIT {int(limit)}"
    with get_connection(db_path) as conn:
        return pd.read_sql_query(query, conn, parse_dates=["timestamp"])


def run_query(query: str, db_path: str | Path = DB_PATH) -> pd.DataFrame:
    """Execute a read-only SQL query and return a dataframe."""
    stripped = query.strip().lower()
    if not stripped.startswith("select") and not stripped.startswith("with"):
        raise ValueError("Only SELECT and WITH queries are allowed from the dashboard.")
    with get_connection(db_path) as conn:
        return pd.read_sql_query(query, conn)


def create_reading(reading: dict[str, Any], db_path: str | Path = DB_PATH) -> int:
    """Insert a single reading and return its generated id."""
    fields = [
        "device_id",
        "timestamp",
        "power_consumption_kwh",
        "voltage",
        "current",
        "temperature",
        "energy_cost",
        "status",
        "anomaly_flag",
    ]
    values = [reading[field] for field in fields]
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            f"INSERT INTO energy_readings ({', '.join(fields)}) VALUES ({', '.join(['?'] * len(fields))})",
            values,
        )
        return int(cursor.lastrowid)


def update_reading(reading_id: int, updates: dict[str, Any], db_path: str | Path = DB_PATH) -> None:
    """Update an energy reading."""
    allowed = {
        "power_consumption_kwh",
        "voltage",
        "current",
        "temperature",
        "energy_cost",
        "status",
        "anomaly_flag",
    }
    updates = {key: value for key, value in updates.items() if key in allowed}
    if not updates:
        return
    set_clause = ", ".join(f"{key} = ?" for key in updates)
    with get_connection(db_path) as conn:
        conn.execute(
            f"UPDATE energy_readings SET {set_clause} WHERE reading_id = ?",
            [*updates.values(), reading_id],
        )


def delete_reading(reading_id: int, db_path: str | Path = DB_PATH) -> None:
    """Delete an energy reading."""
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM energy_readings WHERE reading_id = ?", (reading_id,))
