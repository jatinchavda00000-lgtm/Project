# ============================================
# Retail Sales Data Analysis
# File: src/visualization.py
# Purpose: Create charts and save them as PNG files
# ============================================

"""
This file creates all charts and saves them in the images/ folder.
No API. Uses Matplotlib + Seaborn.

Visualization Functions:
- setup_style()               : Set global plot style
- plot_sales_distribution()   : Sales histogram
- plot_profit_distribution()  : Profit histogram
- plot_region_sales()         : Region-wise bar chart
- plot_region_profit()        : Region-wise profit bar
- plot_category_sales()       : Category-wise pie/bar
- plot_monthly_trend()        : Monthly sales line chart
- plot_quarterly_trend()      : Quarter-wise bar
- plot_top_products()         : Top N products bar
- plot_bottom_products()      : Bottom N products bar
- plot_discount_vs_profit()   : Scatter plot
- plot_discount_band()        : Discount band bar
- plot_profit_status_pie()    : Profit/Loss pie
- plot_season_analysis()      : Season-wise bar
- plot_payment_mode()         : Payment mode bar
- plot_correlation_heatmap()  : Correlation heatmap
- plot_boxplot_outliers()     : Boxplot for outliers
- plot_customer_segment()     : Segment-wise bar
- plot_weekday_analysis()     : Weekday vs Weekend
- create_all_plots()          : Create all plots together
"""

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend (for saving files)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

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
    IMAGES_DIR,
    FIG_SIZE_WIDE,
    FIG_SIZE_SQUARE,
    FIG_SIZE_SMALL,
    FIG_DPI,
    COLOR_PALETTE,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    ACCENT_COLOR,
    DANGER_COLOR,
    SUCCESS_COLOR,
    TOP_N,
    BOTTOM_N,
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
# 0. SETUP STYLE
# ============================================

def setup_style() -> None:
    """Sets global plot style."""
    sns.set_theme(style="whitegrid", palette=COLOR_PALETTE)
    plt.rcParams.update({
        "figure.dpi": 100,
        "savefig.dpi": FIG_DPI,
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.labelweight": "bold",
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.autolayout": True,
    })
    logger.info("Plot style set.")


# ============================================
# HELPER: SAVE FIGURE
# ============================================

