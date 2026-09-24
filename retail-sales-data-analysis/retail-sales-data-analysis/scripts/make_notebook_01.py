# ============================================
# Retail Sales Data Analysis
# File: scripts/make_notebook_01.py
# Purpose: Generate notebooks/01_data_understanding.ipynb
# ============================================

"""
Generates the first notebook in the project.

Run:
    python scripts/make_notebook_01.py

Output:
    notebooks/01_data_understanding.ipynb

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
OUTPUT_PATH = NOTEBOOKS_DIR / "01_data_understanding.ipynb"


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
# 01 - Data Understanding

**Project:** Retail Sales Data Analysis
**Purpose:** Load raw data and understand its structure, size, types, and quality.

---

## Objectives
1. Load raw CSV
2. Check shape, columns, data types
3. Check missing values and duplicates
4. Check value ranges for numeric columns
5. Explore categorical distributions
6. Decide the cleaning strategy
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

# Add project root to path so we can import from src/
PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Project modules
from config import (
    RAW_DATA_FILE,
    PROCESSED_DATA_DIR,
    OUTPUT_DIR,
    EXPECTED_COLUMNS,
    NUMERIC_COLUMNS,
    CATEGORICAL_COLUMNS,
    DATE_COLUMNS,
)
from data_loader import load_csv, get_data_info, preview_data
from utils import print_section

print("Project root :", PROJECT_ROOT)
print("Raw data file:", RAW_DATA_FILE)
print("File exists  :", RAW_DATA_FILE.exists())
"""))


# ---------- Cell 3: Load markdown ----------
CELLS.append(md("""
## 1. Load Raw Data

If the raw CSV is not present, we generate a synthetic dataset so the notebook
can still run end-to-end. Replace `USE_SYNTHETIC = False` once you have the real CSV.
"""))


# ---------- Cell 4: Load code ----------
CELLS.append(code("""
USE_SYNTHETIC = True   # set to False when you have the real dataset

if RAW_DATA_FILE.exists() and not USE_SYNTHETIC:
    df = load_csv(RAW_DATA_FILE)
    print(f"Loaded real dataset: {RAW_DATA_FILE.name}")
else:
    print("Real CSV not found or synthetic mode ON. Generating synthetic data...")

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

    # Inject some messiness for realistic cleaning
    df.loc[0:5, "Region"] = np.nan
    df.loc[10:12, "Category"] = np.nan
    df = pd.concat([df, df.iloc[0:5]], ignore_index=True)

    RAW_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_DATA_FILE, index=False)
    print(f"Synthetic dataset saved to: {RAW_DATA_FILE}")

print(f"\\nShape: {df.shape}")
df.head()
"""))


# ---------- Cell 5 ----------
CELLS.append(md("""
## 2. Basic Info

Shape, columns, data types, memory usage.
"""))


# ---------- Cell 6 ----------
CELLS.append(code("""
info = get_data_info(df, name="Raw Data")

print_section("DATA INFO")
for k, v in info.items():
    if k in ("dtypes", "missing_values"):
        continue
    print(f"{k:<20}: {v}")
"""))


# ---------- Cell 7 ----------
CELLS.append(code("""
print_section("COLUMN DATA TYPES")
print(df.dtypes.to_string())
"""))


# ---------- Cell 8 ----------
CELLS.append(md("""
## 3. Preview (Head / Tail / Sample)
"""))


# ---------- Cell 9 ----------
CELLS.append(code("""
preview_data(df, rows=5, name="Raw Data")
"""))


# ---------- Cell 10 ----------
CELLS.append(md("""
## 4. Missing Values Analysis

Check per-column missing counts and percentages.
"""))


# ---------- Cell 11 ----------
CELLS.append(code("""
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)

missing_df = pd.DataFrame({
    "missing_count": missing,
    "missing_pct": missing_pct,
}).sort_values("missing_count", ascending=False)

missing_df = missing_df[missing_df["missing_count"] > 0]

if len(missing_df) == 0:
    print("No missing values found.")
else:
    print(f"Columns with missing values: {len(missing_df)}")
    display(missing_df)
"""))


# ---------- Cell 12 ----------
CELLS.append(md("""
## 5. Duplicate Rows
"""))


# ---------- Cell 13 ----------
CELLS.append(code("""
total_dupes = df.duplicated().sum()
print(f"Total duplicate rows       : {total_dupes}")

# Order ID duplicates (business key)
if "Order ID" in df.columns:
    order_dupes = df.duplicated(subset=["Order ID"]).sum()
    print(f"Duplicate Order IDs        : {order_dupes}")

# Fully duplicated rows
if total_dupes > 0:
    display(df[df.duplicated(keep=False)].sort_values(list(df.columns)).head(10))
"""))


