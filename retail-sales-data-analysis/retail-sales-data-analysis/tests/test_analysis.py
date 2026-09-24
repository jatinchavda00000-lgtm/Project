# ============================================
# Retail Sales Data Analysis
# File: tests/test_analysis.py
# Purpose: Unit tests for src/analysis.py
# Framework: pytest
# ============================================

"""
Unit tests for the analysis module.

Test coverage:
- overall_kpis()
- region_wise_analysis()
- category_wise_analysis()
- segment_wise_analysis()
- product_wise_analysis()
- top_products()
- bottom_products()
- monthly_sales_trend()
- quarterly_analysis()
- yearly_analysis()
- discount_impact()
- discount_band_analysis()
- profit_status_analysis()
- season_analysis()
- weekday_analysis()
- customer_analysis()
- payment_mode_analysis()
- loss_making_products()
- high_discount_alert()
- run_all_analysis()

Run:
    pytest tests/test_analysis.py -v
"""

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

warnings.filterwarnings("ignore")

# Make src/ importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

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
)


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def sample_df() -> pd.DataFrame:
    """
    A small well-formed DataFrame with all columns
    needed by the analysis module.
    """
    return pd.DataFrame({
        "Order_ID": ["ORD001", "ORD002", "ORD003", "ORD004", "ORD005",
                     "ORD006", "ORD007", "ORD008"],
        "Order_Date": pd.to_datetime([
            "2024-01-15", "2024-02-20", "2024-03-10", "2024-04-05",
            "2024-05-12", "2024-06-18", "2024-07-22", "2024-08-30",
        ]),
        "Customer_Name": ["Alice", "Bob", "Carol", "Bob", "David",
                          "Alice", "Eve", "Frank"],
        "Segment": ["Consumer", "Corporate", "Consumer", "Corporate",
                    "Home Office", "Consumer", "Corporate", "Home Office"],
        "Region": ["North", "South", "East", "West",
                   "North", "South", "East", "West"],
        "Category": ["Furniture", "Technology", "Office Supplies", "Furniture",
                     "Technology", "Office Supplies", "Furniture", "Technology"],
        "Product_Name": ["Chair", "Laptop", "Pen", "Table",
                         "Phone", "Notebook", "Sofa", "Monitor"],
        "Payment_Mode": ["UPI", "Card", "Cash", "UPI",
                         "Card", "Cash", "UPI", "Card"],
        "Quantity": [2, 1, 10, 3, 1, 5, 2, 1],
        "Unit_Price": [1500.0, 50000.0, 20.0, 8000.0,
                       30000.0, 50.0, 25000.0, 15000.0],
        "Discount": [10.0, 20.0, 0.0, 15.0,
                     25.0, 5.0, 35.0, 10.0],
        "Sales": [3000.0, 50000.0, 200.0, 24000.0,
                  30000.0, 250.0, 50000.0, 15000.0],
        "Profit": [600.0, 5000.0, 60.0, 2400.0,
                   1500.0, 100.0, -2500.0, 1500.0],
        "Year": [2024] * 8,
        "Month": [1, 2, 3, 4, 5, 6, 7, 8],
        "Month_Name": ["Jan", "Feb", "Mar", "Apr",
                       "May", "Jun", "Jul", "Aug"],
        "Quarter": [1, 1, 1, 2, 2, 2, 3, 3],
        "Quarter_Label": ["Q1", "Q1", "Q1", "Q2",
                          "Q2", "Q2", "Q3", "Q3"],
        "Year_Month": ["2024-01", "2024-02", "2024-03", "2024-04",
                       "2024-05", "2024-06", "2024-07", "2024-08"],
        "Weekday": ["Monday", "Tuesday", "Sunday", "Friday",
                    "Sunday", "Tuesday", "Monday", "Friday"],
        "Profit_Margin": [20.0, 10.0, 30.0, 10.0,
                          5.0, 40.0, -5.0, 10.0],
        "Discount_Band": ["Low", "Medium", "No Discount", "Medium",
                          "High", "Low", "Very High", "Low"],
        "Profit_Status": ["Profit", "Profit", "Profit", "Profit",
                          "Profit", "Profit", "Loss", "Profit"],
        "Season": ["Winter", "Winter", "Summer", "Summer",
                   "Summer", "Monsoon", "Monsoon", "Monsoon"],
        "Is_Weekend": [False, False, True, False,
                       True, False, False, False],
    })


