-- Smart Energy Optimization Platform schema.

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

CREATE INDEX IF NOT EXISTS idx_energy_timestamp
ON energy_readings(timestamp);

CREATE INDEX IF NOT EXISTS idx_energy_device_timestamp
ON energy_readings(device_id, timestamp);
