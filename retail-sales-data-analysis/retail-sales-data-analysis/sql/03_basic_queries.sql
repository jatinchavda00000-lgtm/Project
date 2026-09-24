-- ============================================
-- Retail Sales Data Analysis
-- File: sql/03_basic_queries.sql
-- Purpose: Basic queries - totals, KPIs, simple aggregations
-- Compatible: MySQL 8.0+ / MariaDB 10.5+ / SQLite 3.35+
-- ============================================
-- ============================================
-- 1. ROW COUNT
-- ============================================
-- 1.1 Total rows in main table
SELECT COUNT(*) AS total_rows
FROM retail_sales;
-- 1.2 Total distinct orders
SELECT COUNT(DISTINCT order_id) AS unique_orders
FROM retail_sales;
-- 1.3 Total distinct customers
SELECT COUNT(DISTINCT customer_name) AS unique_customers
FROM retail_sales;
-- 1.4 Total distinct products
SELECT COUNT(DISTINCT product_name) AS unique_products
FROM retail_sales;
-- 1.5 Distinct regions / categories / segments
SELECT COUNT(DISTINCT region) AS unique_regions
FROM retail_sales;
SELECT COUNT(DISTINCT category) AS unique_categories
FROM retail_sales;
SELECT COUNT(DISTINCT segment) AS unique_segments
FROM retail_sales;
-- ============================================
-- 2. HEADLINE KPIs
-- ============================================
-- 2.1 Total sales, profit, quantity, discount
SELECT ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity,
    ROUND(AVG(discount), 2) AS avg_discount_pct,
    ROUND(SUM(discount_amount), 2) AS total_discount_given
FROM retail_sales;
-- 2.2 Orders and average order value
SELECT COUNT(DISTINCT order_id) AS total_orders,
    ROUND(
        SUM(sales) / NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ) AS avg_order_value
FROM retail_sales;
-- 2.3 Profit margin (overall)
SELECT ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct
FROM retail_sales;
-- 2.4 Combined KPI dashboard (single row)
SELECT COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_name) AS total_customers,
    COUNT(DISTINCT product_name) AS total_products,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(discount), 2) AS avg_discount,
    ROUND(
        SUM(sales) / NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ) AS avg_order_value,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct
FROM retail_sales;
-- ============================================
-- 3. DATE RANGE
-- ============================================
-- 3.1 Earliest and latest order
SELECT MIN(order_date) AS first_order,
    MAX(order_date) AS last_order
FROM retail_sales;
-- 3.2 Number of distinct years / months
SELECT COUNT(DISTINCT year) AS total_years,
    COUNT(DISTINCT year_month) AS total_months
FROM retail_sales;
-- 3.3 First and last year
SELECT MIN(year) AS first_year,
    MAX(year) AS last_year
FROM retail_sales;
-- ============================================
-- 4. DISTINCT VALUES (lookup lists)
-- ============================================
-- 4.1 All regions
SELECT DISTINCT region
FROM retail_sales
ORDER BY region;
-- 4.2 All categories
SELECT DISTINCT category
FROM retail_sales
ORDER BY category;
-- 4.3 All segments
SELECT DISTINCT segment
FROM retail_sales
ORDER BY segment;
-- 4.4 All payment modes
SELECT DISTINCT payment_mode
FROM retail_sales
ORDER BY payment_mode;
-- 4.5 All discount bands
SELECT DISTINCT discount_band
FROM retail_sales
ORDER BY discount_band;
-- 4.6 All profit statuses
SELECT DISTINCT profit_status
FROM retail_sales
ORDER BY profit_status;
-- 4.7 All seasons
SELECT DISTINCT season
FROM retail_sales
ORDER BY season;
-- ============================================
-- 5. SIMPLE GROUP-BY COUNTS
-- ============================================
-- 5.1 Orders per region
SELECT region,
    COUNT(DISTINCT order_id) AS total_orders
