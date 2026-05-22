# API Documentation

Run the API:

```bash
uvicorn api.main:app --reload
```

Interactive documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

### GET `/health`

Returns service health.

### GET `/energy`

Query parameters:

- `limit`: maximum records, default `500`.
- `device_id`: optional device filter.
- `category`: optional device category filter.

Example:

```bash
curl "http://127.0.0.1:8000/energy?limit=10&category=HVAC"
```

### GET `/devices/analytics`

Returns device-level energy, cost, anomaly count, and efficiency scores.

### GET `/forecast`

Returns:

- `next_day`: hourly next-day forecast.
- `weekly`: seven-day moving average forecast.
- `monthly`: thirty-day linear trend forecast.

### GET `/anomalies`

Returns detected anomalies.

Example:

```bash
curl "http://127.0.0.1:8000/anomalies?limit=25"
```

### GET `/recommendations`

Returns optimization recommendations with estimated savings.

### POST `/readings`

Creates one energy reading.

```bash
curl -X POST "http://127.0.0.1:8000/readings" ^
  -H "Content-Type: application/json" ^
  -d "{\"device_id\":\"DEV001\",\"timestamp\":\"2026-01-02 10:00:00\",\"power_consumption_kwh\":3.5,\"voltage\":230,\"current\":15.2,\"temperature\":26,\"energy_cost\":0.63,\"status\":\"ON\",\"anomaly_flag\":0}"
```

### PATCH `/readings/{reading_id}`

Updates one reading.

### DELETE `/readings/{reading_id}`

Deletes one reading.
