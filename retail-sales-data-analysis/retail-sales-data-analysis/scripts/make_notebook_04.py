# ============================================
# Retail Sales Data Analysis
# File: scripts/make_notebook_04.py
# Purpose: Generate notebooks/04_eda.ipynb
# ============================================

"""
Generates the fourth notebook in the project.

Run:
    python scripts/make_notebook_04.py

Output:
    notebooks/04_eda.ipynb

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
OUTPUT_PATH = NOTEBOOKS_DIR / "04_eda.ipynb"


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
# 04 - Exploratory Data Analysis (EDA)

**Project:** Retail Sales Data Analysis
**Purpose:** Explore cleaned data visually and statistically.

---

## Objectives
1. Load cleaned data
2. Compute summary statistics
3. Analyze distributions (sales, profit, discount, quantity)
4. Analyze relationships (discount vs profit, quantity vs sales)
5. Analyze categorical dimensions (region, category, segment, payment)
6. Analyze time trends (monthly, quarterly, season)
7. Generate 18 plots and save them to `images/`
8. Extract top insights
"""))


# ---------- Cell 2: Imports ----------
CELLS.append(code("""
# Standard imports
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

# Inline plots
%matplotlib inline

# Project root
PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Project modules
from config import (
    CLEAN_DATA_FILE,
    IMAGES_DIR,
    OUTPUT_DIR,
    NUMERIC_COLUMNS,
    CATEGORICAL_COLUMNS,
    TOP_N,
    BOTTOM_N,
)
from data_loader import load_csv, get_data_info
from analysis import (
    overall_kpis,
    region_wise_analysis,
    category_wise_analysis,
    segment_wise_analysis,
    product_wise_analysis,
    top_products,
    bottom_products,
    monthly_sales_trend,
    quarterly_analysis,
    yearly_analysis,
    discount_impact,
    discount_band_analysis,
    profit_status_analysis,
    season_analysis,
    weekday_analysis,
    customer_analysis,
    payment_mode_analysis,
    loss_making_products,
    print_kpis,
)
from visualization import (
    setup_style,
    plot_sales_distribution,
    plot_profit_distribution,
    plot_region_sales,
    plot_region_profit,
    plot_category_sales,
    plot_monthly_trend,
    plot_quarterly_trend,
    plot_top_products,
    plot_bottom_products,
    plot_discount_vs_profit,
    plot_discount_band,
    plot_profit_status_pie,
    plot_season_analysis,
    plot_payment_mode,
    plot_correlation_heatmap,
    plot_boxplot_outliers,
    plot_customer_segment,
    plot_weekday_analysis,
    create_all_plots,
)
from utils import print_section, ensure_dir

print("Project root :", PROJECT_ROOT)
print("Clean data   :", CLEAN_DATA_FILE)
print("Images dir   :", IMAGES_DIR)
print("Clean exists :", CLEAN_DATA_FILE.exists())
"""))


# ---------- Cell 3: Load markdown ----------
CELLS.append(md("""
## 1. Load Cleaned Data
"""))


# ---------- Cell 4: Load code ----------
CELLS.append(code('''if not CLEAN_DATA_FILE.exists():
    raise FileNotFoundError(
        f"Cleaned data not found: {CLEAN_DATA_FILE}\\n"
        f"Please run Notebook 02 (Data Cleaning) first."
    )

df = load_csv(CLEAN_DATA_FILE)

print(f"Loaded: {CLEAN_DATA_FILE}")
print(f"Shape : {df.shape}")
print(f"Columns: {list(df.columns)}")
df.head()
'''))


# ---------- Cell 5: Snapshot markdown ----------
CELLS.append(md("""
## 2. Data Snapshot
"""))


# ---------- Cell 6: Snapshot code ----------
CELLS.append(code('''info = get_data_info(df, name="Clean Data")

print_section("CLEAN DATA INFO")
for k, v in info.items():
    if k in ("dtypes", "missing_values", "column_names"):
        continue
    print(f"{k:<20}: {v}")
'''))


# ---------- Cell 7: KPIs markdown ----------
CELLS.append(md("""
## 3. Overall KPIs
"""))


# ---------- Cell 8: KPIs code ----------
CELLS.append(code("""
kpis = overall_kpis(df)
print_kpis(kpis)
"""))


# ---------- Cell 9: Summary stats markdown ----------
CELLS.append(md("""
## 4. Summary Statistics (Numeric Columns)

Central tendency, spread, and range of numeric features.
"""))


# ---------- Cell 10: Summary stats code ----------
CELLS.append(code('''numeric_present = [c for c in NUMERIC_COLUMNS if c in df.columns]
summary = df[numeric_present].describe().T
summary["median"] = df[numeric_present].median()
summary["skew"]   = df[numeric_present].skew()
summary["kurt"]   = df[numeric_present].kurt()

print_section("NUMERIC SUMMARY")
display(summary.round(2))
'''))