@pytest.fixture
def empty_df() -> pd.DataFrame:
    """Empty DataFrame with the required columns."""
    return pd.DataFrame(columns=[
        "Order_ID", "Sales", "Profit", "Quantity",
        "Discount", "Region", "Category", "Segment",
        "Product_Name", "Customer_Name", "Payment_Mode",
        "Year_Month", "Year", "Quarter_Label",
        "Profit_Status", "Discount_Band", "Season", "Is_Weekend",
    ])


# ============================================
# 1. overall_kpis()
# ============================================

class TestOverallKPIs:

    def test_returns_dict(self, sample_df):
        result = overall_kpis(sample_df)
        assert isinstance(result, dict)

    def test_contains_required_keys(self, sample_df):
        result = overall_kpis(sample_df)
        required = [
            "total_sales", "total_profit", "total_orders",
            "total_quantity", "avg_order_value", "profit_margin_pct",
            "avg_discount_pct", "unique_customers", "unique_products",
        ]
        for key in required:
            assert key in result, f"Missing key: {key}"

    def test_total_sales_correct(self, sample_df):
        result = overall_kpis(sample_df)
        expected = float(sample_df["Sales"].sum())
        assert result["total_sales"] == pytest.approx(expected, rel=1e-6)

    def test_total_profit_correct(self, sample_df):
        result = overall_kpis(sample_df)
        expected = float(sample_df["Profit"].sum())
        assert result["total_profit"] == pytest.approx(expected, rel=1e-6)

    def test_total_orders_correct(self, sample_df):
        result = overall_kpis(sample_df)
        assert result["total_orders"] == 8

    def test_profit_margin_correct(self, sample_df):
        result = overall_kpis(sample_df)
        expected = (sample_df["Profit"].sum() / sample_df["Sales"].sum()) * 100
        assert result["profit_margin_pct"] == pytest.approx(expected, rel=1e-4)

    def test_avg_order_value(self, sample_df):
        result = overall_kpis(sample_df)
        expected = sample_df["Sales"].sum() / 8
        assert result["avg_order_value"] == pytest.approx(expected, rel=1e-4)

    def test_unique_customers(self, sample_df):
        result = overall_kpis(sample_df)
        # Alice, Bob, Carol, David, Eve, Frank = 6
        assert result["unique_customers"] == 6


# ============================================
# 2. region_wise_analysis()
# ============================================

