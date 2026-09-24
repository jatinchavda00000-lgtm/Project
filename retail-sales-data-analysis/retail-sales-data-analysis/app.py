# ============================================================
# Retail Sales Analytics Platform
# File: app.py
# Purpose: Interactive analytics dashboard
# Version: 1.1.0
# ============================================================

"""
Retail Sales Analytics Platform.

A Streamlit dashboard for retail sales data analysis.
Run: streamlit run app.py
"""

from __future__ import annotations

import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# ============================================================
# PROJECT IMPORTS
# ============================================================

try:
    from config import (
        RAW_DATA_FILE,
        CLEAN_DATA_FILE,
        SQLITE_DB_PATH,
        TABLE_NAME,
        OUTPUT_DIR,
        CURRENCY_SYMBOL,
        TOP_N,
        create_all_directories,
    )
    from data_loader import load_csv, save_to_sql
    from data_cleaning import clean_pipeline, validate_data
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
        high_discount_alert,
    )
    from utils import ensure_dir, save_json, format_currency, format_percent
except ImportError as exc:
    st.error(f"Import failed: {exc}. Run from project root.")
    st.stop()


# ============================================================
# CONSTANTS
# ============================================================

APP_NAME = "Retail Sales Analytics"
APP_VERSION = "1.1.0"

COLOR_PRIMARY = "#1F4E79"
COLOR_SUCCESS = "#2E7D32"
COLOR_DANGER = "#C62828"
COLOR_WARNING = "#ED6C02"


# ============================================================
# DATA CONTAINER
# ============================================================

@dataclass
class PipelineResult:
    raw_df: pd.DataFrame
    clean_df: pd.DataFrame
    results: dict = field(default_factory=dict)
    validation: dict = field(default_factory=dict)
    elapsed_seconds: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================================
# SYNTHETIC DATA
# ============================================================

