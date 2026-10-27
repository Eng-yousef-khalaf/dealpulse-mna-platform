"""
DealPulse M&A Intelligence Platform
Configuration and Settings Module
"""
import os
import logging
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXPORTS_DIR = DATA_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"

# Ensure runtime directories exist
for path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, EXPORTS_DIR, LOGS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'dealpulse_mna.db'}")
SQLITE_DB_PATH = DATA_DIR / "dealpulse_mna.db"

# Currency Normalization to USD (Base standard for international investment banks)
FX_RATES_TO_USD = {
    "USD": 1.00,
    "EUR": 1.09,
    "GBP": 1.28,
    "CAD": 0.74,
    "CHF": 1.13,
    "AUD": 0.65,
}

# Investment Banking Ontologies & Standardized Taxonomies
STANDARD_SECTORS = [
    "Enterprise Software & SaaS",
    "FinTech & Payments",
    "Digital Healthcare & MedTech",
    "Cybersecurity",
    "CleanTech & Energy Transition",
    "E-Commerce & Digital Consumer",
    "Industrial IoT & Automation",
    "Telecommunications & Infrastructure",
]

DEAL_TYPES = [
    "Full Acquisition",
    "Majority Stake / Buyout",
    "Growth Capital",
    "Corporate Divestiture",
    "Secondary Buyout (PE to PE)",
    "Joint Venture / Strategic Merger",
]

BUYER_TYPES = [
    "Private Equity Sponsor",
    "Strategic / Corporate Acquirer",
    "Venture Capital / Growth Equity",
    "Family Office / Sovereign Wealth",
]

# Scraping & HTTP Client Settings
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 DealPulseBot/1.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0

# Logging Configuration
LOG_FILE = LOGS_DIR / "dealpulse_pipeline.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger instance."""
    return logging.getLogger(name)
