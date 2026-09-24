# ============================================
# Retail Sales Data Analysis
# File: scripts/make_notebook_03.py
# Purpose: Generate notebooks/03_sql_analysis.ipynb
# ============================================

"""
Generates the third notebook in the project.

Run:
    python scripts/make_notebook_03.py

Output:
    notebooks/03_sql_analysis.ipynb

Note:
    - Requires `nbformat` (already in requirements.txt).
    - No API is used anywhere in this project.
"""

import sys
from pathlib import Path

import nbformat as nbf


# ============================================
# PROJECT PATHS
# ============================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
OUTPUT_PATH = NOTEBOOKS_DIR / "03_sql_analysis.ipynb"


# ============================================
# NOTEBOOK CELL HELPERS
# ============================================

def md(text: str):
    """Create a markdown cell."""
    return nbf.v4.new_markdown_cell(text.strip("\n"))


def code(text: str):
    """Create a code cell."""
    return nbf.v4.new_code_cell(text.strip("\n"))


# ============================================
# CELL CONTENT
# ============================================

CELLS = []


# ---------- Cell 1: Title ----------
CELLS.append(md("""
# 03 - SQL Analysis

**Project:** Retail Sales Data Analysis
**Purpose:** Load cleaned data into SQLite and run SQL analysis queries.

---

## Objectives
1. Load cleaned data from `data/processed/retail_sales_clean.csv`
2. Push it into a SQLite database
3. Run basic queries (KPIs, counts, distributions)
4. Run aggregation queries (top products, matrices, growth)
5. Run window-function queries (rank, LAG, moving averages)
6. Save query outputs to `output/` as CSV files
"""))


# ---------- Cell 2: Imports ----------
CELLS.append(code("""
# Standard imports
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import sqlite3
from sqlalchemy import create_engine, text

warnings.filterwarnings("ignore")

# Project root setup
PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Project modules
from config import (
    CLEAN_DATA_FILE,
    SQLITE_DB_PATH,
    SQLITE_CONNECTION_STRING,
    OUTPUT_DIR,
    TABLE_NAME,
)
from data_loader import load_csv, load_from_sql, save_to_sql
from utils import print_section, ensure_dir

print("Project root :", PROJECT_ROOT)
print("Clean data   :", CLEAN_DATA_FILE)
print("SQLite DB    :", SQLITE_DB_PATH)
print("Output dir   :", OUTPUT_DIR)
print("Clean exists :", CLEAN_DATA_FILE.exists())
"""))


# ---------- Cell 3: Load markdown ----------
CELLS.append(md("""
## 1. Load Cleaned Data

If the cleaned CSV does not exist, we run the cleaning pipeline on the fly.
This makes the notebook self-contained.
"""))


# ---------- Cell 4: Load code ----------
CELLS.append(code('''if CLEAN_DATA_FILE.exists():
    clean_df = load_csv(CLEAN_DATA_FILE)
    print(f"Loaded cleaned data: {CLEAN_DATA_FILE}")
else:
    print("Cleaned file not found. Running cleaning pipeline...")
    from data_cleaning import clean_pipeline

    raw_path = PROJECT_ROOT / "data" / "raw" / "retail_sales_raw.csv"
    if not raw_path.exists():
        raise FileNotFoundError(
            f"Neither clean nor raw data found. Run Notebook 01/02 first.\\n"
            f"Expected: {CLEAN_DATA_FILE}\\n"
            f"Or      : {raw_path}"
        )

    raw_df = load_csv(raw_path)
    clean_df = clean_pipeline(raw_df, remove_out=False)

    CLEAN_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(CLEAN_DATA_FILE, index=False)
    print(f"Cleaned data saved: {CLEAN_DATA_FILE}")

print(f"\\nShape: {clean_df.shape}")
print(f"Columns: {list(clean_df.columns)[:10]} ... (+{len(clean_df.columns)-10} more)")
clean_df.head(3)
'''))


# ---------- Cell 5: Push to SQLite markdown ----------
CELLS.append(md("""
## 2. Push Data to SQLite

We store the cleaned DataFrame into a SQLite database.
This lets us run standard SQL queries directly from the notebook.
"""))


