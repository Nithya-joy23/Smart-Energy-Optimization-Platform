"""Command-line utilities for the Smart Energy Optimization Platform."""

from __future__ import annotations

import argparse
from pathlib import Path

from database.db_manager import create_tables, load_csv_to_database
from utils.config import DATA_PATH, DB_PATH
from utils.data_generator import generate_energy_dataset
from utils.logger import get_logger

logger = get_logger(__name__)


def setup_project(days: int = 150, force: bool = False) -> None:
    """Generate the synthetic dataset and load it into SQLite."""
    data_path = Path(DATA_PATH)
    db_path = Path(DB_PATH)
    data_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if force or not data_path.exists():
        logger.info("Generating synthetic energy dataset at %s", data_path)
        generate_energy_dataset(output_path=data_path, days=days)
    else:
        logger.info("Dataset already exists at %s", data_path)

    logger.info("Creating database schema at %s", db_path)
    create_tables(db_path)
    load_csv_to_database(data_path, db_path, replace=True)
    logger.info("Setup complete.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smart Energy Optimization Platform")
    parser.add_argument("--setup", action="store_true", help="Generate data and initialize SQLite")
    parser.add_argument("--force", action="store_true", help="Regenerate data even if files already exist")
    parser.add_argument("--days", type=int, default=150, help="Number of days of hourly synthetic data")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.setup:
        setup_project(days=args.days, force=args.force)
    else:
        print("Run `python main.py --setup` to generate data and initialize the database.")
