"""
DealPulse M&A Platform - Valuation Multiples & Statistical Analytics
Computes distribution statistics, sector valuation benchmarks, and outlier detection
for investment banking pitchbooks and valuation reports.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any

from src.database.db_manager import DatabaseManager
from src.config import get_logger

logger = get_logger("ValuationAnalytics")

class ValuationAnalytics:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def compute_sector_multiples_summary(self) -> pd.DataFrame:
        """
        Computes robust statistical metrics (Median, Mean, P25, P75, IQR)
        for EV/EBITDA and EV/Revenue by sector.
        """
        df = self.db.get_all_deals_df()
        if df.empty:
            logger.warning("No deal records available for multiples calculation.")
            return pd.DataFrame()

        # Filter valid positive multiples
        valid_ebitda = df[df["ev_to_ebitda_multiple"].notnull() & (df["ev_to_ebitda_multiple"] > 0)]

        summary = valid_ebitda.groupby("sector_name").agg(
            total_deals=("deal_id", "count"),
            median_ev_ebitda=("ev_to_ebitda_multiple", "median"),
            mean_ev_ebitda=("ev_to_ebitda_multiple", "mean"),
            p25_ev_ebitda=("ev_to_ebitda_multiple", lambda x: np.percentile(x, 25)),
            p75_ev_ebitda=("ev_to_ebitda_multiple", lambda x: np.percentile(x, 75)),
            median_ev_rev=("ev_to_revenue_multiple", "median"),
            mean_ev_rev=("ev_to_revenue_multiple", "mean"),
            total_volume_usd_m=("deal_value_usd", "sum"),
        ).reset_index()

        summary["iqr_ebitda"] = summary["p75_ev_ebitda"] - summary["p25_ev_ebitda"]
        return summary.round(2)

    def detect_multiple_outliers(self, threshold_std: float = 2.0) -> pd.DataFrame:
        """
        Flags M&A deals where valuation multiples deviate significantly from sector norms.
        Essential for investment banking due diligence and screening.
        """
        df = self.db.get_all_deals_df()
        if df.empty:
            return pd.DataFrame()

        df_filtered = df[df["ev_to_ebitda_multiple"].notnull()].copy()
        df_filtered["sector_mean"] = df_filtered.groupby("sector_name")["ev_to_ebitda_multiple"].transform("mean")
        df_filtered["sector_std"] = df_filtered.groupby("sector_name")["ev_to_ebitda_multiple"].transform("std").fillna(1.0)
        
        df_filtered["z_score"] = (
            (df_filtered["ev_to_ebitda_multiple"] - df_filtered["sector_mean"]) / df_filtered["sector_std"]
        ).abs()

        outliers = df_filtered[df_filtered["z_score"] > threshold_std]
        return outliers[["deal_id", "target_name", "acquirer_name", "sector_name", "ev_to_ebitda_multiple", "z_score"]]
