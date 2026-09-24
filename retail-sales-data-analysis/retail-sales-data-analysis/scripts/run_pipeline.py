# ============================================
# Retail Sales Data Analysis
# File: scripts/run_pipeline.py
# Purpose: Master script — runs the entire pipeline end-to-end
# ============================================

"""
Master pipeline script.

Runs every stage of the project in order:
    1. Setup directories
    2. Load raw data (or generate synthetic if missing)
    3. Clean data
    4. Engineer features
    5. Run analysis
    6. Generate visualizations
    7. Save results to SQLite
    8. Export CSV/JSON outputs
    9. Print summary

Usage:
    python scripts/run_pipeline.py
    python scripts/run_pipeline.py --synthetic
    python scripts/run_pipeline.py --skip-plots
    python scripts/run_pipeline.py --skip-sql

No API is used anywhere in this pipeline.
"""

import argparse
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ============================================
# PROJECT ROOT + SRC PATH
# ============================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# ============================================
# PROJECT IMPORTS
# ============================================

from config import (
    RAW_DATA_FILE,
    CLEAN_DATA_FILE,
    SQLITE_DB_PATH,
    TABLE_NAME,
    OUTPUT_DIR,
    IMAGES_DIR,
    REPORTS_DIR,
    PROCESSED_DATA_DIR,
    create_all_directories,
)
from data_loader import load_csv, save_to_csv, save_to_sql, get_data_info
from data_cleaning import clean_pipeline, validate_data, print_validation_report
from feature_engineering import engineer_features
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
from visualization import create_all_plots
from utils import (
    print_section,
    ensure_dir,
    save_json,
    Timer,
    format_currency,
    format_number,
    format_percent,
)

# ============================================
# CONSTANTS
# ============================================

SEPARATOR = "=" * 70


# ============================================
# 1. SYNTHETIC DATA GENERATOR
# ============================================

