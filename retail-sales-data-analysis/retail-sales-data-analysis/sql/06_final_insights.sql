-- ============================================
-- Retail Sales Data Analysis
-- File: sql/06_final_insights.sql
-- Purpose: Final business insights and recommendations
--          Each query produces an actionable finding
-- Compatible: MySQL 8.0+ / MariaDB 10.5+ / SQLite 3.25+
-- ============================================
-- ============================================
-- NOTES
-- ============================================
-- Every query in this file answers a specific business question.
-- Each result is meant to become a bullet point in the final report.
-- No data modification. Read-only SELECT statements only.
-- ============================================
-- ============================================
-- INSIGHT 1: OVERALL BUSINESS HEALTH
-- ============================================
-- Question: What is the current state of the business?
SELECT COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_name) AS total_customers,
    COUNT(DISTINCT product_name) AS total_products,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(discount), 2) AS avg_discount_pct,
    ROUND(
        SUM(sales) / NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ) AS avg_order_value,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct
FROM retail_sales;
-- ============================================
-- INSIGHT 2: BEST PERFORMING REGION
-- ============================================
-- Question: Which region drives the most revenue and profit?
SELECT region,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct,
    COUNT(DISTINCT order_id) AS total_orders,
    RANK() OVER (
        ORDER BY SUM(sales) DESC
    ) AS sales_rank,
    RANK() OVER (
        ORDER BY SUM(profit) DESC
    ) AS profit_rank
FROM retail_sales
GROUP BY region
ORDER BY total_sales DESC;
-- ============================================
-- INSIGHT 3: REGION WITH HIGH SALES BUT LOW PROFIT
-- ============================================
-- Question: Which regions have high revenue but weak profitability?
-- Finding: Any region below average margin needs a discount review.
SELECT region,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct,
    ROUND(AVG(discount), 2) AS avg_discount_pct,
    CASE
        WHEN (SUM(profit) / NULLIF(SUM(sales), 0)) * 100 < 5 THEN 'Review Discount Policy'
        ELSE 'Healthy'
    END AS recommendation
FROM retail_sales
GROUP BY region
ORDER BY profit_margin_pct ASC;
-- ============================================
-- INSIGHT 4: TOP PERFORMING CATEGORY
-- ============================================
-- Question: Which category generates the most revenue?
SELECT category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct,
    COUNT(DISTINCT order_id) AS total_orders,
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
-- ============================================
-- INSIGHT 5: LOSS-MAKING PRODUCTS
-- ============================================
-- Question: Which products are losing money?
SELECT product_name,
    category,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(discount), 2) AS avg_discount_pct,
    CASE
        WHEN AVG(discount) > 25 THEN 'Reduce Discount'
        WHEN SUM(sales) < 1000 THEN 'Discontinue Product'
        ELSE 'Review Pricing'
    END AS recommendation
FROM retail_sales
GROUP BY product_name,
    category
HAVING SUM(profit) < 0
ORDER BY total_profit ASC
LIMIT 15;
-- ============================================
-- INSIGHT 6: DISCOUNT IMPACT ON PROFIT
-- ============================================
-- Question: At what discount level does profit turn negative?
SELECT discount,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(profit), 2) AS avg_profit_per_order,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct,
    CASE
        WHEN SUM(profit) < 0 THEN 'LOSS - Dangerous Level'
        WHEN (SUM(profit) / NULLIF(SUM(sales), 0)) * 100 < 5 THEN 'Low Margin'
        ELSE 'Healthy'
    END AS status
FROM retail_sales
GROUP BY discount
ORDER BY discount;
-- ============================================
-- INSIGHT 7: DISCOUNT BAND PROFITABILITY
-- ============================================
-- Question: Which discount band should we promote or cut?
SELECT discount_band,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct,
    CASE
        WHEN SUM(profit) < 0 THEN 'AVOID - Loss Band'
        WHEN SUM(profit) = 0 THEN 'Break-even'
        ELSE 'PROMOTE'
    END AS action
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
-- INSIGHT 8: BEST MONTHS FOR SALES
-- ============================================
-- Question: Which months generate the highest sales?
SELECT month,
    month_name,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    RANK() OVER (
        ORDER BY SUM(sales) DESC
    ) AS sales_rank
FROM retail_sales
GROUP BY month,
    month_name
ORDER BY sales_rank;
-- ============================================
-- INSIGHT 9: SEASONAL PATTERNS
-- ============================================
-- Question: Which season performs best?
SELECT season,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct,
    ROUND(
        SUM(sales) * 100.0 / (
            SELECT SUM(sales)
            FROM retail_sales
        ),
        2
    ) AS pct_of_total_sales
