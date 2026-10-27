@echo off
REM ==============================================================================
REM DealPulse M&A Intelligence Platform - Windows Batch Runner
REM ==============================================================================
echo [DealPulse] Starting Pipeline Execution...

python -m pytest tests/ -q
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Tests failed! Aborting pipeline run.
    exit /b %ERRORLEVEL%
)

python -c "import sys; sys.path.insert(0, '.'); from src.database.db_manager import DatabaseManager; from src.pipeline.cleaner import DealPipelineCleaner; from src.scrapers import MnaDealsScraper, FinancialNewsScraper, SecFilingsScraper; db = DatabaseManager(); db.initialize_schema(); cleaner = DealPipelineCleaner(db); deals = []; deals.extend(MnaDealsScraper().scrape_deals()); deals.extend(FinancialNewsScraper().scrape_pe_announcements()); deals.extend(SecFilingsScraper().scrape_regulatory_deals()); print(cleaner.process_and_ingest(deals))"

python dashboard\export_powerbi_data.py
echo [DealPulse] Pipeline Execution Completed Successfully!