@st.cache_data(show_spinner=False)
def generate_synthetic_dataset(n: int = 1500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    regions = ["North", "South", "East", "West"]
    categories = ["Furniture", "Technology", "Office Supplies"]
    segments = ["Consumer", "Corporate", "Home Office"]
    payments = ["UPI", "Card", "Cash", "Net Banking"]

    states = {
        "North": ["Delhi", "Punjab", "Haryana", "Uttar Pradesh"],
        "South": ["Karnataka", "Tamil Nadu", "Kerala", "Telangana"],
        "East": ["West Bengal", "Odisha", "Bihar", "Jharkhand"],
        "West": ["Maharashtra", "Gujarat", "Rajasthan", "Goa"],
    }

    cities = {
        "Delhi": "New Delhi", "Punjab": "Ludhiana",
        "Haryana": "Gurgaon", "Uttar Pradesh": "Lucknow",
        "Karnataka": "Bengaluru", "Tamil Nadu": "Chennai",
        "Kerala": "Kochi", "Telangana": "Hyderabad",
        "West Bengal": "Kolkata", "Odisha": "Bhubaneswar",
        "Bihar": "Patna", "Jharkhand": "Ranchi",
        "Maharashtra": "Mumbai", "Gujarat": "Ahmedabad",
        "Rajasthan": "Jaipur", "Goa": "Panaji",
    }

    dates = pd.date_range("2022-01-01", "2024-12-31", freq="D")
    sample_dates = rng.choice(dates, n)
    region_col = rng.choice(regions, n)
    state_col = [rng.choice(states[r]) for r in region_col]
    city_col = [cities[s] for s in state_col]

    df = pd.DataFrame({
        "Order ID": [f"ORD{10000 + i}" for i in range(n)],
        "Order Date": sample_dates,
        "Customer Name": rng.choice([f"Customer_{i:03d}" for i in range(150)], n),
        "Segment": rng.choice(segments, n),
        "Region": region_col,
        "State": state_col,
        "City": city_col,
        "Product Name": rng.choice([f"Product_{i:02d}" for i in range(60)], n),
        "Category": rng.choice(categories, n),
        "Quantity": rng.integers(1, 12, n),
        "Unit Price": np.round(rng.uniform(100, 5000, n), 2),
        "Discount": rng.choice([0, 5, 10, 15, 20, 25, 30, 35, 40], n),
        "Payment Mode": rng.choice(payments, n),
    })
    df["Sales"] = np.round(df["Quantity"] * df["Unit Price"], 2)
    df["Profit"] = np.round(df["Sales"] * (0.22 - df["Discount"] / 100.0), 2)

    df.loc[0:5, "Region"] = np.nan
    df.loc[10:12, "Category"] = np.nan
    df = pd.concat([df, df.iloc[0:5]], ignore_index=True)
    return df


# ============================================================
# PIPELINE
# ============================================================

def execute_pipeline(uploaded_file=None, force_synthetic=False, progress_callback=None):
    start_ts = datetime.now()

    def notify(pct, message):
        if progress_callback:
            progress_callback(pct, message)

    create_all_directories()

    # Load
    notify(10, "Loading source data")
    if uploaded_file is not None:
        raw_df = pd.read_csv(uploaded_file)
        RAW_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        raw_df.to_csv(RAW_DATA_FILE, index=False)
    elif RAW_DATA_FILE.exists() and not force_synthetic:
        raw_df = load_csv(RAW_DATA_FILE)
    else:
        raw_df = generate_synthetic_dataset()
        RAW_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        raw_df.to_csv(RAW_DATA_FILE, index=False)

    # Clean
    notify(25, "Cleaning data")
    clean_df = clean_pipeline(raw_df, remove_out=False)

    # Features
    notify(40, "Engineering features")
    feature_df = engineer_features(clean_df)

    # Save
    notify(50, "Saving cleaned data")
    CLEAN_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    feature_df.to_csv(CLEAN_DATA_FILE, index=False)

    # SQLite
    notify(60, "Writing to SQLite")
    if SQLITE_DB_PATH.exists():
        SQLITE_DB_PATH.unlink()
    save_to_sql(feature_df, table_name=TABLE_NAME, if_exists="replace")

    # Analysis
    notify(75, "Running analysis")
    results = {
        "kpis": overall_kpis(feature_df),
        "region": region_wise_analysis(feature_df),
        "category": category_wise_analysis(feature_df),
        "segment": segment_wise_analysis(feature_df),
        "product": product_wise_analysis(feature_df),
        "top_products": top_products(feature_df),
        "bottom_products": bottom_products(feature_df),
        "monthly": monthly_sales_trend(feature_df),
        "quarterly": quarterly_analysis(feature_df),
        "yearly": yearly_analysis(feature_df),
        "discount": discount_impact(feature_df),
        "discount_band": discount_band_analysis(feature_df),
        "profit_status": profit_status_analysis(feature_df),
        "season": season_analysis(feature_df),
        "weekday": weekday_analysis(feature_df),
        "customers": customer_analysis(feature_df),
        "payment_mode": payment_mode_analysis(feature_df),
        "loss_products": loss_making_products(feature_df),
        "high_discount": high_discount_alert(feature_df),
    }

    # Export
    notify(90, "Exporting results")
    ensure_dir(OUTPUT_DIR)
    for name, val in results.items():
        if isinstance(val, pd.DataFrame):
            val.to_csv(OUTPUT_DIR / f"app_{name}.csv", index=False)
    save_json(results["kpis"], OUTPUT_DIR / "app_kpis.json")

    notify(100, "Done")
    elapsed = (datetime.now() - start_ts).total_seconds()

    return PipelineResult(
        raw_df=raw_df,
        clean_df=feature_df,
        results=results,
        validation=validate_data(feature_df),
        elapsed_seconds=elapsed,
        timestamp=datetime.now(),
    )


# ============================================================
# CHART HELPERS
# ============================================================

def base_layout(height=400):
    return dict(
        template="plotly_white",
        height=height,
        margin=dict(l=40, r=20, t=60, b=40),
        font=dict(size=12),
    )


def chart_region_sales(df):
    fig = px.bar(df, x="Region", y="Total_Sales",
                 color="Total_Sales", color_continuous_scale="Blues",
                 text_auto=".2s")
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(**base_layout(), title="Revenue by Region",
                      coloraxis_showscale=False, showlegend=False)
    fig.update_yaxes(title="Revenue (Rs.)")
    fig.update_xaxes(title="")
    return fig


def chart_region_profit(df):
    colors = [COLOR_SUCCESS if v >= 0 else COLOR_DANGER for v in df["Total_Profit"]]
    fig = go.Figure(go.Bar(
        x=df["Region"], y=df["Total_Profit"],
        marker_color=colors, text=df["Total_Profit"].round(0),
        textposition="outside", cliponaxis=False,
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="#9ca3af")
    fig.update_layout(**base_layout(), title="Profit by Region", showlegend=False)
    fig.update_yaxes(title="Profit (Rs.)")
    fig.update_xaxes(title="")
    return fig


def chart_category_share(df):
    fig = px.pie(df, names="Category", values="Total_Sales", hole=0.55)
    fig.update_traces(textinfo="percent+label", textposition="outside")
    fig.update_layout(**base_layout(), title="Revenue Share by Category")
    return fig


def chart_category_margin(df):
    fig = px.bar(df, x="Category", y="Profit_Margin_%",
                 color="Profit_Margin_%", color_continuous_scale="RdYlGn",
                 text_auto=".1f")
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(**base_layout(), title="Profit Margin by Category",
                      coloraxis_showscale=False)
    fig.update_yaxes(title="Margin (%)")
    fig.update_xaxes(title="")
    return fig


def chart_monthly_trend(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Year_Month"], y=df["Total_Sales"],
        mode="lines+markers", name="Revenue",
        line=dict(color=COLOR_PRIMARY, width=2.5), marker=dict(size=7),
    ))
    fig.add_trace(go.Scatter(
        x=df["Year_Month"], y=df["Total_Profit"],
        mode="lines+markers", name="Profit",
        line=dict(color=COLOR_SUCCESS, width=2.5),
        marker=dict(size=7), yaxis="y2",
    ))
    layout = base_layout(height=440)
    layout.update(
        title="Monthly Revenue and Profit Trend",
        xaxis=dict(title="", tickangle=-45),
        yaxis=dict(title="Revenue (Rs.)"),
        yaxis2=dict(title="Profit (Rs.)", overlaying="y", side="right",
                    showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
    )
    fig.update_layout(**layout)
    return fig


def chart_top_products(df, n=10):
    data = df.head(n).sort_values("Total_Sales")
    fig = px.bar(data, x="Total_Sales", y="Product_Name", orientation="h",
                 color="Total_Sales", color_continuous_scale="Greens",
                 text_auto=".2s")
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(**base_layout(height=max(400, n * 30)),
                      title=f"Top {n} Products by Revenue",
                      coloraxis_showscale=False, showlegend=False)
    fig.update_xaxes(title="Revenue (Rs.)")
    fig.update_yaxes(title="")
    return fig


def chart_discount_impact(df):
    fig = go.Figure(go.Bar(
        x=df["Discount"], y=df["Total_Profit"],
        marker=dict(color=df["Total_Profit"], colorscale="RdYlGn", cmid=0),
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="#374151")
    fig.update_layout(**base_layout(), title="Profit by Discount Level",
                      showlegend=False)
    fig.update_xaxes(title="Discount (%)")
    fig.update_yaxes(title="Profit (Rs.)")
    return fig


def chart_discount_band(df):
    colors = [COLOR_SUCCESS if v >= 0 else COLOR_DANGER for v in df["Total_Profit"]]
    fig = go.Figure(go.Bar(
        x=df["Discount_Band"], y=df["Total_Profit"],
        marker_color=colors, text=df["Total_Profit"].round(0),
        textposition="outside", cliponaxis=False,
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="#374151")
    fig.update_layout(**base_layout(), title="Profit by Discount Band",
                      showlegend=False)
    fig.update_xaxes(title="Discount Band")
    fig.update_yaxes(title="Profit (Rs.)")
    return fig


def chart_profit_status(df):
    color_map = {"Profit": COLOR_SUCCESS, "Loss": COLOR_DANGER,
                 "Break-even": COLOR_WARNING}
    fig = px.pie(df, names="Profit_Status", values="Orders", hole=0.55,
                 color="Profit_Status", color_discrete_map=color_map)
    fig.update_traces(textinfo="percent+label", textposition="outside")
    fig.update_layout(**base_layout(), title="Order Profitability Split")
    return fig


def chart_payment(df):
    fig = px.bar(df, x="Payment_Mode", y="Total_Sales",
                 color="Total_Sales", color_continuous_scale="Purples",
                 text_auto=".2s")
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(**base_layout(), title="Revenue by Payment Mode",
                      coloraxis_showscale=False)
    fig.update_yaxes(title="Revenue (Rs.)")
    fig.update_xaxes(title="")
    return fig


def chart_season(df):
    fig = px.bar(df, x="Season", y="Total_Sales", color="Season",
                 text_auto=".2s")
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(**base_layout(), title="Revenue by Season",
                      showlegend=False)
    fig.update_yaxes(title="Revenue (Rs.)")
    fig.update_xaxes(title="")
    return fig


def chart_weekday(df):
    fig = px.bar(df, x="Day_Type", y="Total_Sales", color="Day_Type",
                 text_auto=".2s")
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(**base_layout(), title="Revenue: Weekday vs Weekend",
                      showlegend=False)
    fig.update_yaxes(title="Revenue (Rs.)")
    fig.update_xaxes(title="")
    return fig


# ============================================================
# KPI CARD
# ============================================================

def kpi_card(label, value, color=COLOR_PRIMARY):
    st.markdown(
        f"""
        <div style="
            background: white;
            border: 1px solid #e5e7eb;
            border-left: 4px solid {color};
            border-radius: 8px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.5rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        ">
            <div style="
                font-size: 0.75rem;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.3rem;
            ">{label}</div>
            <div style="
                font-size: 1.5rem;
                font-weight: 700;
                color: {color};
                line-height: 1.2;
            ">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    with st.sidebar:
        st.markdown(f"### 📊 {APP_NAME}")
        st.caption(f"Version {APP_VERSION}")
        st.markdown("---")

        st.markdown("#### 📁 Data Source")
        data_mode = st.radio(
            "Choose source",
            options=["Synthetic Data", "Upload CSV", "Existing Raw File"],
            index=0,
            key="data_mode",
        )

        uploaded_file = None
        use_synthetic = False

        if data_mode == "Upload CSV":
            uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        elif data_mode == "Synthetic Data":
            use_synthetic = True

        st.markdown("---")

        run_btn = st.button("🚀 Run Analytics Pipeline",
                            use_container_width=True, type="primary")

        st.markdown("---")

        st.markdown("#### 🧭 Navigation")
        section = st.radio(
            "Select section",
            options=[
                "Executive Overview",
                "Regional Performance",
                "Category Performance",
                "Product Portfolio",
                "Discount & Pricing",
                "Time-Series Trends",
                "Customer Analytics",
                "Payment Behaviour",
                "Profitability Split",
                "Data Explorer",
                "Data Quality",
                "Downloads",
            ],
            index=0,
            key="section",
        )

        st.markdown("---")
        st.caption("No external API used")

    return data_mode, uploaded_file, use_synthetic, run_btn, section


# ============================================================
# PAGE RENDERERS
# ============================================================

def render_overview(result):
    k = result.results["kpis"]
    st.subheader("Key Performance Indicators")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Total Revenue", format_currency(k["total_sales"], CURRENCY_SYMBOL))
    with c2:
        kpi_card("Total Profit", format_currency(k["total_profit"], CURRENCY_SYMBOL),
                 color=COLOR_SUCCESS)
    with c3:
        kpi_card("Profit Margin", format_percent(k["profit_margin_pct"]))
    with c4:
        kpi_card("Total Orders", f"{k['total_orders']:,}")

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        kpi_card("Avg Order Value", format_currency(k["avg_order_value"], CURRENCY_SYMBOL))
    with c6:
        kpi_card("Avg Discount", format_percent(k["avg_discount_pct"]),
                 color=COLOR_WARNING)
    with c7:
        kpi_card("Unique Customers", f"{k['unique_customers']:,}")
    with c8:
        kpi_card("Unique Products", f"{k['unique_products']:,}")

    st.markdown("---")
    st.subheader("Revenue Overview")

    c1, c2 = st.columns([2, 1])
    with c1:
        st.plotly_chart(chart_monthly_trend(result.results["monthly"]),
                        use_container_width=True)
    with c2:
        st.plotly_chart(chart_category_share(result.results["category"]),
                        use_container_width=True)

    st.markdown("---")
    st.subheader("Executive Summary")

    monthly = result.results["monthly"]
    best_month = monthly.loc[monthly["Total_Sales"].idxmax()]
    top_region = result.results["region"].iloc[0]
    top_category = result.results["category"].iloc[0]
    loss_df = result.results["loss_products"]

    st.info(
        f"**Peak revenue month:** {best_month['Year_Month']} "
        f"({format_currency(best_month['Total_Sales'], CURRENCY_SYMBOL)})  \n"
        f"**Leading region:** {top_region['Region']} "
        f"({format_currency(top_region['Total_Sales'], CURRENCY_SYMBOL)})  \n"
        f"**Top category:** {top_category['Category']} "
        f"({format_currency(top_category['Total_Sales'], CURRENCY_SYMBOL)})  \n"
        f"**Loss-making products:** {len(loss_df)}"
    )

    st.markdown("---")
    st.subheader("Pipeline Metadata")

    meta = pd.DataFrame([
        ("Executed At", result.timestamp.strftime("%Y-%m-%d %H:%M:%S")),
        ("Execution Time", f"{result.elapsed_seconds:.2f} s"),
        ("Raw Records", f"{len(result.raw_df):,}"),
        ("Clean Records", f"{len(result.clean_df):,}"),
        ("Columns", result.clean_df.shape[1]),
        ("Data Quality", "PASSED" if result.validation["valid"] else "REVIEW"),
    ], columns=["Metric", "Value"])
    st.dataframe(meta, use_container_width=True, hide_index=True)


def render_region(result):
    df = result.results["region"]
    st.subheader("Regional Summary")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Visualizations")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_region_sales(df), use_container_width=True)
    with c2:
        st.plotly_chart(chart_region_profit(df), use_container_width=True)


def render_category(result):
    df = result.results["category"]
    st.subheader("Category Summary")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Visualizations")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_category_share(df), use_container_width=True)
    with c2:
        st.plotly_chart(chart_category_margin(df), use_container_width=True)


def render_products(result):
    st.subheader("Product Portfolio")
    tab1, tab2, tab3 = st.tabs(["Top Performers", "Underperformers", "Loss-Making"])

    with tab1:
        top = result.results["top_products"]
        st.plotly_chart(chart_top_products(top, n=TOP_N), use_container_width=True)
        st.dataframe(top, use_container_width=True, hide_index=True)

    with tab2:
        bottom = result.results["bottom_products"]
        st.dataframe(bottom, use_container_width=True, hide_index=True)

    with tab3:
        loss = result.results["loss_products"]
        if len(loss) == 0:
            st.success("No loss-making products detected.")
        else:
            st.warning(f"{len(loss)} products are loss-making.")
            st.dataframe(loss, use_container_width=True, hide_index=True)


def render_discount(result):
    st.subheader("Discount Impact Analysis")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_discount_band(result.results["discount_band"]),
                        use_container_width=True)
    with c2:
        st.plotly_chart(chart_discount_impact(result.results["discount"]),
                        use_container_width=True)

    st.markdown("---")
    st.subheader("Discount Band Detail")
    st.dataframe(result.results["discount_band"],
                 use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("High-Discount Exposure")
    alert = result.results["high_discount"]
    if len(alert) == 0:
        st.info("No orders exceeded the high-discount threshold.")
    else:
        st.warning(f"{len(alert):,} orders exceeded the 30% discount threshold.")
        st.dataframe(alert.head(25), use_container_width=True, hide_index=True)


def render_time_trends(result):
    st.subheader("Time-Series Analysis")
    st.plotly_chart(chart_monthly_trend(result.results["monthly"]),
                    use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_season(result.results["season"]),
                        use_container_width=True)
    with c2:
        st.plotly_chart(chart_weekday(result.results["weekday"]),
                        use_container_width=True)

    st.markdown("---")
    st.subheader("Aggregated Time Buckets")
    st.markdown("**Quarterly**")
    st.dataframe(result.results["quarterly"],
                 use_container_width=True, hide_index=True)
    st.markdown("**Yearly**")
    st.dataframe(result.results["yearly"],
                 use_container_width=True, hide_index=True)


def render_customers(result):
    st.subheader("Customer Segment Performance")
    st.dataframe(result.results["segment"],
                 use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Top Customers")
    st.dataframe(result.results["customers"],
                 use_container_width=True, hide_index=True)


def render_payment(result):
    st.subheader("Payment Behaviour")
    st.plotly_chart(chart_payment(result.results["payment_mode"]),
                    use_container_width=True)
    st.dataframe(result.results["payment_mode"],
                 use_container_width=True, hide_index=True)


def render_profitability(result):
    st.subheader("Profitability Split")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_profit_status(result.results["profit_status"]),
                        use_container_width=True)
    with c2:
        st.dataframe(result.results["profit_status"],
                     use_container_width=True, hide_index=True)


def render_data_explorer(result):
    st.subheader("Data Explorer")
    tab1, tab2 = st.tabs(["Raw Data", "Cleaned Data"])

    with tab1:
        st.caption(f"Shape: {result.raw_df.shape}")
        st.dataframe(result.raw_df.head(200),
                     use_container_width=True, hide_index=True)

    with tab2:
        st.caption(f"Shape: {result.clean_df.shape}")
        st.dataframe(result.clean_df.head(200),
                     use_container_width=True, hide_index=True)


def render_data_quality(result):
    st.subheader("Data Quality Report")
    v = result.validation

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Total Rows", f"{v['total_rows']:,}")
    with c2:
        kpi_card("Total Columns", str(v["total_columns"]))
    with c3:
        kpi_card("Missing Values", str(v["missing_values"]),
                 color=COLOR_DANGER if v["missing_values"] > 0 else COLOR_SUCCESS)

    c4, c5, c6 = st.columns(3)
    with c4:
        kpi_card("Duplicate Rows", str(v["duplicates"]))
    with c5:
        kpi_card("Negative Sales", str(v["negative_sales"]))
    with c6:
        kpi_card("Negative Quantity", str(v["negative_quantity"]))

    st.markdown("---")
    if v["valid"]:
        st.success("Validation passed. Dataset is analysis-ready.")
    else:
        st.warning("Validation flagged issues:")
        for issue in v["issues"]:
            st.write(f"- {issue}")


def render_downloads(result):
    st.subheader("Download Artefacts")

    csv_clean = result.clean_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Cleaned Dataset (CSV)",
        data=csv_clean,
        file_name=f"retail_sales_clean_{result.timestamp:%Y%m%d_%H%M}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("---")
    st.subheader("Analytical Outputs")

    for name, value in result.results.items():
        if isinstance(value, pd.DataFrame):
            payload = value.to_csv(index=False).encode("utf-8")
            st.download_button(
                f"📥 Download {name}.csv",
                data=payload,
                file_name=f"app_{name}.csv",
                mime="text/csv",
                key=f"dl_{name}",
            )

    st.markdown("---")
    st.info(f"All artefacts saved to: `{OUTPUT_DIR}`")


# ============================================================
# MAIN
# ============================================================

def main():
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Header
    st.title(f"📊 {APP_NAME}")
    st.caption("Enterprise analytics console for retail sales intelligence.")

    data_mode, uploaded_file, use_synthetic, run_btn, section = render_sidebar()

    if "pipeline_result" not in st.session_state:
        st.session_state.pipeline_result = None

    if run_btn:
        if data_mode == "Upload CSV" and uploaded_file is None:
            st.error("Please upload a CSV file first.")
        else:
            progress = st.progress(0)
            status = st.empty()

            def update(pct, msg):
                progress.progress(pct)
                status.markdown(f"**{msg}** …")

            try:
                with st.spinner("Running pipeline…"):
                    result = execute_pipeline(
                        uploaded_file=uploaded_file,
                        force_synthetic=use_synthetic,
                        progress_callback=update,
                    )
                st.session_state.pipeline_result = result
                progress.empty()
                status.empty()
                st.success(f"✅ Pipeline completed in {result.elapsed_seconds:.2f}s")
            except Exception as exc:
                st.error(f"Pipeline failed: {type(exc).__name__}: {exc}")
                with st.expander("Show stack trace"):
                    st.code(traceback.format_exc())

    result = st.session_state.pipeline_result

    if result is None:
        st.markdown("---")
        st.info(
            "👈 **Select a data source in the sidebar and click "
            "'Run Analytics Pipeline' to begin.**\n\n"
            "Synthetic data is available for immediate demonstration."
        )
        return

    routers: dict[str, Callable] = {
        "Executive Overview": render_overview,
        "Regional Performance": render_region,
        "Category Performance": render_category,
        "Product Portfolio": render_products,
        "Discount & Pricing": render_discount,
        "Time-Series Trends": render_time_trends,
        "Customer Analytics": render_customers,
        "Payment Behaviour": render_payment,
        "Profitability Split": render_profitability,
        "Data Explorer": render_data_explorer,
        "Data Quality": render_data_quality,
        "Downloads": render_downloads,
    }

    renderer = routers.get(section)
    if renderer is None:
        st.error(f"Unknown section: {section}")
        return

    st.markdown("---")

    try:
        renderer(result)
    except Exception as exc:
        st.error(f"Failed to render '{section}': {exc}")
        with st.expander("Show stack trace"):
            st.code(traceback.format_exc())

    st.markdown("---")
    st.caption(
        f"{APP_NAME} · v{APP_VERSION} · "
        f"Last run: {result.timestamp:%Y-%m-%d %H:%M:%S} · "
        "No external API calls"
    )


if __name__ == "__main__":
    main()