-- ============================================
-- Retail Sales Data Analysis
-- File: sql/04_aggregation_queries.sql
-- Purpose: Deep-dive aggregations - top products, matrices,
--          discount impact, growth analysis, rankings
-- Compatible: MySQL 8.0+ / MariaDB 10.5+ / SQLite 3.35+
-- ============================================
-- ============================================
-- 1. TOP N PRODUCTS BY SALES
-- ============================================
-- 1.1 Top 10 products by total sales
SELECT product_name,
    category,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(discount), 2) AS avg_discount,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct
FROM retail_sales
GROUP BY product_name,
    category
ORDER BY total_sales DESC
LIMIT 10;
-- 1.2 Top 10 products by total profit
SELECT product_name,
    category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY product_name,
    category
ORDER BY total_profit DESC
LIMIT 10;
-- 1.3 Top 10 products by quantity sold
SELECT product_name,
    category,
    SUM(quantity) AS total_quantity,
    ROUND(SUM(sales), 2) AS total_sales
FROM retail_sales
GROUP BY product_name,
    category
ORDER BY total_quantity DESC
LIMIT 10;
-- 1.4 Top 10 products by profit margin (min 5 orders)
SELECT product_name,
    category,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct
FROM retail_sales
GROUP BY product_name,
    category
HAVING COUNT(DISTINCT order_id) >= 5
ORDER BY profit_margin_pct DESC
LIMIT 10;
-- ============================================
-- 2. BOTTOM N PRODUCTS
-- ============================================
-- 2.1 Bottom 10 products by profit (biggest loss-makers)
SELECT product_name,
    category,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(discount), 2) AS avg_discount
FROM retail_sales
GROUP BY product_name,
    category
ORDER BY total_profit ASC
LIMIT 10;
-- 2.2 Loss-making products only
SELECT product_name,
    category,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(discount), 2) AS avg_discount
FROM retail_sales
GROUP BY product_name,
    category
HAVING SUM(profit) < 0
ORDER BY total_profit ASC;
-- 2.3 Bottom 10 products by profit margin
SELECT product_name,
    category,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct
FROM retail_sales
GROUP BY product_name,
    category
HAVING COUNT(DISTINCT order_id) >= 5
ORDER BY profit_margin_pct ASC
LIMIT 10;
-- ============================================
-- 3. REGION × CATEGORY MATRIX (PIVOT)
-- ============================================
-- 3.1 Sales by region and category
SELECT region,
    ROUND(
        SUM(
            CASE
                WHEN category = 'Furniture' THEN sales
                ELSE 0
            END
        ),
        2
    ) AS furniture_sales,
    ROUND(
        SUM(
            CASE
                WHEN category = 'Technology' THEN sales
                ELSE 0
            END
        ),
        2
    ) AS technology_sales,
    ROUND(
        SUM(
            CASE
                WHEN category = 'Office Supplies' THEN sales
                ELSE 0
            END
        ),
        2
    ) AS office_supplies_sales,
    ROUND(SUM(sales), 2) AS total_sales
FROM retail_sales
GROUP BY region
ORDER BY total_sales DESC;
-- 3.2 Profit by region and category
SELECT region,
    ROUND(
        SUM(
            CASE
                WHEN category = 'Furniture' THEN profit
                ELSE 0
            END
        ),
        2
    ) AS furniture_profit,
    ROUND(
        SUM(
            CASE
                WHEN category = 'Technology' THEN profit
                ELSE 0
            END
        ),
        2
    ) AS technology_profit,
    ROUND(
        SUM(
            CASE
                WHEN category = 'Office Supplies' THEN profit
                ELSE 0
            END
        ),
        2
    ) AS office_supplies_profit,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY region
ORDER BY total_profit DESC;
-- 3.3 Orders by region and category
SELECT region,
    COUNT(
        DISTINCT CASE
            WHEN category = 'Furniture' THEN order_id
        END
    ) AS furniture_orders,
    COUNT(
        DISTINCT CASE
            WHEN category = 'Technology' THEN order_id
        END
    ) AS technology_orders,
    COUNT(
        DISTINCT CASE
            WHEN category = 'Office Supplies' THEN order_id
        END
    ) AS office_supplies_orders,
    COUNT(DISTINCT order_id) AS total_orders
