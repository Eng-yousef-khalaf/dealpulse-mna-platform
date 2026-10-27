"""
DealPulse Tests - Database Schema & Dimensional Integrity
"""
import pytest
from pathlib import Path
from src.database.db_manager import DatabaseManager
from src.pipeline.cleaner import DealPipelineCleaner

@pytest.fixture
def temp_db(tmp_path):
    test_db_path = tmp_path / "test_dealpulse.db"
    db = DatabaseManager(db_path=test_db_path)
    db.initialize_schema()
    return db

def test_database_initialization(temp_db):
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        assert "fact_mna_deals" in tables
        assert "dim_companies" in tables
        assert "dim_sectors" in tables
        assert "dim_advisors" in tables

def test_deal_ingestion_and_views(temp_db):
    cleaner = DealPipelineCleaner(temp_db)
    sample_deals = [{
        "deal_id": "DEAL-DB-TEST-100",
        "announcement_date": "2026-10-21",
        "target_company": "Apex BioTech Corp",
        "target_country": "United States",
        "acquirer_company": "KKR & Co Inc",
        "acquirer_country": "United States",
        "sector": "Digital Healthcare & MedTech",
        "deal_type": "Majority Stake / Buyout",
        "buyer_type": "Private Equity Sponsor",
        "deal_status": "Completed",
        "deal_currency": "USD",
        "deal_value_native": 300.0,
        "target_revenue_usd": 60.0,
        "target_ebitda_usd": 20.0,
        "lead_advisor": "Lazard",
        "source_feed": "Unit Test Stream",
    }]
    
    res = cleaner.process_and_ingest(sample_deals)
    assert res["ingested"] == 1

    # Verify Fact Record
    df = temp_db.get_all_deals_df()
    assert len(df) == 1
    assert df.iloc[0]["target_name"] == "Apex BioTech"
    assert df.iloc[0]["acquirer_name"] == "KKR & Co"
    assert df.iloc[0]["ev_to_ebitda_multiple"] == 15.0  # 300 / 20
    assert df.iloc[0]["ev_to_revenue_multiple"] == 5.0   # 300 / 60

    # Verify Analytical View
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM v_sector_valuation_benchmarks;")
        benchmarks = cursor.fetchall()
        assert len(benchmarks) > 0
