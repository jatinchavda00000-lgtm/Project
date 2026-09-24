-- ============================================
-- Retail Sales Data Analysis
-- File: sql/01_create_table.sql
-- Purpose: Create retail_sales table + related tables
-- Compatible: MySQL 8.0+ / MariaDB 10.5+ / SQLite 3.35+
-- ============================================
-- ============================================
-- 1. DATABASE CREATE (MySQL only - SQLite me skip)
-- ============================================
-- Uncomment below lines if using MySQL:
-- CREATE DATABASE IF NOT EXISTS retail_sales_db
--     CHARACTER SET utf8mb4
--     COLLATE utf8mb4_unicode_ci;
-- USE retail_sales_db;
-- ============================================
-- 2. DROP EXISTING TABLES (clean slate)
-- ============================================
DROP TABLE IF EXISTS retail_sales;
DROP TABLE IF EXISTS category_summary;
DROP TABLE IF EXISTS region_summary;
DROP TABLE IF EXISTS monthly_summary;
-- ============================================
-- 3. MAIN TABLE: retail_sales
-- ============================================
CREATE TABLE retail_sales (
    -- Primary key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- MySQL users: change above line to:
    -- id                   INT AUTO_INCREMENT PRIMARY KEY,
    -- Original raw columns
    order_id VARCHAR(50) NOT NULL,
    order_date DATE NOT NULL,
    customer_name VARCHAR(150),
    segment VARCHAR(50),
    region VARCHAR(50),
    state VARCHAR(100),
    city VARCHAR(100),
    product_name VARCHAR(200),
    category VARCHAR(100),
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(12, 2) DEFAULT 0.00,
    discount DECIMAL(5, 2) DEFAULT 0.00,
    sales DECIMAL(14, 2) NOT NULL,
    profit DECIMAL(14, 2) DEFAULT 0.00,
    payment_mode VARCHAR(50),
    -- Date-derived features
    year INTEGER,
    month INTEGER,
    month_name VARCHAR(10),
    quarter INTEGER,
    weekday VARCHAR(15),
    year_month VARCHAR(10),
    -- Engineered features
    profit_margin DECIMAL(8, 2) DEFAULT 0.00,
    revenue_per_unit DECIMAL(12, 2) DEFAULT 0.00,
    profit_per_unit DECIMAL(12, 2) DEFAULT 0.00,
    discount_amount DECIMAL(14, 2) DEFAULT 0.00,
    discount_band VARCHAR(20),
    profit_status VARCHAR(20),
    order_size VARCHAR(20),
    is_weekend BOOLEAN DEFAULT 0,
    season VARCHAR(20),
    quarter_label VARCHAR(5),
    customer_type VARCHAR(20),
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ============================================
-- 4. INDEXES (for faster query performance)
-- ============================================
CREATE INDEX idx_order_id ON retail_sales(order_id);
CREATE INDEX idx_order_date ON retail_sales(order_date);
CREATE INDEX idx_region ON retail_sales(region);
CREATE INDEX idx_category ON retail_sales(category);
CREATE INDEX idx_segment ON retail_sales(segment);
CREATE INDEX idx_product_name ON retail_sales(product_name);
CREATE INDEX idx_customer_name ON retail_sales(customer_name);
CREATE INDEX idx_payment_mode ON retail_sales(payment_mode);
CREATE INDEX idx_year_month ON retail_sales(year_month);
CREATE INDEX idx_profit_status ON retail_sales(profit_status);
CREATE INDEX idx_discount_band ON retail_sales(discount_band);
-- ============================================
-- 5. SUMMARY TABLE: category_summary
-- ============================================
CREATE TABLE category_summary (
    category VARCHAR(100) PRIMARY KEY,
    total_sales DECIMAL(18, 2) DEFAULT 0.00,
    total_profit DECIMAL(18, 2) DEFAULT 0.00,
    total_orders INTEGER DEFAULT 0,
    total_quantity INTEGER DEFAULT 0,
    avg_discount DECIMAL(6, 2) DEFAULT 0.00,
    profit_margin_pct DECIMAL(8, 2) DEFAULT 0.00,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ============================================
-- 6. SUMMARY TABLE: region_summary
-- ============================================
CREATE TABLE region_summary (
    region VARCHAR(50) PRIMARY KEY,
    total_sales DECIMAL(18, 2) DEFAULT 0.00,
    total_profit DECIMAL(18, 2) DEFAULT 0.00,
    total_orders INTEGER DEFAULT 0,
    total_quantity INTEGER DEFAULT 0,
    avg_discount DECIMAL(6, 2) DEFAULT 0.00,
    profit_margin_pct DECIMAL(8, 2) DEFAULT 0.00,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ============================================
-- 7. SUMMARY TABLE: monthly_summary
-- ============================================
CREATE TABLE monthly_summary (
    year_month VARCHAR(10) PRIMARY KEY,
    total_sales DECIMAL(18, 2) DEFAULT 0.00,
    total_profit DECIMAL(18, 2) DEFAULT 0.00,
    total_orders INTEGER DEFAULT 0,
    profit_margin_pct DECIMAL(8, 2) DEFAULT 0.00,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ============================================
-- 8. VERIFY TABLES
-- ============================================
-- SQLite:
SELECT name
FROM sqlite_master
WHERE type = 'table';
-- MySQL:
-- SHOW TABLES;
-- ============================================
-- 9. VERIFY STRUCTURE
-- ============================================
-- SQLite:
PRAGMA table_info(retail_sales);
-- MySQL:
-- DESCRIBE retail_sales;
-- ============================================
-- END OF FILE
-- ============================================