FROM retail_sales
GROUP BY region
ORDER BY total_orders DESC;
-- 5.2 Orders per category
SELECT category,
    COUNT(DISTINCT order_id) AS total_orders
FROM retail_sales
GROUP BY category
ORDER BY total_orders DESC;
-- 5.3 Orders per segment
SELECT segment,
    COUNT(DISTINCT order_id) AS total_orders
FROM retail_sales
GROUP BY segment
ORDER BY total_orders DESC;
-- 5.4 Orders per payment mode
SELECT payment_mode,
    COUNT(DISTINCT order_id) AS total_orders
FROM retail_sales
GROUP BY payment_mode
ORDER BY total_orders DESC;
-- 5.5 Orders per year
SELECT year,
    COUNT(DISTINCT order_id) AS total_orders
FROM retail_sales
GROUP BY year
ORDER BY year;
-- 5.6 Orders per month (all years combined)
SELECT month,
    month_name,
    COUNT(DISTINCT order_id) AS total_orders
FROM retail_sales
GROUP BY month,
    month_name
ORDER BY month;
-- 5.7 Orders per weekday
SELECT weekday,
    COUNT(DISTINCT order_id) AS total_orders
FROM retail_sales
GROUP BY weekday
ORDER BY total_orders DESC;
-- ============================================
-- 6. SIMPLE AGGREGATIONS BY DIMENSION
-- ============================================
-- 6.1 Sales and profit by region
SELECT region,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY region
ORDER BY total_sales DESC;
-- 6.2 Sales and profit by category
SELECT category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY category
ORDER BY total_sales DESC;
-- 6.3 Sales and profit by segment
SELECT segment,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY segment
ORDER BY total_sales DESC;
-- 6.4 Sales and profit by payment mode
SELECT payment_mode,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY payment_mode
ORDER BY total_sales DESC;
-- 6.5 Sales and profit by year
SELECT year,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY year
ORDER BY year;
-- 6.6 Sales and profit by year-month
SELECT year_month,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY year_month
ORDER BY year_month;
-- 6.7 Sales and profit by quarter
SELECT year,
    quarter,
    quarter_label,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY year,
    quarter,
    quarter_label
ORDER BY year,
    quarter;
-- 6.8 Sales and profit by season
SELECT season,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY season
ORDER BY total_sales DESC;
-- ============================================
-- 7. AVG METRICS BY DIMENSION
-- ============================================
-- 7.1 Average sales per order by region
SELECT region,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(
        SUM(sales) / NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ) AS avg_order_value
FROM retail_sales
GROUP BY region
ORDER BY avg_order_value DESC;
-- 7.2 Average profit per order by category
SELECT category,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(
        SUM(profit) / NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ) AS avg_profit_per_order
FROM retail_sales
GROUP BY category
ORDER BY avg_profit_per_order DESC;
-- 7.3 Average discount by region
SELECT region,
    ROUND(AVG(discount), 2) AS avg_discount_pct
FROM retail_sales
GROUP BY region
ORDER BY avg_discount_pct DESC;
-- 7.4 Average discount by category
SELECT category,
    ROUND(AVG(discount), 2) AS avg_discount_pct
FROM retail_sales
GROUP BY category
ORDER BY avg_discount_pct DESC;
-- 7.5 Average quantity per order by segment
SELECT segment,
    ROUND(AVG(quantity), 2) AS avg_quantity_per_row
FROM retail_sales
GROUP BY segment
ORDER BY avg_quantity_per_row DESC;
-- ============================================
-- 8. PROFIT STATUS DISTRIBUTION
-- ============================================
-- 8.1 Profit / Loss / Break-even counts
SELECT profit_status,
    COUNT(*) AS row_count,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY profit_status
ORDER BY order_count DESC;
-- 8.2 Profit status share (%)
SELECT profit_status,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(
        COUNT(DISTINCT order_id) * 100.0 / (
            SELECT COUNT(DISTINCT order_id)
            FROM retail_sales
        ),
        2
    ) AS pct_of_orders
