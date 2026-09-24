# ============================================
# Retail Sales Data Analysis
# File: src/data_cleaning.py
# Purpose: Clean raw retail sales data - missing, duplicates, types, outliers
# ============================================

"""
Ye file data cleaning ke saare functions rakhti hai.
Koi API nahi. Input: raw CSV/Excel -> Output: clean CSV.

Functions:
- standardize_columns()    : Column names standard karna
- drop_duplicates_safe()   : Duplicate rows hatana
- handle_missing_values()  : Missing values handle karna
- convert_data_types()     : Data types sahi karna
- parse_dates()            : Date column ko datetime banana
- remove_negative_sales()  : Negative sales hatana
- detect_outliers_iqr()    : Outliers detect karna
- remove_outliers()        : Outliers hatana (optional)
- validate_data()          : Final validation checks
- clean_pipeline()         : Poora cleaning pipeline
- save_cleaned_data()      : Cleaned data save karna
"""

import logging
import numpy as np
import pandas as pd
from pathlib import Path

from config import (
    RAW_DATA_FILE,
    CLEAN_DATA_FILE,
    COL_ORDER_ID,
    COL_ORDER_DATE,
    COL_SALES,
    COL_PROFIT,
    COL_DISCOUNT,
    COL_QUANTITY,
    COL_UNIT_PRICE,
    COL_REGION,
    COL_CATEGORY,
    COL_SEGMENT,
    COL_PAYMENT_MODE,
    COL_PRODUCT_NAME,
    COL_CUSTOMER_NAME,
    COL_STATE,
    COL_CITY,
    NUMERIC_COLUMNS,
    DATE_COLUMNS,
    DROP_IF_MISSING,
    FILL_ZERO_IF_MISSING,
    FILL_UNKNOWN_IF_MISSING,
    IQR_MULTIPLIER,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    LOG_LEVEL,
)

# ============================================
# LOGGING
# ============================================

logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
)
logger = logging.getLogger(__name__)


# ============================================
# 1. STANDARDIZE COLUMN NAMES
# ============================================

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Column names ko standard banata hai:
    - Strip whitespace
    - Lowercase -> Title_Case with underscore
    - Special characters remove
    - Space -> underscore

    Example:
        ' order id '   -> 'Order_Id'
        'Product-Name' -> 'Product_Name'
        'TOTAL SALES'  -> 'Total_Sales'
    """
    df = df.copy()
    new_columns = []
    for col in df.columns:
        clean = str(col).strip()
        clean = clean.replace("-", "_").replace(" ", "_")
        clean = "".join(
            ch if ch.isalnum() or ch == "_" else "" for ch in clean
        )
        clean = "_".join(part.capitalize() for part in clean.split("_") if part)
        if clean == "Order_Id":
            clean = "Order_ID"
            
        new_columns.append(clean)

    df.columns = new_columns
    logger.info(f"Columns standardized: {new_columns}")
    return df


# ============================================
# 2. DROP DUPLICATES
# ============================================

def drop_duplicates_safe(
    df: pd.DataFrame,
    subset: list | None = None,
) -> pd.DataFrame:
    """
    Duplicate rows hatata hai.

    Args:
        df: input DataFrame
        subset: kis columns par duplicate check karna (default: Order_ID)

    Returns:
        Cleaned DataFrame
    """
    df = df.copy()
    before = len(df)

    if subset is None and COL_ORDER_ID in df.columns:
        subset = [COL_ORDER_ID]

    df = df.drop_duplicates(subset=subset, keep="first")
    after = len(df)
    removed = before - after

    logger.info(f"Duplicates removed: {removed} (before: {before}, after: {after})")
    return df


# ============================================
# 3. HANDLE MISSING VALUES
# ============================================

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Missing values ko config rules ke hisaab se handle karta hai:
    - DROP_IF_MISSING     : rows drop karo
    - FILL_ZERO_IF_MISSING: 0 se fill karo
    - FILL_UNKNOWN_IF_MISSING: 'Unknown' se fill karo
    """
    df = df.copy()
    before_rows = len(df)
    before_missing = int(df.isnull().sum().sum())

    # 1. Drop rows jahan critical columns missing hain
    drop_cols = [c for c in DROP_IF_MISSING if c in df.columns]
    if drop_cols:
        df = df.dropna(subset=drop_cols)

    # 2. Fill zero
    for col in FILL_ZERO_IF_MISSING:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # 3. Fill 'Unknown'
    for col in FILL_UNKNOWN_IF_MISSING:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    # 4. Remaining numeric columns -> median
    for col in NUMERIC_COLUMNS:
        if col in df.columns and df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            logger.info(f"Filled missing in '{col}' with median={median_val}")

    # 5. Remaining string columns -> 'Unknown'
    remaining_obj_cols = df.select_dtypes(include=["object"]).columns
    for col in remaining_obj_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna("Unknown")

    after_missing = int(df.isnull().sum().sum())
    after_rows = len(df)

    logger.info(
        f"Missing handled | Rows: {before_rows}->{after_rows} | "
        f"Missing: {before_missing}->{after_missing}"
    )
    return df