# ---------- Cell 11: Distribution markdown ----------
CELLS.append(md("""
## 5. Distribution Analysis

Check the shape of key numeric columns.

Plot 1 and Plot 2 are produced and saved to `images/`.
"""))


# ---------- Cell 12: Distribution code ----------
CELLS.append(code('''ensure_dir(IMAGES_DIR)
setup_style()

p1 = plot_sales_distribution(df)
p2 = plot_profit_distribution(df)

print(f"Saved: {p1.name}")
print(f"Saved: {p2.name}")

from IPython.display import Image, display as disp
disp(Image(filename=str(p1), width=900))
disp(Image(filename=str(p2), width=900))
'''))


# ---------- Cell 13: Outliers markdown ----------
CELLS.append(md("""
## 6. Outlier Check (Boxplots)

Plot 16 — boxplots for Sales and Profit.
"""))


# ---------- Cell 14: Outliers code ----------
CELLS.append(code('''p16 = plot_boxplot_outliers(df)
print(f"Saved: {p16.name}")
disp(Image(filename=str(p16), width=900))
'''))


# ---------- Cell 15: Correlation markdown ----------
CELLS.append(md("""
## 7. Correlation Analysis

Plot 15 — heatmap of all numeric columns.
"""))


# ---------- Cell 16: Correlation code ----------
CELLS.append(code('''p15 = plot_correlation_heatmap(df)
print(f"Saved: {p15.name}")
disp(Image(filename=str(p15), width=850))

# Print top correlated pairs
corr = df.select_dtypes(include=[np.number]).corr()
corr_pairs = (
    corr.where(~np.eye(corr.shape[0], dtype=bool))
    .stack()
    .reset_index()
)
corr_pairs.columns = ["var1", "var2", "correlation"]

# Keep only unique pairs (var1 < var2)
unique_pairs = corr_pairs[corr_pairs["var1"] < corr_pairs["var2"]]
top_corr = unique_pairs.reindex(
    unique_pairs["correlation"].abs().sort_values(ascending=False).index
).head(10)

print_section("TOP CORRELATED PAIRS")
print(top_corr.to_string(index=False))
'''))


# ---------- Cell 17: Region markdown ----------
CELLS.append(md("""
## 8. Region Analysis

Plots 3 and 4 — region-wise sales and profit.
"""))


# ---------- Cell 18: Region table code ----------
CELLS.append(code('''region_df = region_wise_analysis(df)
print_section("REGION-WISE SUMMARY")
display(region_df)
'''))


# ---------- Cell 19: Region plots code ----------
CELLS.append(code('''p3 = plot_region_sales(df)
p4 = plot_region_profit(df)

print(f"Saved: {p3.name}")
print(f"Saved: {p4.name}")

disp(Image(filename=str(p3), width=900))
disp(Image(filename=str(p4), width=900))
'''))


# ---------- Cell 20: Category markdown ----------
CELLS.append(md("""
## 9. Category Analysis

Plot 5 — category-wise sales (bar + pie).
"""))


# ---------- Cell 21: Category table code ----------
CELLS.append(code('''category_df = category_wise_analysis(df)
print_section("CATEGORY-WISE SUMMARY")
display(category_df)
'''))


# ---------- Cell 22: Category plot code ----------
CELLS.append(code('''p5 = plot_category_sales(df)
print(f"Saved: {p5.name}")
disp(Image(filename=str(p5), width=900))
'''))


# ---------- Cell 23: Segment markdown ----------
CELLS.append(md("""
## 10. Segment Analysis

Plot 17 — segment-wise sales + orders.
"""))


# ---------- Cell 24: Segment table code ----------
CELLS.append(code('''segment_df = segment_wise_analysis(df)
print_section("SEGMENT-WISE SUMMARY")
display(segment_df)
'''))


# ---------- Cell 25: Segment plot code ----------
CELLS.append(code('''p17 = plot_customer_segment(df)
print(f"Saved: {p17.name}")
disp(Image(filename=str(p17), width=900))
'''))


# ---------- Cell 26: Product markdown ----------
CELLS.append(md("""
## 11. Product Analysis

Top 10 and Bottom 10 products by sales / profit.

Plots 8 and 9.
"""))


# ---------- Cell 27: Product tables code ----------
CELLS.append(code('''top_df = top_products(df, n=TOP_N)
bottom_df = bottom_products(df, n=BOTTOM_N)

print_section(f"TOP {TOP_N} PRODUCTS BY SALES")
display(top_df)

print_section(f"BOTTOM {BOTTOM_N} PRODUCTS BY PROFIT")
display(bottom_df)
'''))


