# Smart Energy Optimization Platform

A complete portfolio-ready energy analytics project built with Python, Streamlit, Pandas, NumPy, SQLite, FastAPI, SQL, Plotly, Matplotlib, and Power BI.

The platform tracks energy usage across multiple devices and buildings, analyzes trends, detects anomalies, forecasts future usage, and recommends cost-saving actions.

## What It Includes

- Synthetic dataset generator with 24 device profiles and hourly readings.
- CSV and SQLite storage.
- Modular data cleaning, feature engineering, aggregation, and analytics.
- Moving average, hourly profile, and linear regression forecasting.
- Z-score, IQR, and threshold-based anomaly detection.
- Optimization recommendation engine with estimated savings.
- Multi-page Streamlit dashboard.
- FastAPI REST API with interactive docs.
- SQL schema, sample inserts, and analytics queries.
- Power BI connection guide and DAX measures.
- Beginner-friendly setup and documentation.

## Project Structure

```text
SmartEnergyOptimization/
|-- api/
|-- dashboards/
|-- data/
|-- database/
|   |-- scripts/
|-- docs/
|-- models/
|-- notebooks/
|-- powerbi/
|-- utils/
|-- app.py
|-- main.py
|-- requirements.txt
|-- README.md
```

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python main.py --setup
streamlit run app.py
```

Run the API:

```bash
uvicorn api.main:app --reload
```

Open:

- Streamlit: `http://localhost:8501`
- API docs: `http://127.0.0.1:8000/docs`

## Dashboard Pages

1. Home Dashboard: KPI cards, daily trends, monthly cost, category cost, and peak-hour analytics.
2. Device Analytics: device-wise comparisons, efficiency scores, category cost analysis, and Matplotlib distribution chart.
3. Forecast: next-day, weekly, and monthly prediction views.
4. Anomaly Detection: spike alerts, anomaly heatmap, device ranking, and alert table.
5. Optimization Recommendations: device-specific savings recommendations.
6. SQL Analytics: predefined SQL queries and safe interactive SELECT queries.

## API Routes

- `GET /health`
- `GET /energy`
- `GET /devices/analytics`
- `GET /forecast`
- `GET /anomalies`
- `GET /recommendations`
- `POST /readings`
- `PATCH /readings/{reading_id}`
- `DELETE /readings/{reading_id}`

## Power BI

Use `data/energy_consumption.csv` for simple import, or connect to `database/smart_energy.db` through ODBC. See [powerbi/POWERBI_GUIDE.md](powerbi/POWERBI_GUIDE.md) for DAX measures and dashboard design suggestions.

## Documentation

- [Setup Guide](docs/SETUP.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Feature Documentation](docs/FEATURES.md)
- [Testing and Verification](docs/TESTING.md)
- [Future Enhancements](docs/FUTURE_ENHANCEMENTS.md)
- [Screenshot Placeholders](docs/SCREENSHOTS.md)

## How to Extend

- Add more device profiles in `utils/data_generator.py`.
- Add advanced models in `models/forecasting.py`.
- Add new anomaly rules in `models/anomaly_detection.py`.
- Add SQL metrics to `database/scripts/sample_queries.sql`.
- Add Streamlit pages in `app.py` or split pages into `dashboards/`.
- Add Power BI measures in `powerbi/POWERBI_GUIDE.md`.

## Interview Talking Points

- Explain how the schema separates device metadata from time-series readings.
- Discuss the tradeoff between simple statistical anomaly detection and ML-based models.
- Explain why the dashboard uses cached data loading.
- Describe how the REST API exposes analytics to other applications.
- Show how Power BI can consume the generated CSV or SQLite data.
