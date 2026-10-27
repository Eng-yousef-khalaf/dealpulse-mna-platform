"""
DealPulse M&A Platform - High-Performance Polars Analytics Engine
Leverages Apache Arrow memory model via Polars for sub-millisecond aggregations,
percentile benchmarking, and fast vector calculations on transaction datasets.
"""
import time
from typing import Dict, Any, Tuple
import polars as pl
import pandas as pd

from src.database.db_manager import DatabaseManager
from src.config import get_logger

logger = get_logger("PolarsEngine")

class PolarsValuationEngine:
    """High-speed Polars analytics engine for M&A deal benchmarking."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def load_deals_lazy(self) -> pl.LazyFrame:
        """Loads SQLite deal data into a Polars LazyFrame for optimized query planning."""
        pdf = self.db.get_all_deals_df()
        if pdf.empty:
            return pl.LazyFrame()
        return pl.from_pandas(pdf).lazy()

    def compute_sector_benchmarks_polars(self) -> pl.DataFrame:
        """
        Computes sector percentiles and multiples using Polars native expressions.
        Demonstrates vectorized 25th, 50th (median), and 75th percentile calculations.
        """
        lf = self.load_deals_lazy()
        
        benchmarks = (
            lf.filter(pl.col("ev_to_ebitda_multiple").is_not_null() & (pl.col("ev_to_ebitda_multiple") > 0))
            .group_by("sector_name")
            .agg([
                pl.len().alias("deal_count"),
                pl.col("ev_to_ebitda_multiple").median().round(2).alias("median_ev_ebitda"),
                pl.col("ev_to_ebitda_multiple").mean().round(2).alias("mean_ev_ebitda"),
                pl.col("ev_to_ebitda_multiple").quantile(0.25).round(2).alias("p25_ev_ebitda"),
                pl.col("ev_to_ebitda_multiple").quantile(0.75).round(2).alias("p75_ev_ebitda"),
                pl.col("deal_value_usd").sum().round(1).alias("total_capital_usd_m"),
                pl.col("ev_to_revenue_multiple").median().round(2).alias("median_ev_rev")
            ])
            .with_columns([
                (pl.col("p75_ev_ebitda") - pl.col("p25_ev_ebitda")).round(2).alias("iqr_ebitda")
            ])
            .sort("total_capital_usd_m", descending=True)
            .collect()
        )
        return benchmarks

    def benchmark_pandas_vs_polars(self) -> Dict[str, Any]:
        """
        Executes identical aggregation benchmarks across Pandas and Polars
        to measure speedup and throughput.
        """
        pdf = self.db.get_all_deals_df()
        if pdf.empty:
            return {"status": "no_data"}

        # Measure Pandas
        start_pandas = time.perf_counter()
        _ = (
            pdf.dropna(subset=["ev_to_ebitda_multiple"])
            .groupby("sector_name")
            .agg(
                median=("ev_to_ebitda_multiple", "median"),
                mean=("ev_to_ebitda_multiple", "mean"),
                total_vol=("deal_value_usd", "sum")
            )
        )
        pandas_duration_ms = (time.perf_counter() - start_pandas) * 1000

        # Measure Polars
        pldf = pl.from_pandas(pdf)
        start_polars = time.perf_counter()
        _ = (
            pldf.filter(pl.col("ev_to_ebitda_multiple").is_not_null())
            .group_by("sector_name")
            .agg([
                pl.col("ev_to_ebitda_multiple").median().alias("median_multiple"),
                pl.col("ev_to_ebitda_multiple").mean().alias("mean_multiple"),
                pl.col("deal_value_usd").sum().alias("total_deal_vol")
            ])
        )
        polars_duration_ms = (time.perf_counter() - start_polars) * 1000

        speedup = (pandas_duration_ms / polars_duration_ms) if polars_duration_ms > 0 else 1.0

        return {
            "record_count": len(pdf),
            "pandas_ms": round(pandas_duration_ms, 3),
            "polars_ms": round(polars_duration_ms, 3),
            "speedup_factor": f"{round(speedup, 1)}x faster"
        }
