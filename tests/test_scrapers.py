"""
DealPulse Tests - Multi-Source Web Scraper Validation
"""
import pytest
from bs4 import BeautifulSoup
from src.scrapers import MnaDealsScraper, FinancialNewsScraper, SecFilingsScraper

def test_mna_scraper_extraction():
    scraper = MnaDealsScraper()
    deals = scraper.scrape_deals()
    assert isinstance(deals, list)
    assert len(deals) > 0
    assert "deal_id" in deals[0]
    assert deals[0]["deal_value_native"] > 0

def test_card_parsing_regex():
    scraper = MnaDealsScraper()
    html_sample = "<div class='card'><h3>Permira acquires CloudSec for £250M</h3></div>"
    soup = BeautifulSoup(html_sample, "html.parser")
    parsed = scraper.extract_deal_from_html_card(soup)
    assert parsed["currency"] == "GBP"
    assert parsed["raw_value"] == 250.0

def test_financial_news_scraper():
    scraper = FinancialNewsScraper()
    pe_deals = scraper.scrape_pe_announcements()
    assert len(pe_deals) > 0
    assert any(d["buyer_type"] == "Private Equity Sponsor" for d in pe_deals)

def test_sec_filings_scraper():
    scraper = SecFilingsScraper()
    regulatory_deals = scraper.scrape_regulatory_deals()
    assert len(regulatory_deals) > 0
    assert all("SEC" in d["source_feed"] or "Companies House" in d["source_feed"] for d in regulatory_deals)
