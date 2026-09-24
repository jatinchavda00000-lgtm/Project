# Methodology — Retail Sales Data Analysis

**Project:** Retail Sales Data Analysis
**Framework:** CRISP-DM (Cross-Industry Standard Process for Data Mining)
**Data Source:** Static CSV / Excel / SQL dump
**API Usage:** None

---

## Overview

This project follows the CRISP-DM framework, the industry-standard
methodology for data mining and analytics projects. CRISP-DM has six
phases, each with defined inputs, activities, and outputs.

The six phases:

1. Business Understanding
2. Data Understanding
3. Data Preparation
4. Modeling / Analysis
5. Evaluation
6. Deployment

While the phases are presented sequentially, CRISP-DM is iterative — a
finding in a later phase can send the project back to an earlier phase.

---

## Phase 1 — Business Understanding

### Objective
Translate the business problem into an analytics problem with clear
objectives and success criteria.

### Business Problem
A retail store has transactional sales data but no structured way to
understand:
- Which products and categories drive revenue vs. loss
- Which regions are underperforming on profit
- How discount policy affects profitability
- Which months / seasons have the strongest sales
- Which customers are most valuable

### Analytics Objectives
1. Clean and standardize the raw dataset.
2. Compute headline KPIs.
3. Analyze performance by region, category, segment, and product.
4. Quantify the impact of discount on profit.
5. Identify seasonal and monthly patterns.
6. Identify loss-making products and risk bands.
7. Deliver insights with recommendations.

### Success Criteria
- Clean dataset with no missing values or duplicates.
- 10+ actionable insights.
- Interactive dashboard.
- Written report with prioritized recommendations.
- No API used.

### Key Questions
- What is the total revenue and profit?
- Which region and category perform best?
- What discount level starts eroding profit?
- Which products lose money?
- When (month / season) do sales peak?
- Which customers are most valuable?

### Stakeholders
- Business owner / manager
- Sales team
- Marketing team
- Finance team

---

## Phase 2 — Data Understanding

### Objective
Understand the structure, quality, and limitations of the raw dataset.

### Inputs
- Raw dataset: `data/raw/retail_sales_raw.csv`

### Activities

**2.1 Load and inspect**
- Load the CSV with pandas.
- Print shape, column names, dtypes, memory usage.

**2.2 Check data quality**
- Missing values (count and percentage per column).
- Duplicate rows (full-row and by Order_ID).
- Invalid dates.
- Non-numeric values in numeric columns.

**2.3 Describe the data**
- Summary statistics for numeric columns (min, max, mean, median, std).
- Value counts for categorical columns (region, category, segment, payment mode).
- Date range (earliest and latest order).

**2.4 Identify issues**
- Column names with spaces or mixed case.
- Currency symbols (`Rs.`) and separators (`,`) in numeric strings.
- Percent signs (`%`) in discount strings.
- Negative sales / quantity rows.
- Outliers in sales and profit.

### Outputs
- Notebook: `notebooks/01_data_understanding.ipynb`
- Data quality summary
- Cleaning checklist

### Tools
- pandas, numpy, Jupyter Notebook

---

## Phase 3 — Data Preparation

### Objective
Produce a clean, consistent, analysis-ready dataset.

### Inputs
- Raw CSV from Phase 2

### Activities

**3.1 Standardize column names**
- Remove leading/trailing spaces.
- Replace spaces and dashes with underscores.
- Strip special characters.
- Convert to Title_Case.

**3.2 Remove duplicates**
- Drop rows with duplicate `Order_ID` (business key).
- Keep the first occurrence.

**3.3 Handle missing values**
- Critical columns (`Order_ID`, `Order_Date`, `Sales`): drop rows.
- Numeric columns (`Profit`, `Discount`, `Quantity`): fill with 0.
- Categorical columns (`Region`, `Category`, `Segment`, `Payment_Mode`): fill with "Unknown".
- Remaining numeric: fill with median.
- Remaining text: fill with "Unknown".

**3.4 Convert data types**
- Strip `Rs.`, `$`, `,`, `%` from numeric-like strings.
- Cast to numeric with `pd.to_numeric(errors="coerce")`.
- Convert discount in 0–1 range to percentage.
- Cast quantity to integer.