FROM retail_sales
GROUP BY region
ORDER BY total_orders DESC;
-- ============================================
-- 4. SEGMENT × CATEGORY MATRIX
-- ============================================
SELECT segment,
    ROUND(
        SUM(
            CASE
                WHEN category = 'Furniture' THEN sales
                ELSE 0
            END
        ),
        2
    ) AS furniture,
    ROUND(
        SUM(
            CASE
                WHEN category = 'Technology' THEN sales
                ELSE 0
            END
        ),
        2
    ) AS technology,
    ROUND(
        SUM(
            CASE
                WHEN category = 'Office Supplies' THEN sales
                ELSE 0
            END
        ),
        2
    ) AS office_supplies,
    ROUND(SUM(sales), 2) AS total
FROM retail_sales
GROUP BY segment
ORDER BY total DESC;
-- ============================================
-- 5. REGION × YEAR MATRIX (PIVOT)
-- ============================================
SELECT region,
    ROUND(
        SUM(
            CASE
                WHEN year = 2022 THEN sales
                ELSE 0
            END
        ),
        2
    ) AS y2022_sales,
    ROUND(
        SUM(
            CASE
                WHEN year = 2023 THEN sales
                ELSE 0
            END
        ),
        2
    ) AS y2023_sales,
    ROUND(
        SUM(
            CASE
                WHEN year = 2024 THEN sales
                ELSE 0
            END
        ),
        2
    ) AS y2024_sales,
    ROUND(SUM(sales), 2) AS total_sales
FROM retail_sales
GROUP BY region
ORDER BY total_sales DESC;
-- ============================================
-- 6. DISCOUNT IMPACT ANALYSIS
-- ============================================
-- 6.1 Profit by exact discount level
SELECT discount,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(profit), 2) AS avg_profit_per_row,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct
FROM retail_sales
GROUP BY discount
ORDER BY discount;
-- 6.2 Profit by discount band
SELECT discount_band,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(profit), 2) AS avg_profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct
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
-- 6.3 Count of loss-making orders per discount band
SELECT discount_band,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(
        DISTINCT CASE
            WHEN profit < 0 THEN order_id
        END
    ) AS loss_orders,
    ROUND(
        COUNT(
            DISTINCT CASE
                WHEN profit < 0 THEN order_id
            END
        ) * 100.0 / NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ) AS loss_pct
FROM retail_sales
GROUP BY discount_band
ORDER BY loss_pct DESC;
-- 6.4 Average discount in profit vs loss orders
SELECT CASE
        WHEN profit >= 0 THEN 'Profit'
        ELSE 'Loss'
    END AS outcome,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(AVG(discount), 2) AS avg_discount,
    ROUND(AVG(sales), 2) AS avg_sales,
    ROUND(AVG(profit), 2) AS avg_profit
FROM retail_sales
GROUP BY CASE
        WHEN profit >= 0 THEN 'Profit'
        ELSE 'Loss'
    END
ORDER BY outcome;
-- ============================================
-- 7. MONTHLY GROWTH ANALYSIS
-- ============================================
-- 7.1 Month-over-month sales and growth
SELECT year_month,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(
        SUM(sales) - LAG(SUM(sales)) OVER (
            ORDER BY year_month
        ),
        2
    ) AS sales_change,
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
-- 7.2 Year-over-year sales and growth
SELECT year,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(
        SUM(sales) - LAG(SUM(sales)) OVER (
            ORDER BY year
        ),
        2
    ) AS yoy_change,
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
-- 7.3 Quarter-over-quarter growth
SELECT year,
    quarter_label,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(
        (
            SUM(sales) - LAG(SUM(sales)) OVER (
                ORDER BY year,
                    quarter
            )
        ) * 100.0 / NULLIF(
            LAG(SUM(sales)) OVER (
                ORDER BY year,
                    quarter
            ),
            0
        ),
        2
    ) AS qoq_growth_pct
FROM retail_sales
GROUP BY year,
    quarter,
    quarter_label
ORDER BY year,
    quarter;
