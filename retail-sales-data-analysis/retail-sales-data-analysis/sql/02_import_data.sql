-- ============================================
-- Retail Sales Data Analysis
-- File: sql/02_import_data.sql
-- Purpose: Import cleaned data from CSV into retail_sales table
-- Compatible: MySQL 8.0+ / MariaDB 10.5+ / SQLite 3.35+
-- ============================================
-- ============================================
-- NOTES
-- ============================================
-- SQLite does NOT support LOAD DATA / BULK INSERT directly.
-- For SQLite, use one of these methods instead:
--   1. Python (recommended):  pandas .to_sql() - already done in data_loader.py
--   2. SQLite CLI:            .import --csv --skip 1 file.csv table
--   3. sqlite3 module:        executemany() with CSV reader
--
-- This file provides:
--   - MySQL LOAD DATA method
--   - PostgreSQL COPY method (reference)
--   - SQLite .import method (reference)
--   - Verification queries
-- ============================================
-- ============================================
-- METHOD 1: MYSQL - LOAD DATA LOCAL INFILE
-- ============================================
-- Step 1: Enable local infile
-- Run this once per session:
SET GLOBAL local_infile = 1;
-- Step 2: Truncate table (fresh import)
TRUNCATE TABLE retail_sales;
-- Step 3: Load CSV file
-- Adjust path as needed (Windows uses forward slashes or double backslashes)
LOAD DATA LOCAL INFILE 'data/processed/retail_sales_clean.csv' INTO TABLE retail_sales FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES (
    order_id,
    order_date,
    customer_name,
    segment,
    region,
    state,
    city,
    product_name,
    category,
    quantity,
    unit_price,
    discount,
    sales,
    profit,
    payment_mode,
    year,
    month,
    month_name,
    quarter,
    weekday,
    year_month,
    profit_margin,
    revenue_per_unit,
    profit_per_unit,
    discount_amount,
    discount_band,
    profit_status,
    order_size,
    is_weekend,
    season,
    quarter_label,
    customer_type
)
SET order_date = STR_TO_DATE(@order_date, '%Y-%m-%d'),
    is_weekend = CASE
        WHEN @is_weekend IN ('True', '1', 'true') THEN 1
        ELSE 0
    END;
-- Step 4: Verify row count
SELECT COUNT(*) AS total_rows
FROM retail_sales;
-- ============================================
-- METHOD 2: MYSQL - LOAD DATA (server-side path)
-- ============================================
-- Use this if LOCAL INFILE is disabled.
-- File must be placed in MySQL server's secure_file_priv directory.
--
-- LOAD DATA INFILE '/var/lib/mysql-files/retail_sales_clean.csv'
-- INTO TABLE retail_sales
-- FIELDS TERMINATED BY ','
-- OPTIONALLY ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 LINES;
--
-- SHOW VARIABLES LIKE 'secure_file_priv';
-- ============================================
-- METHOD 3: POSTGRESQL - COPY (reference)
-- ============================================
-- PostgreSQL has native COPY support for CSV.
--
-- TRUNCATE TABLE retail_sales;
--
-- COPY retail_sales (
--     order_id, order_date, customer_name, segment, region, state,
--     city, product_name, category, quantity, unit_price, discount,
--     sales, profit, payment_mode, year, month, month_name, quarter,
--     weekday, year_month, profit_margin, revenue_per_unit,
--     profit_per_unit, discount_amount, discount_band, profit_status,
--     order_size, is_weekend, season, quarter_label, customer_type
-- )
-- FROM '/absolute/path/to/retail_sales_clean.csv'
-- WITH (
--     FORMAT CSV,
--     HEADER TRUE,
--     DELIMITER ',',
--     QUOTE '"'
-- );
--
-- SELECT COUNT(*) FROM retail_sales;
-- ============================================
-- METHOD 4: SQLITE - CLI IMPORT (reference)
-- ============================================
-- SQLite uses the .import command from its CLI tool.
--
-- Steps:
--   1. Open database:
--        sqlite3 retail_sales.db
--   2. Set CSV mode:
--        .mode csv
--   3. Skip header row:
--        .headers on
--   4. Import:
--        .import --csv --skip 1 data/processed/retail_sales_clean.csv retail_sales
--   5. Verify:
--        SELECT COUNT(*) FROM retail_sales;
--   6. Exit:
--        .quit
--
-- IMPORTANT:
-- SQLite's .import command maps columns by position.
-- Column order in the CSV MUST match the table column order
-- (excluding 'id' and 'created_at' which have defaults).
-- ============================================
-- METHOD 5: PYTHON (already implemented)
-- ============================================
-- Refer to src/data_loader.py -> save_to_sql() for the Python method.
-- This is the recommended approach for SQLite.
--
-- Example usage:
--     from data_loader import load_csv, save_to_sql
--     df = load_csv("data/processed/retail_sales_clean.csv")
--     save_to_sql(df, table_name="retail_sales", if_exists="replace")
-- ============================================
-- POST-IMPORT VERIFICATION
-- ============================================
-- 1. Row count
SELECT COUNT(*) AS total_rows
FROM retail_sales;
-- 2. Distinct orders
SELECT COUNT(DISTINCT order_id) AS unique_orders
FROM retail_sales;
-- 3. Null check on critical columns
SELECT SUM(
        CASE
            WHEN order_id IS NULL THEN 1
            ELSE 0
        END
    ) AS null_order_id,
    SUM(
        CASE
            WHEN order_date IS NULL THEN 1
            ELSE 0
        END
    ) AS null_order_date,
    SUM(
        CASE
            WHEN sales IS NULL THEN 1
            ELSE 0
        END
    ) AS null_sales,
    SUM(
        CASE
            WHEN profit IS NULL THEN 1
            ELSE 0
        END
    ) AS null_profit