FROM retail_sales
GROUP BY profit_status
ORDER BY orders DESC;
-- ============================================
-- 9. DISCOUNT BAND DISTRIBUTION
-- ============================================
-- 9.1 Orders per discount band
SELECT discount_band,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(discount), 2) AS avg_discount
FROM retail_sales
GROUP BY discount_band
ORDER BY CASE
        discount_band
        WHEN 'No Discount' THEN 1
        WHEN 'Low' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'High' THEN 4
        WHEN 'Very High' THEN 5
        ELSE 6
    END;
-- ============================================
-- 10. ORDER SIZE DISTRIBUTION
-- ============================================
SELECT order_size,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(AVG(quantity), 2) AS avg_quantity,
    ROUND(SUM(sales), 2) AS total_sales
FROM retail_sales
GROUP BY order_size
ORDER BY CASE
        order_size
        WHEN 'Small' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Large' THEN 3
        WHEN 'Bulk' THEN 4
        ELSE 5
    END;
-- ============================================
-- 11. WEEKDAY VS WEEKEND
-- ============================================
SELECT CASE
        WHEN is_weekend = 1 THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(sales), 2) AS avg_sales_per_row
FROM retail_sales
GROUP BY is_weekend
ORDER BY orders DESC;
-- ============================================
-- 12. CUSTOMER TYPE DISTRIBUTION
-- ============================================
SELECT customer_type,
    COUNT(DISTINCT customer_name) AS customers,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY customer_type
ORDER BY total_sales DESC;
-- ============================================
-- 13. TOP / BOTTOM SINGLE RECORDS
-- ============================================
-- 13.1 Top 10 highest sales rows
SELECT order_id,
    order_date,
    customer_name,
    product_name,
    category,
    region,
    sales,
    profit
FROM retail_sales
ORDER BY sales DESC
LIMIT 10;
-- 13.2 Top 10 highest profit rows
SELECT order_id,
    order_date,
    product_name,
    category,
    region,
    sales,
    profit
FROM retail_sales
ORDER BY profit DESC
LIMIT 10;
-- 13.3 Top 10 lowest profit (biggest loss) rows
SELECT order_id,
    order_date,
    product_name,
    category,
    region,
    sales,
    profit,
    discount
FROM retail_sales
ORDER BY profit ASC
LIMIT 10;
-- 13.4 Top 10 highest discount rows
SELECT order_id,
    order_date,
    product_name,
    category,
    sales,
    discount,
    profit
FROM retail_sales
ORDER BY discount DESC
LIMIT 10;
-- ============================================
-- 14. SUMMARY TABLE CHECKS
-- ============================================
SELECT *
FROM category_summary
ORDER BY total_sales DESC;
SELECT *
FROM region_summary
ORDER BY total_sales DESC;
SELECT *
FROM monthly_summary
ORDER BY year_month;
-- ============================================
-- 15. QUICK HEALTH CHECK
-- ============================================
-- 15.1 Row count match
SELECT (
        SELECT COUNT(*)
        FROM retail_sales
    ) AS main_rows,
    (
        SELECT COUNT(*)
        FROM category_summary
    ) AS cat_summary_rows,
    (
        SELECT COUNT(*)
        FROM region_summary
    ) AS reg_summary_rows,
    (
        SELECT COUNT(*)
        FROM monthly_summary
    ) AS mon_summary_rows;
-- 15.2 Null check across key columns
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
    ) AS null_profit,
    SUM(
        CASE
            WHEN region IS NULL THEN 1
            ELSE 0
        END
    ) AS null_region,
    SUM(
        CASE
            WHEN category IS NULL THEN 1
            ELSE 0
        END
    ) AS null_category
FROM retail_sales;
-- ============================================
-- END OF FILE
-- ============================================