-- ============================================
-- 8. RUNNING TOTALS & CUMULATIVE
-- ============================================
-- 8.1 Cumulative sales by month
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
-- 8.2 Cumulative profit by month
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
-- ============================================
-- 9. MOVING AVERAGE (3-MONTH)
-- ============================================
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
-- ============================================
-- 10. CUSTOMER ANALYSIS
-- ============================================
-- 10.1 Top 10 customers by sales
SELECT customer_name,
    segment,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(sales), 2) AS avg_order_value
FROM retail_sales
GROUP BY customer_name,
    segment
ORDER BY total_sales DESC
LIMIT 10;
-- 10.2 Top 10 customers by profit
SELECT customer_name,
    segment,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY customer_name,
    segment
ORDER BY total_profit DESC
LIMIT 10;
-- 10.3 Customer purchase frequency distribution
SELECT total_orders,
    COUNT(*) AS customer_count
FROM (
        SELECT customer_name,
            COUNT(DISTINCT order_id) AS total_orders
        FROM retail_sales
        GROUP BY customer_name
    ) AS customer_orders
GROUP BY total_orders
ORDER BY total_orders;
-- 10.4 Segment revenue contribution (%)
SELECT segment,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(
        SUM(sales) * 100.0 / (
            SELECT SUM(sales)
            FROM retail_sales
        ),
        2
    ) AS pct_of_total_sales
FROM retail_sales
GROUP BY segment
ORDER BY total_sales DESC;
-- ============================================
-- 11. PRODUCT CONTRIBUTION ANALYSIS
-- ============================================
-- 11.1 Category revenue contribution (%)
SELECT category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(
        SUM(sales) * 100.0 / (
            SELECT SUM(sales)
            FROM retail_sales
        ),
        2
    ) AS pct_of_total_sales
FROM retail_sales
GROUP BY category
ORDER BY total_sales DESC;
-- 11.2 Region revenue contribution (%)
SELECT region,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(
        SUM(sales) * 100.0 / (
            SELECT SUM(sales)
            FROM retail_sales
        ),
        2
    ) AS pct_of_total_sales
FROM retail_sales
GROUP BY region
ORDER BY total_sales DESC;
-- 11.3 Payment mode contribution (%)
SELECT payment_mode,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(
        SUM(sales) * 100.0 / (
            SELECT SUM(sales)
            FROM retail_sales
        ),
        2
    ) AS pct_of_total_sales
FROM retail_sales
GROUP BY payment_mode
ORDER BY total_sales DESC;
-- ============================================
-- 12. PARETO ANALYSIS (80/20 RULE)
-- ============================================
-- 12.1 Products that generate cumulative 80% of sales
WITH product_sales AS (
    SELECT product_name,
        SUM(sales) AS total_sales
    FROM retail_sales
    GROUP BY product_name
),
ranked AS (
    SELECT product_name,
        total_sales,
        SUM(total_sales) OVER (
            ORDER BY total_sales DESC
        ) AS cumulative_sales,
        SUM(total_sales) OVER () AS grand_total
    FROM product_sales
)
SELECT product_name,
    ROUND(total_sales, 2) AS total_sales,
    ROUND(cumulative_sales, 2) AS cumulative_sales,
    ROUND(
        cumulative_sales * 100.0 / NULLIF(grand_total, 0),
        2
    ) AS cumulative_pct
FROM ranked
WHERE cumulative_sales * 100.0 / NULLIF(grand_total, 0) <= 80
ORDER BY total_sales DESC;
-- 12.2 Regions that generate 80% of sales
WITH region_sales AS (
    SELECT region,
        SUM(sales) AS total_sales
    FROM retail_sales
    GROUP BY region
),
ranked AS (
    SELECT region,
        total_sales,
        SUM(total_sales) OVER (
            ORDER BY total_sales DESC
        ) AS cumulative_sales,
        SUM(total_sales) OVER () AS grand_total
    FROM region_sales
)
SELECT region,
    ROUND(total_sales, 2) AS total_sales,
    ROUND(
        cumulative_sales * 100.0 / NULLIF(grand_total, 0),
        2
    ) AS cumulative_pct
FROM ranked
ORDER BY total_sales DESC;
-- ============================================
-- 13. HIGH-VALUE ORDERS
-- ============================================
-- 13.1 Orders above average sales value
SELECT order_id,
    order_date,
    customer_name,
    product_name,
    category,
    region,
    ROUND(sales, 2) AS sales,
    ROUND(profit, 2) AS profit
