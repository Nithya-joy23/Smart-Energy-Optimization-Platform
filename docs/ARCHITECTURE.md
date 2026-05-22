# Architecture

## Overview

The platform has five layers:

1. Data generation: creates realistic hourly device consumption data.
2. Storage: persists normalized device and reading tables in SQLite plus a CSV export.
3. Analytics modules: clean data, engineer features, aggregate trends, and score devices.
4. Intelligence modules: forecast usage, detect anomalies, and generate recommendations.
5. Interfaces: Streamlit dashboard, FastAPI REST API, SQL scripts, and Power BI integration.

## Data Flow

```text
Synthetic generator
    -> CSV export
    -> SQLite database
    -> Processing and model modules
    -> Streamlit dashboard / FastAPI API / Power BI
```

## Main Modules

- `utils/data_generator.py`: builds the synthetic dataset with devices, rooms, temperature, peak hours, costs, statuses, and anomalies.
- `database/db_manager.py`: creates schema, loads CSV data, provides CRUD helpers, and executes safe read-only SQL.
- `utils/data_processing.py`: cleans data and provides daily, monthly, device, cost, and peak-hour analytics.
- `models/forecasting.py`: implements moving average, linear regression trend, and hourly profile forecasts.
- `models/anomaly_detection.py`: implements Z-score, IQR, and percentile threshold anomaly detection.
- `models/optimization.py`: generates practical savings recommendations by device.
- `app.py`: Streamlit multi-page dashboard.
- `api/main.py`: FastAPI service with JSON endpoints.

## Database Design

`devices` stores stable device attributes. `energy_readings` stores hourly measurements and references `devices` through `device_id`.

This keeps repeated device metadata out of the readings table while still allowing fast joins for analytics.
