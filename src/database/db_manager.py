"""
DealPulse M&A Platform - Database Manager
Handles connection pooling, Star Schema initialization, and upsert operations.
"""
import sqlite3
from typing import List, Dict, Any, Optional
import pandas as pd
import polars as pl
from pathlib import Path

from src.config import SQLITE_DB_PATH, get_logger

logger = get_logger("DatabaseManager")
SCHEMA_FILE = Path(__file__).parent / "schema.sql"

class DatabaseManager:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or SQLITE_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Returns a configured SQLite connection with foreign keys enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def initialize_schema(self, force_recreate: bool = False):
        """Initializes tables, views, and indexes from schema.sql."""
        if not SCHEMA_FILE.exists():
            raise FileNotFoundError(f"Schema file not found: {SCHEMA_FILE}")

        logger.info(f"Initializing database schema at {self.db_path}...")
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        with self.get_connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()
        logger.info("Database schema initialized successfully.")

    def upsert_company(self, company: Dict[str, Any]):
        """Upsert a company into dim_companies."""
        query = """
        INSERT INTO dim_companies (
            company_id, company_name, ticker, headquarters_country, 
            headquarters_city, founded_year, ownership_type, employee_count
        ) VALUES (
            :company_id, :company_name, :ticker, :headquarters_country, 
            :headquarters_city, :founded_year, :ownership_type, :employee_count
        )
        ON CONFLICT(company_id) DO UPDATE SET
            company_name = excluded.company_name,
            ticker = COALESCE(excluded.ticker, dim_companies.ticker),
            headquarters_country = excluded.headquarters_country,
            headquarters_city = COALESCE(excluded.headquarters_city, dim_companies.headquarters_city),
            ownership_type = excluded.ownership_type,
            employee_count = COALESCE(excluded.employee_count, dim_companies.employee_count);
        """
        with self.get_connection() as conn:
            conn.execute(query, company)
            conn.commit()

    def upsert_sector(self, sector_name: str, sub_industry: str = "", description: str = "") -> int:
        """Upsert a sector and return its sector_id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sector_id FROM dim_sectors WHERE sector_name = ?", (sector_name,))
            row = cursor.fetchone()
            if row:
                return row["sector_id"]

            cursor.execute(
                "INSERT INTO dim_sectors (sector_name, sub_industry, description) VALUES (?, ?, ?)",
                (sector_name, sub_industry, description)
            )
            conn.commit()
            return cursor.lastrowid

    def upsert_advisor(self, advisor_id: str, advisor_name: str, advisor_type: str, country: str):
        """Upsert financial or legal advisor into dim_advisors."""
        query = """
        INSERT INTO dim_advisors (advisor_id, advisor_name, advisor_type, headquarters_country)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(advisor_id) DO UPDATE SET
            advisor_name = excluded.advisor_name,
            advisor_type = excluded.advisor_type,
            headquarters_country = excluded.headquarters_country;
        """
        with self.get_connection() as conn:
            conn.execute(query, (advisor_id, advisor_name, advisor_type, country))
            conn.commit()

    def upsert_deal(self, deal: Dict[str, Any]):
        """Upsert an M&A transaction into fact_mna_deals."""
        query = """
        INSERT INTO fact_mna_deals (
            deal_id, deal_announcement_date, deal_completion_date,
            target_company_id, acquirer_company_id, sector_id, lead_advisor_id,
            deal_type, buyer_type, deal_status, deal_currency,
            deal_value_native, deal_value_usd, target_revenue_usd, target_ebitda_usd,
            ev_to_revenue_multiple, ev_to_ebitda_multiple, stake_percentage_acquired,
            source_feed, source_reference_url
        ) VALUES (
            :deal_id, :deal_announcement_date, :deal_completion_date,
            :target_company_id, :acquirer_company_id, :sector_id, :lead_advisor_id,
            :deal_type, :buyer_type, :deal_status, :deal_currency,
            :deal_value_native, :deal_value_usd, :target_revenue_usd, :target_ebitda_usd,
            :ev_to_revenue_multiple, :ev_to_ebitda_multiple, :stake_percentage_acquired,
            :source_feed, :source_reference_url
        )
        ON CONFLICT(deal_id) DO UPDATE SET
            deal_completion_date = excluded.deal_completion_date,
            deal_status = excluded.deal_status,
            deal_value_usd = excluded.deal_value_usd,
            ev_to_ebitda_multiple = excluded.ev_to_ebitda_multiple,
            ev_to_revenue_multiple = excluded.ev_to_revenue_multiple;
        """
        with self.get_connection() as conn:
            conn.execute(query, deal)
            conn.commit()

    def get_all_deals_df(self) -> pd.DataFrame:
        """Fetch complete joined deal records as a Pandas DataFrame for analysis & reporting."""
        query = """
        SELECT 
            f.deal_id,
            f.deal_announcement_date,
            f.deal_completion_date,
            f.deal_type,
            f.buyer_type,
            f.deal_status,
            f.deal_currency,
            f.deal_value_native,
            f.deal_value_usd,
            f.target_revenue_usd,
            f.target_ebitda_usd,
            f.ev_to_revenue_multiple,
            f.ev_to_ebitda_multiple,
            f.stake_percentage_acquired,
            f.source_feed,
            t.company_name AS target_name,
            t.headquarters_country AS target_country,
            t.ownership_type AS target_ownership,
            a.company_name AS acquirer_name,
            a.headquarters_country AS acquirer_country,
            s.sector_name,
            adv.advisor_name AS lead_advisor
        FROM fact_mna_deals f
        JOIN dim_companies t ON f.target_company_id = t.company_id
        JOIN dim_companies a ON f.acquirer_company_id = a.company_id
        JOIN dim_sectors s ON f.sector_id = s.sector_id
        LEFT JOIN dim_advisors adv ON f.lead_advisor_id = adv.advisor_id
        ORDER BY f.deal_announcement_date DESC;
        """
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def get_all_deals_polars(self) -> pl.DataFrame:
        """High-performance Polars retrieval matching modern investment banking requirements."""
        df = self.get_all_deals_df()
        return pl.from_pandas(df)
