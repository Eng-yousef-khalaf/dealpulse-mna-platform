"""
DealPulse M&A Platform - Seed Data Generator
Generates institutional-grade, realistic M&A transactions across UK, US, and European mid-market.
"""
import random
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.db_manager import DatabaseManager
from src.pipeline.cleaner import DealPipelineCleaner

def generate_seed_deals(count: int = 40):
    db = DatabaseManager()
    db.initialize_schema()
    cleaner = DealPipelineCleaner(db)

    sectors = [
        "Enterprise Software & SaaS",
        "FinTech & Payments",
        "Digital Healthcare & MedTech",
        "Cybersecurity",
        "CleanTech & Energy Transition",
        "Industrial IoT & Automation",
    ]

    pe_sponsors = [
        ("Permira Advisers", "United Kingdom"),
        ("Hg Capital", "United Kingdom"),
        ("Nordic Capital", "Sweden"),
        ("Bridgepoint Group", "United Kingdom"),
        ("Blackstone Group", "United States"),
        ("Thoma Bravo", "United States"),
        ("Vista Equity Partners", "United States"),
        ("EQT Partners", "Sweden"),
        ("Eurazeo", "France"),
    ]

    strategic_acquirers = [
        ("Cisco Systems", "United States"),
        ("Stripe Global", "United States"),
        ("Salesforce Inc", "United States"),
        ("Schneider Electric", "France"),
        ("SAP SE", "Germany"),
        ("RELX Group", "United Kingdom"),
        ("Siemens Digital", "Germany"),
    ]

    advisors = [
        "Rothschild & Co",
        "Lazard",
        "Evercore",
        "Goldman Sachs",
        "Morgan Stanley",
        "Houlihan Lokey",
        "Jefferies",
        "William Blair",
    ]

    targets = [
        ("OmniCyber Defense", "United Kingdom", "London", "Cybersecurity"),
        ("DataMesh Cloud", "United States", "San Francisco", "Enterprise Software & SaaS"),
        ("PayBridge Global", "Germany", "Berlin", "FinTech & Payments"),
        ("BioHealth Analytics", "United Kingdom", "Cambridge", "Digital Healthcare & MedTech"),
        ("EcoGrid Solutions", "France", "Paris", "CleanTech & Energy Transition"),
        ("RoboFlow Automation", "Sweden", "Stockholm", "Industrial IoT & Automation"),
        ("PulseHR SaaS", "United States", "New York", "Enterprise Software & SaaS"),
        ("FinLedger Banking API", "United Kingdom", "London", "FinTech & Payments"),
        ("SecureStack Systems", "United States", "Boston", "Cybersecurity"),
        ("CareSync Telehealth", "United States", "Chicago", "Digital Healthcare & MedTech"),
        ("AeroSensors IoT", "Germany", "Munich", "Industrial IoT & Automation"),
        ("GreenWatt Solar AI", "Spain", "Madrid", "CleanTech & Energy Transition"),
    ]

    deals = []
    base_date = datetime(2026, 10, 25)

    for i in range(count):
        target_info = random.choice(targets)
        is_pe = random.random() > 0.4
        
        if is_pe:
            acquirer, acq_country = random.choice(pe_sponsors)
            buyer_type = "Private Equity Sponsor"
            deal_type = random.choice(["Majority Stake / Buyout", "Secondary Buyout (PE to PE)", "Growth Capital"])
        else:
            acquirer, acq_country = random.choice(strategic_acquirers)
            buyer_type = "Strategic / Corporate Acquirer"
            deal_type = "Full Acquisition"

        currency = "GBP" if target_info[1] == "United Kingdom" else ("EUR" if target_info[1] in ["Germany", "France", "Sweden", "Spain"] else "USD")
        
        # Financials
        revenue = round(random.uniform(25.0, 180.0), 1)
        ebitda_margin = random.uniform(0.18, 0.38)
        ebitda = round(revenue * ebitda_margin, 1)
        
        # Multiple between 10x and 24x EBITDA
        target_multiple = random.uniform(11.0, 22.0)
        deal_value_native = round(ebitda * target_multiple, 1)

        deal_date = (base_date - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d")

        deal_record = {
            "deal_id": f"DEAL-MNA-{2026000 + i}",
            "announcement_date": deal_date,
            "target_company": f"{target_info[0]} {random.choice(['Group', 'Labs', 'Tech', 'Systems', 'Global'])}",
            "target_country": target_info[1],
            "target_city": target_info[2],
            "acquirer_company": acquirer,
            "acquirer_country": acq_country,
            "sector": target_info[3],
            "deal_type": deal_type,
            "buyer_type": buyer_type,
            "deal_status": random.choice(["Completed", "Completed", "Announced"]),
            "deal_currency": currency,
            "deal_value_native": deal_value_native,
            "target_revenue_usd": revenue,
            "target_ebitda_usd": ebitda,
            "lead_advisor": random.choice(advisors),
            "source_feed": "DealPulse Institutional Scraper Network",
            "source_url": f"https://dealpulse.intelligence/transactions/{2026000 + i}",
        }
        deals.append(deal_record)

    cleaner.process_and_ingest(deals)
    print(f"Successfully generated and ingested {len(deals)} institutional M&A transactions.")

if __name__ == "__main__":
    generate_seed_deals(45)
