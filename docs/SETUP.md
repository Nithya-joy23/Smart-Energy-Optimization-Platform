# Installation Guide

## Prerequisites

- Python 3.10 or newer
- Power BI Desktop for the BI portion
- Optional: SQLite browser or SQLite ODBC driver

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python main.py --setup
```

The setup command creates:

- `data/energy_consumption.csv`
- `database/smart_energy.db`
- `devices` and `energy_readings` tables

## Run Streamlit

```bash
streamlit run app.py
```

## Run the REST API

```bash
uvicorn api.main:app --reload
```

Open:

- API root docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## Regenerate Data

```bash
python main.py --setup --force --days 180
```
