# ============================================
# Retail Sales Data Analysis
# File: scripts/make_notebook_02.py
# Purpose: Generate notebooks/02_data_cleaning.ipynb
# ============================================

"""
Generates the second notebook in the project.

Run:
    python scripts/make_notebook_02.py

Output:
    notebooks/02_data_cleaning.ipynb

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
OUTPUT_PATH = NOTEBOOKS_DIR / "02_data_cleaning.ipynb"


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
# 02 - Data Cleaning

**Project:** Retail Sales Data Analysis
**Purpose:** Clean the raw data using the project's cleaning pipeline and validate it.

---

## Objectives
1. Load raw data
2. Standardize column names
3. Drop duplicates
4. Handle missing values
5. Convert data types (strip `Rs.`, `,`, `%`)
6. Parse dates + extract date features
7. Remove negative / invalid rows
8. Validate cleaned data
9. Save to `data/processed/retail_sales_clean.csv`
"""))


# ---------- Cell 2: Imports ----------
CELLS.append(code("""
# Standard imports
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# Project root setup
PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Project modules
from config import (
    RAW_DATA_FILE,
    CLEAN_DATA_FILE,
    PROCESSED_DATA_DIR,
    NUMERIC_COLUMNS,
    DATE_COLUMNS,
)
from data_loader import load_csv, get_data_info, preview_data
from data_cleaning import (
    standardize_columns,
    drop_duplicates_safe,
    handle_missing_values,
    convert_data_types,
    parse_dates,
    remove_negative_sales,
    detect_outliers_iqr,
    remove_outliers,
    validate_data,
    print_validation_report,
    clean_pipeline,
    save_cleaned_data,
)
from utils import print_section

print("Project root :", PROJECT_ROOT)
print("Raw data file:", RAW_DATA_FILE)
print("Clean out    :", CLEAN_DATA_FILE)
print("Raw exists   :", RAW_DATA_FILE.exists())
"""))


# ---------- Cell 3: Load markdown ----------
CELLS.append(md("""
## 1. Load Raw Data

If the raw CSV is missing, we regenerate a synthetic one (same seed as Notebook 01)
so this notebook is reproducible without external files.
"""))


# ---------- Cell 4: Load code ----------
CELLS.append(code('''def make_synthetic_raw() -> pd.DataFrame:
    """Generate the same synthetic raw dataset used in Notebook 01."""
    np.random.seed(42)
    n = 1500

    regions = ["North", "South", "East", "West"]
    categories = ["Furniture", "Technology", "Office Supplies"]
    segments = ["Consumer", "Corporate", "Home Office"]
    payments = ["UPI", "Card", "Cash", "Net Banking"]
    states = {
        "North": ["Delhi", "Punjab", "Haryana", "UP"],
        "South": ["Karnataka", "Tamil Nadu", "Kerala", "Telangana"],
        "East":  ["West Bengal", "Odisha", "Bihar", "Jharkhand"],
        "West":  ["Maharashtra", "Gujarat", "Rajasthan", "Goa"],
    }
    cities = {
        "Delhi": "New Delhi", "Punjab": "Ludhiana",
        "Haryana": "Gurgaon", "UP": "Lucknow",
        "Karnataka": "Bangalore", "Tamil Nadu": "Chennai",
        "Kerala": "Kochi", "Telangana": "Hyderabad",
        "West Bengal": "Kolkata", "Odisha": "Bhubaneswar",
        "Bihar": "Patna", "Jharkhand": "Ranchi",
        "Maharashtra": "Mumbai", "Gujarat": "Ahmedabad",
        "Rajasthan": "Jaipur", "Goa": "Panaji",
    }

    dates = pd.date_range("2022-01-01", "2024-12-31", freq="D")
    sample_dates = np.random.choice(dates, n)

    region_col = np.random.choice(regions, n)
    state_col = [np.random.choice(states[r]) for r in region_col]
    city_col = [cities[s] for s in state_col]

    df = pd.DataFrame({
        "Order ID": [f"ORD{10000 + i}" for i in range(n)],
        "Order Date": sample_dates,
        "Customer Name": np.random.choice([f"Customer_{i}" for i in range(150)], n),
        "Segment": np.random.choice(segments, n),
        "Region": region_col,
        "State": state_col,
        "City": city_col,
        "Product Name": np.random.choice([f"Product_{i}" for i in range(60)], n),
        "Category": np.random.choice(categories, n),
        "Quantity": np.random.randint(1, 12, n),
        "Unit Price": np.round(np.random.uniform(100, 5000, n), 2),
        "Discount": np.random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40], n),
        "Payment Mode": np.random.choice(payments, n),
    })
    df["Sales"] = np.round(df["Quantity"] * df["Unit Price"], 2)
    df["Profit"] = np.round(df["Sales"] * (0.22 - df["Discount"] / 100.0), 2)

    df.loc[0:5, "Region"] = np.nan
    df.loc[10:12, "Category"] = np.nan
    df = pd.concat([df, df.iloc[0:5]], ignore_index=True)
    return df


if RAW_DATA_FILE.exists():
    raw_df = load_csv(RAW_DATA_FILE)
    print(f"Loaded raw data from: {RAW_DATA_FILE}")
else:
    print("Raw data not found. Generating synthetic raw data...")
    raw_df = make_synthetic_raw()
    RAW_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    raw_df.to_csv(RAW_DATA_FILE, index=False)
    print(f"Synthetic raw data saved to: {RAW_DATA_FILE}")

print(f"\\nRaw shape: {raw_df.shape}")
raw_df.head()
'''))


