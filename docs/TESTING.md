# Testing and Verification

## Smoke Test the Core Modules

```bash
python -c "from database.db_manager import fetch_energy_data; from utils.data_processing import calculate_kpis; from models.forecasting import combined_forecast; df=fetch_energy_data(); print(len(df)); print(calculate_kpis(df)); print(combined_forecast(df).keys())"
```

## Test API Endpoints

Start the API:

```bash
uvicorn api.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

Example requests:

```bash
curl "http://127.0.0.1:8000/health"
curl "http://127.0.0.1:8000/energy?limit=5"
curl "http://127.0.0.1:8000/devices/analytics"
curl "http://127.0.0.1:8000/forecast"
curl "http://127.0.0.1:8000/anomalies?limit=5"
curl "http://127.0.0.1:8000/recommendations"
```

## Test SQL

Open the Streamlit SQL Analytics page, choose a predefined query, and click **Run query**.

You can also run queries from `database/scripts/sample_queries.sql` with any SQLite client.
