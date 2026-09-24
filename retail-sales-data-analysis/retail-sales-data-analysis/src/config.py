# ============================================
# Retail Sales Data Analysis
# File: src/config.py
# Purpose: Central configuration - paths, constants, settings
# ============================================

"""
Ye file project ki saari configuration ek jagah rakhti hai.
Paths, column names, database settings, aur constants yahan define hain.
Isse code me hardcoded values nahi likhni padti.
"""

import os
from pathlib import Path

# ============================================
# 1. BASE DIRECTORY SETUP
# ============================================

# Project root directory (retail-sales-data-analysis/)
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# 2. FOLDER PATHS
# ============================================

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

NOTEBOOKS_DIR = BASE_DIR / "notebooks"
SRC_DIR = BASE_DIR / "src"
SQL_DIR = BASE_DIR / "sql"
DASHBOARD_DIR = BASE_DIR / "dashboard"
REPORTS_DIR = BASE_DIR / "reports"
IMAGES_DIR = BASE_DIR / "images"
OUTPUT_DIR = BASE_DIR / "output"
TESTS_DIR = BASE_DIR / "tests"
DOCS_DIR = BASE_DIR / "docs"

# ============================================
# 3. FILE PATHS
# ============================================

# Input files
RAW_DATA_FILE = RAW_DATA_DIR / "retail_sales_raw.csv"
CLEAN_DATA_FILE = PROCESSED_DATA_DIR / "retail_sales_clean.csv"

# Output files
CLEANED_OUTPUT_CSV = OUTPUT_DIR / "cleaned_data.csv"
SUMMARY_STATS_CSV = OUTPUT_DIR / "summary_statistics.csv"
TOP_PRODUCTS_CSV = OUTPUT_DIR / "top_products.csv"
BOTTOM_PRODUCTS_CSV = OUTPUT_DIR / "bottom_products.csv"
REGION_PERFORMANCE_CSV = OUTPUT_DIR / "region_performance.csv"
CATEGORY_PERFORMANCE_CSV = OUTPUT_DIR / "category_performance.csv"
MONTHLY_SALES_CSV = OUTPUT_DIR / "monthly_sales.csv"
DISCOUNT_ANALYSIS_CSV = OUTPUT_DIR / "discount_analysis.csv"
INSIGHTS_FILE = OUTPUT_DIR / "insights.txt"

# ============================================
# 4. DATABASE CONFIGURATION (MySQL / SQLite)
# ============================================

# --- Option A: SQLite (recommended for beginners, no setup needed) ---
SQLITE_DB_PATH = BASE_DIR / "retail_sales.db"
SQLITE_CONNECTION_STRING = f"sqlite:///{SQLITE_DB_PATH}"

# --- Option B: MySQL (agar MySQL installed hai to use karo) ---
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "retail_sales_db"),
}

