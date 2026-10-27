"""
DealPulse M&A Platform - Executive Intelligence Dashboard
Interactive visualization suite for Investment Banking deal sourcing, valuation benchmarking,
and sponsor activity tracking. Built with Streamlit and Plotly.
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.database.db_manager import DatabaseManager
from src.analytics.deal_multiples import ValuationAnalytics
from src.analytics.trends import MarketTrendsAnalytics
from src.analytics.polars_engine import PolarsValuationEngine
from src.pipeline.power_automate import PowerAutomateConnector

# Page configuration
st.set_page_config(
    page_title="DealPulse | M&A Intelligence Platform",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Investment Banking Dark / Navy Theme)
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Data loader
@st.cache_data(ttl=60)
def load_data():
    db = DatabaseManager()
    df = db.get_all_deals_df()
    return df

df = load_data()

# Header
st.markdown('<div class="main-header">DealPulse M&A Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated Mid-Market Deal Sourcing & Valuation Multiples Benchmark (UK, US & Europe)</div>', unsafe_allow_html=True)

if df.empty:
    st.warning("No data found in the database. Run `python scripts/seed_data.py` to populate realistic transactions.")
    st.stop()

# Sidebar Filters
st.sidebar.header("Filter Criteria")
all_sectors = ["All"] + sorted(df["sector_name"].dropna().unique().tolist())
selected_sector = st.sidebar.selectbox("Sector", all_sectors)

all_buyers = ["All"] + sorted(df["buyer_type"].dropna().unique().tolist())
selected_buyer = st.sidebar.selectbox("Buyer Type", all_buyers)

all_countries = ["All"] + sorted(df["target_country"].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Target Geography", all_countries)

# Apply Filters
filtered_df = df.copy()
if selected_sector != "All":
    filtered_df = filtered_df[filtered_df["sector_name"] == selected_sector]
if selected_buyer != "All":
    filtered_df = filtered_df[filtered_df["buyer_type"] == selected_buyer]
if selected_country != "All":
    filtered_df = filtered_df[filtered_df["target_country"] == selected_country]

# Top KPI Summary Cards
total_volume = filtered_df["deal_value_usd"].sum()
deal_count = len(filtered_df)
median_multiple = filtered_df["ev_to_ebitda_multiple"].median()
pe_share = (
    len(filtered_df[filtered_df["buyer_type"] == "Private Equity Sponsor"]) / deal_count * 100
) if deal_count > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Deal Volume", f"${total_volume:,.1f} M")
col2.metric("Tracked Transactions", f"{deal_count:,}")
col3.metric("Median EV/EBITDA Multiple", f"{median_multiple:.1f}x" if pd.notnull(median_multiple) else "N/A")
col4.metric("PE Sponsor Penetration", f"{pe_share:.1f}%")

st.markdown("---")

# Analytics Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Valuation Benchmarks",
    "💼 Capital Allocation",
    "🔍 Deal Screener",
    "⚡ Power Automate & M365",
    "🚀 Polars Performance Engine"
])

with tab1:
    st.subheader("Sector Valuation Multiples (EV / EBITDA)")
    col_chart1, col_chart2 = st.columns([3, 2])
    
    with col_chart1:
        # Boxplot of multiples by sector
        fig_box = px.box(
            filtered_df.dropna(subset=["ev_to_ebitda_multiple"]),
            x="sector_name",
            y="ev_to_ebitda_multiple",
            color="sector_name",
            title="EV / EBITDA Multiple Spread by Industry Sector",
            labels={"ev_to_ebitda_multiple": "EV / EBITDA (x)", "sector_name": "Sector"},
        )
        fig_box.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig_box, use_container_width=True)

    with col_chart2:
        # Scatter of Deal Size vs Multiple
        fig_scatter = px.scatter(
            filtered_df.dropna(subset=["ev_to_ebitda_multiple"]),
            x="deal_value_usd",
            y="ev_to_ebitda_multiple",
            color="buyer_type",
            size="deal_value_usd",
            hover_data=["target_name", "acquirer_name"],
            title="Transaction Size vs. Valuation Multiple",
            labels={"deal_value_usd": "Deal Value ($M)", "ev_to_ebitda_multiple": "EV/EBITDA (x)"},
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    st.subheader("Capital Deployment & Buyer Dynamics")
    c1, c2 = st.columns(2)
    
    with c1:
        # Capital by Buyer Type
        buyer_agg = filtered_df.groupby("buyer_type")["deal_value_usd"].sum().reset_index()
        fig_donut = px.pie(
            buyer_agg,
            names="buyer_type",
            values="deal_value_usd",
            hole=0.45,
            title="Capital Allocation: PE Sponsors vs Corporate Acquirers",
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        # Volume by Sector
        sector_agg = filtered_df.groupby("sector_name")["deal_value_usd"].sum().reset_index().sort_values(by="deal_value_usd")
        fig_bar = px.bar(
            sector_agg,
            x="deal_value_usd",
            y="sector_name",
            orientation="h",
            title="Total Transaction Volume by Sector ($M USD)",
            labels={"deal_value_usd": "Volume ($M)", "sector_name": "Sector"},
            color="deal_value_usd",
            color_continuous_scale="Blues",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

with tab3:
    st.subheader("Institutional M&A Deal Screener")
    st.dataframe(
        filtered_df[[
            "deal_announcement_date", "target_name", "acquirer_name", "sector_name",
            "buyer_type", "deal_value_usd", "ev_to_ebitda_multiple", "lead_advisor", "source_feed"
        ]].rename(columns={
            "deal_announcement_date": "Date",
            "target_name": "Target Company",
            "acquirer_name": "Acquirer / Sponsor",
            "sector_name": "Sector",
            "buyer_type": "Buyer Type",
            "deal_value_usd": "Deal Value ($M)",
            "ev_to_ebitda_multiple": "EV/EBITDA",
            "lead_advisor": "Lead Advisor",
            "source_feed": "Source Feed",
        }),
        use_container_width=True,
    )
    
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Filtered Deals (CSV for Power BI / Excel)",
        data=csv_data,
        file_name="dealpulse_curated_deals.csv",
        mime="text/csv",
    )

with tab4:
    st.subheader("⚡ Microsoft Power Automate & M365 Workflow Automation")
    st.markdown("""
    This module simulates enterprise process automation connecting DealPulse with **Microsoft Power Automate**,
    **SharePoint Lists**, and **Microsoft Teams**. It automatically filters high-value acquisitions ($75M+ or EV/EBITDA > 19x)
    and generates compliant **Adaptive Card JSON payloads** for executive notification channels.
    """)

    pa_connector = PowerAutomateConnector()
    deals_dict_list = filtered_df.to_dict(orient="records")
    marquee_deals = pa_connector.filter_marquee_deals(deals_dict_list)

    col_pa1, col_pa2 = st.columns([1, 1])

    with col_pa1:
        st.markdown(f"**Identified Marquee Alerts ({len(marquee_deals)} high-impact deals)**")
        if marquee_deals:
            selected_alert_deal = st.selectbox(
                "Select Transaction to Trigger Workflow Alert:",
                options=marquee_deals,
                format_func=lambda d: f"{d.get('target_name')} - ${d.get('deal_value_usd')}M ({d.get('buyer_type')})"
            )
            
            if st.button("🚀 Trigger Power Automate Webhook Simulation"):
                sim = pa_connector.dispatch_alert_simulation(selected_alert_deal)
                st.success(f"Webhook Triggered! Status: {sim['status']} -> Action: {sim['action']}")
                st.json(sim["payload"])
        else:
            st.info("No marquee deals matched the current filter threshold ($75M+).")

    with col_pa2:
        st.markdown("**SharePoint List Synchronization Feed**")
        st.write("Exports standardized JSON feed ready for Power Automate `Create item in SharePoint` flow.")
        if st.button("📁 Export SharePoint Import Feed"):
            sp_path = pa_connector.export_sharepoint_migration_feed(deals_dict_list)
            st.success(f"SharePoint List feed successfully generated at `{sp_path.name}`")
            with open(sp_path, "r", encoding="utf-8") as f:
                import json
                sample_sp = json.load(f)[:2]
            st.json(sample_sp)

with tab5:
    st.subheader("🚀 High-Performance Polars Analytics Engine")
    st.markdown("""
    **Apache Arrow & Vectorized Processing:** Benchmarks sub-millisecond aggregations using Polars LazyFrames
    vs. conventional Pandas. Designed to handle institutional datasets with zero-copy memory efficiency.
    """)

    db_m = DatabaseManager()
    polars_engine = PolarsValuationEngine(db_m)

    col_bench1, col_bench2 = st.columns([1, 1])

    with col_bench1:
        st.markdown("**Real-Time Engine Benchmark**")
        if st.button("⚡ Run Polars vs Pandas Benchmark"):
            bench = polars_engine.benchmark_pandas_vs_polars()
            st.metric("Pandas Latency", f"{bench['pandas_ms']} ms")
            st.metric("Polars Latency", f"{bench['polars_ms']} ms", delta=bench['speedup_factor'])
            st.info(f"Polars processed {bench['record_count']} deal rows with vectorized execution: **{bench['speedup_factor']}**")

    with col_bench2:
        st.markdown("**Polars Computed Sector Benchmarks (Median, P25, P75)**")
        pldf = polars_engine.compute_sector_benchmarks_polars()
        st.dataframe(pldf.to_pandas(), use_container_width=True)