# ---------- Cell 6: Push code ----------
CELLS.append(code("""
if SQLITE_DB_PATH.exists():
    SQLITE_DB_PATH.unlink()
    print(f"Removed old DB: {SQLITE_DB_PATH}")

save_to_sql(clean_df, table_name=TABLE_NAME, if_exists="replace")

check = load_from_sql(f"SELECT COUNT(*) AS total FROM {TABLE_NAME}")
print(f"Rows in SQLite: {int(check['total'].iloc[0]):,}")
"""))


# ---------- Cell 7: Helpers markdown ----------
CELLS.append(md("""
## 3. Helper: Run SQL and Return DataFrame

Small wrapper so we can call SQL inside the notebook cleanly.
"""))


# ---------- Cell 8: Helpers code ----------
CELLS.append(code('''def run_sql(query: str) -> pd.DataFrame:
    """Execute a SQL SELECT and return the result as a DataFrame."""
    engine = create_engine(SQLITE_CONNECTION_STRING)
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return df


def show(query: str, title: str | None = None, rows: int = 20) -> pd.DataFrame:
    """Print a header, run the query, and display the first N rows."""
    if title:
        print_section(title)
    df = run_sql(query)
    print(f"Rows: {len(df)}")
    display(df.head(rows))
    return df


print("run_sql() and show() ready.")
'''))


# ---------- Cell 9: Basic KPIs markdown ----------
CELLS.append(md("""
## 4. Basic KPIs
"""))


# ---------- Cell 10: Basic KPIs code ----------
CELLS.append(code('''kpi_query = f"""
SELECT
    COUNT(DISTINCT Order_Id)                                        AS total_orders,
    COUNT(DISTINCT Customer_Name)                                   AS total_customers,
    COUNT(DISTINCT Product_Name)                                    AS total_products,
    SUM(Quantity)                                                   AS total_quantity,
    ROUND(SUM(Sales), 2)                                            AS total_sales,
    ROUND(SUM(Profit), 2)                                           AS total_profit,
    ROUND(AVG(Discount), 2)                                         AS avg_discount_pct,
    ROUND(SUM(Sales) / NULLIF(COUNT(DISTINCT Order_Id), 0), 2)      AS avg_order_value,
    ROUND((SUM(Profit) / NULLIF(SUM(Sales), 0)) * 100, 2)           AS profit_margin_pct
FROM {TABLE_NAME};
"""

kpis = show(kpi_query, "OVERALL KPIs")
'''))


# ---------- Cell 11: Date + distinct markdown ----------
CELLS.append(md("""
## 5. Date Range & Distinct Values
"""))


# ---------- Cell 12: Date range code ----------
CELLS.append(code('''show(f"""
SELECT
    MIN(Order_Date) AS first_order,
    MAX(Order_Date) AS last_order
FROM {TABLE_NAME};
""", "DATE RANGE")
'''))


# ---------- Cell 13: Distinct values code ----------
CELLS.append(code('''show(f"SELECT DISTINCT Region FROM {TABLE_NAME} ORDER BY Region;", "REGIONS")
show(f"SELECT DISTINCT Category FROM {TABLE_NAME} ORDER BY Category;", "CATEGORIES")
show(f"SELECT DISTINCT Segment FROM {TABLE_NAME} ORDER BY Segment;", "SEGMENTS")
show(f"SELECT DISTINCT Payment_Mode FROM {TABLE_NAME} ORDER BY Payment_Mode;", "PAYMENT MODES")
'''))


# ---------- Cell 14: Region markdown ----------
CELLS.append(md("""
## 6. Region-wise Analysis
"""))


# ---------- Cell 15: Region code ----------
CELLS.append(code('''region_query = f"""
SELECT
    Region,
    COUNT(DISTINCT Order_Id)                                        AS orders,
    ROUND(SUM(Sales), 2)                                            AS total_sales,
    ROUND(SUM(Profit), 2)                                           AS total_profit,
    ROUND(AVG(Discount), 2)                                         AS avg_discount,
    ROUND((SUM(Profit) / NULLIF(SUM(Sales), 0)) * 100, 2)           AS profit_margin_pct
FROM {TABLE_NAME}
GROUP BY Region
ORDER BY total_sales DESC;
"""

region_result = show(region_query, "REGION-WISE ANALYSIS")
'''))


