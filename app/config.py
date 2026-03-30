from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CAMPAIGNS_FILE = BASE_DIR / "campaigns.yaml"

# Base URL for QR code generation (override via environment variable)
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "changeme")


def load_campaigns() -> dict[str, dict]:
    with open(CAMPAIGNS_FILE) as f:
        data = yaml.safe_load(f)
    return data.get("campaigns", {})
