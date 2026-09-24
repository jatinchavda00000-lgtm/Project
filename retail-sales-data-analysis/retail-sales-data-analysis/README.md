# Retail Sales Data Analysis

A complete data analytics project that analyzes retail sales data
using Python, SQL, and visualization — **without using any API**.

The project covers the full workflow: data loading, cleaning, feature
engineering, SQL analysis, exploratory data analysis, visualization,
insights, and recommendations.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Notebooks](#notebooks)
- [SQL Scripts](#sql-scripts)
- [Testing](#testing)
- [Outputs](#outputs)
- [Data Source](#data-source)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Notes](#notes)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

This project analyzes a retail sales dataset to answer questions like:

- What is the total revenue, profit, and margin?
- Which region, category, and product perform best?
- How does discount affect profit?
- Which products and customers are loss-making?
- What are the monthly, quarterly, and seasonal trends?
- What recommendations can improve profitability?

**Key point:** No API is used at any stage. Data is loaded from static
CSV files (or a local SQL database).

---

## Features

- **Cleaning pipeline** — standardizes columns, removes duplicates,
  handles missing values, fixes data types, parses dates, removes
  invalid rows.
- **Feature engineering** — creates 12 derived columns like
  `Profit_Margin`, `Discount_Band`, `Season`, `Customer_Type`.
- **SQL analysis** — 6 SQL files covering basics, aggregations,
  window functions, and final insights (SQLite / MySQL compatible).
- **EDA** — 18 plots saved to `images/`, including distributions,
  correlations, trends, and category/region breakdowns.
- **Insights engine** — auto-generated findings and rule-based
  recommendations with priority (High / Medium / Low).
- **Unit tests** — 200+ tests across cleaning, analysis, and utils.
- **Reproducible** — end-to-end flow from raw CSV to final report.

---

## Project Structure

```text
retail-sales-data-analysis/
│
├── data/
│   ├── raw/                          # Source data
│   └── processed/                    # Cleaned data
│
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_sql_analysis.ipynb
│   ├── 04_eda.ipynb
│   └── 05_insights.ipynb
│
├── src/
│   ├── __init__.py
│   ├── config.py                     # Paths, constants, settings
│   ├── data_loader.py                # CSV / Excel / SQL loaders
│   ├── data_cleaning.py              # Cleaning pipeline
│   ├── feature_engineering.py        # Derived features
│   ├── analysis.py                   # Business analysis
│   ├── visualization.py              # 18 plots
│   └── utils.py                      # Helpers
│
├── sql/
│   ├── 01_create_table.sql
│   ├── 02_import_data.sql
│   ├── 03_basic_queries.sql
│   ├── 04_aggregation_queries.sql
│   ├── 05_window_functions.sql
│   └── 06_final_insights.sql
│
├── dashboard/                        # Power BI / Tableau + screenshots
├── reports/                          # Final report, PPT, insights
├── images/                           # 18 PNG plots
├── output/                           # CSV / JSON exports
├── tests/                            # Unit tests (pytest)
├── docs/                             # Documentation
├── scripts/                          # Notebook generators
│
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md