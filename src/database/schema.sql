-- ==============================================================================
-- DealPulse M&A Intelligence Platform
-- Relational Star Schema for Investment Banking Deal Tracking & Valuation Multiples
-- Designed for SQLite & PostgreSQL compatibility
-- ==============================================================================

-- Drop tables if needed (Clean rebuild)
DROP TABLE IF EXISTS fact_mna_deals;
DROP TABLE IF EXISTS dim_advisors;
DROP TABLE IF EXISTS dim_sectors;
DROP TABLE IF EXISTS dim_companies;

-- ------------------------------------------------------------------------------
-- 1. Dimension: Companies (Targets, Acquirers, PE Sponsors)
-- ------------------------------------------------------------------------------
CREATE TABLE dim_companies (
    company_id VARCHAR(64) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    ticker VARCHAR(16),
    headquarters_country VARCHAR(64) NOT NULL,
    headquarters_city VARCHAR(128),
    founded_year INTEGER,
    ownership_type VARCHAR(64) CHECK (ownership_type IN ('Public', 'Private', 'PE-Backed', 'VC-Backed', 'Subsidiary')),
    employee_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_companies_name ON dim_companies(company_name);
CREATE INDEX idx_dim_companies_country ON dim_companies(headquarters_country);

-- ------------------------------------------------------------------------------
-- 2. Dimension: Sectors & Industry Classification
-- ------------------------------------------------------------------------------
CREATE TABLE dim_sectors (
    sector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_name VARCHAR(128) NOT NULL UNIQUE,
    sub_industry VARCHAR(128),
    description TEXT
);

-- ------------------------------------------------------------------------------
-- 3. Dimension: Financial & Legal Advisors (League Table Tracking)
-- ------------------------------------------------------------------------------
CREATE TABLE dim_advisors (
    advisor_id VARCHAR(64) PRIMARY KEY,
    advisor_name VARCHAR(255) NOT NULL UNIQUE,
    advisor_type VARCHAR(64) CHECK (advisor_type IN ('Investment Bank', 'Legal Counsel', 'Due Diligence / Big 4', 'Boutique Advisor')),
    headquarters_country VARCHAR(64)
);

-- ------------------------------------------------------------------------------
-- 4. Fact Table: M&A Transactions & Financial Deal Metrics
-- ------------------------------------------------------------------------------
CREATE TABLE fact_mna_deals (
    deal_id VARCHAR(64) PRIMARY KEY,
    deal_announcement_date DATE NOT NULL,
    deal_completion_date DATE,
    target_company_id VARCHAR(64) NOT NULL,
    acquirer_company_id VARCHAR(64) NOT NULL,
    sector_id INTEGER NOT NULL,
    lead_advisor_id VARCHAR(64),
    
    deal_type VARCHAR(64) NOT NULL,
    buyer_type VARCHAR(64) NOT NULL,
    deal_status VARCHAR(32) NOT NULL DEFAULT 'Announced' CHECK (deal_status IN ('Announced', 'Completed', 'Pending Regulatory Approval', 'Terminated')),
    
    -- Financial Deal Metrics & Valuations
    deal_currency VARCHAR(8) NOT NULL DEFAULT 'USD',
    deal_value_native REAL NOT NULL,
    deal_value_usd REAL NOT NULL,
    target_revenue_usd REAL,
    target_ebitda_usd REAL,
    ev_to_revenue_multiple REAL,
    ev_to_ebitda_multiple REAL,
    stake_percentage_acquired REAL DEFAULT 100.0,
    
    -- Metadata, Auditing & Lineage
    source_feed VARCHAR(128) NOT NULL,
    source_reference_url TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (target_company_id) REFERENCES dim_companies(company_id),
    FOREIGN KEY (acquirer_company_id) REFERENCES dim_companies(company_id),
    FOREIGN KEY (sector_id) REFERENCES dim_sectors(sector_id),
    FOREIGN KEY (lead_advisor_id) REFERENCES dim_advisors(advisor_id)
);

CREATE INDEX idx_fact_deals_date ON fact_mna_deals(deal_announcement_date);
CREATE INDEX idx_fact_deals_sector ON fact_mna_deals(sector_id);
CREATE INDEX idx_fact_deals_acquirer ON fact_mna_deals(acquirer_company_id);
CREATE INDEX idx_fact_deals_target ON fact_mna_deals(target_company_id);
CREATE INDEX idx_fact_deals_buyer_type ON fact_mna_deals(buyer_type);

-- ------------------------------------------------------------------------------
-- Analytics Views for Executive M&A Reporting & Power BI Ingestion
-- ------------------------------------------------------------------------------

-- View 1: Sector Valuation Multiples & Capital Deployment
CREATE VIEW v_sector_valuation_benchmarks AS
SELECT 
    s.sector_name,
    COUNT(f.deal_id) AS total_deals_count,
    ROUND(SUM(f.deal_value_usd), 2) AS total_deal_value_usd_m,
    ROUND(AVG(f.deal_value_usd), 2) AS avg_deal_size_usd_m,
    ROUND(AVG(f.ev_to_ebitda_multiple), 2) AS avg_ev_ebitda_multiple,
    ROUND(AVG(f.ev_to_revenue_multiple), 2) AS avg_ev_revenue_multiple
FROM fact_mna_deals f
JOIN dim_sectors s ON f.sector_id = s.sector_id
WHERE f.deal_status IN ('Announced', 'Completed')
GROUP BY s.sector_name;

-- View 2: Private Equity vs Corporate Strategic Buyers Breakdown
CREATE VIEW v_buyer_strategy_comparison AS
SELECT 
    f.buyer_type,
    strftime('%Y-%m', f.deal_announcement_date) AS deal_month,
    COUNT(f.deal_id) AS deal_count,
    ROUND(SUM(f.deal_value_usd), 2) AS total_capital_deployed_usd_m,
    ROUND(AVG(f.ev_to_ebitda_multiple), 2) AS avg_ebitda_multiple
FROM fact_mna_deals f
GROUP BY f.buyer_type, strftime('%Y-%m', f.deal_announcement_date);

-- View 3: Investment Banking Advisor League Table
CREATE VIEW v_advisor_league_table AS
SELECT 
    a.advisor_name,
    a.advisor_type,
    COUNT(f.deal_id) AS advised_deals_count,
    ROUND(SUM(f.deal_value_usd), 2) AS total_advised_volume_usd_m
FROM fact_mna_deals f
JOIN dim_advisors a ON f.lead_advisor_id = a.advisor_id
GROUP BY a.advisor_name, a.advisor_type
ORDER BY total_advised_volume_usd_m DESC;