# ---------- Cell 16: Category markdown ----------
CELLS.append(md("""
## 7. Category-wise Analysis
"""))


# ---------- Cell 17: Category code ----------
CELLS.append(code('''category_query = f"""
SELECT
    Category,
    COUNT(DISTINCT Order_Id)                                        AS orders,
    ROUND(SUM(Sales), 2)                                            AS total_sales,
    ROUND(SUM(Profit), 2)                                           AS total_profit,
    ROUND((SUM(Profit) / NULLIF(SUM(Sales), 0)) * 100, 2)           AS profit_margin_pct
FROM {TABLE_NAME}
GROUP BY Category
ORDER BY total_sales DESC;
"""

category_result = show(category_query, "CATEGORY-WISE ANALYSIS")
'''))


# ---------- Cell 18: Top products markdown ----------
CELLS.append(md("""
## 8. Top Products by Sales
"""))


# ---------- Cell 19: Top products code ----------
CELLS.append(code('''top_products_query = f"""
SELECT
    Product_Name,
    Category,
    COUNT(DISTINCT Order_Id)                                        AS orders,
    ROUND(SUM(Sales), 2)                                            AS total_sales,
    ROUND(SUM(Profit), 2)                                           AS total_profit,
    ROUND((SUM(Profit) / NULLIF(SUM(Sales), 0)) * 100, 2)           AS profit_margin_pct
FROM {TABLE_NAME}
GROUP BY Product_Name, Category
ORDER BY total_sales DESC
LIMIT 10;
"""

top_products_result = show(top_products_query, "TOP 10 PRODUCTS BY SALES")
'''))


# ---------- Cell 20: Bottom products markdown ----------
CELLS.append(md("""
## 9. Bottom Products by Profit (Loss Makers)
"""))


# ---------- Cell 21: Bottom products code ----------
CELLS.append(code('''bottom_products_query = f"""
SELECT
    Product_Name,
    Category,
    COUNT(DISTINCT Order_Id)                                        AS orders,
    ROUND(SUM(Sales), 2)                                            AS total_sales,
    ROUND(SUM(Profit), 2)                                           AS total_profit,
    ROUND(AVG(Discount), 2)                                         AS avg_discount
FROM {TABLE_NAME}
GROUP BY Product_Name, Category
ORDER BY total_profit ASC
LIMIT 10;
"""

bottom_products_result = show(bottom_products_query, "BOTTOM 10 PRODUCTS BY PROFIT")
'''))


# ---------- Cell 22: Monthly trend markdown ----------
CELLS.append(md("""
## 10. Monthly Sales Trend

Uses the `Year_Month` column created during cleaning.
"""))


# ---------- Cell 23: Monthly trend code ----------
CELLS.append(code('''monthly_query = f"""
SELECT
    Year_Month,
    ROUND(SUM(Sales), 2)                                            AS total_sales,
    ROUND(SUM(Profit), 2)                                           AS total_profit,
    COUNT(DISTINCT Order_Id)                                        AS orders
FROM {TABLE_NAME}
GROUP BY Year_Month
ORDER BY Year_Month;
"""

monthly_result = show(monthly_query, "MONTHLY SALES TREND", rows=30)
'''))


# ---------- Cell 24: Discount impact markdown ----------
CELLS.append(md("""
## 11. Discount Impact on Profit
"""))


# ---------- Cell 25: Discount impact code ----------
CELLS.append(code('''discount_query = f"""
SELECT
    Discount,
    COUNT(DISTINCT Order_Id)                                        AS orders,
    ROUND(SUM(Sales), 2)                                            AS total_sales,
    ROUND(SUM(Profit), 2)                                           AS total_profit,
    ROUND(AVG(Profit), 2)                                           AS avg_profit,
    ROUND((SUM(Profit) / NULLIF(SUM(Sales), 0)) * 100, 2)           AS profit_margin_pct
FROM {TABLE_NAME}
GROUP BY Discount
ORDER BY Discount;
"""

discount_result = show(discount_query, "DISCOUNT vs PROFIT")
'''))


