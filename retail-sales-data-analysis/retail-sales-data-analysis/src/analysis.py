# ============================================
# Retail Sales Data Analysis
# File: src/analysis.py
# Purpose: Business analysis - sales, profit, region, product, discount, time
# ============================================

"""
Ye file saara business analysis karti hai. Koi API nahi.

Analysis Functions:
- overall_kpis()             : Total Sales, Profit, Orders, Margin
- region_wise_analysis()     : Region-wise Sales & Profit
- category_wise_analysis()   : Category-wise Sales & Profit
- segment_wise_analysis()    : Segment-wise Sales & Profit
- product_wise_analysis()    : Product-wise Sales & Profit
- top_products()             : Top N products by Sales
- bottom_products()          : Bottom N products by Profit
- monthly_sales_trend()      : Month-wise trend
- quarterly_analysis()       : Quarter-wise summary
- yearly_analysis()          : Year-wise summary
- discount_impact()          : Discount vs Profit analysis
- discount_band_analysis()   : Discount band wise summary
- profit_status_analysis()   : Profit/Loss breakdown
- season_analysis()          : Season-wise summary
- weekday_analysis()         : Weekday vs Weekend
- customer_analysis()        : Top customers
- payment_mode_analysis()    : Payment mode wise sales
- loss_making_products()     : Products giving loss
- run_all_analysis()         : Saare analysis ek saath
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
    COL_REGION,
    COL_CATEGORY,
    COL_SEGMENT,
    COL_PRODUCT_NAME,
    COL_PAYMENT_MODE,
    TOP_N,
    BOTTOM_N,
    MIN_DISCOUNT_ALERT,
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
# 1. OVERALL KPIs
# ============================================

def overall_kpis(df: pd.DataFrame) -> dict:
    """
    Basic KPIs calculate karta hai.

    Returns:
        dict with total_sales, total_profit, total_orders,
        total_quantity, avg_order_value, profit_margin,
        avg_discount, unique_customers, unique_products
    """
    total_sales = float(df[COL_SALES].sum())
    total_profit = float(df[COL_PROFIT].sum())
    total_orders = int(df[COL_ORDER_ID].nunique())
    total_quantity = int(df[COL_QUANTITY].sum())

    avg_order_value = round(total_sales / total_orders, 2) if total_orders else 0.0
    
    profit_margin = (total_profit / total_sales) * 100 if total_sales else 0.0
    
    avg_discount = round(float(df[COL_DISCOUNT].mean()), 2)

    kpis = {
        "total_sales": round(total_sales, 2),
        "total_profit": round(total_profit, 2),
        "total_orders": total_orders,
        "total_quantity": total_quantity,
        "avg_order_value": avg_order_value,
        "profit_margin_pct": profit_margin,
        "avg_discount_pct": avg_discount,
        "unique_customers": int(df[COL_CUSTOMER_NAME].nunique()),
        "unique_products": int(df[COL_PRODUCT_NAME].nunique()),
    }
    
    logger.info(f"KPIs calculated: Sales={total_sales:.0f}, Profit={total_profit:.0f}")
    return kpis


def print_kpis(kpis: dict) -> None:
    """KPIs ko print karta hai."""
    print("=" * 60)
    print("OVERALL KPIs")
    print("=" * 60)
    print(f"Total Sales         : Rs. {kpis['total_sales']:,.2f}")
    print(f"Total Profit        : Rs. {kpis['total_profit']:,.2f}")
    print(f"Total Orders        : {kpis['total_orders']:,}")
    print(f"Total Quantity      : {kpis['total_quantity']:,}")
    print(f"Avg Order Value     : Rs. {kpis['avg_order_value']:,.2f}")
    print(f"Profit Margin       : {kpis['profit_margin_pct']}%")
    print(f"Avg Discount        : {kpis['avg_discount_pct']}%")
    print(f"Unique Customers    : {kpis['unique_customers']:,}")
    print(f"Unique Products     : {kpis['unique_products']:,}")
    print("=" * 60)


# ============================================
# 2. REGION-WISE ANALYSIS
# ============================================

def region_wise_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Region-wise Sales, Profit, Orders, Margin.
    Sales ke hisaab se descending order.
    """
    result = (
        df.groupby(COL_REGION)
        .agg(
            Total_Sales=(COL_SALES, "sum"),
            Total_Profit=(COL_PROFIT, "sum"),
            Total_Orders=(COL_ORDER_ID, "nunique"),
            Total_Quantity=(COL_QUANTITY, "sum"),
            Avg_Discount=(COL_DISCOUNT, "mean"),
        )
        .reset_index()
    )
    result["Profit_Margin_%"] = (
        (result["Total_Profit"] / result["Total_Sales"]) * 100
    ).round(2)
    result["Avg_Discount"] = result["Avg_Discount"].round(2)
    result = result.sort_values("Total_Sales", ascending=False).reset_index(drop=True)
    logger.info(f"Region-wise analysis: {len(result)} regions")
    return result


