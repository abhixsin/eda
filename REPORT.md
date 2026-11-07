# ChurnIQ dashboard report

## Overview

ChurnIQ is a Streamlit dashboard for exploring customer churn patterns in a CSV dataset. It provides outcome selection, a customer-segment filter, churn metrics, ranked vertical segment charts, searchable tables, a data-quality summary, downloadable CSV and Markdown reports, and an assumption-based churn scenario calculator.

The interface defaults to a dark, editorial style with a floating navigation bar, dotted hero background, pale green accent, and light and dark appearance modes. Scroll motion includes reveal transitions, count-up metrics, clipped headline entrance text, and an SVG path that draws with page progress. Animations honor reduced-motion preferences. The chart can display 5–12 segments, rank by churn rate or difference from the overall rate, and shows the overall rate as a reference line. Both highest- and lowest-churn segments are highlighted.

## Bundled sample data

The included `achive.csv` contains **7,043 customer records** and **21 columns**. With `Churn = Yes` as the churn outcome:

- **1,869** customers are marked as churned.
- The overall churn rate is **26.54%**.

The following segments have elevated churn rates in the sample:

| Factor | Segment | Customers | Churned | Churn rate | Difference vs. overall |
|---|---|---:|---:|---:|---:|
| Tenure | 0–9 months | 1,854 | 923 | 49.78% | +23.25 pp |
| Payment method | Electronic check | 2,365 | 1,071 | 45.29% | +18.75 pp |
| Contract | Month-to-month | 3,875 | 1,655 | 42.71% | +16.17 pp |
| Internet service | Fiber optic | 3,096 | 1,297 | 41.89% | +15.36 pp |

These are descriptive comparisons, not evidence that a customer attribute causes churn. Segment rates can also vary with the selected outcome and filter.

## Using the dashboard

1. Run the app using the instructions in [README.md](./README.md).
2. Optionally upload another CSV, then choose its outcome column and churn label.
3. Optionally filter by a low-cardinality customer field in the sidebar.
4. Choose light or dark appearance, chart ranking, and the number of segments to display.
5. In Decision simulator, choose a segment and relative churn-reduction assumption, then run the scenario to see the arithmetic estimate.
6. Review the metrics, high- and low-churn highlights, chart, searchable segment table, and dataset summary.
7. Download the visible segment report, filtered customer rows, or the current analysis as a Markdown report.

The scenario calculator applies the chosen relative reduction to the segment's observed churn count and estimates the resulting overall churn rate. It does not predict or prove the effectiveness of an intervention.

The generated Markdown report contains the current dataset name, outcome, filter, analyzed customer count, churn count and rate, missing-cell count, and up to 15 highest-risk segments.