FROM retail_sales
WHERE sales > (
        SELECT AVG(sales)
        FROM retail_sales
    )
ORDER BY sales DESC;
-- 13.2 High discount + negative profit orders (danger zone)
SELECT order_id,
    order_date,
    product_name,
    category,
    region,
    discount,
    ROUND(sales, 2) AS sales,
    ROUND(profit, 2) AS profit
FROM retail_sales
WHERE discount > 30
    AND profit < 0
ORDER BY profit ASC;
-- 13.3 High sales but low margin orders
SELECT order_id,
    order_date,
    product_name,
    category,
    ROUND(sales, 2) AS sales,
    ROUND(profit, 2) AS profit,
    ROUND(profit_margin, 2) AS profit_margin_pct
FROM retail_sales
WHERE sales > (
        SELECT AVG(sales) * 2
        FROM retail_sales
    )
    AND profit_margin < 5
ORDER BY sales DESC;
-- ============================================
-- 14. STATE-LEVEL ANALYSIS (TOP 15 STATES)
-- ============================================
SELECT state,
    region,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct
FROM retail_sales
GROUP BY state,
    region
ORDER BY total_sales DESC
LIMIT 15;
-- ============================================
-- 15. SEASON vs CATEGORY MATRIX
-- ============================================
SELECT season,
    ROUND(
        SUM(
            CASE
                WHEN category = 'Furniture' THEN sales
                ELSE 0
            END
        ),
        2
    ) AS furniture,
    ROUND(
        SUM(
            CASE
                WHEN category = 'Technology' THEN sales
                ELSE 0
            END
        ),
        2
    ) AS technology,
    ROUND(
        SUM(
            CASE
                WHEN category = 'Office Supplies' THEN sales
                ELSE 0
            END
        ),
        2
    ) AS office_supplies,
    ROUND(SUM(sales), 2) AS total_sales
FROM retail_sales
GROUP BY season
ORDER BY total_sales DESC;
-- ============================================
-- 16. WEEKDAY PERFORMANCE
-- ============================================
SELECT weekday,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(sales), 2) AS avg_sales
FROM retail_sales
GROUP BY weekday
ORDER BY total_sales DESC;
-- ============================================
-- 17. PROFITABILITY SEGMENTS
-- ============================================
-- 17.1 Product profitability buckets
SELECT CASE
        WHEN profit_margin >= 20 THEN 'High Margin (>=20%)'
        WHEN profit_margin >= 10 THEN 'Medium Margin (10-20%)'
        WHEN profit_margin >= 0 THEN 'Low Margin (0-10%)'
        ELSE 'Loss'
    END AS margin_bucket,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY CASE
        WHEN profit_margin >= 20 THEN 'High Margin (>=20%)'
        WHEN profit_margin >= 10 THEN 'Medium Margin (10-20%)'
        WHEN profit_margin >= 0 THEN 'Low Margin (0-10%)'
        ELSE 'Loss'
    END
ORDER BY total_sales DESC;
-- 17.2 Order size vs profitability
SELECT order_size,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(AVG(profit_margin), 2) AS avg_profit_margin,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY order_size
ORDER BY avg_profit_margin DESC;
-- ============================================
-- 18. RANKING WITH WINDOW FUNCTIONS
-- ============================================
-- 18.1 Rank products within each category by sales
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
-- 18.2 Rank regions by profit within each year
SELECT year,
    region,
    ROUND(SUM(profit), 2) AS total_profit,
    RANK() OVER (
        PARTITION BY year
        ORDER BY SUM(profit) DESC
    ) AS rank_in_year
FROM retail_sales
GROUP BY year,
    region
ORDER BY year,
    rank_in_year;
-- 18.3 Dense rank customers by total sales
SELECT customer_name,
    ROUND(SUM(sales), 2) AS total_sales,
    DENSE_RANK() OVER (
        ORDER BY SUM(sales) DESC
    ) AS customer_rank
FROM retail_sales
GROUP BY customer_name
ORDER BY customer_rank
LIMIT 20;
-- ============================================
-- END OF FILE
-- ============================================