# ---------- Cell 14 ----------
CELLS.append(md("""
## 6. Numeric Columns - Statistical Summary
"""))


# ---------- Cell 15 ----------
CELLS.append(code("""
numeric_cols_present = [c for c in NUMERIC_COLUMNS if c in df.columns]
print_section("NUMERIC SUMMARY")
display(df[numeric_cols_present].describe().T)
"""))


# ---------- Cell 16 ----------
CELLS.append(code("""
print_section("NEGATIVE VALUE CHECK")
for col in numeric_cols_present:
    neg = (df[col] < 0).sum()
    print(f"{col:<15} negative values: {neg}")
"""))


# ---------- Cell 17 ----------
CELLS.append(md("""
## 7. Categorical Columns - Value Counts
"""))


# ---------- Cell 18 ----------
CELLS.append(code("""
cat_cols_present = [c for c in CATEGORICAL_COLUMNS if c in df.columns]

for col in cat_cols_present:
    print_section(f"{col} — unique: {df[col].nunique()}")
    print(df[col].value_counts(dropna=False).head(10).to_string())
    print()
"""))


# ---------- Cell 19 ----------
CELLS.append(md("""
## 8. Date Column Check
"""))


# ---------- Cell 20 ----------
CELLS.append(code("""
date_cols_present = [c for c in DATE_COLUMNS if c in df.columns]

for col in date_cols_present:
    parsed = pd.to_datetime(df[col], errors="coerce")
    invalid = parsed.isnull().sum()

    print_section(f"DATE COLUMN: {col}")
    print(f"Invalid values   : {invalid}")
    print(f"Earliest date    : {parsed.min()}")
    print(f"Latest date      : {parsed.max()}")
    print(f"Date span (days) : {(parsed.max() - parsed.min()).days}")
"""))


# ---------- Cell 21 ----------
CELLS.append(md("""
## 9. Missing vs Expected Columns

Compare what we have against the config's `EXPECTED_COLUMNS`.
Note: raw CSV uses display names ("Order ID") while config uses snake-case
("Order_Id"). We list what's actually present so the cleaning step can map.
"""))


# ---------- Cell 22 ----------
CELLS.append(code("""
print_section("ACTUAL COLUMNS IN RAW DATA")
for i, c in enumerate(df.columns, 1):
    print(f"{i:>2}. {c}")

print(f"\\nTotal columns: {len(df.columns)}")
print(f"Expected     : {len(EXPECTED_COLUMNS)}")
"""))


# ---------- Cell 23 ----------
CELLS.append(md("""
## 10. Data Quality Summary

A quick one-glance view of everything we found.
"""))


# ---------- Cell 24 ----------
CELLS.append(code("""
quality = {
    "total_rows":          len(df),
    "total_columns":       df.shape[1],
    "missing_values":      int(df.isnull().sum().sum()),
    "columns_with_missing": int((df.isnull().sum() > 0).sum()),
    "duplicate_rows":      int(df.duplicated().sum()),
    "numeric_columns":     len(numeric_cols_present),
    "categorical_columns": len(cat_cols_present),
    "date_columns":        len(date_cols_present),
    "memory_mb":           round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
}

print_section("DATA QUALITY SUMMARY")
for k, v in quality.items():
    print(f"{k:<25}: {v}")
"""))


# ---------- Cell 25 ----------
CELLS.append(md("""
## 11. Observations & Next Steps

Write down what you found. This becomes your cleaning checklist.

### Observations
- Raw column names use spaces and mixed case — need standardization.
- Missing values present in some categorical columns.
- Duplicate rows present — will be removed using Order ID.
- Sales and Profit are numeric; Discount is in percent form (0–40).
- Date column parses cleanly.

### Next Steps (File 02 - Data Cleaning)
1. Standardize column names → `Order_Id`, `Order_Date`, etc.
2. Drop duplicates on `Order_Id`.
3. Handle missing values per `config.DROP_IF_MISSING` / `FILL_*` rules.
4. Convert numeric columns (strip `Rs.`, `,`, `%`).
5. Parse `Order_Date` → datetime, extract Year/Month/Quarter/Weekday.
6. Remove negative sales / quantity rows.
7. Save to `data/processed/retail_sales_clean.csv`.
"""))


# ---------- Cell 26 ----------
CELLS.append(code("""
print("=" * 60)
print("DATA UNDERSTANDING COMPLETE")
print("=" * 60)
print(f"Rows               : {len(df):,}")
print(f"Columns            : {df.shape[1]}")
print(f"Missing values     : {int(df.isnull().sum().sum())}")
print(f"Duplicate rows     : {int(df.duplicated().sum())}")
print(f"Ready for cleaning : YES")
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
    print("GENERATING NOTEBOOK 01 — DATA UNDERSTANDING")
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