# ============================================
# 3. CATEGORY-WISE ANALYSIS
# ============================================

def category_wise_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Category-wise Sales, Profit, Orders, Margin."""
    result = (
        df.groupby(COL_CATEGORY)
        .agg(
            Total_Sales=(COL_SALES, "sum"),
            Total_Profit=(COL_PROFIT, "sum"),
            Total_Orders=(COL_ORDER_ID, "nunique"),
            Total_Quantity=(COL_QUANTITY, "sum"),
        )
        .reset_index()
    )
    result["Profit_Margin_%"] = (
        (result["Total_Profit"] / result["Total_Sales"]) * 100
    ).round(2)
    result = result.sort_values("Total_Sales", ascending=False).reset_index(drop=True)
    logger.info(f"Category-wise analysis: {len(result)} categories")
    return result


# ============================================
# 4. SEGMENT-WISE ANALYSIS
# ============================================

def segment_wise_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Segment-wise Sales, Profit."""
    result = (
        df.groupby(COL_SEGMENT)
        .agg(
            Total_Sales=(COL_SALES, "sum"),
            Total_Profit=(COL_PROFIT, "sum"),
            Total_Orders=(COL_ORDER_ID, "nunique"),
        )
        .reset_index()
    )
    result["Profit_Margin_%"] = (
        (result["Total_Profit"] / result["Total_Sales"]) * 100
    ).round(2)
    result = result.sort_values("Total_Sales", ascending=False).reset_index(drop=True)
    return result


# ============================================
# 5. PRODUCT-WISE ANALYSIS
# ============================================

def product_wise_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Product-wise Sales, Profit, Orders, Margin."""
    result = (
        df.groupby(COL_PRODUCT_NAME)
        .agg(
            Total_Sales=(COL_SALES, "sum"),
            Total_Profit=(COL_PROFIT, "sum"),
            Total_Orders=(COL_ORDER_ID, "nunique"),
            Total_Quantity=(COL_QUANTITY, "sum"),
            Avg_Discount=(COL_DISCOUNT, "mean"),
        )
        .reset_index()
    )
    result["Profit_Margin_%"] = (
        (result["Total_Profit"] / result["Total_Sales"]) * 100
    ).round(2)
    result["Avg_Discount"] = result["Avg_Discount"].round(2)
    result = result.sort_values("Total_Sales", ascending=False).reset_index(drop=True)
    return result


# ============================================
# 6. TOP PRODUCTS
# ============================================

def top_products(df: pd.DataFrame, n: int = TOP_N) -> pd.DataFrame:
    """Top N products by Sales."""
    result = product_wise_analysis(df).head(n).reset_index(drop=True)
    logger.info(f"Top {n} products calculated")
    return result


# ============================================
# 7. BOTTOM PRODUCTS
# ============================================

def bottom_products(df: pd.DataFrame, n: int = BOTTOM_N) -> pd.DataFrame:
    """Bottom N products by Profit (sabse kam profit / loss)."""
    result = (
        product_wise_analysis(df)
        .sort_values("Total_Profit", ascending=True)
        .head(n)
        .reset_index(drop=True)
    )
    logger.info(f"Bottom {n} products calculated")
    return result


# ============================================
# 8. MONTHLY SALES TREND
# ============================================

def monthly_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Year_Month ke hisaab se Sales, Profit, Orders."""
    result = (
        df.groupby("Year_Month")
        .agg(
            Total_Sales=(COL_SALES, "sum"),
            Total_Profit=(COL_PROFIT, "sum"),
            Total_Orders=(COL_ORDER_ID, "nunique"),
        )
        .reset_index()
        .sort_values("Year_Month")
        .reset_index(drop=True)
    )
    result["Profit_Margin_%"] = (
        (result["Total_Profit"] / result["Total_Sales"]) * 100
    ).round(2)
    logger.info(f"Monthly trend: {len(result)} months")
    return result


# ============================================
# 9. QUARTERLY ANALYSIS
# ============================================

