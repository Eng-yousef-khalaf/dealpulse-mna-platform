"""
DealPulse M&A Platform - Macro Trends & Deal Flow Analytics
Analyzes private equity market share, cross-border capital flows, and deal velocity.
"""
import pandas as pd
from typing import Dict, Any
from src.database.db_manager import DatabaseManager

class MarketTrendsAnalytics:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_buyer_type_breakdown(self) -> pd.DataFrame:
        """Breakdown of deal volume and value by buyer archetype (PE vs Corporate)."""
        df = self.db.get_all_deals_df()
        if df.empty:
            return pd.DataFrame()

        summary = df.groupby("buyer_type").agg(
            deal_count=("deal_id", "count"),
            total_value_usd_m=("deal_value_usd", "sum"),
            avg_deal_size_usd_m=("deal_value_usd", "mean"),
            avg_ev_ebitda=("ev_to_ebitda_multiple", "mean")
        ).reset_index()

        total_val = summary["total_value_usd_m"].sum()
        summary["share_of_market_pct"] = ((summary["total_value_usd_m"] / total_val) * 100).round(1)
        return summary.round(2)

    def get_cross_border_flow(self) -> pd.DataFrame:
        """Tracks cross-border investment flows between US, UK, and European markets."""
        df = self.db.get_all_deals_df()
        if df.empty:
            return pd.DataFrame()

        flow = df.groupby(["acquirer_country", "target_country"]).agg(
            deal_count=("deal_id", "count"),
            capital_deployed_usd_m=("deal_value_usd", "sum")
        ).reset_index().sort_values(by="capital_deployed_usd_m", ascending=False)
        return flow
