"""
DealPulse M&A Platform - Data Cleaner & Pipeline Orchestrator
Normalizes financial metrics, handles FX conversion, computes valuation multiples,
and ingests clean records into the Dimensional Database.
"""
from typing import List, Dict, Any
import pandas as pd
import polars as pl
from pathlib import Path

from src.config import FX_RATES_TO_USD, EXPORTS_DIR, get_logger
from src.database.db_manager import DatabaseManager
from .ontology import clean_company_name, generate_entity_id, map_to_standard_sector
from .data_quality import validate_deal_records

logger = get_logger("PipelineCleaner")

class DealPipelineCleaner:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def process_and_ingest(self, raw_deals: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Full ETL cleaning, enrichment, and dimensional ingestion pipeline.
        """
        logger.info(f"Starting pipeline ingestion for {len(raw_deals)} raw records...")

        # Step 1: Validation & Quality Control
        valid_records, failed_records = validate_deal_records(raw_deals)
        if not valid_records:
            logger.warning("No valid records found after data quality inspection.")
            return {"valid": 0, "failed": len(failed_records), "ingested": 0}

        # Step 2: High performance cleaning via Pandas
        df = pd.DataFrame(valid_records)

        # Currency Normalization (Deal Value in USD)
        df["deal_currency"] = df["deal_currency"].str.upper()
        df["fx_rate"] = df["deal_currency"].map(FX_RATES_TO_USD).fillna(1.0)
        df["deal_value_usd"] = (df["deal_value_native"] * df["fx_rate"]).round(2)

        # Compute M&A Valuation Multiples
        df["ev_to_revenue_multiple"] = (
            df["deal_value_usd"] / df["target_revenue_usd"]
        ).round(2).where(df["target_revenue_usd"] > 0, None)

        df["ev_to_ebitda_multiple"] = (
            df["deal_value_usd"] / df["target_ebitda_usd"]
        ).round(2).where(df["target_ebitda_usd"] > 0, None)

        # Step 3: Dimensional Database Ingestion
        ingested_count = 0
        for _, row in df.iterrows():
            # Standardize Companies
            target_clean = clean_company_name(row["target_company"])
            target_id = generate_entity_id(target_clean, row.get("target_country", "US"))
            self.db.upsert_company({
                "company_id": target_id,
                "company_name": target_clean,
                "ticker": None,
                "headquarters_country": row.get("target_country", "United States"),
                "headquarters_city": row.get("target_city"),
                "founded_year": None,
                "ownership_type": "Private",
                "employee_count": None,
            })

            acquirer_clean = clean_company_name(row["acquirer_company"])
            acquirer_id = generate_entity_id(acquirer_clean, row.get("acquirer_country", "US"))
            is_pe = "Private Equity" in row["buyer_type"]
            self.db.upsert_company({
                "company_id": acquirer_id,
                "company_name": acquirer_clean,
                "ticker": None,
                "headquarters_country": row.get("acquirer_country", "United States"),
                "headquarters_city": None,
                "founded_year": None,
                "ownership_type": "PE-Backed" if is_pe else "Public",
                "employee_count": None,
            })

            # Sector Resolution
            std_sector = map_to_standard_sector(row["sector"])
            sector_id = self.db.upsert_sector(std_sector)

            # Lead Advisor Resolution
            advisor_id = None
            if row.get("lead_advisor"):
                adv_name = row["lead_advisor"].strip()
                advisor_id = f"ADV-{adv_name.replace(' ', '-').upper()}"
                self.db.upsert_advisor(
                    advisor_id=advisor_id,
                    advisor_name=adv_name,
                    advisor_type="Investment Bank",
                    country="Global",
                )

            # Insert Fact Deal
            deal_payload = {
                "deal_id": row["deal_id"],
                "deal_announcement_date": row["announcement_date"],
                "deal_completion_date": row.get("announcement_date"),
                "target_company_id": target_id,
                "acquirer_company_id": acquirer_id,
                "sector_id": sector_id,
                "lead_advisor_id": advisor_id,
                "deal_type": row["deal_type"],
                "buyer_type": row["buyer_type"],
                "deal_status": row.get("deal_status", "Announced"),
                "deal_currency": row["deal_currency"],
                "deal_value_native": float(row["deal_value_native"]),
                "deal_value_usd": float(row["deal_value_usd"]),
                "target_revenue_usd": float(row["target_revenue_usd"]) if pd.notnull(row["target_revenue_usd"]) else None,
                "target_ebitda_usd": float(row["target_ebitda_usd"]) if pd.notnull(row["target_ebitda_usd"]) else None,
                "ev_to_revenue_multiple": float(row["ev_to_revenue_multiple"]) if pd.notnull(row["ev_to_revenue_multiple"]) else None,
                "ev_to_ebitda_multiple": float(row["ev_to_ebitda_multiple"]) if pd.notnull(row["ev_to_ebitda_multiple"]) else None,
                "stake_percentage_acquired": 100.0,
                "source_feed": row["source_feed"],
                "source_reference_url": row.get("source_url"),
            }
            self.db.upsert_deal(deal_payload)
            ingested_count += 1

        logger.info(f"Pipeline successfully ingested {ingested_count} deals into database.")

        # Step 4: Export Power BI & Tableau ready curated CSV files
        self.export_curated_data()

        return {
            "valid": len(valid_records),
            "failed": len(failed_records),
            "ingested": ingested_count
        }

    def export_curated_data(self):
        """Exports star-schema tables to CSV for Power BI / Excel import."""
        deals_df = self.db.get_all_deals_df()
        export_path = EXPORTS_DIR / "powerbi_deals_feed.csv"
        deals_df.to_csv(export_path, index=False)
        logger.info(f"Exported curated Power BI dataset to {export_path}")