**3.5 Parse dates and extract features**
- Convert `Order_Date` to datetime.
- Extract `Year`, `Month`, `Month_Name`, `Quarter`, `Weekday`.
- Drop rows with invalid dates.

**3.6 Remove invalid rows**
- Drop rows where `Sales <= 0`.
- Drop rows where `Quantity <= 0`.

**3.7 Detect outliers (do not remove)**
- Use IQR method on `Sales` and `Profit`.
- Report outlier counts but keep them, because extreme values represent real business events (bulk orders, big deals).

**3.8 Feature engineering**
- `Profit_Margin` = Profit / Sales × 100
- `Revenue_Per_Unit` = Sales / Quantity
- `Profit_Per_Unit` = Profit / Quantity
- `Discount_Amount` = Sales × Discount / 100
- `Discount_Band` = No Discount / Low / Medium / High / Very High
- `Profit_Status` = Profit / Loss / Break-even
- `Order_Size` = Small / Medium / Large / Bulk
- `Is_Weekend` = True / False
- `Season` = Winter / Summer / Monsoon / Post-Monsoon
- `Quarter_Label` = Q1 / Q2 / Q3 / Q4
- `Year_Month` = "YYYY-MM"
- `Customer_Type` = New / Repeat

**3.9 Validate**
- Confirm no missing values.
- Confirm no duplicates.
- Confirm no negative sales or quantity.
- Confirm date range.

### Outputs
- Clean CSV: `data/processed/retail_sales_clean.csv`
- Notebook: `notebooks/02_data_cleaning.ipynb`
- Module: `src/data_cleaning.py`, `src/feature_engineering.py`

### Tools
- pandas, numpy

---

## Phase 4 — Modeling / Analysis

### Objective
Extract meaningful patterns, trends, and relationships from the clean data.

### Inputs
- Clean CSV

### Activities

**4.1 SQL Analysis**

Four layers of SQL queries:

**Layer 1 — Basic queries**
- Row counts, distinct values, date range
- Total sales, profit, orders, quantity
- Profit margin, average order value
- Group-by counts per dimension

**Layer 2 — Aggregation queries**
- Region-wise sales / profit / margin
- Category-wise sales / profit / margin
- Segment-wise performance
- Product-wise performance
- Top N and Bottom N products
- Region × Category pivot
- Season × Category pivot
- Discount impact
- Discount band analysis
- Profit status distribution

**Layer 3 — Window functions**
- `ROW_NUMBER()` for deduplication and sequencing
- `RANK()` / `DENSE_RANK()` for product / region ranking
- `LAG()` / `LEAD()` for month-over-month and year-over-year comparison
- `SUM() OVER (ORDER BY ...)` for running totals
- `AVG() OVER (ROWS BETWEEN ...)` for moving averages
- `NTILE()` for quartile / decile bucketing
- `FIRST_VALUE()` / `LAST_VALUE()` for best / worst per group

**Layer 4 — Final insights**
- Executive summary metrics
- Recommendations based on thresholds
- Findings checklist (boolean validation)

**4.2 Exploratory Data Analysis**

- Distributions: sales, profit, discount, quantity
- Outliers: boxplots
- Correlations: heatmap of numeric columns
- Region analysis: bar + summary
- Category analysis: bar + pie
- Segment analysis: bar + line
- Product analysis: top and bottom
- Time series: monthly, quarterly, yearly
- Discount impact: scatter with trendline
- Discount bands: bar + orders
- Profit status: pie
- Season: bar
- Payment mode: bar + pie
- Weekday vs Weekend: bar

**4.3 Visualization Outputs**

18 plots saved to `images/`:
1. Sales distribution
2. Profit distribution
3. Region-wise sales
4. Region-wise profit
5. Category-wise sales
6. Monthly trend
7. Quarterly trend
8. Top products
9. Bottom products
10. Discount vs profit
11. Discount band
12. Profit status pie
13. Season analysis
14. Payment mode
15. Correlation heatmap
16. Boxplot outliers
17. Customer segment
18. Weekday analysis

### Outputs
- SQL scripts (6 files in `sql/`)
- Notebooks: `03_sql_analysis.ipynb`, `04_eda.ipynb`
- 18 PNG images in `images/`
- CSV exports in `output/`

### Tools
- SQLite / MySQL
- pandas, numpy
- matplotlib, seaborn

---

## Phase 5 — Evaluation

