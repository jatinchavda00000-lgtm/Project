# Data Dictionary — Retail Sales Data Analysis

**Project:** Retail Sales Data Analysis
**Scope:** Columns in the raw, cleaned, and engineered datasets
**API Usage:** None

---

## Overview

This document describes every column used in the project:

- **Raw columns** — as they appear in the source CSV
- **Standardized columns** — after renaming in the cleaning pipeline
- **Derived columns** — computed during cleaning (date features)
- **Engineered columns** — computed during feature engineering
- **Metadata columns** — created during database import

Column names use snake-case-with-underscores convention throughout the
cleaned and engineered datasets.

---

## 1. Raw Columns

These are the columns expected in the source CSV. Source data may have
variations in casing and spacing, which are normalized by the cleaning
pipeline.

| # | Raw Column Name | Data Type | Required | Description |
|---|-----------------|-----------|----------|-------------|
| 1 | Order ID | String | Yes | Unique order identifier |
| 2 | Order Date | Date (String) | Yes | Date of the order |
| 3 | Customer Name | String | No | Name of the customer |
| 4 | Segment | String | No | Customer segment |
| 5 | Region | String | No | Geographic region |
| 6 | State | String | No | State name |
| 7 | City | String | No | City name |
| 8 | Product Name | String | No | Product name |
| 9 | Category | String | No | Product category |
| 10 | Quantity | Integer (String) | Yes | Number of units |
| 11 | Unit Price | Float (String) | No | Price per unit |
| 12 | Discount | Float (String) | No | Discount percentage |
| 13 | Sales | Float (String) | Yes | Total sales amount |
| 14 | Profit | Float (String) | No | Profit amount |
| 15 | Payment Mode | String | No | Payment method |

**Notes:**
- Numeric columns may arrive as strings with symbols like `Rs.`, `,`, `%`.
- Date column may arrive in different formats.
- `Required = Yes` means rows missing this column are dropped.

---

## 2. Standardized Column Names

After `standardize_columns()`:

| Raw Name | Standardized Name |
|----------|-------------------|
| Order ID | Order_Id |
| Order Date | Order_Date |
| Customer Name | Customer_Name |
| Segment | Segment |
| Region | Region |
| State | State |
| City | City |
| Product Name | Product_Name |
| Category | Category |
| Quantity | Quantity |
| Unit Price | Unit_Price |
| Discount | Discount |
| Sales | Sales |
| Profit | Profit |
| Payment Mode | Payment_Mode |

---

## 3. Core Columns (After Cleaning)

### 3.1 Identifiers

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| Order_Id | String | No | Unique order ID. Business key for deduplication. |
| Customer_Name | String | No | Customer name. Filled with "Unknown" if missing. |

### 3.2 Date

| Column | Data Type | Nullable | Description |
|--------|-----------|----------|-------------|
| Order_Date | Datetime64 | No | Parsed order date. Rows with invalid dates are dropped. |

### 3.3 Categorical Dimensions

| Column | Data Type | Nullable | Allowed Values |
|--------|-----------|----------|----------------|
| Segment | String | No | Consumer, Corporate, Home Office, Unknown |
| Region | String | No | North, South, East, West, Unknown |
| State | String | No | Any state name, Unknown |
| City | String | No | Any city name, Unknown |
| Category | String | No | Furniture, Technology, Office Supplies, Unknown |
| Product_Name | String | No | Product name, Unknown |
| Payment_Mode | String | No | UPI, Card, Cash, Net Banking, Unknown |

### 3.4 Numeric Measures

| Column | Data Type | Nullable | Min | Description |
|--------|-----------|----------|-----|-------------|
| Quantity | Integer | No | 1 | Number of units sold |
| Unit_Price | Float | No | 0 | Price per unit in INR |
| Discount | Float | No | 0 | Discount percentage (0–100) |
| Sales | Float | No | > 0 | Total sales amount in INR |
| Profit | Float | No | any | Profit amount in INR (can be negative) |

**Notes:**
- `Sales` and `Quantity` rows with values ≤ 0 are dropped.
- `Profit` may be negative (loss).
- `Discount` values in 0–1 range are scaled to percentages.