# ============================================
# 4. CONVERT DATA TYPES
# ============================================

def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            s = df[col].astype(str).str.strip()
            s = s.str.replace(r"(?i)rs\.?", "", regex=True)
            s = s.str.replace(r"[$,\s]", "", regex=True)
            s = s.str.replace("%", "", regex=False)

            df[col] = pd.to_numeric(s, errors="coerce")

    if COL_DISCOUNT in df.columns:
        mask = df[COL_DISCOUNT].between(0, 1, inclusive="both")
        df.loc[mask, COL_DISCOUNT] *= 100

    if COL_QUANTITY in df.columns:
        df[COL_QUANTITY] = df[COL_QUANTITY].fillna(0).astype(int)

    logger.info("Data types converted successfully.")
    return df
    


# ============================================
# 5. PARSE DATES
# ============================================

def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Date columns ko datetime me convert karta hai.
    Extra columns bhi banata hai: Year, Month, Month_Name, Quarter, Weekday
    """
    df = df.copy()

    for col in DATE_COLUMNS:
        if col not in df.columns:
            continue

        df[col] = pd.to_datetime(df[col], errors="coerce")
        # Invalid dates drop
        invalid = df[col].isnull().sum()
        if invalid > 0:
            logger.warning(f"Invalid dates dropped from '{col}': {invalid}")
            df = df.dropna(subset=[col])

        # Extra date features
        df["Year"] = df[col].dt.year
        df["Month"] = df[col].dt.month
        df["Month_Name"] = df[col].dt.strftime("%b")
        df["Quarter"] = df[col].dt.quarter
        df["Weekday"] = df[col].dt.day_name()
        df["Year_Month"] = df[col].dt.strftime("%Y-%m")

        df["Season"] = df[col].dt.month.map({
            12: "Winter", 1: "Winter", 2: "Winter",
            3: "Summer", 4: "Summer", 5: "Summer",
            6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
            10: "Post-Monsoon", 11: "Post-Monsoon"
        })  

        df["Quarter_Label"] = "Q" + df["Quarter"].astype(str)

        df["Is_Weekend"] = df[col].dt.weekday >= 5

        df[COL_DISCOUNT] = pd.to_numeric(
            df[COL_DISCOUNT].astype(str).str.replace("%", "", regex=False),
            errors="coerce"
        )

        df[COL_PROFIT] = pd.to_numeric(df[COL_PROFIT], errors="coerce")
        df[COL_SALES] = pd.to_numeric(df[COL_SALES], errors="coerce")

        df["Profit_Margin"] = (
            df[COL_PROFIT] / df[COL_SALES].replace(0, np.nan) * 100
        ).round(2)

        df["Discount_Band"] = pd.cut(
            df[COL_DISCOUNT],
            bins=[-1, 0, 10, 20, 30, 100],
            labels=["No Discount", "Low", "Medium", "High", "Very High"]
        ).astype(str)

        df["Profit_Status"] = np.where(
            df[COL_PROFIT] > 0,
            "Profit",
            np.where(df[COL_PROFIT] == 0, "Break-even", "Loss")
        )

    logger.info(f"Dates parsed. Added: Year, Month, Month_Name, Quarter, Weekday")
    return df


# ============================================
# 6. REMOVE NEGATIVE / INVALID SALES
# ============================================

def remove_negative_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sales <= 0 wali rows ko hata deta hai.
    Quantity <= 0 bhi hata deta hai.
    """
    df = df.copy()
    before = len(df)

    if COL_SALES in df.columns:
        df = df[df[COL_SALES] > 0]

    if COL_QUANTITY in df.columns:
        df = df[df[COL_QUANTITY] > 0]

    after = len(df)
    logger.info(f"Invalid sales/quantity removed: {before - after}")
    return df


