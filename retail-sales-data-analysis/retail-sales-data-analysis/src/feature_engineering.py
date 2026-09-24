# ============================================
# Retail Sales Data Analysis
# File: src/feature_engineering.py
# Purpose: Create new features from cleaned data for analysis
# ============================================

"""
Ye file naye features (columns) banati hai jo analysis aur dashboard
ke liye useful hain. Koi API nahi.

New Features:
- Profit_Margin          : Profit / Sales * 100
- Revenue_Per_Unit       : Sales / Quantity
- Discount_Amount        : Sales * Discount / 100
- Discount_Band          : Low / Medium / High / Very High
- Profit_Status          : Profit / Loss
- Order_Size             : Small / Medium / Large
- Is_Weekend             : Weekend par order hua ya nahi
- Season                : Winter / Summer / Monsoon / Post-Monsoon
- Quarter_Label          : Q1, Q2, Q3, Q4
- Year_Month             : 'YYYY-MM'
- Customer_Type          : New / Repeat
- Profit_Per_Unit        : Profit / Quantity
"""

import logging
import numpy as np
import pandas as pd

from config import (
    COL_ORDER_ID,
    COL_ORDER_DATE,
    COL_CUSTOMER_NAME,
    COL_SALES,
    COL_PROFIT,
    COL_DISCOUNT,
    COL_QUANTITY,
    COL_UNIT_PRICE,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    LOG_LEVEL,
)

logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
)
logger = logging.getLogger(__name__)


# ============================================
# 1. PROFIT MARGIN
# ============================================

def add_profit_margin(df: pd.DataFrame) -> pd.DataFrame:
    """
    Profit_Margin = (Profit / Sales) * 100
    Sales 0 ho to NaN, baad me 0 se fill.
    """
    df = df.copy()
    df["Profit_Margin"] = np.where(
        df[COL_SALES] > 0,
        (df[COL_PROFIT] / df[COL_SALES]) * 100,
        0.0,
    )
    df["Profit_Margin"] = df["Profit_Margin"].round(2)
    logger.info("Feature added: Profit_Margin")
    return df


# ============================================
# 2. REVENUE PER UNIT
# ============================================