# ---------- Cell 28: Product plots code ----------
CELLS.append(code('''p8 = plot_top_products(df, n=TOP_N)
p9 = plot_bottom_products(df, n=BOTTOM_N)

print(f"Saved: {p8.name}")
print(f"Saved: {p9.name}")

disp(Image(filename=str(p8), width=900))
disp(Image(filename=str(p9), width=900))
'''))


# ---------- Cell 29: Time series markdown ----------
CELLS.append(md("""
## 12. Time Series Analysis

Monthly and quarterly trends.

Plots 6 and 7.
"""))


# ---------- Cell 30: Time tables code ----------
CELLS.append(code('''monthly_df = monthly_sales_trend(df)
print_section("MONTHLY TREND (FIRST 12)")
display(monthly_df.head(12))

quarterly_df = quarterly_analysis(df)
print_section("QUARTERLY ANALYSIS")
display(quarterly_df)

yearly_df = yearly_analysis(df)
print_section("YEARLY ANALYSIS")
display(yearly_df)
'''))


# ---------- Cell 31: Time plots code ----------
CELLS.append(code('''p6 = plot_monthly_trend(df)
p7 = plot_quarterly_trend(df)

print(f"Saved: {p6.name}")
print(f"Saved: {p7.name}")

disp(Image(filename=str(p6), width=900))
disp(Image(filename=str(p7), width=900))
'''))


# ---------- Cell 32: Discount markdown ----------
CELLS.append(md("""
## 13. Discount Analysis

Impact of discount on profit.

Plots 10 and 11.
"""))


# ---------- Cell 33: Discount tables code ----------
CELLS.append(code('''discount_df = discount_impact(df)
print_section("DISCOUNT IMPACT")
display(discount_df)

band_df = discount_band_analysis(df)
print_section("DISCOUNT BAND ANALYSIS")
display(band_df)
'''))


# ---------- Cell 34: Discount plots code ----------
CELLS.append(code('''p10 = plot_discount_vs_profit(df)
p11 = plot_discount_band(df)

print(f"Saved: {p10.name}")
print(f"Saved: {p11.name}")

disp(Image(filename=str(p10), width=900))
disp(Image(filename=str(p11), width=900))
'''))


# ---------- Cell 35: Profit status markdown ----------
CELLS.append(md("""
## 14. Profit Status Analysis

Plot 12 — pie chart of Profit / Loss / Break-even.
"""))


# ---------- Cell 36: Profit status table code ----------
CELLS.append(code('''profit_status_df = profit_status_analysis(df)
print_section("PROFIT STATUS")
display(profit_status_df)
'''))


# ---------- Cell 37: Profit status plot code ----------
CELLS.append(code('''p12 = plot_profit_status_pie(df)
print(f"Saved: {p12.name}")
disp(Image(filename=str(p12), width=600))
'''))


# ---------- Cell 38: Season markdown ----------
CELLS.append(md("""
## 15. Season Analysis

Plot 13 — season-wise sales and profit.
"""))


# ---------- Cell 39: Season table code ----------
CELLS.append(code('''season_df = season_analysis(df)
print_section("SEASON ANALYSIS")
display(season_df)
'''))


# ---------- Cell 40: Season plot code ----------
CELLS.append(code('''p13 = plot_season_analysis(df)
print(f"Saved: {p13.name}")
disp(Image(filename=str(p13), width=900))
'''))


# ---------- Cell 41: Payment markdown ----------
CELLS.append(md("""
## 16. Payment Mode Analysis

Plot 14 — payment mode sales bar + pie.
"""))


# ---------- Cell 42: Payment table code ----------
CELLS.append(code('''payment_df = payment_mode_analysis(df)
print_section("PAYMENT MODE ANALYSIS")
display(payment_df)
'''))


# ---------- Cell 43: Payment plot code ----------
CELLS.append(code('''p14 = plot_payment_mode(df)
print(f"Saved: {p14.name}")
disp(Image(filename=str(p14), width=900))
'''))


# ---------- Cell 44: Weekday markdown ----------
CELLS.append(md("""
## 17. Weekday vs Weekend

Plot 18 — weekday vs weekend comparison.
"""))


# ---------- Cell 45: Weekday table code ----------
CELLS.append(code('''weekday_df = weekday_analysis(df)
print_section("WEEKDAY vs WEEKEND")
display(weekday_df)
'''))


# ---------- Cell 46: Weekday plot code ----------
CELLS.append(code('''p18 = plot_weekday_analysis(df)
print(f"Saved: {p18.name}")
disp(Image(filename=str(p18), width=900))
'''))


# ---------- Cell 47: Loss products markdown ----------
CELLS.append(md("""
## 18. Loss-Making Products
"""))