### Objective
Validate analysis, extract insights, and confirm the project meets business objectives.

### Inputs
- Analysis results
- Visualizations
- SQL query outputs

### Activities

**5.1 Validate results**
- Cross-check SQL outputs against Python computations.
- Confirm total sales in SQL matches the total in pandas.
- Confirm region sums add up to overall totals.
- Confirm row counts across tables match.

**5.2 Extract insights**
Auto-generated insights include:
- Overall revenue, profit, margin
- Top region, category, month
- Loss-making products and their count
- Loss-making discount bands
- Profit / Loss / Break-even distribution
- Top payment mode
- Top customer
- Weekday vs Weekend performance

**5.3 Generate recommendations**
Rule-based recommendations with priority:
- **High**: Low-margin region, loss-making discount band, high-discount orders
- **Medium**: Loss-making products, best region / category expansion
- **Low**: Customer loyalty for top customers

**5.4 Run findings checklist**
15 boolean checks:
- Data loaded and cleaned
- KPIs computed
- Region / category analysis done
- Top products identified
- Loss-making products identified
- Discount impact analyzed
- Time trends analyzed
- Customer analysis done
- Payment mode analyzed
- Insights generated
- Recommendations generated
- Summary markdown exported
- JSON exported
- No API used

### Outputs
- `reports/insights_summary.md`
- `output/insights.json`
- `output/recommendations.csv`
- `output/executive_summary.csv`
- Notebook: `05_insights.ipynb`

### Tools
- pandas, JSON

---

## Phase 6 — Deployment

### Objective
Deliver the project in a usable, reproducible form.

### Inputs
- All previous outputs

### Activities

**6.1 Dashboard**
- Build 4-page dashboard in Power BI / Tableau:
  1. Overview (KPIs + trend)
  2. Product performance
  3. Region performance
  4. Time analysis
- Add filters: Date, Region, Category, Segment, Payment Mode
- Export screenshots

**6.2 Final report**
- Write `reports/final_report.pdf` covering:
  - Executive summary
  - Data description
  - Methodology
  - Findings per dimension
  - Recommendations
  - Appendix

**6.3 Presentation**
- Create `reports/presentation.pptx` (10–15 slides):
  - Title
  - Problem statement
  - Approach
  - Data overview
  - Key findings
  - Recommendations
  - Conclusion

**6.4 Documentation**
- `README.md` with setup and usage
- `docs/project_plan.md`
- `docs/methodology.md`
- `docs/data_dictionary.md`
- `docs/conclusions.md`

**6.5 Version control**
- Push all code, docs, notebooks, tests, images to GitHub.
- Ensure `.gitignore` excludes virtual environments and large files.

**6.6 Testing**
- Run `pytest tests/` — all tests must pass.
- Verify pipeline reproducibility from raw CSV to final output.

### Outputs
- Dashboard file + screenshots
- Final report PDF
- Presentation PPTX
- GitHub repo
- Test reports

### Tools
- Power BI / Tableau
- Word / Google Docs
- PowerPoint / Google Slides
- Git + GitHub
- pytest

---

## Iteration Points

CRISP-DM is iterative. In this project, iteration typically happens at:

- **Phase 2 → Phase 3**: After data understanding, if quality issues require re-thinking cleaning rules.
- **Phase 4 → Phase 3**: If a required feature is missing during analysis, go back to feature engineering.
- **Phase 5 → Phase 4**: If insights are weak, add more analysis or visualizations.
- **Phase 6 → Phase 5**: If the dashboard exposes a gap, revisit evaluation.

---

## Summary of Phase Outputs

| Phase | Key Output |
|-------|-----------|
| Business Understanding | Objectives, KPIs, success criteria |
| Data Understanding | Data quality report |
| Data Preparation | Clean CSV + features |
| Modeling / Analysis | SQL scripts, EDA plots, insights |
| Evaluation | Recommendations + checklist |
| Deployment | Dashboard, report, PPT, GitHub repo |

---

## Constraints Applied

- No API integration at any stage.
- All data comes from static CSV / Excel / SQL dump.
- Project must run offline.
- Reproducible by anyone with the repository.

---

## References

- CRISP-DM 1.0 — Step-by-step data mining guide
- Pandas documentation
- SQL window functions reference
- Matplotlib / Seaborn galleries
- Power BI / Tableau official documentation

---

**End of Methodology Document**