# ============================================
# 7. DETECT OUTLIERS (IQR)
# ============================================

def detect_outliers_iqr(
    df: pd.DataFrame,
    column: str,
    multiplier: float = IQR_MULTIPLIER,
) -> pd.Series:
    """
    IQR method se outliers detect karta hai.

    Returns:
        Boolean Series: True jahan outlier hai
    """
    if column not in df.columns:
        raise KeyError(f"Column not found: {column}")

    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1

    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr

    outliers = (df[column] < lower) | (df[column] > upper)
    logger.info(
        f"Outliers in '{column}': {outliers.sum()} "
        f"(bounds: {lower:.2f} - {upper:.2f})"
    )
    return outliers


def remove_outliers(
    df: pd.DataFrame,
    columns: list | None = None,
    multiplier: float = IQR_MULTIPLIER,
) -> pd.DataFrame:
    """
    Diye gaye columns ke outliers remove karta hai.
    Default: [Sales, Profit]
    """
    df = df.copy()
    if columns is None:
        columns = [COL_SALES, COL_PROFIT]

    before = len(df)
    mask = pd.Series(True, index=df.index)
    for col in columns:
        if col in df.columns:
            mask &= ~detect_outliers_iqr(df, col, multiplier)

    df = df[mask]
    logger.info(f"Outliers removed: {before - len(df)}")
    return df


# ============================================
# 8. VALIDATE DATA
# ============================================

def validate_data(df: pd.DataFrame) -> dict:
    """
    Final validation checks.

    Returns:
        dict with validation results
    """
    report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": int(df.isnull().sum().sum()),
        "duplicates": int(df.duplicated().sum()),
        "negative_sales": int((df[COL_SALES] <= 0).sum())
            if COL_SALES in df.columns else 0,
        "negative_quantity": int((df[COL_QUANTITY] <= 0).sum())
            if COL_QUANTITY in df.columns else 0,
        "valid": True,
        "issues": [],
    }

    if report["missing_values"] > 0:
        report["valid"] = False
        report["issues"].append(f"Missing values: {report['missing_values']}")

    if report["duplicates"] > 0:
        report["valid"] = False
        report["issues"].append(f"Duplicates: {report['duplicates']}")

    if report["negative_sales"] > 0:
        report["valid"] = False
        report["issues"].append(f"Negative sales: {report['negative_sales']}")

    if report["negative_quantity"] > 0:
        report["valid"] = False
        report["issues"].append(f"Negative quantity: {report['negative_quantity']}")

    logger.info(f"Validation: {'PASSED' if report['valid'] else 'FAILED'}")
    return report


def print_validation_report(report: dict) -> None:
    """Validation report ko sundar tarike se print karta hai."""
    print("=" * 60)
    print("DATA VALIDATION REPORT")
    print("=" * 60)
    print(f"Total Rows      : {report['total_rows']}")
    print(f"Total Columns   : {report['total_columns']}")
    print(f"Missing Values  : {report['missing_values']}")
    print(f"Duplicates      : {report['duplicates']}")
    print(f"Negative Sales  : {report['negative_sales']}")
    print(f"Negative Qty    : {report['negative_quantity']}")
    print(f"Status          : {'VALID' if report['valid'] else 'INVALID'}")
    if report["issues"]:
        print("\nIssues:")
        for issue in report["issues"]:
            print(f"  - {issue}")
    print("=" * 60)