---

## 4. Derived Date Features

Added by `parse_dates()`:

| Column | Data Type | Description | Example |
|--------|-----------|-------------|---------|
| Year | Integer | Order year | 2024 |
| Month | Integer | Month number (1–12) | 6 |
| Month_Name | String | 3-letter month abbreviation | Jun |
| Quarter | Integer | Quarter number (1–4) | 2 |
| Weekday | String | Full day name | Thursday |

---

## 5. Engineered Features

Added by `feature_engineering.py`:

### 5.1 Financial Metrics

| Column | Formula | Data Type | Description |
|--------|---------|-----------|-------------|
| Profit_Margin | (Profit / Sales) × 100 | Float | Profit as a percentage of sales |
| Revenue_Per_Unit | Sales / Quantity | Float | Revenue per unit sold |
| Profit_Per_Unit | Profit / Quantity | Float | Profit per unit sold |
| Discount_Amount | Sales × Discount / 100 | Float | Approximate discount value in INR |

### 5.2 Categorical Buckets

| Column | Allowed Values | Description |
|--------|---------------|-------------|
| Discount_Band | No Discount, Low, Medium, High, Very High | Discount buckets: 0%, 1–10%, 11–20%, 21–30%, >30% |
| Profit_Status | Profit, Loss, Break-even | Profit > 0, Profit < 0, Profit = 0 |
| Order_Size | Small, Medium, Large, Bulk | Quantity: 1–2, 3–5, 6–10, >10 |
| Season | Winter, Summer, Monsoon, Post-Monsoon | Dec–Feb, Mar–May, Jun–Sep, Oct–Nov |
| Quarter_Label | Q1, Q2, Q3, Q4 | Quarter as a label |
| Customer_Type | New, Repeat | Repeat if customer appears more than once |

### 5.3 Boolean Flags

| Column | Data Type | Description |
|--------|-----------|-------------|
| Is_Weekend | Boolean | True if Saturday or Sunday |

### 5.4 Time-Series Key

| Column | Data Type | Format | Description |
|--------|-----------|--------|-------------|
| Year_Month | String | YYYY-MM | Sortable month key for trends |

---

## 6. Full Cleaned Dataset Schema

After `clean_pipeline()` + `engineer_features()`, the dataset has:

| # | Column | Group |
|---|--------|-------|
| 1 | Order_Id | Identifier |
| 2 | Order_Date | Date |
| 3 | Customer_Name | Identifier |
| 4 | Segment | Dimension |
| 5 | Region | Dimension |
| 6 | State | Dimension |
| 7 | City | Dimension |
| 8 | Product_Name | Dimension |
| 9 | Category | Dimension |
| 10 | Quantity | Measure |
| 11 | Unit_Price | Measure |
| 12 | Discount | Measure |
| 13 | Sales | Measure |
| 14 | Profit | Measure |
| 15 | Payment_Mode | Dimension |
| 16 | Year | Derived |
| 17 | Month | Derived |
| 18 | Month_Name | Derived |
| 19 | Quarter | Derived |
| 20 | Weekday | Derived |
| 21 | Profit_Margin | Engineered |
| 22 | Revenue_Per_Unit | Engineered |
| 23 | Profit_Per_Unit | Engineered |
| 24 | Discount_Amount | Engineered |
| 25 | Discount_Band | Engineered |
| 26 | Profit_Status | Engineered |
| 27 | Order_Size | Engineered |
| 28 | Is_Weekend | Engineered |
| 29 | Season | Engineered |
| 30 | Quarter_Label | Engineered |
| 31 | Year_Month | Engineered |
| 32 | Customer_Type | Engineered |

**Total: 32 columns**

---

## 7. Database Columns (After Import)

When imported into SQLite via `save_to_sql()`, the table
`retail_sales` includes two additional columns:

| Column | Data Type | Description |
|--------|-----------|-------------|
| id | Integer (PK) | Auto-increment primary key |
| created_at | Timestamp | Row insert timestamp |

These are added for database-level metadata and are not used in analysis.

