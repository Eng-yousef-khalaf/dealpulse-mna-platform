"""
DealPulse Tests - Pipeline Cleaner, Quality Checks & Ontology
"""
import pytest
from src.pipeline.ontology import clean_company_name, generate_entity_id, map_to_standard_sector
from src.pipeline.data_quality import validate_deal_records

def test_company_name_cleaning():
    assert clean_company_name("Acme Software Inc.") == "Acme Software"
    assert clean_company_name("Beta Technologies LLC") == "Beta"
    assert clean_company_name("Gamma Partners Ltd") == "Gamma"
    assert clean_company_name("Delta Group Plc") == "Delta"

def test_entity_id_generation():
    ent_id = generate_entity_id("Permira Advisers Ltd", "United Kingdom")
    assert ent_id == "COMP-UNI-PERMIRA-ADVISERS"

def test_sector_mapping():
    assert map_to_standard_sector("AI enterprise SaaS analytics") == "Enterprise Software & SaaS"
    assert map_to_standard_sector("FinTech mobile payment gateway") == "FinTech & Payments"
    assert map_to_standard_sector("Cyber security perimeter defense") == "Cybersecurity"

def test_data_quality_validation():
    valid_sample = [{
        "deal_id": "DEAL-TEST-001",
        "announcement_date": "2026-10-20",
        "target_company": "Test Target",
        "acquirer_company": "Test Acquirer",
        "sector": "FinTech & Payments",
        "deal_type": "Full Acquisition",
        "buyer_type": "Strategic / Corporate Acquirer",
        "deal_status": "Completed",
        "deal_currency": "USD",
        "deal_value_native": 100.0,
        "source_feed": "Test Feed",
    }]
    valid, failed = validate_deal_records(valid_sample)
    assert len(valid) == 1
    assert len(failed) == 0

def test_data_quality_rejection_negative_value():
    invalid_sample = [{
        "deal_id": "DEAL-FAIL-001",
        "announcement_date": "2026-10-20",
        "target_company": "Test Target",
        "acquirer_company": "Test Acquirer",
        "sector": "FinTech",
        "deal_type": "Full Acquisition",
        "buyer_type": "Strategic",
        "deal_status": "Completed",
        "deal_currency": "USD",
        "deal_value_native": -50.0,  # Invalid negative price
        "source_feed": "Test Feed",
    }]
    valid, failed = validate_deal_records(invalid_sample)
    assert len(valid) == 0
    assert len(failed) == 1