# ---------- Cell 26: Discount band markdown ----------
CELLS.append(md("""
## 12. Discount Band Analysis
"""))


# ---------- Cell 27: Discount band code ----------
CELLS.append(code('''discount_band_query = f"""
SELECT
    Discount_Band,
    COUNT(DISTINCT Order_Id)                                        AS orders,
    ROUND(SUM(Sales), 2)                                            AS total_sales,
    ROUND(SUM(Profit), 2)                                           AS total_profit,
    ROUND((SUM(Profit) / NULLIF(SUM(Sales), 0)) * 100, 2)           AS profit_margin_pct
FROM {TABLE_NAME}
GROUP BY Discount_Band
ORDER BY
    CASE Discount_Band
        WHEN 'No Discount' THEN 1
        WHEN 'Low'         THEN 2
        WHEN 'Medium'      THEN 3
        WHEN 'High'        THEN 4
        WHEN 'Very High'   THEN 5
        ELSE 6
    END;
"""

discount_band_result = show(discount_band_query, "DISCOUNT BAND ANALYSIS")
'''))


# ---------- Cell 28: Profit status markdown ----------
CELLS.append(md("""
## 13. Profit Status Distribution
"""))


# ---------- Cell 29: Profit status code ----------
CELLS.append(code('''profit_status_query = f"""
SELECT
    Profit_Status,
    COUNT(DISTINCT Order_Id)                                        AS orders,
    ROUND(SUM(Sales), 2)                                            AS total_sales,
    ROUND(SUM(Profit), 2)                                           AS total_profit,
    ROUND(
        COUNT(DISTINCT Order_Id) * 100.0 /
        (SELECT COUNT(DISTINCT Order_Id) FROM {TABLE_NAME}),
        2
    )                                                               AS pct_of_orders
FROM {TABLE_NAME}
GROUP BY Profit_Status
ORDER BY orders DESC;
"""

profit_status_result = show(profit_status_query, "PROFIT STATUS")
'''))


# ---------- Cell 30: Season markdown ----------
CELLS.append(md("""
## 14. Season Analysis
"""))


# ---------- Cell 31: Season code ----------
CELLS.append(code('''season_query = f"""
SELECT
    Season,
    COUNT(DISTINCT Order_Id)                                        AS orders,
    ROUND(SUM(Sales), 2)                                            AS total_sales,
    ROUND(SUM(Profit), 2)                                           AS total_profit,
    ROUND((SUM(Profit) / NULLIF(SUM(Sales), 0)) * 100, 2)           AS profit_margin_pct
FROM {TABLE_NAME}
GROUP BY Season
ORDER BY total_sales DESC;
"""

season_result = show(season_query, "SEASON ANALYSIS")
'''))


# ---------- Cell 32: Payment mode markdown ----------
CELLS.append(md("""
## 15. Payment Mode Analysis
"""))


# ---------- Cell 33: Payment mode code ----------
CELLS.append(code('''payment_query = f"""
SELECT
    Payment_Mode,
    COUNT(DISTINCT Order_Id)                                        AS orders,
    ROUND(SUM(Sales), 2)                                            AS total_sales,
    ROUND(SUM(Profit), 2)                                           AS total_profit,
    ROUND(SUM(Sales) / NULLIF(COUNT(DISTINCT Order_Id), 0), 2)      AS avg_order_value
FROM {TABLE_NAME}
GROUP BY Payment_Mode
ORDER BY total_sales DESC;
"""

payment_result = show(payment_query, "PAYMENT MODE ANALYSIS")
'''))


# ---------- Cell 34: Region x Category markdown ----------
CELLS.append(md("""
## 16. Region x Category Matrix (Pivot)

Pivot built with `CASE WHEN` inside `SUM()`.
"""))


