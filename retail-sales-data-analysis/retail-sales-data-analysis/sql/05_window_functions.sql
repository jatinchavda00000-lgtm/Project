-- ============================================
-- Retail Sales Data Analysis
-- File: sql/05_window_functions.sql
-- Purpose: Dedicated window functions - RANK, LAG, LEAD, NTILE,
--          cumulative, moving averages, PARTITION BY
-- Compatible: MySQL 8.0+ / MariaDB 10.5+ / SQLite 3.25+
-- ============================================
-- ============================================
-- NOTES
-- ============================================
-- Window functions require:
--   - MySQL 8.0+ / MariaDB 10.5+
--   - SQLite 3.25+
--   - PostgreSQL 8.4+
--
-- All queries below are read-only SELECT statements.
-- No data modification is performed.
-- ============================================
-- ============================================
-- 1. ROW_NUMBER
-- ============================================
-- 1.1 Assign a unique sequential number to each row
SELECT ROW_NUMBER() OVER (
        ORDER BY order_date,
            order_id
    ) AS row_num,
    order_id,
    order_date,
    customer_name,
    product_name,
    ROUND(sales, 2) AS sales
FROM retail_sales
ORDER BY row_num
LIMIT 50;
-- 1.2 Row number within each region (restart per region)
SELECT region,
    order_id,
    order_date,
    ROUND(sales, 2) AS sales,
    ROW_NUMBER() OVER (
        PARTITION BY region
        ORDER BY sales DESC
    ) AS row_in_region
FROM retail_sales
ORDER BY region,
    row_in_region
LIMIT 50;
-- 1.3 Deduplicate: keep only the first order per customer
SELECT *
FROM (
        SELECT customer_name,
            order_id,
            order_date,
            sales,
            ROW_NUMBER() OVER (
                PARTITION BY customer_name
                ORDER BY order_date ASC
            ) AS rn
        FROM retail_sales
    ) ranked
WHERE rn = 1
ORDER BY customer_name;
-- ============================================
-- 2. RANK / DENSE_RANK / PERCENT_RANK
-- ============================================
-- 2.1 Rank products by total sales
SELECT product_name,
    ROUND(SUM(sales), 2) AS total_sales,
    RANK() OVER (
        ORDER BY SUM(sales) DESC
    ) AS rank_val,
    DENSE_RANK() OVER (
        ORDER BY SUM(sales) DESC
    ) AS dense_rank_val,
    PERCENT_RANK() OVER (
        ORDER BY SUM(sales) DESC
    ) AS pct_rank,
    ROUND(
        ROUND(SUM(sales), 2) * 100.0 / (
            SELECT SUM(sales)
            FROM retail_sales
        ),
        2
    ) AS pct_of_total
FROM retail_sales
GROUP BY product_name
ORDER BY rank_val
LIMIT 20;
-- 2.2 Rank products within each category
SELECT category,
    product_name,
    ROUND(SUM(sales), 2) AS total_sales,
    RANK() OVER (
        PARTITION BY category
        ORDER BY SUM(sales) DESC
    ) AS rank_in_category
FROM retail_sales
GROUP BY category,
    product_name
ORDER BY category,
    rank_in_category;
-- 2.3 Rank regions by profit within each year
SELECT year,
    region,
    ROUND(SUM(profit), 2) AS total_profit,
    RANK() OVER (
        PARTITION BY year
        ORDER BY SUM(profit) DESC
    ) AS region_rank
FROM retail_sales
GROUP BY year,
    region
ORDER BY year,
    region_rank;
-- 2.4 Rank customers by lifetime value
SELECT customer_name,
    ROUND(SUM(sales), 2) AS lifetime_value,
    ROUND(SUM(profit), 2) AS lifetime_profit,
    RANK() OVER (
        ORDER BY SUM(sales) DESC
    ) AS sales_rank,
    DENSE_RANK() OVER (
        ORDER BY SUM(profit) DESC
    ) AS profit_rank
FROM retail_sales
GROUP BY customer_name
ORDER BY sales_rank
LIMIT 20;
-- ============================================
-- 3. LAG / LEAD (Previous / Next Row)
-- ============================================
-- 3.1 Month-over-month sales comparison
SELECT year_month,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(
        LAG(SUM(sales)) OVER (
            ORDER BY year_month
        ),
        2
    ) AS prev_month_sales,
    ROUND(
        SUM(sales) - LAG(SUM(sales)) OVER (
            ORDER BY year_month
        ),
        2
    ) AS mom_change,
    ROUND(
        (
            SUM(sales) - LAG(SUM(sales)) OVER (
                ORDER BY year_month
            )
        ) * 100.0 / NULLIF(
            LAG(SUM(sales)) OVER (
                ORDER BY year_month
            ),
            0
        ),
        2
    ) AS mom_growth_pct,
    ROUND(
        LEAD(SUM(sales)) OVER (
            ORDER BY year_month
        ),
        2
    ) AS next_month_sales
