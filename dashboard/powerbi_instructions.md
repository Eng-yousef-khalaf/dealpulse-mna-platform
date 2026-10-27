# Power BI Implementation Guide: DealPulse M&A Intelligence

This guide provides instructions to connect Microsoft Power BI to the **DealPulse M&A Platform** database or curated feeds, configure the Star Schema relationships, and apply institutional-grade DAX measures.

---

## 1. Connecting Data Sources in Power BI Desktop

### Option A: Direct SQLite / ODBC Connection
1. In Power BI Desktop, click **Get Data** > **ODBC** or **Blank Query**.
2. Point the connection string to `data/dealpulse_mna.db`.
3. Import the tables: `fact_mna_deals`, `dim_companies`, `dim_sectors`, and `dim_advisors`.

### Option B: Curated Star-Schema CSV Feeds (Fastest)
1. Run `python dashboard/export_powerbi_data.py`.
2. In Power BI Desktop, click **Get Data** > **Text/CSV**.
3. Load `data/exports/powerbi_deals_feed.csv`.

---

## 2. Dimensional Data Model (Relationships)

In the **Model View**, verify or configure the following 1-to-Many (`1:*`) single-direction relationships:

- `dim_sectors[sector_id]` (1) ───< (Many) `fact_mna_deals[sector_id]`
- `dim_companies[company_id]` (1) ───< (Many) `fact_mna_deals[target_company_id]`
- `dim_companies[company_id]` (1) ───< (Many) `fact_mna_deals[acquirer_company_id]`
- `dim_advisors[advisor_id]` (1) ───< (Many) `fact_mna_deals[lead_advisor_id]`

---

## 3. Core DAX Measures for Investment Banking Analytics

Create a dedicated measure table called `_M&A Measures` and paste the following DAX calculations:

### 1. Total Capital Deployed (USD Millions)
```dax
Total Deal Volume USD = 
SUM(fact_mna_deals[deal_value_usd])
```

### 2. Transaction Count
```dax
Total Deals Count = 
COUNTROWS(fact_mna_deals)
```

### 3. Median EV / EBITDA Valuation Multiple
```dax
Median EV to EBITDA = 
MEDIAN(fact_mna_deals[ev_to_ebitda_multiple])
```

### 4. Average Deal Size
```dax
Avg Deal Size USD = 
DIVIDE([Total Deal Volume USD], [Total Deals Count], 0)
```

### 5. Private Equity Penetration Rate (%)
```dax
PE Sponsor Market Share % = 
DIVIDE(
    CALCULATE([Total Deal Volume USD], fact_mna_deals[buyer_type] = "Private Equity Sponsor"),
    [Total Deal Volume USD],
    0
) * 100
```

### 6. Cross-Border Deal Ratio (%)
```dax
Cross Border Deal % = 
DIVIDE(
    CALCULATE(
        [Total Deals Count], 
        RELATED(TargetCompany[headquarters_country]) <> RELATED(AcquirerCompany[headquarters_country])
    ),
    [Total Deals Count],
    0
) * 100
```

---

## 4. Recommended Dashboard Layout

1. **Executive KPI Ribbon (Top)**:
   - 4 Card Visuals: `Total Deal Volume ($M)`, `Total Transactions`, `Median EV/EBITDA`, `PE Sponsor Share %`.
2. **Left Panel (Valuation Benchmark)**:
   - Clustered Bar Chart: `Median EV to EBITDA` by `dim_sectors[sector_name]`.
3. **Center Panel (Capital Allocation)**:
   - Donut Chart: `Total Deal Volume USD` by `buyer_type` (PE vs Corporate Strategic).
4. **Bottom Matrix (Deal League Table)**:
   - Columns: Target, Acquirer, Sector, Value ($M), EV/EBITDA multiple, Lead Advisor.
5. **Interactive Slicers**:
   - Date Hierarchy, Industry Sector, Buyer Type, Target Country.
