"""
DealPulse Tests - Power Automate Integration & Polars High-Performance Engine
"""
import pytest
from src.pipeline.power_automate import PowerAutomateConnector
from src.analytics.polars_engine import PolarsValuationEngine
from src.database.db_manager import DatabaseManager

def test_power_automate_adaptive_card_generation():
    connector = PowerAutomateConnector()
    sample_deal = {
        "deal_id": "DEAL-MOCK-999",
        "target_company": "SecureNet Systems",
        "acquirer_company": "Permira Advisers",
        "sector": "Cybersecurity",
        "deal_value_usd": 185.0,
        "ev_to_ebitda_multiple": 21.4,
        "buyer_type": "Private Equity Sponsor",
        "lead_advisor": "Evercore",
        "source_feed": "PE News Wire",
    }
    card = connector.build_adaptive_card_payload(sample_deal)
    assert card["type"] == "message"
    attachments = card["attachments"]
    assert len(attachments) == 1
    content = attachments[0]["content"]
    assert content["type"] == "AdaptiveCard"
    body = content["body"]
    assert len(body) == 2
    # Check alert simulation
    sim_result = connector.dispatch_alert_simulation(sample_deal)
    assert sim_result["status"] == "success"
    assert sim_result["target_deal_id"] == "DEAL-MOCK-999"

def test_power_automate_sharepoint_feed_export():
    connector = PowerAutomateConnector()
    sample_deals = [
        {
            "deal_id": "DEAL-SP-001",
            "announcement_date": "2026-10-25",
            "target_company": "CloudWave SaaS",
            "acquirer_company": "Oracle",
            "sector": "Enterprise Software & SaaS",
            "deal_value_usd": 320.0,
            "ev_to_ebitda_multiple": 18.5,
            "buyer_type": "Strategic / Corporate Acquirer",
        }
    ]
    path = connector.export_sharepoint_migration_feed(sample_deals)
    assert path.exists()

def test_polars_engine_benchmarks():
    db = DatabaseManager()
    engine = PolarsValuationEngine(db)
    benchmarks = engine.compute_sector_benchmarks_polars()
    assert benchmarks.height > 0
    assert "median_ev_ebitda" in benchmarks.columns
    assert "total_capital_usd_m" in benchmarks.columns

def test_polars_vs_pandas_speed_benchmark():
    db = DatabaseManager()
    engine = PolarsValuationEngine(db)
    result = engine.benchmark_pandas_vs_polars()
    assert "pandas_ms" in result
    assert "polars_ms" in result
    assert "speedup_factor" in result