# ---------- Cell 5: Raw snapshot markdown ----------
CELLS.append(md("""
## 2. Raw Data Snapshot

Baseline metrics before cleaning.
"""))


# ---------- Cell 6: Raw snapshot code ----------
CELLS.append(code("""
raw_info = get_data_info(raw_df, name="Raw")

print_section("BEFORE CLEANING")
print(f"Rows             : {raw_info['rows']:,}")
print(f"Columns          : {raw_info['columns']}")
print(f"Missing values   : {raw_info['total_missing']:,}")
print(f"Duplicate rows   : {raw_info['duplicates']:,}")
print(f"Memory           : {raw_info['memory_usage_mb']} MB")
print(f"\\nColumns: {raw_info['column_names']}")
"""))


# ---------- Cell 7: Step-by-step intro ----------
CELLS.append(md("""
## 3. Step-by-Step Cleaning

We apply each cleaning step individually so the effect of each step is visible.

### 3.1 Standardize column names

`Order ID` → `Order_Id`, `Order Date` → `Order_Date`, and so on.
"""))


# ---------- Cell 8: Standardize columns ----------
CELLS.append(code("""
step_df = raw_df.copy()

step_df = standardize_columns(step_df)
print(f"After standardize_columns | Shape: {step_df.shape}")
print(f"Columns: {list(step_df.columns)}")
step_df.head(3)
"""))


# ---------- Cell 9: Drop dupes markdown ----------
CELLS.append(md("""
### 3.2 Drop duplicates

Uses `Order_Id` as the business key (falls back to full-row dedupe if missing).
"""))


# ---------- Cell 10: Drop dupes code ----------
CELLS.append(code("""
before = len(step_df)
step_df = drop_duplicates_safe(step_df)
after = len(step_df)

print(f"Rows: {before:,} -> {after:,} | Removed: {before - after}")
"""))


# ---------- Cell 11: Missing values markdown ----------
CELLS.append(md("""
### 3.3 Handle missing values

Rules come from `config.py`:
- `DROP_IF_MISSING`         → drop rows
- `FILL_ZERO_IF_MISSING`    → fill with 0
- `FILL_UNKNOWN_IF_MISSING` → fill with `"Unknown"`
- Remaining numeric → median
- Remaining object  → `"Unknown"`
"""))


# ---------- Cell 12: Missing values code ----------
CELLS.append(code("""
before_missing = int(step_df.isnull().sum().sum())
before_rows = len(step_df)

step_df = handle_missing_values(step_df)

after_missing = int(step_df.isnull().sum().sum())
after_rows = len(step_df)

print(f"Missing: {before_missing} -> {after_missing}")
print(f"Rows   : {before_rows} -> {after_rows}")
"""))


# ---------- Cell 13: Convert types markdown ----------
CELLS.append(md("""
### 3.4 Convert data types

Strips `Rs.`, `$`, `,`, `%` from numeric-like strings and casts to numeric.
Also handles 0–1 discounts → percentage.
"""))


# ---------- Cell 14: Convert types code ----------
CELLS.append(code("""
step_df = convert_data_types(step_df)

print("Data types after conversion:")
print(step_df[NUMERIC_COLUMNS].dtypes.to_string())
"""))


# ---------- Cell 15: Parse dates markdown ----------
CELLS.append(md("""
### 3.5 Parse dates and add date features

Adds: `Year`, `Month`, `Month_Name`, `Quarter`, `Weekday`.

Invalid dates are dropped (rare, logged).
"""))


# ---------- Cell 16: Parse dates code ----------
CELLS.append(code("""
before = len(step_df)
step_df = parse_dates(step_df)
after = len(step_df)

print(f"Rows after date parsing: {before} -> {after}")
date_feats = [c for c in step_df.columns if c in ['Year','Month','Month_Name','Quarter','Weekday']]
print(f"New columns: {date_feats}")
"""))


# ---------- Cell 17: Remove invalid markdown ----------
CELLS.append(md("""
### 3.6 Remove negative / invalid rows

Drops rows where `Sales <= 0` or `Quantity <= 0`.
"""))


# ---------- Cell 18: Remove invalid code ----------
CELLS.append(code("""
before = len(step_df)
step_df = remove_negative_sales(step_df)
after = len(step_df)

print(f"Rows: {before:,} -> {after:,} | Removed: {before - after}")
"""))


