# Customer Churn EDA

A presentation-ready, single-page Streamlit dashboard for exploring customer churn data. It uses Pandas and NumPy to summarize the data and compare churn rates across customer groups.

## Objective

Use Pandas to manipulate customer retention data and NumPy to calculate and aggregate statistics.

## Expected outcome

The dashboard highlights the highest-risk segment, summarizes key churn metrics, and creates a structured DataFrame report ranking customer segments by churn rate and difference from the overall rate. This helps identify potential churn risk factors for further investigation.

## Run on Windows

1. Open this folder in Command Prompt or PowerShell.
2. (Optional) Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Start the app:

   ```powershell
   python -m streamlit run app.py
   ```

The included `achive.csv` is loaded automatically. To analyze a different dataset, upload a CSV in the sidebar and select its churn/outcome column and the value that represents churn.

The dashboard uses a dark, editorial layout by default, with a light/dark appearance switch, floating navigation, a dotted hero, and scroll-triggered reveal animations. Headline text slides through a clipping mask; key metrics count up when they enter the viewport; and a decorative SVG journey line draws as the page scrolls. Motion respects the operating system's reduced-motion preference. The decision simulator estimates the arithmetic impact of a chosen relative churn reduction in an observed customer segment; it is an assumption-based scenario, not a causal forecast. Use the sidebar to filter the analysis by a low-cardinality customer field, choose how many segments to chart, and rank the chart by churn rate or difference from the overall rate. The vertical chart marks the overall churn rate for comparison. The dashboard also highlights the lowest-churn segment, lets you search the segment report, and exports filtered data. Both reports reflect the selected filter.

## Report fields

- **Factor / Segment:** The customer characteristic and its category or numeric range.
- **Customers / Churned:** The number of records in the segment and the number marked as churned.
- **Churn rate (%):** The share of customers in the segment marked as churned.
- **vs overall (pp):** The segment churn rate minus the overall churn rate, in percentage points.

The app filters out very small groups, displays the report and exports it as `churn_risk_report.csv`. These are exploratory associations, not proof that a factor causes churn or a predictive model.

See [REPORT.md](./REPORT.md) for a snapshot of the bundled sample data and dashboard capabilities.
