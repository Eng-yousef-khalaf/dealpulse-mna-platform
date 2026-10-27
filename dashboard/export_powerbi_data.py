"""
DealPulse M&A Platform - Power BI Exporter
Prepares and exports clean Star Schema tables and denormalized views for Power BI / Tableau.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.db_manager import DatabaseManager
from src.config import EXPORTS_DIR, get_logger

logger = get_logger("PowerBIExporter")

def export_all_tables():
    db = DatabaseManager()
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    with db.get_connection() as conn:
        import pandas as pd
        
        tables = ["fact_mna_deals", "dim_companies", "dim_sectors", "dim_advisors"]
        for table in tables:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            dest = EXPORTS_DIR / f"{table}.csv"
            df.to_csv(dest, index=False)
            logger.info(f"Exported {table} ({len(df)} rows) to {dest}")

        # Also export the master denormalized view
        master_df = db.get_all_deals_df()
        master_dest = EXPORTS_DIR / "powerbi_deals_feed.csv"
        master_df.to_csv(master_dest, index=False)
        logger.info(f"Exported Master Power BI Feed ({len(master_df)} rows) to {master_dest}")

if __name__ == "__main__":
    export_all_tables()