# ---------- Cell 48: Loss products code ----------
CELLS.append(code('''loss_df = loss_making_products(df)
print_section("LOSS-MAKING PRODUCTS")

if len(loss_df) == 0:
    print("No loss-making products found.")
else:
    display(loss_df)
'''))


# ---------- Cell 49: Batch markdown ----------
CELLS.append(md("""
## 19. Generate All Plots (Batch)

Runs all 18 plots in one shot and saves them to `images/`.
Useful for CI or when re-running after data changes.
"""))


# ---------- Cell 50: Batch code ----------
CELLS.append(code('''print_section("BATCH GENERATION")
saved_paths = create_all_plots(df)

print(f"\\nTotal plots saved: {len(saved_paths)}")
print_section("FILES IN IMAGES FOLDER")
for p in sorted(IMAGES_DIR.glob("*.png")):
    size_kb = p.stat().st_size / 1024
    print(f"  {p.name:<35} {size_kb:>7.1f} KB")
'''))


# ---------- Cell 51: Insights markdown ----------
CELLS.append(md("""
## 20. Key Insights

Consolidated findings from all EDA sections above.
"""))


# ---------- Cell 52: Insights code ----------
CELLS.append(code('''print_section("KEY INSIGHTS")

# Top region
top_region = region_df.iloc[0]
print(f"1. Top region by sales        : {top_region['Region']} "
      f"(Rs.{top_region['Total_Sales']:,.0f}, margin {top_region['Profit_Margin_%']}%)")

# Lowest margin region
low_margin_region = region_df.sort_values("Profit_Margin_%").iloc[0]
print(f"2. Lowest margin region       : {low_margin_region['Region']} "
      f"(margin {low_margin_region['Profit_Margin_%']}%)")

# Top category
top_category = category_df.iloc[0]
print(f"3. Top category by sales      : {top_category['Category']} "
      f"(Rs.{top_category['Total_Sales']:,.0f})")

# Best month
best_month = monthly_df.sort_values("Total_Sales", ascending=False).iloc[0]
print(f"4. Best month                 : {best_month['Year_Month']} "
      f"(Rs.{best_month['Total_Sales']:,.0f})")

# Discount impact
if len(band_df) > 0:
    loss_band = band_df[band_df["Total_Profit"] < 0]
    if len(loss_band) > 0:
        worst_band = loss_band.iloc[0]
        print(f"5. Loss-making discount band  : {worst_band['Discount_Band']} "
              f"(profit Rs.{worst_band['Total_Profit']:,.0f})")

# Loss products
print(f"6. Loss-making products count : {len(loss_df)}")

# Profit status
if len(profit_status_df) > 0:
    for _, row in profit_status_df.iterrows():
        print(f"   - {row['Profit_Status']:<12}: {row['Orders']:,} orders ({row['Orders_%']}%)")

# Top payment mode
top_payment = payment_df.iloc[0]
print(f"7. Top payment mode           : {top_payment['Payment_Mode']} "
      f"(Rs.{top_payment['Total_Sales']:,.0f})")

# Top customer
top_customer = customer_analysis(df, n=1).iloc[0]
print(f"8. Top customer               : {top_customer['Customer_Name']} "
      f"(Rs.{top_customer['Total_Sales']:,.0f})")

# Weekend vs weekday
if len(weekday_df) > 0:
    for _, row in weekday_df.iterrows():
        print(f"9. {row['Day_Type']:<10} sales        : Rs.{row['Total_Sales']:,.0f}")
'''))


# ---------- Cell 53: Summary markdown ----------
CELLS.append(md("""
## 21. Summary

### What was done
1. Loaded cleaned data
2. Computed summary statistics
3. Analyzed distributions, outliers, correlations
4. Analyzed region, category, segment dimensions
5. Analyzed products (top/bottom)
6. Analyzed time trends (monthly, quarterly, yearly)
7. Analyzed discount impact and bands
8. Analyzed profit status, season, payment, weekday
9. Generated 18 plots saved to `images/`
10. Extracted 9 key insights

### Outputs
- 18 PNG files in `images/`
- All summary tables printed inline
- Key insights for the final report
"""))


# ---------- Cell 54: Completion code ----------
CELLS.append(code('''print("=" * 60)
print("EDA COMPLETE")
print("=" * 60)
print(f"Rows analyzed  : {len(df):,}")
print(f"Columns        : {df.shape[1]}")
print(f"Plots saved    : {len(list(IMAGES_DIR.glob('*.png')))}")
print(f"Images folder  : {IMAGES_DIR}")
print("=" * 60)
print("Next: Notebook 05 - Final Insights")
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
    print("GENERATING NOTEBOOK 04 — EDA")
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