FROM retail_sales
GROUP BY year_month
ORDER BY year_month;
-- 3.2 Year-over-year sales comparison
SELECT year,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(
        LAG(SUM(sales)) OVER (
            ORDER BY year
        ),
        2
    ) AS prev_year_sales,
    ROUND(
        (
            SUM(sales) - LAG(SUM(sales)) OVER (
                ORDER BY year
            )
        ) * 100.0 / NULLIF(
            LAG(SUM(sales)) OVER (
                ORDER BY year
            ),
            0
        ),
        2
    ) AS yoy_growth_pct
FROM retail_sales
GROUP BY year
ORDER BY year;
-- 3.3 Previous order's sales per customer
SELECT customer_name,
    order_id,
    order_date,
    ROUND(sales, 2) AS sales,
    ROUND(
        LAG(sales) OVER (
            PARTITION BY customer_name
            ORDER BY order_date
        ),
        2
    ) AS previous_order_sales,
    ROUND(
        sales - LAG(sales) OVER (
            PARTITION BY customer_name
            ORDER BY order_date
        ),
        2
    ) AS change_from_previous
FROM retail_sales
ORDER BY customer_name,
    order_date
LIMIT 50;
-- 3.4 Previous and next product in category (by sales)
SELECT category,
    product_name,
    ROUND(SUM(sales), 2) AS total_sales,
    LAG(product_name) OVER (
        PARTITION BY category
        ORDER BY SUM(sales) DESC
    ) AS higher_sales_product,
    LEAD(product_name) OVER (
        PARTITION BY category
        ORDER BY SUM(sales) DESC
    ) AS lower_sales_product
FROM retail_sales
GROUP BY category,
    product_name
ORDER BY category,
    total_sales DESC;