FROM retail_sales
GROUP BY season
ORDER BY total_sales DESC;
-- ============================================
-- INSIGHT 10: BEST PERFORMING PRODUCTS
-- ============================================
-- Question: Which products should we push harder?
SELECT product_name,
    category,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct,
    RANK() OVER (
        ORDER BY SUM(profit) DESC
    ) AS profit_rank
FROM retail_sales
GROUP BY product_name,
    category
ORDER BY total_profit DESC
LIMIT 10;
-- ============================================
-- INSIGHT 11: CUSTOMER SEGMENT PERFORMANCE
-- ============================================
-- Question: Which customer segment is most valuable?
SELECT segment,
    COUNT(DISTINCT customer_name) AS customers,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(
        SUM(sales) / NULLIF(COUNT(DISTINCT customer_name), 0),
        2
    ) AS avg_customer_value,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2) AS profit_margin_pct
FROM retail_sales
GROUP BY segment
ORDER BY total_sales DESC;
-- ============================================
-- INSIGHT 12: TOP 10 CUSTOMERS (VIP LIST)
-- ============================================
-- Question: Who are the most valuable customers?
SELECT customer_name,
    segment,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(sales), 2) AS avg_order_value,
    ROUND(AVG(discount), 2) AS avg_discount_pct
FROM retail_sales
GROUP BY customer_name,
    segment
ORDER BY total_sales DESC
LIMIT 10;
-- ============================================
-- INSIGHT 13: AT-RISK CUSTOMERS (HIGH DISCOUNT)
-- ============================================
-- Question: Which high-value customers are only buying on discount?
SELECT customer_name,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(AVG(discount), 2) AS avg_discount_pct,
    ROUND(
        SUM(
            CASE
                WHEN discount > 20 THEN sales
                ELSE 0
            END
        ) * 100.0 / NULLIF(SUM(sales), 0),
        2
    ) AS pct_sales_on_high_discount,
    CASE
        WHEN AVG(discount) > 25 THEN 'Discount Dependent'
        ELSE 'Loyal'
    END AS customer_status
FROM retail_sales
GROUP BY customer_name
HAVING SUM(sales) > (
        SELECT AVG(sales) * 5
        FROM retail_sales
    )
ORDER BY avg_discount_pct DESC
LIMIT 15;
-- ============================================
-- INSIGHT 14: BEST PAYMENT MODE
-- ============================================
-- Question: Which payment mode drives the most revenue?
SELECT payment_mode,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(sales), 2) AS avg_order_value,
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
-- INSIGHT 15: WEEKDAY VS WEEKEND PATTERN
-- ============================================
-- Question: When do customers shop more?
SELECT CASE
        WHEN is_weekend = 1 THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(sales), 2) AS avg_order_value,
    ROUND(
        COUNT(DISTINCT order_id) * 100.0 / (
            SELECT COUNT(DISTINCT order_id)
            FROM retail_sales
        ),
        2
    ) AS pct_of_orders
FROM retail_sales
GROUP BY is_weekend
ORDER BY orders DESC;
-- ============================================
-- INSIGHT 16: PROFIT DISTRIBUTION HEALTH
-- ============================================
-- Question: What percentage of orders are profitable?
SELECT profit_status,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
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
-- INSIGHT 17: GROWTH TRAJECTORY (YEAR-OVER-YEAR)
-- ============================================
-- Question: Is the business growing?
SELECT year,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    COUNT(DISTINCT order_id) AS total_orders,
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
    ) AS yoy_sales_growth_pct,
    ROUND(
        (
            SUM(profit) - LAG(SUM(profit)) OVER (
                ORDER BY year
            )
        ) * 100.0 / NULLIF(
            LAG(SUM(profit)) OVER (
                ORDER BY year
            ),
            0
        ),
        2
    ) AS yoy_profit_growth_pct
FROM retail_sales
GROUP BY year
ORDER BY year;
-- ============================================
-- INSIGHT 18: TOP PERFORMING STATE
-- ============================================
-- Question: Which states are driving business?
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
LIMIT 10;
-- ============================================
-- INSIGHT 19: DANGER ZONE ORDERS
-- ============================================
-- Question: How many orders are in the danger zone (high discount + loss)?
SELECT COUNT(*) AS danger_orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_loss,
    ROUND(
        COUNT(*) * 100.0 / (
            SELECT COUNT(*)
            FROM retail_sales
        ),
        2
    ) AS pct_of_all_orders,
    ROUND(AVG(discount), 2) AS avg_discount_pct