def quarterly_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Quarter-wise Sales, Profit."""
    result = (
        df.groupby(["Year", "Quarter_Label"])
        .agg(
            Total_Sales=(COL_SALES, "sum"),
            Total_Profit=(COL_PROFIT, "sum"),
            Total_Orders=(COL_ORDER_ID, "nunique"),
        )
        .reset_index()
        .sort_values(["Year", "Quarter_Label"])
        .reset_index(drop=True)
    )
    return result


# ============================================
# 10. YEARLY ANALYSIS
# ============================================

def yearly_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Year-wise Sales, Profit, Orders."""
    result = (
        df.groupby("Year")
        .agg(
            Total_Sales=(COL_SALES, "sum"),
            Total_Profit=(COL_PROFIT, "sum"),
            Total_Orders=(COL_ORDER_ID, "nunique"),
        )
        .reset_index()
        .sort_values("Year")
        .reset_index(drop=True)
    )
    result["Profit_Margin_%"] = (
        (result["Total_Profit"] / result["Total_Sales"]) * 100
    ).round(2)
    return result


# ============================================
# 11. DISCOUNT IMPACT
# ============================================

def discount_impact(df: pd.DataFrame) -> pd.DataFrame:
    """
    Discount level ke hisaab se Avg Profit, Total Sales.
    Discount vs Profit relationship dekhne ke liye.
    """
    result = (
        df.groupby(COL_DISCOUNT)
        .agg(
            Total_Sales=(COL_SALES, "sum"),
            Total_Profit=(COL_PROFIT, "sum"),
            Orders=(COL_ORDER_ID, "nunique"),
            Avg_Profit=(COL_PROFIT, "mean"),
        )
        .reset_index()
        .sort_values(COL_DISCOUNT)
        .reset_index(drop=True)
    )
    result["Total_Sales"] = result["Total_Sales"].round(2)
    result["Total_Profit"] = result["Total_Profit"].round(2)
    result["Avg_Profit"] = result["Avg_Profit"].round(2)
    return result


# ============================================
# 12. DISCOUNT BAND ANALYSIS
# ============================================

def discount_band_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Discount_Band ke hisaab se summary."""
    order = ["No Discount", "Low", "Medium", "High", "Very High"]
    result = (
        df.groupby("Discount_Band")
        .agg(
            Total_Sales=(COL_SALES, "sum"),
            Total_Profit=(COL_PROFIT, "sum"),
            Orders=(COL_ORDER_ID, "nunique"),
            Avg_Profit_Margin=("Profit_Margin", "mean"),
        )
        .reset_index()
    )
    result["Profit_Margin_%"] = (
        (result["Total_Profit"] / result["Total_Sales"]) * 100
    ).round(2)
    result["Avg_Profit_Margin"] = result["Avg_Profit_Margin"].round(2)
    result["Discount_Band"] = pd.Categorical(
        result["Discount_Band"], categories=order, ordered=True
    )
    result = result.sort_values("Discount_Band").reset_index(drop=True)
    return result


# ============================================
# 13. PROFIT STATUS ANALYSIS
# ============================================

def profit_status_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Profit_Status (Profit/Loss/Break-even) breakdown."""
    result = (
        df.groupby("Profit_Status")
        .agg(
            Orders=(COL_ORDER_ID, "nunique"),
            Total_Sales=(COL_SALES, "sum"),
            Total_Profit=(COL_PROFIT, "sum"),
        )
        .reset_index()
    )
    total_orders = result["Orders"].sum()
    result["Orders_%"] = (result["Orders"] / total_orders * 100).round(2)
    return result


# ============================================
# 14. SEASON ANALYSIS
# ============================================

def season_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Season-wise Sales, Profit."""
    result = (
        df.groupby("Season")
        .agg(
            Total_Sales=(COL_SALES, "sum"),
            Total_Profit=(COL_PROFIT, "sum"),
            Orders=(COL_ORDER_ID, "nunique"),
        )
        .reset_index()
        .sort_values("Total_Sales", ascending=False)
        .reset_index(drop=True)
    )
    result["Profit_Margin_%"] = (
        (result["Total_Profit"] / result["Total_Sales"]) * 100
    ).round(2)
    return result


# ============================================
# 15. WEEKDAY ANALYSIS
# ============================================

def weekday_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Weekday vs Weekend summary."""
    result = (
        df.groupby("Is_Weekend")
        .agg(
            Total_Sales=(COL_SALES, "sum"),
            Total_Profit=(COL_PROFIT, "sum"),
            Orders=(COL_ORDER_ID, "nunique"),
        )
        .reset_index()
    )
    result["Day_Type"] = result["Is_Weekend"].map(
        {True: "Weekend", False: "Weekday"}
    )
    result = result[["Day_Type", "Total_Sales", "Total_Profit", "Orders"]]
    return result