def generate_synthetic_raw(n: int = 1500, seed: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic raw dataset for demonstration.
    Used only when the real raw CSV is missing.
    """
    np.random.seed(seed)

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
        "Order ID":      [f"ORD{10000 + i}" for i in range(n)],
        "Order Date":    sample_dates,
        "Customer Name": np.random.choice(
            [f"Customer_{i}" for i in range(150)], n
        ),
        "Segment":       np.random.choice(segments, n),
        "Region":        region_col,
        "State":         state_col,
        "City":          city_col,
        "Product Name":  np.random.choice(
            [f"Product_{i}" for i in range(60)], n
        ),
        "Category":      np.random.choice(categories, n),
        "Quantity":      np.random.randint(1, 12, n),
        "Unit Price":    np.round(np.random.uniform(100, 5000, n), 2),
        "Discount":      np.random.choice(
            [0, 5, 10, 15, 20, 25, 30, 35, 40], n
        ),
        "Payment Mode":  np.random.choice(payments, n),
    })

    df["Sales"]  = np.round(df["Quantity"] * df["Unit Price"], 2)
    df["Profit"] = np.round(
        df["Sales"] * (0.22 - df["Discount"] / 100.0), 2
    )

    # Inject some messiness for realistic cleaning
    df.loc[0:5, "Region"] = np.nan
    df.loc[10:12, "Category"] = np.nan
    df = pd.concat([df, df.iloc[0:5]], ignore_index=True)

    return df


# ============================================
# 2. STEP FUNCTIONS
# ============================================

def step_setup() -> None:
    """Create project directories."""
    print_section("STEP 0 — SETUP DIRECTORIES")
    create_all_directories()
    ensure_dir(OUTPUT_DIR)
    ensure_dir(IMAGES_DIR)
    ensure_dir(REPORTS_DIR)
    ensure_dir(PROCESSED_DATA_DIR)
    print("  Directories ready.")
    print(f"  Project root : {PROJECT_ROOT}")


def step_load_raw(force_synthetic: bool = False) -> pd.DataFrame:
    """Load raw data. Generate synthetic if missing or forced."""
    print_section("STEP 1 — LOAD RAW DATA")

    if force_synthetic or not RAW_DATA_FILE.exists():
        if force_synthetic:
            print("  Forced synthetic mode.")
        else:
            print(f"  Raw file not found: {RAW_DATA_FILE}")
        print("  Generating synthetic raw data...")
        raw_df = generate_synthetic_raw()
        RAW_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        raw_df.to_csv(RAW_DATA_FILE, index=False)
        print(f"  Synthetic raw data saved: {RAW_DATA_FILE}")
    else:
        raw_df = load_csv(RAW_DATA_FILE)
        print(f"  Loaded raw data: {RAW_DATA_FILE}")

    info = get_data_info(raw_df, name="Raw")
    print(f"  Shape       : {info['rows']:,} rows x {info['columns']} columns")
    print(f"  Missing     : {info['total_missing']:,}")
    print(f"  Duplicates  : {info['duplicates']:,}")
    print(f"  Memory      : {info['memory_usage_mb']} MB")
    return raw_df


def step_clean(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw data."""
    print_section("STEP 2 — CLEAN DATA")

    with Timer("clean_pipeline", log=False) as t:
        clean_df = clean_pipeline(raw_df, remove_out=False)

    print(f"  Rows after cleaning : {len(clean_df):,}")
    print(f"  Columns             : {clean_df.shape[1]}")
    print(f"  Time                : {t.elapsed:.2f}s")

    report = validate_data(clean_df)
    print(f"  Validation          : "
          f"{'PASSED' if report['valid'] else 'FAILED'}")

    if not report["valid"]:
        print("  Issues:")
        for issue in report["issues"]:
            print(f"    - {issue}")

    return clean_df


def step_engineer_features(clean_df: pd.DataFrame) -> pd.DataFrame:
    """Add derived features."""
    print_section("STEP 3 — FEATURE ENGINEERING")

    before = clean_df.shape[1]
    with Timer("engineer_features", log=False) as t:
        feature_df = engineer_features(clean_df)

    after = feature_df.shape[1]
    print(f"  Columns added : {after - before}")
    print(f"  Total columns : {after}")
    print(f"  Time          : {t.elapsed:.2f}s")
    return feature_df


def step_save_clean(feature_df: pd.DataFrame) -> None:
    """Save cleaned dataset to CSV."""
    print_section("STEP 4 — SAVE CLEANED DATA")

    CLEAN_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    feature_df.to_csv(CLEAN_DATA_FILE, index=False)
    print(f"  Saved: {CLEAN_DATA_FILE}")

    alt_path = OUTPUT_DIR / "retail_sales_clean.csv"
    feature_df.to_csv(alt_path, index=False)
    print(f"  Saved: {alt_path}")


def step_save_sql(feature_df: pd.DataFrame) -> None:
    """Push data into SQLite."""
    print_section("STEP 5 — SAVE TO SQLITE")

    if SQLITE_DB_PATH.exists():
        SQLITE_DB_PATH.unlink()
        print(f"  Removed old DB: {SQLITE_DB_PATH.name}")

    save_to_sql(feature_df, table_name=TABLE_NAME, if_exists="replace")
    print(f"  Table   : {TABLE_NAME}")
    print(f"  Rows    : {len(feature_df):,}")
    print(f"  DB path : {SQLITE_DB_PATH}")


def step_analysis(feature_df: pd.DataFrame) -> dict:
    """Run all analyses and return results."""
    print_section("STEP 6 — RUN ANALYSIS")

    results = {}

    with Timer("analysis", log=False) as t:
        results["kpis"]            = overall_kpis(feature_df)
        results["region"]          = region_wise_analysis(feature_df)
        results["category"]        = category_wise_analysis(feature_df)
        results["segment"]         = segment_wise_analysis(feature_df)
        results["product"]         = product_wise_analysis(feature_df)
        results["top_products"]    = top_products(feature_df)
        results["bottom_products"] = bottom_products(feature_df)
        results["monthly_trend"]   = monthly_sales_trend(feature_df)
        results["quarterly"]       = quarterly_analysis(feature_df)
        results["yearly"]          = yearly_analysis(feature_df)
        results["discount"]        = discount_impact(feature_df)
        results["discount_band"]   = discount_band_analysis(feature_df)
        results["profit_status"]   = profit_status_analysis(feature_df)
        results["season"]          = season_analysis(feature_df)
        results["weekday"]         = weekday_analysis(feature_df)
        results["customers"]       = customer_analysis(feature_df)
        results["payment_mode"]    = payment_mode_analysis(feature_df)
        results["loss_products"]   = loss_making_products(feature_df)

    print(f"  Sections computed : {len(results)}")
    print(f"  Time              : {t.elapsed:.2f}s")

    print_kpis(results["kpis"])
    return results


def step_visualize(feature_df: pd.DataFrame) -> list:
    """Generate all plots."""
    print_section("STEP 7 — GENERATE VISUALIZATIONS")

    with Timer("create_all_plots", log=False) as t:
        saved = create_all_plots(feature_df)

    print(f"  Plots saved : {len(saved)}")
    print(f"  Time        : {t.elapsed:.2f}s")
    print(f"  Folder      : {IMAGES_DIR}")
    return saved


def step_export(results: dict) -> None:
    """Export CSV outputs."""
    print_section("STEP 8 — EXPORT RESULTS")

    ensure_dir(OUTPUT_DIR)

    exports = {
        "sql_kpis.csv":            pd.DataFrame([results["kpis"]]),
        "sql_region.csv":          results["region"],
        "sql_category.csv":        results["category"],
        "sql_segment.csv":         results["segment"],
        "sql_product.csv":         results["product"],
        "sql_top_products.csv":    results["top_products"],
        "sql_bottom_products.csv": results["bottom_products"],
        "sql_monthly_trend.csv":   results["monthly_trend"],
        "sql_quarterly.csv":       results["quarterly"],
        "sql_yearly.csv":          results["yearly"],
        "sql_discount.csv":        results["discount"],
        "sql_discount_band.csv":   results["discount_band"],
        "sql_profit_status.csv":   results["profit_status"],
        "sql_season.csv":          results["season"],
        "sql_weekday.csv":         results["weekday"],
        "sql_customers.csv":       results["customers"],
        "sql_payment_mode.csv":    results["payment_mode"],
        "sql_loss_products.csv":   results["loss_products"],
    }

    for filename, df in exports.items():
        path = OUTPUT_DIR / filename
        df.to_csv(path, index=False)

    # Save KPIs as JSON
    save_json(results["kpis"], OUTPUT_DIR / "kpis.json")

    print(f"  CSV files  : {len(exports)}")
    print(f"  JSON files : 1")
    print(f"  Folder     : {OUTPUT_DIR}")


def step_summary(results: dict, n_plots: int) -> None:
    """Print final summary."""
    print_section("PIPELINE COMPLETE — SUMMARY")

    kpis = results["kpis"]
    print(f"  Total Revenue     : {format_currency(kpis['total_sales'])}")
    print(f"  Total Profit      : {format_currency(kpis['total_profit'])}")
    print(f"  Profit Margin     : {format_percent(kpis['profit_margin_pct'])}")
    print(f"  Total Orders      : {format_number(kpis['total_orders'], 0)}")
    print(f"  Avg Order Value   : {format_currency(kpis['avg_order_value'])}")
    print(f"  Avg Discount      : {format_percent(kpis['avg_discount_pct'])}")
    print(f"  Unique Customers  : {format_number(kpis['unique_customers'], 0)}")
    print(f"  Unique Products   : {format_number(kpis['unique_products'], 0)}")
    print()
    print(f"  Plots generated   : {n_plots}")
    print(f"  Analysis sections : {len(results)}")
    print(f"  API used          : No")


# ============================================
# 3. ARGPARSE
# ============================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the full retail sales analytics pipeline."
    )
    parser.add_argument(
        "--synthetic",
        action="store_true",
        help="Force synthetic data generation (ignore any existing raw CSV).",
    )
    parser.add_argument(
        "--skip-plots",
        action="store_true",
        help="Skip visualization step.",
    )
    parser.add_argument(
        "--skip-sql",
        action="store_true",
        help="Skip saving to SQLite.",
    )
    return parser.parse_args()