MYSQL_CONNECTION_STRING = (
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# Active connection (default SQLite)
ACTIVE_DB_CONNECTION = SQLITE_CONNECTION_STRING
TABLE_NAME = "retail_sales"

# ============================================
# 5. COLUMN NAMES (Standard)
# ============================================

COL_ORDER_ID = "Order_ID"
COL_ORDER_DATE = "Order_Date"
COL_CUSTOMER_NAME = "Customer_Name"
COL_SEGMENT = "Segment"
COL_REGION = "Region"
COL_STATE = "State"
COL_CITY = "City"
COL_PRODUCT_NAME = "Product_Name"
COL_CATEGORY = "Category"
COL_QUANTITY = "Quantity"
COL_UNIT_PRICE = "Unit_Price"
COL_DISCOUNT = "Discount"
COL_SALES = "Sales"
COL_PROFIT = "Profit"
COL_PAYMENT_MODE = "Payment_Mode"

# Expected columns (order matters for validation)
EXPECTED_COLUMNS = [
    COL_ORDER_ID,
    COL_ORDER_DATE,
    COL_CUSTOMER_NAME,
    COL_SEGMENT,
    COL_REGION,
    COL_STATE,
    COL_CITY,
    COL_PRODUCT_NAME,
    COL_CATEGORY,
    COL_QUANTITY,
    COL_UNIT_PRICE,
    COL_DISCOUNT,
    COL_SALES,
    COL_PROFIT,
    COL_PAYMENT_MODE,
]

# Numeric columns
NUMERIC_COLUMNS = [
    COL_QUANTITY,
    COL_UNIT_PRICE,
    COL_DISCOUNT,
    COL_SALES,
    COL_PROFIT,
]

# Categorical columns
CATEGORICAL_COLUMNS = [
    COL_SEGMENT,
    COL_REGION,
    COL_STATE,
    COL_CITY,
    COL_CATEGORY,
    COL_PAYMENT_MODE,
]

# Date columns
DATE_COLUMNS = [COL_ORDER_DATE]

# ============================================
# 6. DATA CLEANING SETTINGS
# ============================================

# Missing value handling
DROP_IF_MISSING = [COL_ORDER_ID, COL_ORDER_DATE, COL_SALES]
FILL_ZERO_IF_MISSING = [COL_PROFIT, COL_DISCOUNT, COL_QUANTITY]
FILL_UNKNOWN_IF_MISSING = [COL_REGION, COL_CATEGORY, COL_SEGMENT, COL_PAYMENT_MODE]

# Outlier detection (IQR method)
IQR_MULTIPLIER = 1.5

# ============================================
# 7. ANALYSIS SETTINGS
# ============================================

TOP_N = 10                  # Top N products/regions
BOTTOM_N = 10               # Bottom N products/regions
MIN_DISCOUNT_ALERT = 0.30   # 30% se zyada discount par warning
CURRENCY = "INR"            # Currency symbol
CURRENCY_SYMBOL = "Rs."

# ============================================
# 8. VISUALIZATION SETTINGS
# ============================================

# Figure size
FIG_SIZE_WIDE = (14, 6)
FIG_SIZE_SQUARE = (10, 8)
FIG_SIZE_SMALL = (8, 5)

# DPI for saved images
FIG_DPI = 300

# Color palette
COLOR_PALETTE = "viridis"
PRIMARY_COLOR = "#2E86AB"
SECONDARY_COLOR = "#A23B72"
ACCENT_COLOR = "#F18F01"
DANGER_COLOR = "#C73E1D"
SUCCESS_COLOR = "#3B945E"

# Style
PLOT_STYLE = "seaborn-v0_8-darkgrid"
FONT_SIZE = 11

# ============================================
# 9. LOGGING SETTINGS
# ============================================

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE = BASE_DIR / "project.log"

# ============================================
# 10. HELPER FUNCTION - CREATE ALL FOLDERS
# ============================================

def create_all_directories() -> None:
    """
    Saari required folders create karta hai agar exist nahi karti.
    Project run karne se pehle ek baar call karna.
    """
    directories = [
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        NOTEBOOKS_DIR,
        SRC_DIR,
        SQL_DIR,
        DASHBOARD_DIR,
        REPORTS_DIR,
        IMAGES_DIR,
        OUTPUT_DIR,
        TESTS_DIR,
        DOCS_DIR,
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def print_config() -> None:
    """Debug ke liye current configuration print karta hai."""
    print("=" * 60)
    print("RETAIL SALES DATA ANALYSIS - CONFIGURATION")
    print("=" * 60)
    print(f"Base Directory     : {BASE_DIR}")
    print(f"Raw Data File      : {RAW_DATA_FILE}")
    print(f"Clean Data File    : {CLEAN_DATA_FILE}")
    print(f"Output Directory   : {OUTPUT_DIR}")
    print(f"Database           : {ACTIVE_DB_CONNECTION}")
    print(f"Table Name         : {TABLE_NAME}")
    print(f"Top N              : {TOP_N}")
    print(f"Currency           : {CURRENCY}")
    print("=" * 60)


# ============================================
# 11. AUTO-RUN (only when file executed directly)
# ============================================

if __name__ == "__main__":
    create_all_directories()
    print_config()
    print("\n[OK] All directories created successfully.")