def add_revenue_per_unit(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue_Per_Unit = Sales / Quantity"""
    df = df.copy()
    df["Revenue_Per_Unit"] = np.where(
        df[COL_QUANTITY] > 0,
        df[COL_SALES] / df[COL_QUANTITY],
        0.0,
    )
    df["Revenue_Per_Unit"] = df["Revenue_Per_Unit"].round(2)
    logger.info("Feature added: Revenue_Per_Unit")
    return df


# ============================================
# 3. PROFIT PER UNIT
# ============================================

def add_profit_per_unit(df: pd.DataFrame) -> pd.DataFrame:
    """Profit_Per_Unit = Profit / Quantity"""
    df = df.copy()
    df["Profit_Per_Unit"] = np.where(
        df[COL_QUANTITY] > 0,
        df[COL_PROFIT] / df[COL_QUANTITY],
        0.0,
    )
    df["Profit_Per_Unit"] = df["Profit_Per_Unit"].round(2)
    logger.info("Feature added: Profit_Per_Unit")
    return df


# ============================================
# 4. DISCOUNT AMOUNT
# ============================================

def add_discount_amount(df: pd.DataFrame) -> pd.DataFrame:
    """
    Discount_Amount = Sales * Discount / 100
    Approximate discount value in currency.
    """
    df = df.copy()
    df["Discount_Amount"] = (
        df[COL_SALES] * df[COL_DISCOUNT] / 100
    ).round(2)
    logger.info("Feature added: Discount_Amount")
    return df


# ============================================
# 5. DISCOUNT BAND
# ============================================

def add_discount_band(df: pd.DataFrame) -> pd.DataFrame:
    """
    Discount ko band me divide karta hai:
        0%          -> No Discount
        1-10%       -> Low
        11-20%      -> Medium
        21-30%      -> High
        >30%        -> Very High
    """
    df = df.copy()

    def band(val):
        if pd.isna(val) or val <= 0:
            return "No Discount"
        if val <= 10:
            return "Low"
        if val <= 20:
            return "Medium"
        if val <= 30:
            return "High"
        return "Very High"

    df["Discount_Band"] = df[COL_DISCOUNT].apply(band)
    logger.info("Feature added: Discount_Band")
    return df


# ============================================
# 6. PROFIT STATUS
# ============================================

def add_profit_status(df: pd.DataFrame) -> pd.DataFrame:
    """
    Profit_Status:
        Profit  > 0 -> Profit
        Profit == 0 -> Break-even
        Profit  < 0 -> Loss
    """
    df = df.copy()
    df["Profit_Status"] = np.where(
        df[COL_PROFIT] > 0,
        "Profit",
        np.where(df[COL_PROFIT] == 0, "Break-even", "Loss"),
    )
    logger.info("Feature added: Profit_Status")
    return df


# ============================================
# 7. ORDER SIZE
# ============================================

def add_order_size(df: pd.DataFrame) -> pd.DataFrame:
    """
    Quantity ke hisaab se Order_Size:
        1-2  -> Small
        3-5  -> Medium
        6-10 -> Large
        >10  -> Bulk
    """
    df = df.copy()

    def size(qty):
        if qty <= 2:
            return "Small"
        if qty <= 5:
            return "Medium"
        if qty <= 10:
            return "Large"
        return "Bulk"

    df["Order_Size"] = df[COL_QUANTITY].apply(size)
    logger.info("Feature added: Order_Size")
    return df


# ============================================
# 8. WEEKEND FLAG
# ============================================

def add_weekend_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Is_Weekend:
        True  -> Saturday / Sunday
        False -> Baaki din
    """
    df = df.copy()
    if COL_ORDER_DATE in df.columns:
        df["Is_Weekend"] = df[COL_ORDER_DATE].dt.weekday >= 5
    else:
        df["Is_Weekend"] = False
    logger.info("Feature added: Is_Weekend")
    return df


# ============================================
# 9. SEASON
# ============================================

def add_season(df: pd.DataFrame) -> pd.DataFrame:
    """
    Month ke hisaab se Indian season:
        12, 1, 2   -> Winter
        3, 4, 5    -> Summer
        6, 7, 8, 9 -> Monsoon
        10, 11     -> Post-Monsoon
    """
    df = df.copy()

    def season(month):
        if month in (12, 1, 2):
            return "Winter"
        if month in (3, 4, 5):
            return "Summer"
        if month in (6, 7, 8, 9):
            return "Monsoon"
        return "Post-Monsoon"

    if "Month" in df.columns:
        df["Season"] = df["Month"].apply(season)
    else:
        df["Season"] = "Unknown"

    logger.info("Feature added: Season")
    return df


# ============================================
# 10. QUARTER LABEL
# ============================================

def add_quarter_label(df: pd.DataFrame) -> pd.DataFrame:
    """Quarter_Label: Q1, Q2, Q3, Q4"""
    df = df.copy()
    if "Quarter" in df.columns:
        df["Quarter_Label"] = "Q" + df["Quarter"].astype(str)
    else:
        df["Quarter_Label"] = "Q0"
    logger.info("Feature added: Quarter_Label")
    return df


# ============================================
# 11. YEAR-MONTH
# ============================================

def add_year_month(df: pd.DataFrame) -> pd.DataFrame:
    """Year_Month: 'YYYY-MM' string (time series ke liye)"""
    df = df.copy()
    if COL_ORDER_DATE in df.columns:
        df["Year_Month"] = df[COL_ORDER_DATE].dt.strftime("%Y-%m")
    else:
        df["Year_Month"] = "Unknown"
    logger.info("Feature added: Year_Month")
    return df


# ============================================
# 12. CUSTOMER TYPE
# ============================================

def add_customer_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    Customer_Type:
        Agar Customer_Name ek hi baar aaya -> New
        Agar multiple baar aaya -> Repeat
    """
    df = df.copy()

    if COL_CUSTOMER_NAME in df.columns:
        counts = df[COL_CUSTOMER_NAME].value_counts()
        df["Customer_Type"] = df[COL_CUSTOMER_NAME].map(
            lambda x: "Repeat" if counts.get(x, 0) > 1 else "New"
        )
    else:
        df["Customer_Type"] = "Unknown"

    logger.info("Feature added: Customer_Type")
    return df


# ============================================
# 13. MASTER PIPELINE
# ============================================

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Saare feature engineering steps ek saath chalata hai.
    Order important hai - dependencies ke hisaab se.
    """
    logger.info("=" * 50)
    logger.info("STARTING FEATURE ENGINEERING")
    logger.info("=" * 50)

    initial_cols = df.shape[1]

    df = add_profit_margin(df)
    df = add_revenue_per_unit(df)
    df = add_profit_per_unit(df)
    df = add_discount_amount(df)
    df = add_discount_band(df)
    df = add_profit_status(df)
    df = add_order_size(df)
    df = add_weekend_flag(df)
    df = add_season(df)
    df = add_quarter_label(df)
    df = add_year_month(df)
    df = add_customer_type(df)

    final_cols = df.shape[1]
    logger.info(
        f"Feature engineering complete | "
        f"Columns: {initial_cols} -> {final_cols} "
        f"(+{final_cols - initial_cols})"
    )
    return df


# ============================================
# 14. MAIN (self-test)
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("FEATURE ENGINEERING - SELF TEST")
    print("=" * 70)

    sample = pd.DataFrame({
        "Order_Id": ["ORD001", "ORD002", "ORD003", "ORD004", "ORD005"],
        "Order_Date": pd.to_datetime([
            "2024-01-15", "2024-06-20", "2024-08-25",
            "2024-11-05", "2024-12-31",
        ]),
        "Customer_Name": ["A", "B", "A", "C", "B"],
        "Product_Name": ["Chair", "Table", "Lamp", "Sofa", "Chair"],
        "Region": ["North", "South", "East", "West", "North"],
        "Category": ["Furniture", "Furniture", "Lighting", "Furniture", "Furniture"],
        "Quantity": [2, 1, 5, 12, 3],
        "Unit_Price": [1500.0, 2500.0, 800.0, 5000.0, 1500.0],
        "Discount": [0.0, 10.0, 20.0, 35.0, 15.0],
        "Sales": [3000.0, 2250.0, 3200.0, 39000.0, 3825.0],
        "Profit": [600.0, 450.0, 320.0, -1500.0, 800.0],
        "Segment": ["Consumer", "Corporate", "Consumer", "Home Office", "Corporate"],
        "State": ["Delhi", "KA", "WB", "MH", "Delhi"],
        "City": ["Delhi", "Bangalore", "Kolkata", "Mumbai", "Delhi"],
        "Payment_Mode": ["UPI", "Card", "Cash", "Card", "UPI"],
        "Year": [2024, 2024, 2024, 2024, 2024],
        "Month": [1, 6, 8, 11, 12],
        "Month_Name": ["Jan", "Jun", "Aug", "Nov", "Dec"],
        "Quarter": [1, 2, 3, 4, 4],
        "Weekday": ["Monday", "Thursday", "Sunday", "Tuesday", "Tuesday"],
    })

    print("\n[STEP 1] Original shape:", sample.shape)
    print("Original columns:", list(sample.columns))

    print("\n[STEP 2] Running engineer_features()...")
    df = engineer_features(sample)

    print("\n[STEP 3] New shape:", df.shape)
    print("New columns:", list(df.columns))

    new_cols = [
        "Profit_Margin", "Revenue_Per_Unit", "Profit_Per_Unit",
        "Discount_Amount", "Discount_Band", "Profit_Status",
        "Order_Size", "Is_Weekend", "Season", "Quarter_Label",
        "Year_Month", "Customer_Type",
    ]
    print("\n[STEP 4] Sample of new features:")
    print(df[["Order_Id"] + new_cols].to_string(index=False))

    print("\n[STEP 5] Discount_Band value counts:")
    print(df["Discount_Band"].value_counts().to_string())

    print("\n[STEP 6] Profit_Status value counts:")
    print(df["Profit_Status"].value_counts().to_string())

    print("\n[STEP 7] Season value counts:")
    print(df["Season"].value_counts().to_string())

    print("\n" + "=" * 70)
    print("[OK] feature_engineering.py - All features created.")
    print("=" * 70)