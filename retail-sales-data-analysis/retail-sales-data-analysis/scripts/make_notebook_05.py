# ============================================
# Retail Sales Data Analysis
# File: scripts/make_notebook_05.py
# Purpose: Generate notebooks/05_insights.ipynb
# ============================================

"""
Generates the fifth notebook in the project.

Run:
    python scripts/make_notebook_05.py

Output:
    notebooks/05_insights.ipynb

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
OUTPUT_PATH = NOTEBOOKS_DIR / "05_insights.ipynb"


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
# 05 - Final Insights & Recommendations

**Project:** Retail Sales Data Analysis
**Purpose:** Convert analysis results into business insights, recommendations, and an executive summary.

---

## Objectives
1. Load cleaned data
2. Re-run all analyses (reuse `analysis.py` functions)
3. Build an executive summary
4. Extract actionable insights per dimension
5. Generate recommendations
6. Write the final summary to `reports/insights_summary.md`
7. Print the completion status
"""))


# ---------- Cell 2: Imports ----------
CELLS.append(code("""
# Standard imports
import sys
import warnings
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# Project root setup
PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Project modules
from config import (
    CLEAN_DATA_FILE,
    OUTPUT_DIR,
    REPORTS_DIR,
    TOP_N,
    BOTTOM_N,
    CURRENCY_SYMBOL,
    MIN_DISCOUNT_ALERT,
)
from data_loader import load_csv
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
    high_discount_alert,
    run_all_analysis,
    print_kpis,
)
from utils import (
    print_section,
    ensure_dir,
    save_text,
    save_json,
    get_timestamp,
    format_currency,
    format_number,
    format_percent,
)

print("Project root :", PROJECT_ROOT)
print("Clean data   :", CLEAN_DATA_FILE)
print("Reports dir  :", REPORTS_DIR)
print("Output dir   :", OUTPUT_DIR)
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
df.head(3)
'''))


# ---------- Cell 5: Run all analyses markdown ----------
CELLS.append(md("""
## 2. Run All Analyses

One call to `run_all_analysis()` produces every summary table we need.
"""))


# ---------- Cell 6: Run all analyses code ----------
CELLS.append(code('''print_section("RUNNING ALL ANALYSES")
results = run_all_analysis(df)

print(f"\\nSections computed: {len(results)}")
for key in results.keys():
    value = results[key]
    if isinstance(value, pd.DataFrame):
        print(f"  {key:<20} -> DataFrame {value.shape}")
    elif isinstance(value, dict):
        print(f"  {key:<20} -> dict ({len(value)} keys)")
'''))


# ---------- Cell 7: Executive summary markdown ----------
CELLS.append(md("""
## 3. Executive Summary

Single-table view of the business at a glance.
"""))


# ---------- Cell 8: Executive summary code ----------
CELLS.append(code('''kpis = results["kpis"]

exec_summary = pd.DataFrame([
    {"Metric": "Total Revenue",       "Value": format_currency(kpis["total_sales"], CURRENCY_SYMBOL)},
    {"Metric": "Total Profit",        "Value": format_currency(kpis["total_profit"], CURRENCY_SYMBOL)},
    {"Metric": "Profit Margin",       "Value": format_percent(kpis["profit_margin_pct"])},
    {"Metric": "Total Orders",        "Value": format_number(kpis["total_orders"], 0)},
    {"Metric": "Total Quantity",      "Value": format_number(kpis["total_quantity"], 0)},
    {"Metric": "Avg Order Value",     "Value": format_currency(kpis["avg_order_value"], CURRENCY_SYMBOL)},
    {"Metric": "Avg Discount",        "Value": format_percent(kpis["avg_discount_pct"])},
    {"Metric": "Unique Customers",    "Value": format_number(kpis["unique_customers"], 0)},
    {"Metric": "Unique Products",     "Value": format_number(kpis["unique_products"], 0)},
])

print_section("EXECUTIVE SUMMARY")
display(exec_summary)
'''))


# ---------- Cell 9: Regional insights markdown ----------
CELLS.append(md("""
## 4. Regional Insights
"""))


# ---------- Cell 10: Regional insights code ----------
CELLS.append(code('''region_df = results["region"]
print_section("REGION PERFORMANCE")
display(region_df)

best_region_by_sales  = region_df.iloc[0]
best_region_by_profit = region_df.sort_values("Total_Profit", ascending=False).iloc[0]
worst_margin_region   = region_df.sort_values("Profit_Margin_%").iloc[0]

print(f"Best region by sales  : {best_region_by_sales['Region']} "
      f"({format_currency(best_region_by_sales['Total_Sales'], CURRENCY_SYMBOL)})")
print(f"Best region by profit : {best_region_by_profit['Region']} "
      f"({format_currency(best_region_by_profit['Total_Profit'], CURRENCY_SYMBOL)})")
print(f"Lowest margin region  : {worst_margin_region['Region']} "
      f"({format_percent(worst_margin_region['Profit_Margin_%'])})")
'''))


# ---------- Cell 11: Category insights markdown ----------
CELLS.append(md("""
## 5. Category Insights
"""))


# ---------- Cell 12: Category insights code ----------
CELLS.append(code('''category_df = results["category"]
print_section("CATEGORY PERFORMANCE")
display(category_df)

best_category = category_df.iloc[0]
print(f"Top category: {best_category['Category']} "
      f"({format_currency(best_category['Total_Sales'], CURRENCY_SYMBOL)}, "
      f"margin {format_percent(best_category['Profit_Margin_%'])})")
'''))


# ---------- Cell 13: Product insights markdown ----------
CELLS.append(md("""
## 6. Product Insights

Top performers + loss-making products.
"""))


# ---------- Cell 14: Product insights code ----------
CELLS.append(code('''top_df    = results["top_products"]
bottom_df = results["bottom_products"]
loss_df   = results["loss_products"]

print_section(f"TOP {TOP_N} PRODUCTS BY SALES")
display(top_df)

print_section(f"BOTTOM {BOTTOM_N} PRODUCTS BY PROFIT")
display(bottom_df)

print_section("LOSS-MAKING PRODUCTS")
if len(loss_df) == 0:
    print("No loss-making products.")
else:
    display(loss_df)
'''))


# ---------- Cell 15: Discount insights markdown ----------
CELLS.append(md("""
## 7. Discount Insights

Discount level and band analysis.
"""))


# ---------- Cell 16: Discount insights code ----------
CELLS.append(code('''discount_df = results["discount_impact"]
band_df     = results["discount_band"]

print_section("DISCOUNT IMPACT")
display(discount_df)

print_section("DISCOUNT BAND")
display(band_df)

loss_bands = band_df[band_df["Total_Profit"] < 0]
if len(loss_bands) > 0:
    print(f"\\nLoss-making discount bands: {list(loss_bands['Discount_Band'])}")
else:
    print("\\nNo loss-making discount band found.")
'''))


# ---------- Cell 17: Time trend markdown ----------
CELLS.append(md("""
## 8. Time Trend Insights
"""))


# ---------- Cell 18: Time trend code ----------
CELLS.append(code('''monthly_df   = results["monthly_trend"]
quarterly_df = results["quarterly"]
yearly_df    = results["yearly"]

print_section("MONTHLY TREND (FIRST 12)")
display(monthly_df.head(12))

print_section("YEARLY ANALYSIS")
display(yearly_df)

if len(monthly_df) > 0:
    best_month  = monthly_df.sort_values("Total_Sales", ascending=False).iloc[0]
    worst_month = monthly_df.sort_values("Total_Sales", ascending=True).iloc[0]
    print(f"Best month  : {best_month['Year_Month']} "
          f"({format_currency(best_month['Total_Sales'], CURRENCY_SYMBOL)})")
    print(f"Worst month : {worst_month['Year_Month']} "
          f"({format_currency(worst_month['Total_Sales'], CURRENCY_SYMBOL)})")
'''))


# ---------- Cell 19: Customer insights markdown ----------
CELLS.append(md("""
## 9. Customer Insights
"""))


# ---------- Cell 20: Customer insights code ----------
CELLS.append(code('''segment_df  = results["segment"]
customer_df = results["customers"]

print_section("SEGMENT PERFORMANCE")
display(segment_df)

print_section(f"TOP {TOP_N} CUSTOMERS")
display(customer_df)
'''))


# ---------- Cell 21: Payment + weekday markdown ----------
CELLS.append(md("""
## 10. Payment & Weekday Insights
"""))


# ---------- Cell 22: Payment + weekday code ----------
CELLS.append(code('''payment_df = results["payment_mode"]
weekday_df = results["weekday"]

print_section("PAYMENT MODE")
display(payment_df)

print_section("WEEKDAY vs WEEKEND")
display(weekday_df)
'''))


# ---------- Cell 23: Season markdown ----------
CELLS.append(md("""
## 11. Season Insights
"""))


# ---------- Cell 24: Season code ----------
CELLS.append(code('''season_df = results["season"]
print_section("SEASON PERFORMANCE")
display(season_df)
'''))


# ---------- Cell 25: Profit status markdown ----------
CELLS.append(md("""
## 12. Profit Status Breakdown
"""))


# ---------- Cell 26: Profit status code ----------
CELLS.append(code('''profit_status_df = results["profit_status"]
print_section("PROFIT STATUS")
display(profit_status_df)
'''))


# ---------- Cell 27: High discount markdown ----------
CELLS.append(md("""
## 13. High-Discount Alert

Orders where discount exceeds the configured threshold.
"""))


# ---------- Cell 28: High discount code ----------
CELLS.append(code('''alert_df = high_discount_alert(df)

print_section(f"HIGH DISCOUNT ALERT (>{int(MIN_DISCOUNT_ALERT * 100)}%)")
print(f"Orders flagged : {len(alert_df):,}")
print(f"Total sales    : {format_currency(alert_df['Sales'].sum(), CURRENCY_SYMBOL)}")
print(f"Total profit   : {format_currency(alert_df['Profit'].sum(), CURRENCY_SYMBOL)}")

if len(alert_df) > 0:
    display(alert_df.head(10))
'''))


# ---------- Cell 29: Recommendations markdown ----------
CELLS.append(md("""
## 14. Recommendation Engine

Rule-based recommendations derived from the analysis results.
Each row is a business action with supporting evidence.
"""))


# ---------- Cell 30: Recommendations code ----------
CELLS.append(code('''recommendations = []

# 14.1 Region with low margin
if len(region_df) > 0:
    low_margin = region_df.sort_values("Profit_Margin_%").iloc[0]
    if low_margin["Profit_Margin_%"] < 5:
        recommendations.append({
            "Area": "Region",
            "Target": low_margin["Region"],
            "Issue": f"Low profit margin ({low_margin['Profit_Margin_%']}%)",
            "Action": "Review discount policy and cost structure",
            "Priority": "High",
        })

# 14.2 Loss-making discount bands
if len(loss_bands) > 0:
    for _, row in loss_bands.iterrows():
        recommendations.append({
            "Area": "Discount",
            "Target": row["Discount_Band"],
            "Issue": f"Negative profit ({format_currency(row['Total_Profit'], CURRENCY_SYMBOL)})",
            "Action": "Reduce or cap discounts in this band",
            "Priority": "High",
        })

# 14.3 Loss-making products
if len(loss_df) > 0:
    for _, row in loss_df.head(5).iterrows():
        recommendations.append({
            "Area": "Product",
            "Target": row["Product_Name"],
            "Issue": f"Total loss {format_currency(row['Total_Profit'], CURRENCY_SYMBOL)}",
            "Action": "Review pricing, or discontinue",
            "Priority": "Medium",
        })

# 14.4 Best region - push harder
if len(region_df) > 0:
    best = region_df.iloc[0]
    recommendations.append({
        "Area": "Region",
        "Target": best["Region"],
        "Issue": "Best performing region",
        "Action": "Increase stock and marketing investment",
        "Priority": "Medium",
    })

# 14.5 Best category - push harder
if len(category_df) > 0:
    best = category_df.iloc[0]
    recommendations.append({
        "Area": "Category",
        "Target": best["Category"],
        "Issue": "Top revenue category",
        "Action": "Expand product range in this category",
        "Priority": "Medium",
    })

# 14.6 Top customer - retention
if len(customer_df) > 0:
    recommendations.append({
        "Area": "Customer",
        "Target": customer_df.iloc[0]["Customer_Name"],
        "Issue": "Top revenue customer",
        "Action": "Offer loyalty rewards to retain",
        "Priority": "Low",
    })

# 14.7 High discount orders
if len(alert_df) > 0:
    recommendations.append({
        "Area": "Pricing",
        "Target": f"{len(alert_df)} orders",
        "Issue": f"Discount exceeds {int(MIN_DISCOUNT_ALERT*100)}%",
        "Action": "Approve high discounts manually",
        "Priority": "High",
    })

rec_df = pd.DataFrame(recommendations)

print_section("RECOMMENDATIONS")
if len(rec_df) == 0:
    print("No recommendations triggered.")
else:
    display(rec_df)
'''))


# ---------- Cell 31: Key insights markdown ----------
CELLS.append(md("""
## 15. Key Insights (Auto-extracted)

One-line summaries that can be copied directly into the final report.
"""))


# ---------- Cell 32: Key insights code ----------
CELLS.append(code('''insights = []

# Overall
insights.append(
    f"Total revenue is {format_currency(kpis['total_sales'], CURRENCY_SYMBOL)} "
    f"with a profit margin of {format_percent(kpis['profit_margin_pct'])}."
)

# Region
if len(region_df) > 0:
    top = region_df.iloc[0]
    insights.append(
        f"{top['Region']} region leads with "
        f"{format_currency(top['Total_Sales'], CURRENCY_SYMBOL)} in sales."
    )

# Category
if len(category_df) > 0:
    top = category_df.iloc[0]
    insights.append(
        f"{top['Category']} is the top category "
        f"({format_currency(top['Total_Sales'], CURRENCY_SYMBOL)})."
    )

# Best month
if len(monthly_df) > 0:
    best = monthly_df.sort_values("Total_Sales", ascending=False).iloc[0]
    insights.append(
        f"{best['Year_Month']} was the strongest month "
        f"({format_currency(best['Total_Sales'], CURRENCY_SYMBOL)})."
    )

# Loss products
if len(loss_df) > 0:
    insights.append(
        f"{len(loss_df)} products are generating losses. "
        f"Biggest loss: {loss_df.iloc[0]['Product_Name']}."
    )

# Discount impact
if len(loss_bands) > 0:
    insights.append(
        f"Discount bands causing loss: {', '.join(loss_bands['Discount_Band'].tolist())}."
    )

# Profit status
if len(profit_status_df) > 0:
    for _, row in profit_status_df.iterrows():
        insights.append(
            f"{row['Profit_Status']}: {row['Orders']:,} orders ({row['Orders_%']}%)."
        )

# Payment mode
if len(payment_df) > 0:
    top = payment_df.iloc[0]
    insights.append(
        f"{top['Payment_Mode']} is the top payment mode "
        f"({format_currency(top['Total_Sales'], CURRENCY_SYMBOL)})."
    )

# Weekday
if len(weekday_df) > 0:
    for _, row in weekday_df.iterrows():
        insights.append(
            f"{row['Day_Type']}: {format_currency(row['Total_Sales'], CURRENCY_SYMBOL)} in sales."
        )

# Top customer
if len(customer_df) > 0:
    top = customer_df.iloc[0]
    insights.append(
        f"Top customer is {top['Customer_Name']} "
        f"({format_currency(top['Total_Sales'], CURRENCY_SYMBOL)})."
    )

print_section("KEY INSIGHTS")
for i, insight in enumerate(insights, 1):
    print(f"{i:>2}. {insight}")
'''))


# ---------- Cell 33: Export markdown ----------
CELLS.append(md("""
## 16. Export Insights to Files

Writes:
- `reports/insights_summary.md` — human-readable summary
- `output/insights.json` — machine-readable JSON
- `output/recommendations.csv` — recommendations table
- `output/executive_summary.csv` — executive summary table
"""))


# ---------- Cell 34: Export code ----------
CELLS.append(code('''ensure_dir(REPORTS_DIR)
ensure_dir(OUTPUT_DIR)

# ----- 16.1 Build markdown summary -----
lines = []
lines.append("# Retail Sales Data Analysis — Insights Summary")
lines.append("")
lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
lines.append("")
lines.append("---")
lines.append("")

# Executive summary
lines.append("## Executive Summary")
lines.append("")
lines.append("| Metric | Value |")
lines.append("|--------|-------|")
for _, row in exec_summary.iterrows():
    lines.append(f"| {row['Metric']} | {row['Value']} |")
lines.append("")

# Key insights
lines.append("## Key Insights")
lines.append("")
for i, insight in enumerate(insights, 1):
    lines.append(f"{i}. {insight}")
lines.append("")

# Recommendations
lines.append("## Recommendations")
lines.append("")
if len(rec_df) == 0:
    lines.append("_No recommendations triggered._")
else:
    lines.append("| Area | Target | Issue | Action | Priority |")
    lines.append("|------|--------|-------|--------|----------|")
    for _, row in rec_df.iterrows():
        lines.append(
            f"| {row['Area']} | {row['Target']} | "
            f"{row['Issue']} | {row['Action']} | {row['Priority']} |"
        )
lines.append("")

# Appendix
lines.append("## Appendix — Data Source")
lines.append("")
lines.append(f"- Cleaned data: `{CLEAN_DATA_FILE.name}`")
lines.append(f"- Rows analyzed: {len(df):,}")
lines.append(f"- Columns: {df.shape[1]}")
lines.append(f"- API used: No")
lines.append(f"- Data source: CSV file (static)")
lines.append("")

markdown_text = "\\n".join(lines)

# ----- 16.2 Save markdown -----
md_path = REPORTS_DIR / "insights_summary.md"
save_text(markdown_text, md_path)

# ----- 16.3 Save JSON -----
json_data = {
    "generated_at": datetime.now().isoformat(),
    "kpis": kpis,
    "insights": insights,
    "recommendations": rec_df.to_dict(orient="records") if len(rec_df) > 0 else [],
    "executive_summary": exec_summary.to_dict(orient="records"),
    "meta": {
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "api_used": False,
        "data_source": "CSV",
    },
}
json_path = OUTPUT_DIR / "insights.json"
save_json(json_data, json_path)

# ----- 16.4 Save CSVs -----
rec_path = OUTPUT_DIR / "recommendations.csv"
exec_path = OUTPUT_DIR / "executive_summary.csv"

rec_df.to_csv(rec_path, index=False)
exec_summary.to_csv(exec_path, index=False)

print_section("EXPORTED FILES")
print(f"Markdown        : {md_path}")
print(f"JSON            : {json_path}")
print(f"Recommendations : {rec_path}")
print(f"Exec summary    : {exec_path}")
'''))


# ---------- Cell 35: Preview markdown ----------
CELLS.append(md("""
## 17. Preview the Markdown Report

Displays the generated `insights_summary.md`.
"""))


# ---------- Cell 36: Preview code ----------
CELLS.append(code('''from IPython.display import Markdown, display as disp

print_section("INSIGHTS SUMMARY PREVIEW")
disp(Markdown(markdown_text))
'''))


# ---------- Cell 37: Checklist markdown ----------
CELLS.append(md("""
## 18. Findings Checklist

Final YES/NO validation of what was found.
"""))


# ---------- Cell 38: Checklist code ----------
CELLS.append(code('''checklist = [
    ("Data loaded and cleaned", CLEAN_DATA_FILE.exists()),
    ("Overall KPIs computed", "total_sales" in kpis and kpis["total_sales"] > 0),
    ("Region analysis done", len(region_df) > 0),
    ("Category analysis done", len(category_df) > 0),
    ("Top products identified", len(top_df) > 0),
    ("Loss-making products identified", len(loss_df) > 0),
    ("Discount impact analyzed", len(discount_df) > 0 and len(band_df) > 0),
    ("Time trends analyzed", len(monthly_df) > 0),
    ("Customer analysis done", len(customer_df) > 0),
    ("Payment mode analyzed", len(payment_df) > 0),
    ("Insights generated", len(insights) > 0),
    ("Recommendations generated", len(rec_df) > 0),
    ("Summary markdown exported", md_path.exists()),
    ("JSON exported", json_path.exists()),
    ("No API used", True),
]

check_df = pd.DataFrame(checklist, columns=["Check", "Passed"])
check_df["Passed"] = check_df["Passed"].map({True: "YES", False: "NO"})

print_section("FINDINGS CHECKLIST")
display(check_df)

passed = (check_df["Passed"] == "YES").sum()
total  = len(check_df)
print(f"\\nPassed: {passed}/{total}")
'''))


# ---------- Cell 39: Summary markdown ----------
CELLS.append(md("""
## 19. Summary

### Deliverables produced by this notebook
1. Executive summary table
2. Per-dimension insights
3. Rule-based recommendations
4. `reports/insights_summary.md`
5. `output/insights.json`
6. `output/recommendations.csv`
7. `output/executive_summary.csv`

### Project is ready for
- Final report writing
- PPT preparation
- Dashboard building
- Portfolio / resume use
"""))


# ---------- Cell 40: Completion code ----------
CELLS.append(code('''print("=" * 60)
print("FINAL INSIGHTS COMPLETE")
print("=" * 60)
print(f"Insights generated      : {len(insights)}")
print(f"Recommendations         : {len(rec_df)}")
print(f"Markdown summary        : {md_path.name}")
print(f"JSON export             : {json_path.name}")
print(f"Checklist passed        : {passed}/{total}")
print(f"API used                : No")
print("=" * 60)
print("Project complete.")
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
    print("GENERATING NOTEBOOK 05 — FINAL INSIGHTS")
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