FROM retail_sales;
-- 4. Date range
SELECT MIN(order_date) AS earliest_date,
    MAX(order_date) AS latest_date
FROM retail_sales;
-- 5. Category breakdown
SELECT category,
    COUNT(*) AS row_count
FROM retail_sales
GROUP BY category
ORDER BY row_count DESC;
-- 6. Region breakdown
SELECT region,
    COUNT(*) AS row_count
FROM retail_sales
GROUP BY region
ORDER BY row_count DESC;
-- 7. Total sales / profit after import
SELECT ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales;
-- 8. Sample rows
SELECT order_id,
    order_date,
    region,
    category,
    sales,
    profit
FROM retail_sales
LIMIT 10;
-- ============================================
-- POPULATE SUMMARY TABLES (run after main import)
-- ============================================
-- Category summary
INSERT INTO category_summary (
        category,
        total_sales,
        total_profit,
        total_orders,
        total_quantity,
        avg_discount,
        profit_margin_pct
    )
SELECT category,
    ROUND(SUM(sales), 2),
    ROUND(SUM(profit), 2),
    COUNT(DISTINCT order_id),
    SUM(quantity),
    ROUND(AVG(discount), 2),
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2)
FROM retail_sales
GROUP BY category;
-- Region summary
INSERT INTO region_summary (
        region,
        total_sales,
        total_profit,
        total_orders,
        total_quantity,
        avg_discount,
        profit_margin_pct
    )
SELECT region,
    ROUND(SUM(sales), 2),
    ROUND(SUM(profit), 2),
    COUNT(DISTINCT order_id),
    SUM(quantity),
    ROUND(AVG(discount), 2),
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2)
FROM retail_sales
GROUP BY region;
-- Monthly summary
INSERT INTO monthly_summary (
        year_month,
        total_sales,
        total_profit,
        total_orders,
        profit_margin_pct
    )
SELECT year_month,
    ROUND(SUM(sales), 2),
    ROUND(SUM(profit), 2),
    COUNT(DISTINCT order_id),
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2)
FROM retail_sales
GROUP BY year_month;
-- ============================================
-- FINAL VERIFICATION
-- ============================================
SELECT 'retail_sales' AS table_name,
    COUNT(*) AS rows
FROM retail_sales
UNION ALL
SELECT 'category_summary' AS table_name,
    COUNT(*) AS rows
FROM category_summary
UNION ALL
SELECT 'region_summary' AS table_name,
    COUNT(*) AS rows
FROM region_summary
UNION ALL
SELECT 'monthly_summary' AS table_name,
    COUNT(*) AS rows
FROM monthly_summary;
-- ============================================
-- END OF FILE
-- ============================================