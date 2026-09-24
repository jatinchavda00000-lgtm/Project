# Retail Sales Data Analysis — Project Plan

**Project Name:** Retail Sales Data Analysis
**Type:** Data Analytics (No API)
**Data Source:** Static CSV / Excel / SQL dump
**Duration:** 4 weeks (adjustable)
**Status:** Planning

---

## 1. Project Overview

This project analyzes a retail sales dataset to uncover patterns in
revenue, profit, product performance, regional performance, discount
behavior, and seasonality. The final deliverables are a cleaned dataset,
a set of SQL analysis scripts, an interactive dashboard, a written report,
and a business recommendation summary.

The project does **not** use any API. All data is loaded from static files
(CSV / Excel) or a local SQL database.

---

## 2. Objectives

1. Clean and standardize a raw retail sales dataset.
2. Compute headline business KPIs (sales, profit, orders, margin).
3. Analyze performance across regions, categories, segments, and products.
4. Quantify the impact of discounts on profitability.
5. Identify seasonal and monthly trends.
6. Identify loss-making products and high-risk discount bands.
7. Build an interactive dashboard for exploration.
8. Deliver a written report with actionable recommendations.

---

## 3. Scope

### In Scope
- Static CSV / Excel / SQL-dump based analysis
- Data cleaning pipeline
- SQL-based analysis (SQLite / MySQL compatible)
- Python-based EDA and visualization
- Interactive dashboard (Power BI / Tableau)
- Final report and presentation

### Out of Scope
- API integration of any kind
- Real-time data streaming
- Web scraping
- Machine learning model deployment
- Mobile or web application development

---

## 4. Data Source

- **Primary:** Static CSV file (`data/raw/retail_sales_raw.csv`)
- **Backup:** Excel file or SQL dump if CSV not available
- **No API calls** are made at any stage.

### Expected Dataset Columns

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| Order_ID | String | Unique order identifier |
| Order_Date | Date | Order date |
| Customer_Name | String | Customer name |
| Segment | String | Consumer / Corporate / Home Office |
| Region | String | North / South / East / West |
| State | String | State name |
| City | String | City name |
| Product_Name | String | Product name |
| Category | String | Furniture / Technology / Office Supplies |
| Quantity | Integer | Number of items |
| Unit_Price | Float | Price per unit |
| Discount | Float | Discount percentage |
| Sales | Float | Total sales amount |
| Profit | Float | Profit amount |
| Payment_Mode | String | UPI / Card / Cash / Net Banking |

---

## 5. Tools & Technologies

| Layer | Tool |
|-------|------|
| Data Cleaning | Python (pandas, numpy) |
| Data Storage | SQLite / MySQL / PostgreSQL |
| SQL Analysis | SQL (window functions, CTEs) |
| EDA & Visualization | Matplotlib, Seaborn |
| Interactive Dashboard | Power BI / Tableau |
| Notebook | Jupyter / VS Code |
| Version Control | Git + GitHub |
| Testing | pytest |
| Documentation | Markdown |
| Report | PDF (from Word/Google Docs) |
| Presentation | PowerPoint / Google Slides |

---

## 6. Methodology (CRISP-DM)

1. **Business Understanding** — Define objectives, KPIs, success criteria.
2. **Data Understanding** — Inspect raw data, identify quality issues.
3. **Data Preparation** — Clean, standardize, engineer features.
4. **Modeling / Analysis** — SQL queries, EDA, dashboard.
5. **Evaluation** — Validate results, extract insights.
6. **Deployment** — Report, PPT, dashboard, GitHub repo.

---

## 7. Phase-wise Plan

### Phase 0 — Setup (Day 1)
- Create project folder structure
- Initialize Git repository
- Install dependencies (`pip install -r requirements.txt`)
- Create `config.py` with paths, column names, settings

### Phase 1 — Data Collection (Day 2)
- Download or arrange raw CSV / Excel / SQL dump
- Store in `data/raw/`
- Write `docs/data_dictionary.md`

### Phase 2 — Data Cleaning (Days 3–5)
- Standardize column names
- Drop duplicates by `Order_ID`
- Handle missing values (drop / fill 0 / fill Unknown / median)
- Convert data types (strip `Rs.`, `,`, `%`)
- Parse dates + extract Year / Month / Quarter / Weekday
- Remove negative sales and quantity rows
- Detect (but keep) outliers
- Save to `data/processed/retail_sales_clean.csv`

### Phase 3 — SQL Analysis (Days 6–9)
- Create tables (`sql/01_create_table.sql`)
- Import clean data (`sql/02_import_data.sql`)
- Basic queries: KPIs, counts, distributions
- Aggregation queries: region, category, product, discount
- Window-function queries: LAG, LEAD, RANK, NTILE, running totals
- Final insight queries: recommendations, executive summary

### Phase 4 — EDA & Visualization (Days 10–14)
- Compute summary statistics
- Analyze distributions and correlations
- Analyze region, category, segment, product
- Analyze time trends (monthly, quarterly, yearly)
- Analyze discount impact and bands
- Generate 18 plots saved to `images/`

### Phase 5 — Dashboard Development (Days 15–19)
- Build 4-page dashboard:
  1. Overview (KPIs + trend)
  2. Product performance
  3. Region performance
  4. Time analysis
- Add filters: Date, Region, Category, Segment, Payment Mode
- Export screenshots to `dashboard/dashboard_screenshots/`

### Phase 6 — Insights & Recommendations (Days 20–22)
- Consolidate findings into `reports/insights_summary.md`
- Generate recommendations with priority (High / Medium / Low)
- Build executive summary table

### Phase 7 — Documentation & Presentation (Days 23–26)
- Write final report (`reports/final_report.pdf`)
- Prepare PPT (`reports/presentation.pptx`)
- Write `README.md`
- Push everything to GitHub

### Phase 8 — Testing & Validation (Days 27–28)
- Run `pytest` on all test files
- Validate row counts, null checks, duplicate checks
- Cross-check SQL outputs with Python results

---

## 8. Week-wise Timeline

| Week | Focus | Deliverables |
|------|-------|--------------|
| Week 1 | Setup + Data Collection + Cleaning | Clean CSV, data dictionary |
| Week 2 | SQL Analysis + EDA | SQL files, notebook, 18 plots |
| Week 3 | Dashboard Development | Power BI / Tableau file + screenshots |
| Week 4 | Insights + Report + PPT + Testing | Final report, PPT, GitHub repo |

---

## 9. Folder Structure

```text
retail-sales-data-analysis/
│
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_sql_analysis.ipynb
│   ├── 04_eda.ipynb
│   └── 05_insights.ipynb
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   ├── analysis.py
│   ├── visualization.py
│   └── utils.py
├── sql/
│   ├── 01_create_table.sql
│   ├── 02_import_data.sql
│   ├── 03_basic_queries.sql
│   ├── 04_aggregation_queries.sql
│   ├── 05_window_functions.sql
│   └── 06_final_insights.sql
├── dashboard/
│   ├── retail_sales_dashboard.pbix
│   └── dashboard_screenshots/
├── reports/
│   ├── final_report.pdf
│   ├── presentation.pptx
│   └── insights_summary.md
├── images/
│   └── (18 PNG plots)
├── output/
│   └── (CSV exports, insights.json)
├── tests/
│   ├── test_data_cleaning.py
│   ├── test_analysis.py
│   └── test_utils.py
├── docs/
│   ├── project_plan.md
│   ├── methodology.md
│   ├── data_dictionary.md
│   └── conclusions.md
├── scripts/
│   └── make_notebook_*.py
├── requirements.txt
├── .gitignore
└── README.md