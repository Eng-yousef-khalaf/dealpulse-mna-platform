#!/usr/bin/env bash
# ==============================================================================
# DealPulse M&A Intelligence Platform
# Automated Pipeline Execution & Ingestion Script (Linux / Shell)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
TIMESTAMP="$(date +'%Y-%m-%d_%H-%M-%S')"
LOG_FILE="$LOG_DIR/cron_run_${TIMESTAMP}.log"

mkdir -p "$LOG_DIR"

echo "==========================================================" | tee -a "$LOG_FILE"
echo "Starting DealPulse M&A Ingestion Pipeline: $(date)" | tee -a "$LOG_FILE"
echo "Project Root: $PROJECT_ROOT" | tee -a "$LOG_FILE"
echo "==========================================================" | tee -a "$LOG_FILE"

cd "$PROJECT_ROOT"

# Check Python environment
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo "Activating virtual environment..." | tee -a "$LOG_FILE"
    source "$PROJECT_ROOT/.venv/bin/activate"
elif command -v python3 &> /dev/null; then
    PYTHON_BIN="python3"
else
    PYTHON_BIN="python"
fi

# Step 1: Run Unit & Quality Tests
echo "[Step 1/3] Executing Data Quality & Ingestion Unit Tests..." | tee -a "$LOG_FILE"
python -m pytest tests/ -q | tee -a "$LOG_FILE"

# Step 2: Run Multi-Source Scraping & Pipeline Ingestion
echo "[Step 2/3] Extracting Multi-Source M&A Feeds & Populating Database..." | tee -a "$LOG_FILE"
python -c "
import sys
from pathlib import Path
sys.path.insert(0, '.')
from src.database.db_manager import DatabaseManager
from src.pipeline.cleaner import DealPipelineCleaner
from src.scrapers import MnaDealsScraper, FinancialNewsScraper, SecFilingsScraper

db = DatabaseManager()
db.initialize_schema()
cleaner = DealPipelineCleaner(db)

deals = []
deals.extend(MnaDealsScraper().scrape_deals())
deals.extend(FinancialNewsScraper().scrape_pe_announcements())
deals.extend(SecFilingsScraper().scrape_regulatory_deals())

results = cleaner.process_and_ingest(deals)
print(f'Pipeline Run Summary: {results}')
" | tee -a "$LOG_FILE"

# Step 3: Export Clean Power BI Datasets
echo "[Step 3/3] Exporting Star Schema tables for Power BI..." | tee -a "$LOG_FILE"
python dashboard/export_powerbi_data.py | tee -a "$LOG_FILE"

echo "==========================================================" | tee -a "$LOG_FILE"
echo "DealPulse Pipeline Completed Successfully at $(date)" | tee -a "$LOG_FILE"
echo "==========================================================" | tee -a "$LOG_FILE"