# ============================================
# 9. CLEAN PIPELINE
# ============================================

def clean_pipeline(
    df: pd.DataFrame,
    remove_out: bool = False,
) -> pd.DataFrame:
    """
    Poora cleaning pipeline ek saath chalata hai.

    Steps:
        1. Standardize columns
        2. Drop duplicates
        3. Handle missing values
        4. Convert data types
        5. Parse dates
        6. Remove negative/invalid sales
        7. (Optional) Remove outliers

    Args:
        df: raw DataFrame
        remove_out: outliers hatane hain ya nahi (default False)

    Returns:
        Clean DataFrame
    """
    logger.info("=" * 50)
    logger.info("STARTING CLEANING PIPELINE")
    logger.info("=" * 50)

    initial_shape = df.shape

    df = standardize_columns(df)
    df = drop_duplicates_safe(df)
    df = handle_missing_values(df)
    df = convert_data_types(df)
    df = parse_dates(df)
    df = remove_negative_sales(df)

    if remove_out:
        df = remove_outliers(df)

    df = df.reset_index(drop=True)

    logger.info(
        f"Pipeline complete | Shape: {initial_shape} -> {df.shape}"
    )
    return df


# ============================================
# 10. SAVE CLEANED DATA
# ============================================

def save_cleaned_data(
    df: pd.DataFrame,
    output_path: Path | str = CLEAN_DATA_FILE,
) -> None:
    """Cleaned DataFrame ko CSV me save karta hai."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Cleaned data saved: {output_path}")


# ============================================
# 11. MAIN (self-test)
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("DATA CLEANING - SELF TEST")
    print("=" * 70)

    # Sample messy DataFrame
    raw = pd.DataFrame({
        " order id ": ["ORD001", "ORD002", "ORD002", "ORD004", "ORD005"],
        "Order-Date": [
            "2024-01-15", "2024-02-20", "2024-02-20",
            "invalid_date", "2024-03-10"
        ],
        "Product-Name": ["Chair", "Table", "Table", None, "Lamp"],
        "Region": ["North", "South", "South", "East", None],
        "Quantity": ["2", "1", "1", "3", "-1"],
        "Unit_Price": ["Rs.1500", "2500", "2500", "800", "500"],
        "Discount": ["10%", "0.20", "0.20", "0", "5%"],
        "Sales": ["3000", "2500", "2500", "2400", "-500"],
        "Profit": ["600", "500", "500", "120", "-100"],
        "Category": ["Furniture", "Furniture", "Furniture", "Lighting", None],
        "Segment": ["Consumer", "Corporate", "Corporate", "Consumer", "Consumer"],
        "Customer_Name": ["A", "B", "B", "C", "D"],
        "State": ["Delhi", "Karnataka", "Karnataka", "WB", "MH"],
        "City": ["New Delhi", "Bangalore", "Bangalore", "Kolkata", "Mumbai"],
        "Payment_Mode": ["UPI", "Card", "Card", "Cash", "UPI"],
    })

    print("\n[STEP 1] Raw shape:", raw.shape)
    print("\nRaw columns:", list(raw.columns))

    print("\n[STEP 2] Running clean_pipeline()...")
    clean_df = clean_pipeline(raw)

    print("\n[STEP 3] Clean shape:", clean_df.shape)
    print("\nClean columns:", list(clean_df.columns))

    print("\n[STEP 4] Clean preview:")
    print(clean_df.head().to_string())

    print("\n[STEP 5] Validation:")
    report = validate_data(clean_df)
    print_validation_report(report)

    print("\n[STEP 6] Saving cleaned data...")
    save_cleaned_data(clean_df, output_path="output/test_cleaned.csv")
    print("  Saved: output/test_cleaned.csv")

    print("\n" + "=" * 70)
    print("[OK] data_cleaning.py - All steps passed.")
    print("=" * 70)