---

## 8. Sample Row (Cleaned Dataset)

| Field | Value |
|-------|-------|
| Order_Id | ORD10001 |
| Order_Date | 2024-03-15 |
| Customer_Name | Customer_042 |
| Segment | Consumer |
| Region | North |
| State | Delhi |
| City | New Delhi |
| Product_Name | Product_017 |
| Category | Furniture |
| Quantity | 3 |
| Unit_Price | 1500.00 |
| Discount | 10.00 |
| Sales | 4050.00 |
| Profit | 486.00 |
| Payment_Mode | UPI |
| Year | 2024 |
| Month | 3 |
| Month_Name | Mar |
| Quarter | 1 |
| Weekday | Friday |
| Profit_Margin | 12.00 |
| Revenue_Per_Unit | 1350.00 |
| Profit_Per_Unit | 162.00 |
| Discount_Amount | 405.00 |
| Discount_Band | Low |
| Profit_Status | Profit |
| Order_Size | Medium |
| Is_Weekend | False |
| Season | Summer |
| Quarter_Label | Q1 |
| Year_Month | 2024-03 |
| Customer_Type | Repeat |

---

## 9. Value Ranges & Business Rules

| Column | Rule |
|--------|------|
| Quantity | Must be > 0 |
| Unit_Price | Must be ≥ 0 |
| Discount | 0 ≤ Discount ≤ 100 |
| Sales | Must be > 0 |
| Profit | Any real number (may be negative) |
| Profit_Margin | Any real number; typically −50 to +50 |
| Year_Month | Format "YYYY-MM" |
| Order_Id | Unique after deduplication |

---

## 10. Missing Value Handling Rules

From `config.py`:

| Column | Rule |
|--------|------|
| Order_Id | Drop row if missing |
| Order_Date | Drop row if missing |
| Sales | Drop row if missing |
| Profit | Fill with 0 |
| Discount | Fill with 0 |
| Quantity | Fill with 0 |
| Region | Fill with "Unknown" |
| Category | Fill with "Unknown" |
| Segment | Fill with "Unknown" |
| Payment_Mode | Fill with "Unknown" |
| Other numeric | Fill with median |
| Other text | Fill with "Unknown" |

---

## 11. Notes on Data Quality

- Column names may arrive with spaces, mixed case, or special characters.
- Numeric columns may contain currency symbols (`Rs.`, `$`), thousands separators (`,`), or percent signs (`%`).
- Date columns may arrive in `YYYY-MM-DD`, `DD/MM/YYYY`, or other formats.
- Duplicate rows are dropped by `Order_Id`.
- Rows with invalid or missing critical fields are dropped.
- Outliers are detected but **not removed** by default — extreme values represent real business events.

---

## 12. Column Groups Summary

| Group | Count | Columns |
|-------|-------|---------|
| Identifiers | 2 | Order_Id, Customer_Name |
| Date | 1 | Order_Date |
| Dimensions | 8 | Segment, Region, State, City, Product_Name, Category, Payment_Mode, Profit_Status |
| Measures | 5 | Quantity, Unit_Price, Discount, Sales, Profit |
| Date Features | 5 | Year, Month, Month_Name, Quarter, Weekday |
| Financial Features | 4 | Profit_Margin, Revenue_Per_Unit, Profit_Per_Unit, Discount_Amount |
| Categorical Features | 5 | Discount_Band, Order_Size, Season, Quarter_Label, Customer_Type |
| Boolean Feature | 1 | Is_Weekend |
| Time-Series Key | 1 | Year_Month |
| Database Metadata | 2 | id, created_at |
| **Total** | **34** | (32 in CSV + 2 in DB) |

---

## 13. Glossary

| Term | Meaning |
|------|---------|
| KPI | Key Performance Indicator |
| AOV | Average Order Value |
| MoM | Month-over-Month |
| YoY | Year-over-Year |
| QoQ | Quarter-over-Quarter |
| IQR | Interquartile Range |
| CRISP-DM | Cross-Industry Standard Process for Data Mining |
| PK | Primary Key |

---

**End of Data Dictionary**