def _save_fig(fig, filename: str, tight: bool = True) -> Path:
    """Saves figure to images/ folder."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    path = IMAGES_DIR / filename
    if tight:
        fig.tight_layout()
    fig.savefig(path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved: {path.name}")
    return path


# ============================================
# 1. SALES DISTRIBUTION
# ============================================

def plot_sales_distribution(df: pd.DataFrame) -> Path:
    """Sales histogram + KDE."""
    fig, axes = plt.subplots(1, 2, figsize=FIG_SIZE_WIDE)

    sns.histplot(df[COL_SALES], bins=30, kde=True, ax=axes[0],
                 color=PRIMARY_COLOR)
    axes[0].set_title("Sales Distribution (Histogram)")
    axes[0].set_xlabel("Sales (Rs.)")
    axes[0].set_ylabel("Frequency")

    sns.boxplot(x=df[COL_SALES], ax=axes[1], color=SECONDARY_COLOR)
    axes[1].set_title("Sales Boxplot (Outliers)")
    axes[1].set_xlabel("Sales (Rs.)")

    fig.suptitle("Sales Distribution Analysis", fontsize=15, fontweight="bold")
    return _save_fig(fig, "01_sales_distribution.png")


# ============================================
# 2. PROFIT DISTRIBUTION
# ============================================

def plot_profit_distribution(df: pd.DataFrame) -> Path:
    """Profit histogram + KDE."""
    fig, axes = plt.subplots(1, 2, figsize=FIG_SIZE_WIDE)

    sns.histplot(df[COL_PROFIT], bins=30, kde=True, ax=axes[0],
                 color=SUCCESS_COLOR)
    axes[0].axvline(0, color="red", linestyle="--", linewidth=1.5,
                    label="Break-even")
    axes[0].set_title("Profit Distribution")
    axes[0].set_xlabel("Profit (Rs.)")
    axes[0].legend()

    sns.boxplot(x=df[COL_PROFIT], ax=axes[1], color=ACCENT_COLOR)
    axes[1].axvline(0, color="red", linestyle="--", linewidth=1.5)
    axes[1].set_title("Profit Boxplot")
    axes[1].set_xlabel("Profit (Rs.)")

    fig.suptitle("Profit Distribution Analysis", fontsize=15, fontweight="bold")
    return _save_fig(fig, "02_profit_distribution.png")


# ============================================
# 3. REGION-WISE SALES
# ============================================

def plot_region_sales(df: pd.DataFrame) -> Path:
    """Region-wise Sales bar chart."""
    data = (
        df.groupby(COL_REGION)[COL_SALES].sum()
        .sort_values(ascending=False).reset_index()
    )

    fig, ax = plt.subplots(figsize=FIG_SIZE_WIDE)
    sns.barplot(data=data, x=COL_REGION, y=COL_SALES,
                ax=ax, palette=COLOR_PALETTE)

    for i, v in enumerate(data[COL_SALES]):
        ax.text(i, v, f"Rs.{v:,.0f}", ha="center", va="bottom",
                fontsize=10, fontweight="bold")

    ax.set_title("Region-wise Total Sales")
    ax.set_xlabel("Region")
    ax.set_ylabel("Total Sales (Rs.)")
    return _save_fig(fig, "03_region_sales.png")


# ============================================
# 4. REGION-WISE PROFIT
# ============================================

def plot_region_profit(df: pd.DataFrame) -> Path:
    """Region-wise Profit bar chart."""
    data = (
        df.groupby(COL_REGION)[COL_PROFIT].sum()
        .sort_values(ascending=False).reset_index()
    )

    colors = [SUCCESS_COLOR if v >= 0 else DANGER_COLOR
              for v in data[COL_PROFIT]]

    fig, ax = plt.subplots(figsize=FIG_SIZE_WIDE)
    sns.barplot(data=data, x=COL_REGION, y=COL_PROFIT,
                ax=ax, palette=colors)

    ax.axhline(0, color="black", linewidth=1)
    for i, v in enumerate(data[COL_PROFIT]):
        offset = abs(v) * 0.02 if v != 0 else 0
        ax.text(i, v + (offset if v >= 0 else -offset),
                f"Rs.{v:,.0f}", ha="center",
                va="bottom" if v >= 0 else "top",
                fontsize=10, fontweight="bold")

    ax.set_title("Region-wise Total Profit")
    ax.set_xlabel("Region")
    ax.set_ylabel("Total Profit (Rs.)")
    return _save_fig(fig, "04_region_profit.png")


# ============================================
# 5. CATEGORY-WISE SALES
# ============================================

def plot_category_sales(df: pd.DataFrame) -> Path:
    """Category-wise Sales bar + pie."""
    data = (
        df.groupby(COL_CATEGORY)[COL_SALES].sum()
        .sort_values(ascending=False).reset_index()
    )

    fig, axes = plt.subplots(1, 2, figsize=FIG_SIZE_WIDE)

    sns.barplot(data=data, x=COL_CATEGORY, y=COL_SALES, ax=axes[0],
                palette=COLOR_PALETTE)
    axes[0].set_title("Category-wise Sales (Bar)")
    axes[0].set_xlabel("Category")
    axes[0].set_ylabel("Total Sales (Rs.)")
    axes[0].tick_params(axis="x", rotation=15)

    axes[1].pie(data[COL_SALES], labels=data[COL_CATEGORY],
                autopct="%1.1f%%", startangle=90,
                colors=sns.color_palette(COLOR_PALETTE, len(data)))
    axes[1].set_title("Category Share (Pie)")

    fig.suptitle("Category-wise Sales Analysis", fontsize=15, fontweight="bold")
    return _save_fig(fig, "05_category_sales.png")


# ============================================
# 6. MONTHLY SALES TREND
# ============================================

def plot_monthly_trend(df: pd.DataFrame) -> Path:
    """Monthly Sales + Profit line chart (dual axis)."""
    data = (
        df.groupby("Year_Month")
        .agg(Sales=(COL_SALES, "sum"), Profit=(COL_PROFIT, "sum"))
        .reset_index().sort_values("Year_Month")
    )

    fig, ax1 = plt.subplots(figsize=FIG_SIZE_WIDE)

    ax1.plot(data["Year_Month"], data["Sales"], marker="o",
             color=PRIMARY_COLOR, linewidth=2, label="Sales")
    ax1.set_xlabel("Year-Month")
    ax1.set_ylabel("Sales (Rs.)", color=PRIMARY_COLOR)
    ax1.tick_params(axis="y", labelcolor=PRIMARY_COLOR)
    ax1.tick_params(axis="x", rotation=45)

    ax2 = ax1.twinx()
    ax2.plot(data["Year_Month"], data["Profit"], marker="s",
             color=SECONDARY_COLOR, linewidth=2, label="Profit")
    ax2.set_ylabel("Profit (Rs.)", color=SECONDARY_COLOR)
    ax2.tick_params(axis="y", labelcolor=SECONDARY_COLOR)
    ax2.axhline(0, color="red", linestyle="--", linewidth=1, alpha=0.6)

    ax1.set_title("Monthly Sales & Profit Trend")
    fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.95))
    return _save_fig(fig, "06_monthly_trend.png")


# ============================================
# 7. QUARTERLY TREND
# ============================================

def plot_quarterly_trend(df: pd.DataFrame) -> Path:
    """Quarter-wise Sales bar chart."""
    data = (
        df.groupby(["Year", "Quarter_Label"])[COL_SALES].sum()
        .reset_index()
    )
    data["Period"] = data["Year"].astype(str) + "-" + data["Quarter_Label"]

    fig, ax = plt.subplots(figsize=FIG_SIZE_WIDE)
    sns.barplot(data=data, x="Period", y=COL_SALES,
                ax=ax, palette=COLOR_PALETTE)
    ax.set_title("Quarterly Sales Trend")
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Total Sales (Rs.)")
    ax.tick_params(axis="x", rotation=45)
    return _save_fig(fig, "07_quarterly_trend.png")


# ============================================
# 8. TOP PRODUCTS
# ============================================

def plot_top_products(df: pd.DataFrame, n: int = TOP_N) -> Path:
    """Top N products by Sales."""
    data = (
        df.groupby(COL_PRODUCT_NAME)[COL_SALES].sum()
        .sort_values(ascending=False).head(n).reset_index()
    )

    fig, ax = plt.subplots(figsize=FIG_SIZE_WIDE)
    sns.barplot(data=data, y=COL_PRODUCT_NAME, x=COL_SALES,
                ax=ax, palette="Greens_r")

    for i, v in enumerate(data[COL_SALES]):
        ax.text(v, i, f" Rs.{v:,.0f}", va="center",
                fontsize=9, fontweight="bold")

    ax.set_title(f"Top {n} Products by Sales")
    ax.set_xlabel("Total Sales (Rs.)")
    ax.set_ylabel("Product")
    return _save_fig(fig, "08_top_products.png")


# ============================================
# 9. BOTTOM PRODUCTS
# ============================================

def plot_bottom_products(df: pd.DataFrame, n: int = BOTTOM_N) -> Path:
    """Bottom N products by Profit."""
    data = (
        df.groupby(COL_PRODUCT_NAME)[COL_PROFIT].sum()
        .sort_values(ascending=True).head(n).reset_index()
    )

    colors = [DANGER_COLOR if v < 0 else ACCENT_COLOR
              for v in data[COL_PROFIT]]

    fig, ax = plt.subplots(figsize=FIG_SIZE_WIDE)
    sns.barplot(data=data, y=COL_PRODUCT_NAME, x=COL_PROFIT,
                ax=ax, palette=colors)
    ax.axvline(0, color="black", linewidth=1)

    for i, v in enumerate(data[COL_PROFIT]):
        ax.text(v, i, f" Rs.{v:,.0f}", va="center",
                fontsize=9, fontweight="bold",
                color=DANGER_COLOR if v < 0 else "black")

    ax.set_title(f"Bottom {n} Products by Profit")
    ax.set_xlabel("Total Profit (Rs.)")
    ax.set_ylabel("Product")
    return _save_fig(fig, "09_bottom_products.png")


# ============================================
# 10. DISCOUNT VS PROFIT
# ============================================

def plot_discount_vs_profit(df: pd.DataFrame) -> Path:
    """Discount vs Profit scatter plot with trend line."""
    fig, ax = plt.subplots(figsize=FIG_SIZE_WIDE)

    sns.scatterplot(data=df, x=COL_DISCOUNT, y=COL_PROFIT,
                    hue=COL_CATEGORY, alpha=0.6, ax=ax,
                    palette=COLOR_PALETTE, s=50)

    # Trend line
    if df[COL_DISCOUNT].nunique() > 1:
        z = np.polyfit(df[COL_DISCOUNT], df[COL_PROFIT], 1)
        p = np.poly1d(z)
        x_line = np.linspace(df[COL_DISCOUNT].min(),
                             df[COL_DISCOUNT].max(), 100)
        ax.plot(x_line, p(x_line), "r--", linewidth=2,
                label=f"Trend (slope={z[0]:.2f})")

    ax.axhline(0, color="black", linewidth=1, linestyle="--")
    ax.set_title("Discount vs Profit Relationship")
    ax.set_xlabel("Discount (%)")
    ax.set_ylabel("Profit (Rs.)")
    ax.legend(loc="best", fontsize=9)
    return _save_fig(fig, "10_discount_vs_profit.png")


# ============================================
# 11. DISCOUNT BAND
# ============================================

def plot_discount_band(df: pd.DataFrame) -> Path:
    """Discount band wise profit + margin."""
    order = ["No Discount", "Low", "Medium", "High", "Very High"]
    data = (
        df.groupby("Discount_Band")
        .agg(Sales=(COL_SALES, "sum"),
             Profit=(COL_PROFIT, "sum"),
             Orders=(COL_ORDER_ID, "nunique"))
        .reindex(order).dropna().reset_index()
    )

    fig, axes = plt.subplots(1, 2, figsize=FIG_SIZE_WIDE)

    sns.barplot(data=data, x="Discount_Band", y="Profit",
                ax=axes[0], palette="RdYlGn")
    axes[0].axhline(0, color="black", linewidth=1)
    axes[0].set_title("Profit by Discount Band")
    axes[0].set_xlabel("Discount Band")
    axes[0].set_ylabel("Total Profit (Rs.)")

    sns.barplot(data=data, x="Discount_Band", y="Orders",
                ax=axes[1], palette="Blues")
    axes[1].set_title("Orders by Discount Band")
    axes[1].set_xlabel("Discount Band")
    axes[1].set_ylabel("Number of Orders")

    fig.suptitle("Discount Band Analysis", fontsize=15, fontweight="bold")
    return _save_fig(fig, "11_discount_band.png")


# ============================================
# 12. PROFIT STATUS PIE
# ============================================

def plot_profit_status_pie(df: pd.DataFrame) -> Path:
    """Profit / Loss / Break-even pie chart."""
    data = df.groupby("Profit_Status")[COL_ORDER_ID].nunique().reset_index()
    data.columns = ["Status", "Orders"]

    color_map = {"Profit": SUCCESS_COLOR,
                 "Loss": DANGER_COLOR,
                 "Break-even": ACCENT_COLOR}
    colors = [color_map.get(s, PRIMARY_COLOR) for s in data["Status"]]

    fig, ax = plt.subplots(figsize=FIG_SIZE_SMALL)
    ax.pie(data["Orders"], labels=data["Status"], autopct="%1.1f%%",
           startangle=90, colors=colors, explode=[0.03] * len(data))
    ax.set_title("Profit Status Distribution")
    return _save_fig(fig, "12_profit_status_pie.png")


# ============================================
# 13. SEASON ANALYSIS
# ============================================

def plot_season_analysis(df: pd.DataFrame) -> Path:
    """Season-wise Sales + Profit."""
    data = (
        df.groupby("Season")
        .agg(Sales=(COL_SALES, "sum"), Profit=(COL_PROFIT, "sum"))
        .reset_index().sort_values("Sales", ascending=False)
    )

    fig, ax = plt.subplots(figsize=FIG_SIZE_WIDE)
    x = np.arange(len(data))
    width = 0.38

    ax.bar(x - width/2, data["Sales"], width,
           label="Sales", color=PRIMARY_COLOR)
    ax.bar(x + width/2, data["Profit"], width,
           label="Profit", color=SECONDARY_COLOR)

    ax.set_xticks(x)
    ax.set_xticklabels(data["Season"])
    ax.axhline(0, color="black", linewidth=1)
    ax.set_title("Season-wise Sales & Profit")
    ax.set_xlabel("Season")
    ax.set_ylabel("Amount (Rs.)")
    ax.legend()
    return _save_fig(fig, "13_season_analysis.png")


# ============================================
# 14. PAYMENT MODE
# ============================================

def plot_payment_mode(df: pd.DataFrame) -> Path:
    """Payment mode wise Sales bar + pie."""
    data = (
        df.groupby(COL_PAYMENT_MODE)[COL_SALES].sum()
        .sort_values(ascending=False).reset_index()
    )

    fig, axes = plt.subplots(1, 2, figsize=FIG_SIZE_WIDE)

    sns.barplot(data=data, x=COL_PAYMENT_MODE, y=COL_SALES,
                ax=axes[0], palette=COLOR_PALETTE)
    axes[0].set_title("Sales by Payment Mode")
    axes[0].set_xlabel("Payment Mode")
    axes[0].set_ylabel("Total Sales (Rs.)")

    axes[1].pie(data[COL_SALES], labels=data[COL_PAYMENT_MODE],
                autopct="%1.1f%%", startangle=90,
                colors=sns.color_palette(COLOR_PALETTE, len(data)))
    axes[1].set_title("Payment Mode Share")

    fig.suptitle("Payment Mode Analysis", fontsize=15, fontweight="bold")
    return _save_fig(fig, "14_payment_mode.png")


# ============================================
# 15. CORRELATION HEATMAP
# ============================================

def plot_correlation_heatmap(df: pd.DataFrame) -> Path:
    """Correlation heatmap of numeric columns."""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        logger.warning("At least 2 numeric columns required for correlation.")
        fig, ax = plt.subplots(figsize=FIG_SIZE_SMALL)
        ax.text(0.5, 0.5, "Not enough numeric columns",
                ha="center", va="center")
        return _save_fig(fig, "15_correlation_heatmap.png")

    corr = numeric_df.corr(numeric_only=True)

    fig, ax = plt.subplots(figsize=FIG_SIZE_SQUARE)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                center=0, linewidths=0.5, ax=ax,
                cbar_kws={"shrink": 0.8})
    ax.set_title("Correlation Heatmap (Numeric Columns)")
    return _save_fig(fig, "15_correlation_heatmap.png")


# ============================================
# 16. BOXPLOT OUTLIERS
# ============================================

def plot_boxplot_outliers(df: pd.DataFrame) -> Path:
    """Boxplots for Sales and Profit."""
    fig, axes = plt.subplots(1, 2, figsize=FIG_SIZE_WIDE)

    sns.boxplot(y=df[COL_SALES], ax=axes[0], color=PRIMARY_COLOR)
    axes[0].set_title("Sales - Outlier Check")
    axes[0].set_ylabel("Sales (Rs.)")

    sns.boxplot(y=df[COL_PROFIT], ax=axes[1], color=SECONDARY_COLOR)
    axes[1].axhline(0, color="red", linestyle="--", linewidth=1)
    axes[1].set_title("Profit - Outlier Check")
    axes[1].set_ylabel("Profit (Rs.)")

    fig.suptitle("Outlier Detection (Boxplots)",
                 fontsize=15, fontweight="bold")
    return _save_fig(fig, "16_boxplot_outliers.png")


# ============================================
# 17. CUSTOMER SEGMENT
# ============================================

def plot_customer_segment(df: pd.DataFrame) -> Path:
    """Segment-wise Sales + Orders."""
    data = (
        df.groupby(COL_SEGMENT)
        .agg(Sales=(COL_SALES, "sum"),
             Orders=(COL_ORDER_ID, "nunique"))
        .reset_index().sort_values("Sales", ascending=False)
    )

    fig, ax1 = plt.subplots(figsize=FIG_SIZE_WIDE)

    x = np.arange(len(data))
    bars = ax1.bar(x, data["Sales"], color=PRIMARY_COLOR,
                   label="Sales", width=0.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels(data[COL_SEGMENT])
    ax1.set_ylabel("Total Sales (Rs.)", color=PRIMARY_COLOR)
    ax1.set_xlabel("Customer Segment")

    ax2 = ax1.twinx()
    ax2.plot(x, data["Orders"], "o--", color=SECONDARY_COLOR,
             linewidth=2, markersize=10, label="Orders")
    ax2.set_ylabel("Number of Orders", color=SECONDARY_COLOR)
    ax2.tick_params(axis="y", labelcolor=SECONDARY_COLOR)

    ax1.set_title("Customer Segment Analysis")
    fig.legend(loc="upper right", bbox_to_anchor=(0.9, 0.95))
    return _save_fig(fig, "17_customer_segment.png")


# ============================================
# 18. WEEKDAY ANALYSIS
# ============================================

def plot_weekday_analysis(df: pd.DataFrame) -> Path:
    """Weekday vs Weekend sales."""
    data = (
        df.groupby("Is_Weekend")
        .agg(Sales=(COL_SALES, "sum"),
             Profit=(COL_PROFIT, "sum"),
             Orders=(COL_ORDER_ID, "nunique"))
        .reset_index()
    )
    data["Day_Type"] = data["Is_Weekend"].map(
        {True: "Weekend", False: "Weekday"}
    )

    fig, axes = plt.subplots(1, 2, figsize=FIG_SIZE_WIDE)

    sns.barplot(data=data, x="Day_Type", y="Sales",
                ax=axes[0], palette=[PRIMARY_COLOR, ACCENT_COLOR])
    axes[0].set_title("Sales: Weekday vs Weekend")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Total Sales (Rs.)")

    sns.barplot(data=data, x="Day_Type", y="Orders",
                ax=axes[1], palette=[PRIMARY_COLOR, ACCENT_COLOR])
    axes[1].set_title("Orders: Weekday vs Weekend")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Number of Orders")

    fig.suptitle("Weekday vs Weekend Analysis",
                 fontsize=15, fontweight="bold")
    return _save_fig(fig, "18_weekday_analysis.png")


# ============================================
# 19. CREATE ALL PLOTS
# ============================================

def create_all_plots(df: pd.DataFrame) -> list:
    """
    Creates all plots together.
    Returns list of saved file paths.
    """
    logger.info("=" * 50)
    logger.info("CREATING ALL VISUALIZATIONS")
    logger.info("=" * 50)

    setup_style()
    saved = []

    plot_functions = [
        ("sales_distribution", plot_sales_distribution),
        ("profit_distribution", plot_profit_distribution),
        ("region_sales", plot_region_sales),
        ("region_profit", plot_region_profit),
        ("category_sales", plot_category_sales),
        ("monthly_trend", plot_monthly_trend),
        ("quarterly_trend", plot_quarterly_trend),
        ("top_products", plot_top_products),
        ("bottom_products", plot_bottom_products),
        ("discount_vs_profit", plot_discount_vs_profit),
        ("discount_band", plot_discount_band),
        ("profit_status_pie", plot_profit_status_pie),
        ("season_analysis", plot_season_analysis),
        ("payment_mode", plot_payment_mode),
        ("correlation_heatmap", plot_correlation_heatmap),
        ("boxplot_outliers", plot_boxplot_outliers),
        ("customer_segment", plot_customer_segment),
        ("weekday_analysis", plot_weekday_analysis),
    ]

    for name, func in plot_functions:
        try:
            path = func(df)
            saved.append(path)
        except Exception as e:
            logger.error(f"Plot '{name}' failed: {e}")

    logger.info(f"Total plots saved: {len(saved)}")
    return saved


# ============================================
# 20. MAIN (self-test)
# ============================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("VISUALIZATION - SELF TEST")
    print("=" * 70)

    np.random.seed(42)
    n = 300
    dates = pd.date_range("2023-01-01", periods=n, freq="D")

    sample = pd.DataFrame({
        "Order_ID": [f"ORD{i:04d}" for i in range(n)],
        "Order_Date": dates,
        "Customer_Name": np.random.choice([f"C{i}" for i in range(50)], n),
        "Region": np.random.choice(["North", "South", "East", "West"], n),
        "Category": np.random.choice(
            ["Furniture", "Technology", "Office Supplies"], n),
        "Segment": np.random.choice(
            ["Consumer", "Corporate", "Home Office"], n),
        "Product_Name": np.random.choice([f"P{i}" for i in range(15)], n),
        "Payment_Mode": np.random.choice(["UPI", "Card", "Cash"], n),
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
        sample["Profit"] / sample["Sales"] * 100).round(2)

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
        np.where(sample["Profit"] == 0, "Break-even", "Loss"))
    sample["Customer_Type"] = "New"

    print(f"\nSample data: {sample.shape}")
    print("\n[RUNNING] Creating all plots...")

    paths = create_all_plots(sample)

    print(f"\n[RESULT] Total {len(paths)} plots saved:")
    for p in paths:
        print(f"  - {p.name}")

    print("\n" + "=" * 70)
    print("[OK] visualization.py - All plots created.")
    print(f"[OK] Check folder: {IMAGES_DIR}")
    print("=" * 70)