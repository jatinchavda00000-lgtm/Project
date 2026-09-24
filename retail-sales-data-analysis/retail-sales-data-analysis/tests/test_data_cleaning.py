# ============================================
# Retail Sales Data Analysis
# File: tests/test_data_cleaning.py
# Purpose: Unit tests for src/data_cleaning.py
# Framework: pytest
# ============================================

"""
Unit tests for the data cleaning module.

Test coverage:
- standardize_columns()
- drop_duplicates_safe()
- handle_missing_values()
- convert_data_types()
- parse_dates()
- remove_negative_sales()
- detect_outliers_iqr()
- remove_outliers()
- validate_data()
- clean_pipeline()
- save_cleaned_data()

Run:
    pytest tests/test_data_cleaning.py -v
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
    clean_pipeline,
    save_cleaned_data,
)


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def raw_messy_df() -> pd.DataFrame:
    """
    A small messy DataFrame that mimics the raw input:
    - column names with spaces / mixed case
    - missing values
    - duplicate rows
    - invalid dates
    - negative sales and quantity
    """
    return pd.DataFrame({
        " order id ":   ["ORD001", "ORD002", "ORD002", "ORD004", "ORD005"],
        "Order-Date":   ["2024-01-15", "2024-02-20", "2024-02-20",
                         "invalid_date", "2024-03-10"],
        "Customer Name": ["Alice", "Bob", "Bob", "Carol", "David"],
        "Segment":      ["Consumer", "Corporate", "Corporate",
                         "Consumer", "Consumer"],
        "Region":       ["North", "South", "South", "East", None],
        "State":        ["Delhi", "KA", "KA", "WB", "MH"],
        "City":         ["New Delhi", "Bangalore", "Bangalore",
                         "Kolkata", "Mumbai"],
        "Product Name": ["Chair", "Table", "Table", None, "Lamp"],
        "Category":     ["Furniture", "Furniture", "Furniture",
                         "Lighting", None],
        "Quantity":     ["2", "1", "1", "3", "-1"],
        "Unit Price":   ["Rs.1500", "2500", "2500", "800", "500"],
        "Discount":     ["10%", "0.20", "0.20", "0", "5%"],
        "Sales":        ["3000", "2500", "2500", "2400", "-500"],
        "Profit":       ["600", "500", "500", "120", "-100"],
        "Payment Mode": ["UPI", "Card", "Card", "Cash", "UPI"],
    })


@pytest.fixture
def clean_df() -> pd.DataFrame:
    """A minimal well-formed DataFrame for validation tests."""
    return pd.DataFrame({
        "Order_ID":      ["ORD001", "ORD002", "ORD003"],
        "Order_Date":    pd.to_datetime(
            ["2024-01-15", "2024-02-20", "2024-03-10"]
        ),
        "Customer_Name": ["Alice", "Bob", "Carol"],
        "Region":        ["North", "South", "East"],
        "Category":      ["Furniture", "Furniture", "Lighting"],
        "Quantity":      [2, 1, 3],
        "Unit_Price":    [1500.0, 2500.0, 800.0],
        "Discount":      [10.0, 20.0, 0.0],
        "Sales":         [3000.0, 2500.0, 2400.0],
        "Profit":        [600.0, 500.0, 120.0],
        "Payment_Mode":  ["UPI", "Card", "Cash"],
    })


# ============================================
# 1. standardize_columns()
# ============================================

class TestStandardizeColumns:

    def test_removes_whitespace(self, raw_messy_df):
        out = standardize_columns(raw_messy_df)
        assert " order id " not in out.columns
        assert "Order_ID" in out.columns

    def test_replaces_dashes(self, raw_messy_df):
        out = standardize_columns(raw_messy_df)
        assert "Order_Date" in out.columns
        assert "Order-Date" not in out.columns

    def test_spaces_to_underscores(self, raw_messy_df):
        out = standardize_columns(raw_messy_df)
        assert "Customer_Name" in out.columns
        assert "Product_Name" in out.columns
        assert "Unit_Price" in out.columns
        assert "Payment_Mode" in out.columns

    def test_no_special_characters(self, raw_messy_df):
        out = standardize_columns(raw_messy_df)
        for col in out.columns:
            assert all(c.isalnum() or c == "_" for c in col), \
                f"Special char found in column: {col}"

    def test_returns_copy(self, raw_messy_df):
        original_cols = list(raw_messy_df.columns)
        _ = standardize_columns(raw_messy_df)
        assert list(raw_messy_df.columns) == original_cols, \
            "Original DataFrame was mutated."


# ============================================
# 2. drop_duplicates_safe()
# ============================================

class TestDropDuplicatesSafe:

    def test_removes_duplicates_by_order_ID(self, raw_messy_df):
        df = standardize_columns(raw_messy_df)
        out = drop_duplicates_safe(df)
        assert len(out) < len(df)
        assert out["Order_ID"].duplicated().sum() == 0

    def test_keeps_first_occurrence(self, raw_messy_df):
        df = standardize_columns(raw_messy_df)
        out = drop_duplicates_safe(df)
        # ORD002 appeared twice with same values, only one should remain
        assert (out["Order_ID"] == "ORD002").sum() == 1

    def test_no_duplicates_unchanged(self, clean_df):
        out = drop_duplicates_safe(clean_df)
        assert len(out) == len(clean_df)

    def test_subset_argument(self):
        df = pd.DataFrame({
            "A": [1, 1, 2, 2],
            "B": [10, 20, 30, 40],
        })
        out = drop_duplicates_safe(df, subset=["A"])
        assert len(out) == 2


# ============================================
# 3. handle_missing_values()
# ============================================

class TestHandleMissingValues:

    def test_no_missing_values_left(self, raw_messy_df):
        df = standardize_columns(raw_messy_df)
        df = drop_duplicates_safe(df)
        out = handle_missing_values(df)
        assert out.isnull().sum().sum() == 0

    def test_unknown_filled_in_object_columns(self, raw_messy_df):
        df = standardize_columns(raw_messy_df)
        df = drop_duplicates_safe(df)
        out = handle_missing_values(df)
        # After handling, no NaN in object columns
        object_cols = out.select_dtypes(include=["object"]).columns
        for col in object_cols:
            assert not out[col].isnull().any(), \
                f"NaN still present in object column: {col}"

    def test_numeric_filled(self, clean_df):
        df = clean_df.copy()
        df.loc[0, "Profit"] = np.nan
        out = handle_missing_values(df)
        assert not out["Profit"].isnull().any()

    def test_empty_dataframe(self):
        df = pd.DataFrame(columns=["A", "B", "C"])
        out = handle_missing_values(df)
        assert len(out) == 0


# ============================================
# 4. convert_data_types()
# ============================================

class TestConvertDataTypes:

    def test_quantity_becomes_int(self, raw_messy_df):
        df = standardize_columns(raw_messy_df)
        df = drop_duplicates_safe(df)
        df = handle_missing_values(df)
        out = convert_data_types(df)
        assert pd.api.types.is_integer_dtype(out["Quantity"])

    def test_sales_becomes_numeric(self, raw_messy_df):
        df = standardize_columns(raw_messy_df)
        df = drop_duplicates_safe(df)
        df = handle_missing_values(df)
        out = convert_data_types(df)
        assert pd.api.types.is_numeric_dtype(out["Sales"])

    def test_strips_rs_symbol(self):
        df = pd.DataFrame({
            "Sales": ["Rs.1000", "Rs.2500"],
            "Quantity": [1, 2],
        })
        out = convert_data_types(df)
        assert out["Sales"].iloc[0] == 1000.0
        assert out["Sales"].iloc[1] == 2500.0

    def test_strips_commas(self):
        df = pd.DataFrame({
            "Sales": ["Rs.1,200", "Rs.3,400"],
            "Quantity": [1, 2],
        })
        out = convert_data_types(df)
        assert out["Sales"].iloc[0] == 1200.0
        assert out["Sales"].iloc[1] == 3400.0

    def test_strips_percent_from_discount(self):
        df = pd.DataFrame({
            "Discount": ["10%", "20%"],
            "Quantity": [1, 1],
        })
        out = convert_data_types(df)
        assert out["Discount"].iloc[0] == 10.0
        assert out["Discount"].iloc[1] == 20.0

    def test_discount_0_to_1_converted_to_percent(self):
        df = pd.DataFrame({
            "Discount": [0.10, 0.20, 0.30],
            "Quantity": [1, 1, 1],
        })
        out = convert_data_types(df)
        assert out["Discount"].iloc[0] == 10.0
        assert out["Discount"].iloc[1] == 20.0
        assert out["Discount"].iloc[2] == 30.0

        

# ============================================
# 5. parse_dates()
# ============================================

class TestParseDates:

    def test_adds_date_features(self, clean_df):
        out = parse_dates(clean_df)
        for col in ["Year", "Month", "Month_Name", "Quarter", "Weekday"]:
            assert col in out.columns, f"Missing date feature: {col}"

    def test_parses_date_column(self, clean_df):
        out = parse_dates(clean_df)
        assert pd.api.types.is_datetime64_any_dtype(out["Order_Date"])

    def test_drops_invalid_dates(self, raw_messy_df):
        df = standardize_columns(raw_messy_df)
        df = drop_duplicates_safe(df)
        before = len(df)
        out = parse_dates(df)
        # One row had "invalid_date"
        assert len(out) < before

    def test_year_extracted_correctly(self, clean_df):
        out = parse_dates(clean_df)
        assert set(out["Year"].unique()) == {2024}

    def test_month_extracted_correctly(self, clean_df):
        out = parse_dates(clean_df)
        assert set(out["Month"].unique()) == {1, 2, 3}

    def test_quarter_extracted_correctly(self, clean_df):
        out = parse_dates(clean_df)
        assert set(out["Quarter"].unique()) == {1}


# ============================================
# 6. remove_negative_sales()
# ============================================

class TestRemoveNegativeSales:

    def test_removes_negative_sales(self):
        df = pd.DataFrame({
            "Sales": [100, 200, -50, 300],
            "Quantity": [1, 2, 3, 4],
        })
        out = remove_negative_sales(df)
        assert (out["Sales"] > 0).all()
        assert len(out) == 3

    def test_removes_zero_sales(self):
        df = pd.DataFrame({
            "Sales": [100, 0, 300],
            "Quantity": [1, 1, 1],
        })
        out = remove_negative_sales(df)
        assert (out["Sales"] > 0).all()
        assert len(out) == 2

    def test_removes_negative_quantity(self):
        df = pd.DataFrame({
            "Sales": [100, 200, 300],
            "Quantity": [1, -1, 3],
        })
        out = remove_negative_sales(df)
        assert (out["Quantity"] > 0).all()
        assert len(out) == 2

    def test_no_invalid_rows_unchanged(self, clean_df):
        out = remove_negative_sales(clean_df)
        assert len(out) == len(clean_df)


# ============================================
# 7. detect_outliers_iqr()
# ============================================

class TestDetectOutliersIQR:

    def test_detects_outliers(self):
        # Mostly 10, one extreme value 1000
        df = pd.DataFrame({"Sales": [10, 10, 10, 10, 10, 10, 10, 1000]})
        mask = detect_outliers_iqr(df, "Sales")
        assert mask.sum() == 1
        assert mask.iloc[-1] is True or mask.iloc[-1] == True

    def test_no_outliers_in_tight_data(self):
        df = pd.DataFrame({"Sales": [10, 11, 12, 13, 14, 15]})
        mask = detect_outliers_iqr(df, "Sales")
        assert mask.sum() == 0

    def test_raises_on_missing_column(self, clean_df):
        with pytest.raises(KeyError):
            detect_outliers_iqr(clean_df, "Nonexistent_Column")

    def test_returns_boolean_series(self):
        df = pd.DataFrame({"Sales": list(range(100)) + [10000]})
        mask = detect_outliers_iqr(df, "Sales")
        assert mask.dtype == bool


# ============================================
# 8. remove_outliers()
# ============================================

class TestRemoveOutliers:

    def test_removes_outlier_rows(self):
        df = pd.DataFrame({
            "Sales":  [10, 11, 12, 13, 14, 15, 16, 17, 1000],
            "Profit": [1, 1, 1, 1, 1, 1, 1, 1, 500],
        })
        out = remove_outliers(df, columns=["Sales"])
        assert len(out) < len(df)

    def test_no_outliers_unchanged(self):
        df = pd.DataFrame({
            "Sales":  [10, 11, 12, 13, 14],
            "Profit": [1, 1, 1, 1, 1],
        })
        out = remove_outliers(df, columns=["Sales"])
        assert len(out) == len(df)

    def test_default_columns(self):
        df = pd.DataFrame({
            "Sales":  [10, 11, 12, 13, 14, 15, 1000],
            "Profit": [1, 1, 1, 1, 1, 1, 500],
        })
        out = remove_outliers(df)
        # Should detect on both Sales and Profit (default)
        assert len(out) <= len(df)


# ============================================
# 9. validate_data()
# ============================================

class TestValidateData:

    def test_valid_data(self, clean_df):
        report = validate_data(clean_df)
        assert report["valid"] is True
        assert report["total_rows"] == len(clean_df)
        assert report["issues"] == []

    def test_detects_missing_values(self, clean_df):
        df = clean_df.copy()
        df.loc[0, "Region"] = None
        report = validate_data(df)
        assert report["valid"] is False
        assert report["missing_values"] > 0

    def test_detects_duplicates(self, clean_df):
        df = pd.concat([clean_df, clean_df.iloc[[0]]], ignore_index=True)
        report = validate_data(df)
        assert report["valid"] is False
        assert report["duplicates"] > 0

    def test_detects_negative_sales(self, clean_df):
        df = clean_df.copy()
        df.loc[0, "Sales"] = -100
        report = validate_data(df)
        assert report["valid"] is False
        assert report["negative_sales"] > 0

    def test_returns_required_keys(self, clean_df):
        report = validate_data(clean_df)
        for key in [
            "total_rows", "total_columns", "missing_values",
            "duplicates", "negative_sales", "negative_quantity",
            "valid", "issues",
        ]:
            assert key in report, f"Missing key in report: {key}"


# ============================================
# 10. clean_pipeline()
# ============================================

class TestCleanPipeline:

    def test_pipeline_returns_dataframe(self, raw_messy_df):
        out = clean_pipeline(raw_messy_df)
        assert isinstance(out, pd.DataFrame)
        assert len(out) > 0

    def test_pipeline_standardizes_columns(self, raw_messy_df):
        out = clean_pipeline(raw_messy_df)
        for col in out.columns:
            assert " " not in col
            assert "-" not in col

    def test_pipeline_removes_duplicates(self, raw_messy_df):
        out = clean_pipeline(raw_messy_df)
        if "Order_ID" in out.columns:
            assert out["Order_ID"].duplicated().sum() == 0

    def test_pipeline_no_missing_values(self, raw_messy_df):
        out = clean_pipeline(raw_messy_df)
        assert out.isnull().sum().sum() == 0

    def test_pipeline_adds_date_features(self, raw_messy_df):
        out = clean_pipeline(raw_messy_df)
        for col in ["Year", "Month", "Quarter", "Weekday"]:
            assert col in out.columns, f"Missing feature: {col}"

    def test_pipeline_no_negative_sales(self, raw_messy_df):
        out = clean_pipeline(raw_messy_df)
        assert (out["Sales"] > 0).all()

    def test_pipeline_no_negative_quantity(self, raw_messy_df):
        out = clean_pipeline(raw_messy_df)
        assert (out["Quantity"] > 0).all()

    def test_pipeline_with_outlier_removal(self):
        np.random.seed(42)
        df = pd.DataFrame({
            "Order_ID": [f"ORD{i}" for i in range(100)],
            "Order_Date": pd.date_range("2024-01-01", periods=100),
            "Sales": list(np.random.randint(100, 500, 99)) + [100000],
            "Profit": list(np.random.randint(10, 100, 99)) + [50000],
            "Quantity": [1] * 100,
            "Discount": [10] * 100,
        })
        out = clean_pipeline(df, remove_out=True)
        # The huge outlier row should be removed
        assert out["Sales"].max() < 100000


# ============================================
# 11. save_cleaned_data()
# ============================================

class TestSaveCleanedData:

    def test_save_creates_file(self, clean_df, tmp_path):
        out_path = tmp_path / "clean.csv"
        save_cleaned_data(clean_df, output_path=out_path)
        assert out_path.exists()

    def test_save_creates_parent_dirs(self, clean_df, tmp_path):
        out_path = tmp_path / "sub" / "nested" / "clean.csv"
        save_cleaned_data(clean_df, output_path=out_path)
        assert out_path.exists()

    def test_saved_file_readable(self, clean_df, tmp_path):
        out_path = tmp_path / "clean.csv"
        save_cleaned_data(clean_df, output_path=out_path)
        loaded = pd.read_csv(out_path)
        assert loaded.shape[0] == len(clean_df)
        assert loaded.shape[1] == clean_df.shape[1]


# ============================================
# 12. End-to-end sanity test
# ============================================

class TestEndToEnd:

    def test_full_flow(self, raw_messy_df, tmp_path):
        # Clean
        clean = clean_pipeline(raw_messy_df, remove_out=False)
        assert isinstance(clean, pd.DataFrame)
        assert len(clean) > 0

        # Validate
        report = validate_data(clean)
        assert report["valid"] is True

        # Save
        out_path = tmp_path / "e2e_clean.csv"
        save_cleaned_data(clean, output_path=out_path)
        assert out_path.exists()

        # Reload and verify
        reloaded = pd.read_csv(out_path)
        assert reloaded.shape[0] == len(clean)
        assert reloaded.shape[1] == clean.shape[1]


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    import pytest as _pytest
    sys.exit(_pytest.main([__file__, "-v", "--tb=short"]))