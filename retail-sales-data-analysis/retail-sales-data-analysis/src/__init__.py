# ============================================
# Retail Sales Data Analysis
# File: src/__init__.py
# Purpose: Package initialization for the src module
# ============================================

"""
Retail Sales Data Analysis — Source Package

This package contains all core modules for the project:

- config              : Central configuration (paths, constants, settings)
- data_loader         : Load data from CSV, Excel, or SQL
- data_cleaning       : Cleaning pipeline (missing, duplicates, types, dates)
- feature_engineering : Derived features (Profit_Margin, Discount_Band, etc.)
- analysis            : Business analysis (KPIs, region, category, products)
- visualization       : 18 plots for EDA and reporting
- utils               : Common helper functions

Usage:
    from src.config import RAW_DATA_FILE
    from src.data_loader import load_csv
    from src.data_cleaning import clean_pipeline
    from src.analysis import overall_kpis

    df = load_csv(RAW_DATA_FILE)
    df = clean_pipeline(df)
    kpis = overall_kpis(df)

Note:
    No API is used anywhere in this project.
    All data comes from static CSV / Excel / SQL dump files.
"""

# ============================================
# PACKAGE METADATA
# ============================================

__version__ = "1.0.0"
__author__ = "Retail Sales Data Analysis"
__license__ = "MIT"
__api_used__ = False


# ============================================
# PUBLIC EXPORTS
# ============================================

__all__ = [
    "config",
    "data_loader",
    "data_cleaning",
    "feature_engineering",
    "analysis",
    "visualization",
    "utils",
]