# ---------- Cell 35: Region x Category code ----------
CELLS.append(code('''matrix_query = f"""
SELECT
    Region,
    ROUND(SUM(CASE WHEN Category = 'Furniture'       THEN Sales ELSE 0 END), 2) AS furniture_sales,
    ROUND(SUM(CASE WHEN Category = 'Technology'      THEN Sales ELSE 0 END), 2) AS technology_sales,
    ROUND(SUM(CASE WHEN Category = 'Office Supplies' THEN Sales ELSE 0 END), 2) AS office_supplies_sales,
    ROUND(SUM(Sales), 2)                                                        AS total_sales
FROM {TABLE_NAME}
GROUP BY Region
ORDER BY total_sales DESC;
"""

matrix_result = show(matrix_query, "REGION x CATEGORY MATRIX")
'''))


# ---------- Cell 36: MoM markdown ----------
CELLS.append(md("""
## 17. Month-over-Month Growth (Window Function)

Uses the `LAG()` window function.
"""))


# ---------- Cell 37: MoM code ----------
CELLS.append(code('''mom_query = f"""
SELECT
    Year_Month,
    ROUND(SUM(Sales), 2)                                            AS monthly_sales,
    ROUND(LAG(SUM(Sales)) OVER (ORDER BY Year_Month), 2)            AS prev_month_sales,
    ROUND(
        (SUM(Sales) - LAG(SUM(Sales)) OVER (ORDER BY Year_Month)) * 100.0 /
        NULLIF(LAG(SUM(Sales)) OVER (ORDER BY Year_Month), 0),
        2
    )                                                               AS mom_growth_pct
FROM {TABLE_NAME}
GROUP BY Year_Month
ORDER BY Year_Month;
"""

mom_result = show(mom_query, "MONTH-OVER-MONTH GROWTH", rows=30)
'''))


# ---------- Cell 38: Running total markdown ----------
CELLS.append(md("""
## 18. Running Total of Sales

Cumulative sum using `SUM() OVER`.
"""))


# ---------- Cell 39: Running total code ----------
CELLS.append(code('''running_query = f"""
SELECT
    Year_Month,
    ROUND(SUM(Sales), 2)                                            AS monthly_sales,
    ROUND(SUM(SUM(Sales)) OVER (ORDER BY Year_Month), 2)            AS running_total
FROM {TABLE_NAME}
GROUP BY Year_Month
ORDER BY Year_Month;
"""

running_result = show(running_query, "RUNNING TOTAL SALES", rows=30)
'''))


# ---------- Cell 40: Top customers markdown ----------
CELLS.append(md("""
## 19. Top 10 Customers by Sales
"""))


# ---------- Cell 41: Top customers code ----------
CELLS.append(code('''top_customers_query = f"""
SELECT
    Customer_Name,
    Segment,
    COUNT(DISTINCT Order_Id)                                        AS orders,
    ROUND(SUM(Sales), 2)                                            AS total_sales,
    ROUND(SUM(Profit), 2)                                           AS total_profit,
    ROUND(AVG(Sales), 2)                                            AS avg_order_value
FROM {TABLE_NAME}
GROUP BY Customer_Name, Segment
ORDER BY total_sales DESC
LIMIT 10;
"""

top_customers_result = show(top_customers_query, "TOP 10 CUSTOMERS")
'''))


# ---------- Cell 42: Ranking markdown ----------
CELLS.append(md("""
## 20. Product Ranking with Window Functions

`RANK()` partitioned by category.
"""))


# ---------- Cell 43: Ranking code ----------
CELLS.append(code('''ranking_query = f"""
SELECT
    Category,
    Product_Name,
    ROUND(SUM(Sales), 2)                                            AS total_sales,
    RANK() OVER (
        PARTITION BY Category
        ORDER BY SUM(Sales) DESC
    )                                                               AS rank_in_category
FROM {TABLE_NAME}
GROUP BY Category, Product_Name
ORDER BY Category, rank_in_category;
"""

ranking_result = show(ranking_query, "PRODUCT RANKING WITHIN CATEGORY", rows=30)
'''))


# ---------- Cell 44: Loss products markdown ----------
CELLS.append(md("""
## 21. Loss-Making Products
"""))


