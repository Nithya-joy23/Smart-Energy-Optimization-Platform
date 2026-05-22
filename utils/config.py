"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = os.getenv("ENERGY_CSV_PATH", str(BASE_DIR / "data" / "energy_consumption.csv"))
DB_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "database" / "smart_energy.db"))
DEFAULT_ENERGY_RATE = float(os.getenv("DEFAULT_ENERGY_RATE", "0.18"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