-- ============================================
-- 4. FIRST_VALUE / LAST_VALUE / NTH_VALUE
-- ============================================
-- 4.1 Best and worst product per category
SELECT DISTINCT category,
    FIRST_VALUE(product_name) OVER (
        PARTITION BY category
        ORDER BY SUM(sales) DESC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS best_product,
    LAST_VALUE(product_name) OVER (
        PARTITION BY category
        ORDER BY SUM(sales) DESC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS worst_product
FROM retail_sales
GROUP BY category,
    product_name;
-- 4.2 First order and last order per customer (with values)
SELECT DISTINCT customer_name,
    FIRST_VALUE(order_id) OVER (
        PARTITION BY customer_name
        ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS first_order_id,
    FIRST_VALUE(order_date) OVER (
        PARTITION BY customer_name
        ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS first_order_date,
    LAST_VALUE(order_id) OVER (
        PARTITION BY customer_name
        ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_order_id,
    LAST_VALUE(order_date) OVER (
        PARTITION BY customer_name
        ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_order_date
FROM retail_sales
ORDER BY customer_name;
-- 4.3 Second highest product per category
SELECT DISTINCT category,
    NTH_VALUE(product_name, 2) OVER (
        PARTITION BY category
        ORDER BY SUM(sales) DESC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS second_best_product
FROM retail_sales
GROUP BY category,
    product_name;
-- ============================================
-- 5. CUMULATIVE (RUNNING) TOTALS
-- ============================================
-- 5.1 Running total of sales by month
SELECT year_month,
    ROUND(SUM(sales), 2) AS monthly_sales,
    ROUND(
        SUM(SUM(sales)) OVER (
            ORDER BY year_month
        ),
        2
    ) AS running_total_sales
FROM retail_sales
GROUP BY year_month
ORDER BY year_month;
-- 5.2 Running total of profit by month
SELECT year_month,
    ROUND(SUM(profit), 2) AS monthly_profit,
    ROUND(
        SUM(SUM(profit)) OVER (
            ORDER BY year_month
        ),
        2
    ) AS running_total_profit
FROM retail_sales
GROUP BY year_month
ORDER BY year_month;
-- 5.3 Running total of sales within each region
SELECT region,
    year_month,
    ROUND(SUM(sales), 2) AS monthly_sales,
    ROUND(
        SUM(SUM(sales)) OVER (
            PARTITION BY region
            ORDER BY year_month
        ),
        2
    ) AS region_running_total
FROM retail_sales
GROUP BY region,
    year_month
ORDER BY region,
    year_month;
-- 5.4 Running total of orders by day
SELECT order_date,
    COUNT(DISTINCT order_id) AS daily_orders,
    SUM(COUNT(DISTINCT order_id)) OVER (
        ORDER BY order_date
    ) AS cumulative_orders
FROM retail_sales
GROUP BY order_date
ORDER BY order_date;
-- ============================================
-- 6. MOVING AVERAGES
-- ============================================
-- 6.1 3-month moving average of sales
SELECT year_month,
    ROUND(SUM(sales), 2) AS monthly_sales,
    ROUND(
        AVG(SUM(sales)) OVER (
            ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS moving_avg_3m
FROM retail_sales
GROUP BY year_month
ORDER BY year_month;
-- 6.2 6-month moving average of sales
SELECT year_month,
    ROUND(SUM(sales), 2) AS monthly_sales,
    ROUND(
        AVG(SUM(sales)) OVER (
            ORDER BY year_month ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS moving_avg_6m
FROM retail_sales
GROUP BY year_month
ORDER BY year_month;
-- 6.3 3-month moving average within each region
SELECT region,
    year_month,
    ROUND(SUM(sales), 2) AS monthly_sales,
    ROUND(
        AVG(SUM(sales)) OVER (
            PARTITION BY region
            ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS region_moving_avg_3m
FROM retail_sales
GROUP BY region,
    year_month
ORDER BY region,
    year_month;
-- ============================================
-- 7. WINDOW FRAMES (ROWS BETWEEN)
-- ============================================
-- 7.1 Compare each month to previous and next month
SELECT year_month,
    ROUND(SUM(sales), 2) AS monthly_sales,
    ROUND(
        SUM(SUM(sales)) OVER (
            ORDER BY year_month ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
        ),
        2
    ) AS three_month_window_total
FROM retail_sales
GROUP BY year_month
ORDER BY year_month;
-- 7.2 Expanding window (all months up to current)
SELECT year_month,
    ROUND(SUM(sales), 2) AS monthly_sales,
    ROUND(
        SUM(SUM(sales)) OVER (
            ORDER BY year_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ),
        2
    ) AS expanding_total
FROM retail_sales
GROUP BY year_month
ORDER BY year_month;
-- 7.3 Full partition window
SELECT region,
    order_id,
    ROUND(sales, 2) AS sales,
    ROUND(AVG(sales) OVER (PARTITION BY region), 2) AS region_avg_sales,
    ROUND(SUM(sales) OVER (PARTITION BY region), 2) AS region_total_sales
FROM retail_sales
ORDER BY region,
    sales DESC
LIMIT 50;
-- ============================================
-- 8. NTILE (BUCKETING / QUARTILES)
-- ============================================
-- 8.1 Divide products into 4 quartiles by sales
SELECT product_name,
    ROUND(SUM(sales), 2) AS total_sales,
    NTILE(4) OVER (
        ORDER BY SUM(sales) DESC
    ) AS sales_quartile,
    CASE
        NTILE(4) OVER (
            ORDER BY SUM(sales) DESC
        )
        WHEN 1 THEN 'Top 25% (Best)'
        WHEN 2 THEN 'Upper Middle'
        WHEN 3 THEN 'Lower Middle'
        WHEN 4 THEN 'Bottom 25% (Worst)'
    END AS performance_band
FROM retail_sales
GROUP BY product_name
ORDER BY sales_quartile,
    total_sales DESC;
-- 8.2 Divide customers into 5 quintiles by lifetime value
SELECT customer_name,
    ROUND(SUM(sales), 2) AS lifetime_value,
    NTILE(5) OVER (
        ORDER BY SUM(sales) DESC
    ) AS value_quintile
FROM retail_sales
GROUP BY customer_name
ORDER BY value_quintile,
    lifetime_value DESC;
-- 8.3 Divide orders into 10 deciles by sales
SELECT order_id,
    ROUND(SUM(sales), 2) AS order_sales,
    NTILE(10) OVER (
        ORDER BY SUM(sales) DESC
    ) AS sales_decile
FROM retail_sales
GROUP BY order_id
ORDER BY sales_decile,
    order_sales DESC
LIMIT 100;
-- ============================================
-- 9. COMBINED: RANK + RUNNING TOTAL + MOVING AVG
-- ============================================
-- 9.1 Full dashboard for monthly performance
SELECT year_month,
    ROUND(SUM(sales), 2) AS monthly_sales,
    ROUND(SUM(profit), 2) AS monthly_profit,
    RANK() OVER (
        ORDER BY SUM(sales) DESC
    ) AS sales_rank,
    ROUND(
        SUM(SUM(sales)) OVER (
            ORDER BY year_month
        ),
        2
    ) AS running_sales,
    ROUND(
        AVG(SUM(sales)) OVER (
            ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS moving_avg_3m,
    ROUND(
        (
            SUM(sales) - LAG(SUM(sales)) OVER (
                ORDER BY year_month
            )
        ) * 100.0 / NULLIF(
            LAG(SUM(sales)) OVER (
                ORDER BY year_month
            ),
            0
        ),
        2
    ) AS mom_growth_pct
FROM retail_sales
GROUP BY year_month
ORDER BY year_month;
-- 9.2 Product performance scorecard
SELECT product_name,
    category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    RANK() OVER (
        ORDER BY SUM(sales) DESC
    ) AS sales_rank,
    RANK() OVER (
        ORDER BY SUM(profit) DESC
    ) AS profit_rank,
    ROUND(
        SUM(sales) * 100.0 / (
            SELECT SUM(sales)
            FROM retail_sales
        ),
        2
    ) AS pct_of_total_sales,
    ROUND(
        SUM(SUM(sales)) OVER (
            ORDER BY SUM(sales) DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) * 100.0 / (
            SELECT SUM(sales)
            FROM retail_sales
        ),
        2
    ) AS cumulative_sales_pct
FROM retail_sales
GROUP BY product_name,
    category
ORDER BY sales_rank
LIMIT 20;
-- 9.3 Customer RFM-style scoring (Recency, Frequency, Monetary)
WITH customer_stats AS (
    SELECT customer_name,
        MAX(order_date) AS last_order_date,
        COUNT(DISTINCT order_id) AS frequency,
        ROUND(SUM(sales), 2) AS monetary
    FROM retail_sales
    GROUP BY customer_name
)
SELECT customer_name,
    last_order_date,
    frequency,
    monetary,
    NTILE(4) OVER (
        ORDER BY last_order_date DESC
    ) AS recency_score,
    NTILE(4) OVER (
        ORDER BY frequency DESC
    ) AS frequency_score,
    NTILE(4) OVER (
        ORDER BY monetary DESC
    ) AS monetary_score,
    (
        NTILE(4) OVER (
            ORDER BY last_order_date DESC
        ) + NTILE(4) OVER (
            ORDER BY frequency DESC
        ) + NTILE(4) OVER (
            ORDER BY monetary DESC
        )
    ) AS rfm_total
FROM customer_stats
ORDER BY rfm_total DESC
LIMIT 30;
-- ============================================
-- 10. PRODUCT RANKING OVER TIME
-- ============================================
-- 10.1 Product rank changes month over month
SELECT year_month,
    product_name,
    ROUND(SUM(sales), 2) AS monthly_sales,
    RANK() OVER (
        PARTITION BY year_month
        ORDER BY SUM(sales) DESC
    ) AS rank_in_month
FROM retail_sales
GROUP BY year_month,
    product_name
ORDER BY year_month,
    rank_in_month
LIMIT 100;
-- 10.2 Category rank within each year
SELECT year,
    category,
    ROUND(SUM(sales), 2) AS yearly_sales,
    RANK() OVER (
        PARTITION BY year
        ORDER BY SUM(sales) DESC
    ) AS rank_in_year
FROM retail_sales
GROUP BY year,
    category
ORDER BY year,
    rank_in_year;
-- ============================================
-- 11. REGIONAL RANKING & COMPARISON
-- ============================================
-- 11.1 Region ranking with monthly contribution
SELECT year_month,
    region,
    ROUND(SUM(sales), 2) AS monthly_sales,
    RANK() OVER (
        PARTITION BY year_month
        ORDER BY SUM(sales) DESC
    ) AS rank_in_month,
    ROUND(
        SUM(sales) * 100.0 / SUM(SUM(sales)) OVER (PARTITION BY year_month),
        2
    ) AS pct_of_month_sales
FROM retail_sales
GROUP BY year_month,
    region
ORDER BY year_month,
    rank_in_month;
-- 11.2 Each region's sales vs overall average
SELECT region,
    year_month,
    ROUND(SUM(sales), 2) AS monthly_sales,
    ROUND(AVG(SUM(sales)) OVER (PARTITION BY region), 2) AS region_avg,
    ROUND(
        SUM(sales) - AVG(SUM(sales)) OVER (PARTITION BY region),
        2
    ) AS diff_from_region_avg
FROM retail_sales
GROUP BY region,
    year_month
ORDER BY region,
    year_month;
-- ============================================
-- 12. DISCOUNT IMPACT WITH WINDOW FUNCTIONS
-- ============================================
-- 12.1 Rank discount levels by profit
SELECT discount,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    RANK() OVER (
        ORDER BY SUM(profit) DESC
    ) AS profit_rank,
    ROUND(
        SUM(profit) * 100.0 / SUM(SUM(profit)) OVER (),
        2
    ) AS pct_of_total_profit
FROM retail_sales
GROUP BY discount
ORDER BY discount;
-- 12.2 Running profit by discount level (cumulative)
SELECT discount,
    ROUND(SUM(profit), 2) AS profit_at_level,
    ROUND(
        SUM(SUM(profit)) OVER (
            ORDER BY discount
        ),
        2
    ) AS cumulative_profit
FROM retail_sales
GROUP BY discount
ORDER BY discount;
-- ============================================
-- END OF FILE
-- ============================================