# ---------- Cell 45: Loss products code ----------
CELLS.append(code('''loss_query = f"""
SELECT
    Product_Name,
    Category,
    COUNT(DISTINCT Order_Id)                                        AS orders,
    ROUND(SUM(Sales), 2)                                            AS total_sales,
    ROUND(SUM(Profit), 2)                                           AS total_profit,
    ROUND(AVG(Discount), 2)                                         AS avg_discount
FROM {TABLE_NAME}
GROUP BY Product_Name, Category
HAVING SUM(Profit) < 0
ORDER BY total_profit ASC;
"""

loss_result = show(loss_query, "LOSS-MAKING PRODUCTS")
'''))


# ---------- Cell 46: Export markdown ----------
CELLS.append(md("""
## 22. Save Query Results to CSV

All outputs go to `output/` so they can be used in reports or dashboards.
Each result becomes a separate CSV file.
"""))


# ---------- Cell 47: Export code ----------
CELLS.append(code('''ensure_dir(OUTPUT_DIR)

saved_files = []

exports = {
    "sql_kpis.csv":            kpis,
    "sql_region.csv":          region_result,
    "sql_category.csv":        category_result,
    "sql_top_products.csv":    top_products_result,
    "sql_bottom_products.csv": bottom_products_result,
    "sql_monthly_trend.csv":   monthly_result,
    "sql_discount.csv":        discount_result,
    "sql_discount_band.csv":   discount_band_result,
    "sql_profit_status.csv":   profit_status_result,
    "sql_season.csv":          season_result,
    "sql_payment_mode.csv":    payment_result,
    "sql_region_category.csv": matrix_result,
    "sql_mom_growth.csv":      mom_result,
    "sql_running_total.csv":   running_result,
    "sql_top_customers.csv":   top_customers_result,
    "sql_ranking.csv":         ranking_result,
    "sql_loss_products.csv":   loss_result,
}

for filename, df in exports.items():
    path = OUTPUT_DIR / filename
    df.to_csv(path, index=False)
    saved_files.append(path)

print_section("EXPORTED CSV FILES")
for p in saved_files:
    print(f"  - {p.name}")
print(f"\\nTotal: {len(saved_files)} files in {OUTPUT_DIR}")
'''))


# ---------- Cell 48: Summary markdown ----------
CELLS.append(md("""
## 23. Summary

### What was done
1. Loaded cleaned data
2. Pushed to SQLite (`retail_sales.db`)
3. Ran basic KPI queries
4. Ran aggregation queries (region, category, products)
5. Ran window-function queries (MoM, running total, rank)
6. Exported 17 result CSVs to `output/`

### Key numbers
- Total orders, sales, profit, margin
- Top category, top region, top product
- Loss-making products, high-discount bands
"""))


# ---------- Cell 49: Completion code ----------
CELLS.append(code('''print("=" * 60)
print("SQL ANALYSIS COMPLETE")
print("=" * 60)
print(f"Table         : {TABLE_NAME}")
print(f"Rows in DB    : {len(clean_df):,}")
print(f"Queries run   : {len(exports)}")
print(f"CSV exports   : {len(saved_files)} files")
print(f"Output folder : {OUTPUT_DIR}")
print("=" * 60)
'''))


# ============================================
# BUILD NOTEBOOK
# ============================================

def build_notebook() -> nbf.NotebookNode:
    """Assemble the notebook node."""
    nb = nbf.v4.new_notebook()
    nb["cells"] = CELLS
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.11",
            "mimetype": "text/x-python",
            "file_extension": ".py",
        },
    }
    return nb


def write_notebook(path: Path) -> None:
    """Write the notebook to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    nb = build_notebook()
    nbf.write(nb, str(path))


# ============================================
# MAIN
# ============================================

def main() -> int:
    print("=" * 60)
    print("GENERATING NOTEBOOK 03 — SQL ANALYSIS")
    print("=" * 60)
    print(f"Output path : {OUTPUT_PATH}")
    print(f"Total cells : {len(CELLS)}")

    try:
        write_notebook(OUTPUT_PATH)
    except Exception as e:
        print(f"\n[FAILED] {type(e).__name__}: {e}")
        return 1

    print(f"\n[OK] Notebook written successfully.")
    print(f"[OK] Open with: jupyter notebook {OUTPUT_PATH}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())