# ============================================
# 4. MAIN
# ============================================

def main() -> int:
    args = parse_args()

    print()
    print(SEPARATOR)
    print("RETAIL SALES DATA ANALYSIS — FULL PIPELINE".center(70))
    print(SEPARATOR)

    start = time.perf_counter()

    try:
        # 0. Setup
        step_setup()

        # 1. Load raw
        raw_df = step_load_raw(force_synthetic=args.synthetic)

        # 2. Clean
        clean_df = step_clean(raw_df)

        # 3. Feature engineering
        feature_df = step_engineer_features(clean_df)

        # 4. Save cleaned CSV
        step_save_clean(feature_df)

        # 5. Save to SQLite
        if not args.skip_sql:
            step_save_sql(feature_df)
        else:
            print_section("STEP 5 — SKIPPED (SQL)")
            print("  --skip-sql flag set.")

        # 6. Analysis
        results = step_analysis(feature_df)

        # 7. Visualizations
        if not args.skip_plots:
            n_plots = len(step_visualize(feature_df))
        else:
            print_section("STEP 7 — SKIPPED (PLOTS)")
            print("  --skip-plots flag set.")
            n_plots = 0

        # 8. Export
        step_export(results)

        # 9. Summary
        elapsed = time.perf_counter() - start
        step_summary(results, n_plots)
        print()
        print(f"  Total time: {elapsed:.2f}s")
        print(SEPARATOR)

        return 0

    except KeyboardInterrupt:
        print("\n[ABORTED] Interrupted by user.")
        return 130

    except Exception as e:
        print()
        print(SEPARATOR)
        print("[FAILED] Pipeline error")
        print(SEPARATOR)
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())