# ============================================
# 16. CUSTOMER ANALYSIS
# ============================================

def customer_analysis(df: pd.DataFrame, n: int = TOP_N) -> pd.DataFrame:
    """Top N customers by Sales."""
    result = (
        df.groupby(COL_CUSTOMER_NAME)
        .agg(
            Total_Sales=(COL_SALES, "sum"),
            Total_Profit=(COL_PROFIT, "sum"),
            Orders=(COL_ORDER_ID, "nunique"),
        )
        .reset_index()
        .sort_values("Total_Sales", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )
    return result


# ============================================
# 17. PAYMENT MODE ANALYSIS
# ============================================

def payment_mode_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Payment_Mode wise Sales, Profit, Orders."""
    result = (
        df.groupby(COL_PAYMENT_MODE)
        .agg(
            Total_Sales=(COL_SALES, "sum"),
            Total_Profit=(COL_PROFIT, "sum"),
            Orders=(COL_ORDER_ID, "nunique"),
        )
        .reset_index()
        .sort_values("Total_Sales", ascending=False)
        .reset_index(drop=True)
    )
    return result


# ============================================
# 18. LOSS MAKING PRODUCTS
# ============================================

def loss_making_products(df: pd.DataFrame) -> pd.DataFrame:
    """Sirf woh products jo loss de rahe hain."""
    prod = product_wise_analysis(df)
    result = prod[prod["Total_Profit"] < 0].sort_values(
        "Total_Profit", ascending=True
    ).reset_index(drop=True)
    logger.info(f"Loss-making products: {len(result)}")
    return result


# ============================================
# 19. HIGH DISCOUNT ALERT
# ============================================

def high_discount_alert(
    df: pd.DataFrame,
    threshold: float = MIN_DISCOUNT_ALERT * 100,
) -> pd.DataFrame:
    """Jin orders me discount threshold se zyada hai."""
    result = df[df[COL_DISCOUNT] > threshold].copy()
    result = result.sort_values(COL_DISCOUNT, ascending=False)
    logger.info(f"High discount orders (>{threshold}%): {len(result)}")
    return result


# ============================================
# 20. RUN ALL ANALYSIS
# ============================================

def run_all_analysis(df: pd.DataFrame) -> dict:
    """
    Saare analysis ek saath run karke dict return karta hai.
    """
    logger.info("=" * 50)
    logger.info("RUNNING ALL ANALYSIS")
    logger.info("=" * 50)

    results = {
        "kpis": overall_kpis(df),
        "region": region_wise_analysis(df),
        "category": category_wise_analysis(df),
        "segment": segment_wise_analysis(df),
        "product": product_wise_analysis(df),
        "top_products": top_products(df),
        "bottom_products": bottom_products(df),
        "monthly_trend": monthly_sales_trend(df),
        "quarterly": quarterly_analysis(df),
        "yearly": yearly_analysis(df),
        "discount_impact": discount_impact(df),
        "discount_band": discount_band_analysis(df),
        "profit_status": profit_status_analysis(df),
        "season": season_analysis(df),
        "weekday": weekday_analysis(df),
        "customers": customer_analysis(df),
        "payment_mode": payment_mode_analysis(df),
        "loss_products": loss_making_products(df),
    }
    logger.info("All analysis complete.")
    return results


# ============================================
# 21. PRINT SUMMARY
# ============================================

def print_analysis_summary(results: dict) -> None:
    """Analysis ka short summary print karta hai."""
    print("\n" + "=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)

    print_kpis(results["kpis"])

    print("\n--- TOP 5 REGIONS ---")
    print(results["region"].head(5).to_string(index=False))

    print("\n--- TOP 5 CATEGORIES ---")
    print(results["category"].head(5).to_string(index=False))

    print("\n--- TOP 5 PRODUCTS ---")
    print(results["top_products"].head(5).to_string(index=False))

    print("\n--- BOTTOM 5 PRODUCTS (by Profit) ---")
    print(results["bottom_products"].head(5).to_string(index=False))

    print("\n--- DISCOUNT BAND ---")
    print(results["discount_band"].to_string(index=False))

    print("\n--- PROFIT STATUS ---")
    print(results["profit_status"].to_string(index=False))

    print("\n--- SEASON ---")
    print(results["season"].to_string(index=False))

    print("\n--- PAYMENT MODE ---")
    print(results["payment_mode"].to_string(index=False))

    print("=" * 70)


# ============================================
# 22. MAIN (self-test)
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ANALYSIS - SELF TEST")
    print("=" * 70)

    np.random.seed(42)
    n = 200
    dates = pd.date_range("2023-01-01", periods=n, freq="2D")

    sample = pd.DataFrame({
        "Order_ID": [f"ORD{i:04d}" for i in range(n)],
        "Order_Date": dates,
        "Customer_Name": np.random.choice(
            [f"Cust{i}" for i in range(30)], n
        ),
        "Region": np.random.choice(
            ["North", "South", "East", "West"], n
        ),
        "Category": np.random.choice(
            ["Furniture", "Technology", "Office Supplies"], n
        ),
        "Segment": np.random.choice(
            ["Consumer", "Corporate", "Home Office"], n
        ),
        "Product_Name": np.random.choice(
            [f"Product{i}" for i in range(20)], n
        ),
        "Payment_Mode": np.random.choice(
            ["UPI", "Card", "Cash"], n
        ),
        "Quantity": np.random.randint(1, 10, n),
        "Unit_Price": np.random.randint(200, 5000, n).astype(float),
        "Discount": np.random.choice([0, 5, 10, 15, 20, 25, 30, 40], n),
    })
    sample["Sales"] = (sample["Quantity"] * sample["Unit_Price"]).round(2)
    sample["Profit"] = (
        sample["Sales"] * (0.20 - sample["Discount"] / 100)
    ).round(2)

    sample["Year"] = sample["Order_Date"].dt.year
    sample["Month"] = sample["Order_Date"].dt.month
    sample["Month_Name"] = sample["Order_Date"].dt.strftime("%b")
    sample["Quarter"] = sample["Order_Date"].dt.quarter
    sample["Quarter_Label"] = "Q" + sample["Quarter"].astype(str)
    sample["Year_Month"] = sample["Order_Date"].dt.strftime("%Y-%m")
    sample["Weekday"] = sample["Order_Date"].dt.day_name()
    sample["Is_Weekend"] = sample["Order_Date"].dt.weekday >= 5
    sample["Profit_Margin"] = (
        sample["Profit"] / sample["Sales"] * 100
    ).round(2)

    def season(m):
        if m in (12, 1, 2): return "Winter"
        if m in (3, 4, 5): return "Summer"
        if m in (6, 7, 8, 9): return "Monsoon"
        return "Post-Monsoon"

    sample["Season"] = sample["Month"].apply(season)
    sample["Discount_Band"] = pd.cut(
        sample["Discount"],
        bins=[-1, 0, 10, 20, 30, 100],
        labels=["No Discount", "Low", "Medium", "High", "Very High"],
    ).astype(str)
    sample["Profit_Status"] = np.where(
        sample["Profit"] > 0, "Profit",
        np.where(sample["Profit"] == 0, "Break-even", "Loss")
    )

    print(f"\nSample data: {sample.shape}")

    print("\n[TEST 1] overall_kpis()")
    kpis = overall_kpis(sample)
    print_kpis(kpis)

    print("\n[TEST 2] region_wise_analysis()")
    print(region_wise_analysis(sample).to_string(index=False))

    print("\n[TEST 3] category_wise_analysis()")
    print(category_wise_analysis(sample).to_string(index=False))

    print("\n[TEST 4] top_products()")
    print(top_products(sample, n=5).to_string(index=False))

    print("\n[TEST 5] bottom_products()")
    print(bottom_products(sample, n=5).to_string(index=False))

    print("\n[TEST 6] monthly_sales_trend() (first 5)")
    print(monthly_sales_trend(sample).head().to_string(index=False))

    print("\n[TEST 7] discount_band_analysis()")
    print(discount_band_analysis(sample).to_string(index=False))

    print("\n[TEST 8] profit_status_analysis()")
    print(profit_status_analysis(sample).to_string(index=False))

    print("\n[TEST 9] season_analysis()")
    print(season_analysis(sample).to_string(index=False))

    print("\n[TEST 10] payment_mode_analysis()")
    print(payment_mode_analysis(sample).to_string(index=False))

    print("\n[TEST 11] loss_making_products()")
    loss_df = loss_making_products(sample)
    print(f"  Loss making products: {len(loss_df)}")
    if len(loss_df) > 0:
        print(loss_df.head().to_string(index=False))

    print("\n[TEST 12] high_discount_alert()")
    alert_df = high_discount_alert(sample)
    print(f"  High discount orders: {len(alert_df)}")

    print("\n[TEST 13] run_all_analysis()")
    all_res = run_all_analysis(sample)
    print(f"  Analysis sections: {list(all_res.keys())}")

    print("\n" + "=" * 70)
    print("[OK] analysis.py - All tests passed.")
    print("=" * 70)