# ---------- Cell 19: Outliers markdown ----------
CELLS.append(md("""
### 3.7 Outlier detection (report only)

We detect outliers using IQR but do **not** remove them by default.
Rationale: extreme orders are real business events (bulk purchases, big deals)
and should stay in analysis.
"""))


# ---------- Cell 20: Outliers code ----------
CELLS.append(code("""
outlier_report = {}
for col in ["Sales", "Profit"]:
    if col in step_df.columns:
        mask = detect_outliers_iqr(step_df, col)
        outlier_report[col] = int(mask.sum())

print_section("OUTLIER REPORT (IQR)")
for col, count in outlier_report.items():
    pct = round(count / len(step_df) * 100, 2)
    print(f"{col:<10} outliers: {count:>5} ({pct}%)")
"""))


# ---------- Cell 21: Full pipeline markdown ----------
CELLS.append(md("""
## 4. Full Pipeline (one-shot)

Now we re-run everything through `clean_pipeline()` for a single-shot reproducible result.
"""))


# ---------- Cell 22: Full pipeline code ----------
CELLS.append(code("""
print_section("RUNNING FULL PIPELINE")
clean_df = clean_pipeline(raw_df, remove_out=False)

print(f"\\nRaw shape   : {raw_df.shape}")
print(f"Clean shape : {clean_df.shape}")
print(f"Columns added: {clean_df.shape[1] - raw_df.shape[1]}")
"""))


# ---------- Cell 23: Validation markdown ----------
CELLS.append(md("""
## 5. Validation

Run the built-in validator to confirm the cleaned data is ready for analysis.
"""))


# ---------- Cell 24: Validation code ----------
CELLS.append(code("""
report = validate_data(clean_df)
print_validation_report(report)
"""))


# ---------- Cell 25: Preview markdown ----------
CELLS.append(md("""
## 6. Clean Data Preview
"""))


# ---------- Cell 26: Preview code ----------
CELLS.append(code("""
preview_data(clean_df, rows=5, name="Clean Data")
"""))


# ---------- Cell 27: Comparison markdown ----------
CELLS.append(md("""
## 7. Before vs After Comparison
"""))


# ---------- Cell 28: Comparison code ----------
CELLS.append(code("""
comparison = pd.DataFrame({
    "metric": [
        "Rows",
        "Columns",
        "Missing values",
        "Duplicate rows",
        "Numeric columns",
        "Date parsed",
    ],
    "raw": [
        len(raw_df),
        raw_df.shape[1],
        int(raw_df.isnull().sum().sum()),
        int(raw_df.duplicated().sum()),
        len(raw_df.select_dtypes(include=[np.number]).columns),
        "No",
    ],
    "clean": [
        len(clean_df),
        clean_df.shape[1],
        int(clean_df.isnull().sum().sum()),
        int(clean_df.duplicated().sum()),
        len(clean_df.select_dtypes(include=[np.number]).columns),
        "Yes",
    ],
})

print_section("BEFORE vs AFTER")
print(comparison.to_string(index=False))
"""))


# ---------- Cell 29: Save markdown ----------
CELLS.append(md("""
## 8. Save Cleaned Data

Saves to `data/processed/retail_sales_clean.csv`.
"""))


# ---------- Cell 30: Save code ----------
CELLS.append(code("""
save_cleaned_data(clean_df, output_path=CLEAN_DATA_FILE)

alt_path = PROJECT_ROOT / "output" / "retail_sales_clean.csv"
alt_path.parent.mkdir(parents=True, exist_ok=True)
clean_df.to_csv(alt_path, index=False)

print(f"Saved: {CLEAN_DATA_FILE}")
print(f"Saved: {alt_path}")
print(f"File exists: {CLEAN_DATA_FILE.exists()}")
"""))


# ---------- Cell 31: Summary markdown ----------
CELLS.append(md("""
## 9. Cleaning Summary

### What was done
1. Standardized column names
2. Dropped duplicates on `Order_Id`
3. Handled missing values (drop / fill 0 / fill Unknown / median)
4. Converted numeric columns (stripped symbols, cast to numeric)
5. Parsed dates and added Year / Month / Month_Name / Quarter / Weekday
6. Removed negative / invalid sales and quantity rows
7. Detected (but kept) outliers

### What's next
- Notebook 03 — SQL analysis
- Notebook 04 — EDA & visualization
- Notebook 05 — Final insights
"""))


# ---------- Cell 32: Completion code ----------
CELLS.append(code("""
print("=" * 60)
print("DATA CLEANING COMPLETE")
print("=" * 60)
print(f"Raw rows      : {len(raw_df):,}")
print(f"Clean rows    : {len(clean_df):,}")
print(f"Clean columns : {clean_df.shape[1]}")
print(f"Missing values: {int(clean_df.isnull().sum().sum())}")
print(f"Duplicates    : {int(clean_df.duplicated().sum())}")
print(f"Saved to      : {CLEAN_DATA_FILE}")
print("=" * 60)
"""))


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
    print("GENERATING NOTEBOOK 02 — DATA CLEANING")
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