class TestRegionWiseAnalysis:

    def test_returns_dataframe(self, sample_df):
        result = region_wise_analysis(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_required_columns(self, sample_df):
        result = region_wise_analysis(sample_df)
        for col in ["Region", "Total_Sales", "Total_Profit", "Total_Orders"]:
            assert col in result.columns

    def test_row_count(self, sample_df):
        result = region_wise_analysis(sample_df)
        assert len(result) == 4  # North, South, East, West

    def test_sorted_by_sales_desc(self, sample_df):
        result = region_wise_analysis(sample_df)
        assert result["Total_Sales"].is_monotonic_decreasing

    def test_profit_margin_column(self, sample_df):
        result = region_wise_analysis(sample_df)
        assert "Profit_Margin_%" in result.columns

    def test_sales_sum_matches_total(self, sample_df):
        result = region_wise_analysis(sample_df)
        assert result["Total_Sales"].sum() == pytest.approx(
            sample_df["Sales"].sum(), rel=1e-6
        )


# ============================================
# 3. category_wise_analysis()
# ============================================

class TestCategoryWiseAnalysis:

    def test_returns_dataframe(self, sample_df):
        result = category_wise_analysis(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_row_count(self, sample_df):
        result = category_wise_analysis(sample_df)
        assert len(result) == 3  # Furniture, Technology, Office Supplies

    def test_sorted_by_sales(self, sample_df):
        result = category_wise_analysis(sample_df)
        assert result["Total_Sales"].is_monotonic_decreasing

    def test_sales_sum_matches(self, sample_df):
        result = category_wise_analysis(sample_df)
        assert result["Total_Sales"].sum() == pytest.approx(
            sample_df["Sales"].sum(), rel=1e-6
        )


# ============================================
# 4. segment_wise_analysis()
# ============================================

class TestSegmentWiseAnalysis:

    def test_returns_dataframe(self, sample_df):
        result = segment_wise_analysis(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_row_count(self, sample_df):
        result = segment_wise_analysis(sample_df)
        assert len(result) == 3  # Consumer, Corporate, Home Office

    def test_has_sales_column(self, sample_df):
        result = segment_wise_analysis(sample_df)
        assert "Total_Sales" in result.columns
        assert "Total_Profit" in result.columns


# ============================================
# 5. product_wise_analysis()
# ============================================

class TestProductWiseAnalysis:

    def test_returns_dataframe(self, sample_df):
        result = product_wise_analysis(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_row_count(self, sample_df):
        result = product_wise_analysis(sample_df)
        assert len(result) == 8  # 8 unique products

    def test_required_columns(self, sample_df):
        result = product_wise_analysis(sample_df)
        for col in ["Product_Name", "Total_Sales", "Total_Profit"]:
            assert col in result.columns


# ============================================
# 6. top_products()
# ============================================

class TestTopProducts:

    def test_returns_dataframe(self, sample_df):
        result = top_products(sample_df, n=3)
        assert isinstance(result, pd.DataFrame)

    def test_respects_n_limit(self, sample_df):
        result = top_products(sample_df, n=3)
        assert len(result) <= 3

    def test_sorted_by_sales_desc(self, sample_df):
        result = top_products(sample_df, n=5)
        assert result["Total_Sales"].is_monotonic_decreasing

    def test_top_product_highest_sales(self, sample_df):
        result = top_products(sample_df, n=1)
        max_sales = sample_df.groupby("Product_Name")["Sales"].sum().max()
        assert result["Total_Sales"].iloc[0] == pytest.approx(max_sales, rel=1e-6)

    def test_n_greater_than_products(self, sample_df):
        result = top_products(sample_df, n=100)
        assert len(result) == 8


# ============================================
# 7. bottom_products()
# ============================================

class TestBottomProducts:

    def test_returns_dataframe(self, sample_df):
        result = bottom_products(sample_df, n=3)
        assert isinstance(result, pd.DataFrame)

    def test_sorted_by_profit_asc(self, sample_df):
        result = bottom_products(sample_df, n=5)
        assert result["Total_Profit"].is_monotonic_increasing

    def test_bottom_includes_loss(self, sample_df):
        result = bottom_products(sample_df, n=1)
        # Sofa has -2500 profit
        assert result["Total_Profit"].iloc[0] < 0


# ============================================
# 8. monthly_sales_trend()
# ============================================

class TestMonthlySalesTrend:

    def test_returns_dataframe(self, sample_df):
        result = monthly_sales_trend(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_required_columns(self, sample_df):
        result = monthly_sales_trend(sample_df)
        for col in ["Year_Month", "Total_Sales", "Total_Profit"]:
            assert col in result.columns

    def test_row_count(self, sample_df):
        result = monthly_sales_trend(sample_df)
        assert len(result) == 8  # 8 months

    def test_sorted_chronologically(self, sample_df):
        result = monthly_sales_trend(sample_df)
        assert result["Year_Month"].is_monotonic_increasing

    def test_sales_sum_matches(self, sample_df):
        result = monthly_sales_trend(sample_df)
        assert result["Total_Sales"].sum() == pytest.approx(
            sample_df["Sales"].sum(), rel=1e-6
        )


# ============================================
# 9. quarterly_analysis()
# ============================================

class TestQuarterlyAnalysis:

    def test_returns_dataframe(self, sample_df):
        result = quarterly_analysis(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_required_columns(self, sample_df):
        result = quarterly_analysis(sample_df)
        for col in ["Year", "Quarter_Label", "Total_Sales"]:
            assert col in result.columns

    def test_row_count(self, sample_df):
        result = quarterly_analysis(sample_df)
        # 3 quarters (Q1, Q2, Q3) in year 2024
        assert len(result) == 3


# ============================================
# 10. yearly_analysis()
# ============================================

class TestYearlyAnalysis:

    def test_returns_dataframe(self, sample_df):
        result = yearly_analysis(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_single_year(self, sample_df):
        result = yearly_analysis(sample_df)
        assert len(result) == 1
        assert result["Year"].iloc[0] == 2024

    def test_sales_sum_matches(self, sample_df):
        result = yearly_analysis(sample_df)
        assert result["Total_Sales"].iloc[0] == pytest.approx(
            sample_df["Sales"].sum(), rel=1e-6
        )


# ============================================
# 11. discount_impact()
# ============================================

class TestDiscountImpact:

    def test_returns_dataframe(self, sample_df):
        result = discount_impact(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_required_columns(self, sample_df):
        result = discount_impact(sample_df)
        for col in ["Discount", "Total_Sales", "Total_Profit", "Orders"]:
            assert col in result.columns

    def test_sorted_by_discount(self, sample_df):
        result = discount_impact(sample_df)
        assert result["Discount"].is_monotonic_increasing


# ============================================
# 12. discount_band_analysis()
# ============================================

class TestDiscountBandAnalysis:

    def test_returns_dataframe(self, sample_df):
        result = discount_band_analysis(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_required_columns(self, sample_df):
        result = discount_band_analysis(sample_df)
        for col in ["Discount_Band", "Total_Sales", "Total_Profit"]:
            assert col in result.columns

    def test_band_order(self, sample_df):
        result = discount_band_analysis(sample_df)
        # Bands should follow the defined order
        valid_order = ["No Discount", "Low", "Medium", "High", "Very High"]
        bands = result["Discount_Band"].tolist()
        indices = [valid_order.index(b) for b in bands if b in valid_order]
        assert indices == sorted(indices)


# ============================================
# 13. profit_status_analysis()
# ============================================

class TestProfitStatusAnalysis:

    def test_returns_dataframe(self, sample_df):
        result = profit_status_analysis(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_required_columns(self, sample_df):
        result = profit_status_analysis(sample_df)
        for col in ["Profit_Status", "Orders", "Total_Sales", "Total_Profit"]:
            assert col in result.columns

    def test_has_pct_column(self, sample_df):
        result = profit_status_analysis(sample_df)
        assert "Orders_%" in result.columns

    def test_pct_sum_approx_100(self, sample_df):
        result = profit_status_analysis(sample_df)
        assert result["Orders_%"].sum() == pytest.approx(100.0, abs=0.5)


# ============================================
# 14. season_analysis()
# ============================================

class TestSeasonAnalysis:

    def test_returns_dataframe(self, sample_df):
        result = season_analysis(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_required_columns(self, sample_df):
        result = season_analysis(sample_df)
        for col in ["Season", "Total_Sales", "Total_Profit"]:
            assert col in result.columns

    def test_sorted_by_sales(self, sample_df):
        result = season_analysis(sample_df)
        assert result["Total_Sales"].is_monotonic_decreasing


# ============================================
# 15. weekday_analysis()
# ============================================

class TestWeekdayAnalysis:

    def test_returns_dataframe(self, sample_df):
        result = weekday_analysis(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_has_day_type(self, sample_df):
        result = weekday_analysis(sample_df)
        assert "Day_Type" in result.columns

    def test_day_types_valid(self, sample_df):
        result = weekday_analysis(sample_df)
        for day_type in result["Day_Type"]:
            assert day_type in ["Weekday", "Weekend"]

    def test_max_two_rows(self, sample_df):
        result = weekday_analysis(sample_df)
        assert len(result) <= 2


# ============================================
# 16. customer_analysis()
# ============================================

class TestCustomerAnalysis:

    def test_returns_dataframe(self, sample_df):
        result = customer_analysis(sample_df, n=3)
        assert isinstance(result, pd.DataFrame)

    def test_respects_n(self, sample_df):
        result = customer_analysis(sample_df, n=3)
        assert len(result) <= 3

    def test_sorted_by_sales_desc(self, sample_df):
        result = customer_analysis(sample_df, n=5)
        assert result["Total_Sales"].is_monotonic_decreasing

    def test_required_columns(self, sample_df):
        result = customer_analysis(sample_df, n=3)
        for col in ["Customer_Name", "Total_Sales", "Total_Profit"]:
            assert col in result.columns


# ============================================
# 17. payment_mode_analysis()
# ============================================

class TestPaymentModeAnalysis:

    def test_returns_dataframe(self, sample_df):
        result = payment_mode_analysis(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_row_count(self, sample_df):
        result = payment_mode_analysis(sample_df)
        assert len(result) == 3  # UPI, Card, Cash

    def test_sorted_by_sales(self, sample_df):
        result = payment_mode_analysis(sample_df)
        assert result["Total_Sales"].is_monotonic_decreasing


# ============================================
# 18. loss_making_products()
# ============================================

class TestLossMakingProducts:

    def test_returns_dataframe(self, sample_df):
        result = loss_making_products(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_only_loss_products(self, sample_df):
        result = loss_making_products(sample_df)
        if len(result) > 0:
            assert (result["Total_Profit"] < 0).all()

    def test_sorted_by_profit_asc(self, sample_df):
        result = loss_making_products(sample_df)
        if len(result) > 1:
            assert result["Total_Profit"].is_monotonic_increasing

    def test_no_loss_products_returns_empty(self):
        df = pd.DataFrame({
            "Order_ID": ["A", "B"],
            "Product_Name": ["P1", "P2"],
            "Sales": [100, 200],
            "Profit": [10, 20],
            "Quantity": [1, 1],
            "Discount": [0, 0],
        })
        result = loss_making_products(df)
        assert len(result) == 0


# ============================================
# 19. high_discount_alert()
# ============================================

class TestHighDiscountAlert:

    def test_returns_dataframe(self, sample_df):
        result = high_discount_alert(sample_df, threshold=20.0)
        assert isinstance(result, pd.DataFrame)

    def test_only_above_threshold(self, sample_df):
        result = high_discount_alert(sample_df, threshold=20.0)
        if len(result) > 0:
            assert (result["Discount"] > 20.0).all()

    def test_default_threshold_30(self, sample_df):
        result = high_discount_alert(sample_df)
        if len(result) > 0:
            assert (result["Discount"] > 30.0).all()

    def test_sorted_by_discount_desc(self, sample_df):
        result = high_discount_alert(sample_df, threshold=5.0)
        if len(result) > 1:
            assert result["Discount"].is_monotonic_decreasing

    def test_no_alerts_when_threshold_high(self, sample_df):
        result = high_discount_alert(sample_df, threshold=99.0)
        assert len(result) == 0


# ============================================
# 20. run_all_analysis()
# ============================================

class TestRunAllAnalysis:

    def test_returns_dict(self, sample_df):
        result = run_all_analysis(sample_df)
        assert isinstance(result, dict)

    def test_contains_all_sections(self, sample_df):
        result = run_all_analysis(sample_df)
        expected_keys = [
            "kpis", "region", "category", "segment", "product",
            "top_products", "bottom_products", "monthly_trend",
            "quarterly", "yearly", "discount_impact", "discount_band",
            "profit_status", "season", "weekday", "customers",
            "payment_mode", "loss_products",
        ]
        for key in expected_keys:
            assert key in result, f"Missing section: {key}"

    def test_kpis_is_dict(self, sample_df):
        result = run_all_analysis(sample_df)
        assert isinstance(result["kpis"], dict)

    def test_dataframes_have_rows(self, sample_df):
        result = run_all_analysis(sample_df)
        for key, value in result.items():
            if isinstance(value, pd.DataFrame):
                assert len(value) > 0, f"Empty DataFrame for: {key}"


# ============================================
# 21. Edge cases
# ============================================

class TestEdgeCases:

    def test_single_row(self):
        df = pd.DataFrame({
            "Order_ID": ["ORD001"],
            "Sales": [1000.0],
            "Profit": [200.0],
            "Quantity": [1],
            "Discount": [0.0],
            "Region": ["North"],
            "Category": ["Furniture"],
            "Segment": ["Consumer"],
            "Product_Name": ["Chair"],
            "Customer_Name": ["Alice"],
            "Payment_Mode": ["UPI"],
            "Year_Month": ["2024-01"],
            "Year": [2024],
            "Quarter_Label": ["Q1"],
            "Profit_Status": ["Profit"],
            "Discount_Band": ["No Discount"],
            "Season": ["Winter"],
            "Is_Weekend": [False],
        })
        kpis = overall_kpis(df)
        assert kpis["total_orders"] == 1
        assert kpis["total_sales"] == 1000.0
        assert kpis["profit_margin_pct"] == pytest.approx(20.0, rel=1e-4)

    def test_zero_sales_safe_division(self):
        df = pd.DataFrame({
            "Order_ID": ["A"],
            "Sales": [0.0],
            "Profit": [0.0],
            "Quantity": [1],
            "Discount": [0.0],
            "Region": ["North"],
            "Category": ["Furniture"],
            "Segment": ["Consumer"],
            "Product_Name": ["Chair"],
            "Customer_Name": ["Alice"],
            "Payment_Mode": ["UPI"],
        })
        kpis = overall_kpis(df)
        # Should not raise; margin defaults to 0
        assert kpis["profit_margin_pct"] == 0.0

    def test_discount_band_all_bands(self, sample_df):
        result = discount_band_analysis(sample_df)
        bands = set(result["Discount_Band"].tolist())
        # Sample has: No Discount, Low, Medium, High, Very High
        assert "No Discount" in bands
        assert "Low" in bands
        assert "Very High" in bands


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    import pytest as _pytest
    sys.exit(_pytest.main([__file__, "-v", "--tb=short"]))