FROM retail_sales
WHERE discount > 30
    AND profit < 0;
-- ============================================
-- INSIGHT 20: ACTIONABLE RECOMMENDATION SUMMARY
-- ============================================
-- Question: What is the single-page summary for management?
SELECT 'Total Revenue' AS metric,
    ROUND(SUM(sales), 2) AS value,
    'Rs.' AS unit
FROM retail_sales
UNION ALL
SELECT 'Total Profit',
    ROUND(SUM(profit), 2),
    'Rs.'
FROM retail_sales
UNION ALL
SELECT 'Profit Margin',
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100, 2),
    '%'
FROM retail_sales
UNION ALL
SELECT 'Total Orders',
    COUNT(DISTINCT order_id),
    'count'
FROM retail_sales
UNION ALL
SELECT 'Total Customers',
    COUNT(DISTINCT customer_name),
    'count'
FROM retail_sales
UNION ALL
SELECT 'Avg Order Value',
    ROUND(
        SUM(sales) / NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ),
    'Rs.'
FROM retail_sales
UNION ALL
SELECT 'Avg Discount',
    ROUND(AVG(discount), 2),
    '%'
FROM retail_sales
UNION ALL
SELECT 'Loss-Making Orders',
    COUNT(DISTINCT order_id),
    'count'
FROM retail_sales
WHERE profit < 0
UNION ALL
SELECT 'Loss-Making Products',
    COUNT(DISTINCT product_name),
    'count'
FROM (
        SELECT product_name
        FROM retail_sales
        GROUP BY product_name
        HAVING SUM(profit) < 0
    ) AS loss_products;
-- ============================================
-- INSIGHT 21: BUSINESS RECOMMENDATIONS
-- ============================================
-- Generated based on data patterns.
-- These queries return the raw numbers behind each recommendation.
-- 21.1 Recommendation: Reduce discount on Low-Margin products
SELECT 'Reduce discount above 25%' AS recommendation,
    COUNT(DISTINCT order_id) AS affected_orders,
    ROUND(SUM(profit), 2) AS current_profit,
    ROUND(SUM(sales), 2) AS current_sales
FROM retail_sales
WHERE discount > 25
    AND profit < 0;
-- 21.2 Recommendation: Push High-Margin products
SELECT 'Push high-margin products' AS recommendation,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
WHERE profit_margin > 20;
-- 21.3 Recommendation: Focus on Best Region
SELECT 'Focus on best region: ' || region AS recommendation,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY region
ORDER BY total_sales DESC
LIMIT 1;
-- 21.4 Recommendation: Improve loss-making states
SELECT 'Review state: ' || state AS recommendation,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM retail_sales
GROUP BY state
HAVING SUM(profit) < 0
ORDER BY total_profit ASC
LIMIT 5;
-- ============================================
-- INSIGHT 22: KEY FINDINGS CHECKLIST
-- ============================================
-- These are boolean-style indicators used in the final report.
-- Each row tells whether a condition is met.
SELECT 'Top region identified' AS check_item,
    CASE
        WHEN COUNT(*) > 0 THEN 'YES'
        ELSE 'NO'
    END AS status
FROM (
        SELECT region
        FROM retail_sales
        GROUP BY region
        LIMIT 1
    )
UNION ALL
SELECT 'Loss-making products exist',
    CASE
        WHEN COUNT(*) > 0 THEN 'YES'
        ELSE 'NO'
    END
FROM (
        SELECT product_name
        FROM retail_sales
        GROUP BY product_name
        HAVING SUM(profit) < 0
    )
UNION ALL
SELECT 'High discount orders exist',
    CASE
        WHEN COUNT(*) > 0 THEN 'YES'
        ELSE 'NO'
    END
FROM retail_sales
WHERE discount > 30
UNION ALL
SELECT 'Seasonal pattern present',
    CASE
        WHEN COUNT(DISTINCT season) >= 3 THEN 'YES'
        ELSE 'NO'
    END
FROM retail_sales
UNION ALL
SELECT 'Repeat customers exist',
    CASE
        WHEN COUNT(*) > 0 THEN 'YES'
        ELSE 'NO'
    END
FROM (
        SELECT customer_name
        FROM retail_sales
        GROUP BY customer_name
        HAVING COUNT(DISTINCT order_id) > 1
    );
-- ============================================
-- END OF FILE
-- ============================================