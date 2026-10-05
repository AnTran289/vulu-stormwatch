# centralising configuration.
# API keys and environment-specific settings should come from .env
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[3]

load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
RAW_S3_BUCKET = os.getenv("RAW_S3_BUCKET")
LOG_DIR = BASE_DIR / "logs"

PROVINCE_API_BASE_URL = os.getenv(
    "PROVINCE_API_BASE_URL",
    "https://provinces.open-api.vn/api",
)
OPEN_METEO_BASE_URL = os.getenv(
    "OPEN_METEO_BASE_URL",
    "https://api.open-meteo.com/v1/forecast",
)

REQUEST_TIMEOUT_SECONDS = 30

PIPELINE_LOCATION_MAX_ATTEMPTS = int(
    os.getenv("PIPELINE_LOCATION_MAX_ATTEMPTS", "3")
)
PIPELINE_RETRY_BACKOFF_SECONDS = float(
    os.getenv("PIPELINE_RETRY_BACKOFF_SECONDS", "5")
)
PIPELINE_INTERVAL_SECONDS = int(
    os.getenv("PIPELINE_INTERVAL_SECONDS", "3600")
)
PIPELINE_ADVISORY_LOCK_ID = int(
    os.getenv("PIPELINE_ADVISORY_LOCK_ID", "836986827")
)
STATUS_STALE_AFTER_SECONDS = int(
    os.getenv("STATUS_STALE_AFTER_SECONDS", "14400")
)
STATUS_SLIGHTLY_STALE_AFTER_SECONDS = int(
    os.getenv("STATUS_SLIGHTLY_STALE_AFTER_SECONDS", "7200")
)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "vulu_stormwatch")
DB_USER = os.getenv("DB_USER", "vulu")
DB_PASSWORD = os.getenv("DB_PASSWORD", "vulu_password")
DB_SCHEMA = os.getenv("DB_SCHEMA", "public")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "3"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "2"))
DB_POOL_TIMEOUT_SECONDS = int(os.getenv("DB_POOL_TIMEOUT_SECONDS", "10"))
DB_POOL_RECYCLE_SECONDS = int(os.getenv("DB_POOL_RECYCLE_SECONDS", "300"))

REFERENCE_DATA_DIR = (
    DATA_DIR / "reference"
)

PROVINCE_COORDINATES_FILE = (
    REFERENCE_DATA_DIR
    / "province_coordinates.csv"
)
