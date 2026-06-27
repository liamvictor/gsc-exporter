# Period Comparison Report

A script to compare performance across two time periods, providing charts
and query-level delta analysis.

---

## Command Line Usage

### Standard Example
```bash
python reports/period_comparison_report.py <site_url> --last-month
```

### Argument Reference
* **`site_url`** *(positional)*: The GSC property URL (e.g. `sc-domain:example.com` or `https://example.com/`).
* **`--start-date YYYY-MM-DD`**: Specify a custom start date for the analysis.
* **`--end-date YYYY-MM-DD`**: Specify a custom end date.
* **`--last-month`**: Automatically run the report for the last complete calendar month.
* **`--last-7-days`**: Run for the last 7 full days of available data.

No custom optional arguments defined for this report.


---

## Expected Output Files

This report generates the following files in the output directory:

* `output/<domain>/period-comparison-{slug}-{start_date}-to-{end_date}.csv` (CSV dataset)
* `output/<domain>/period-comparison-template.html` (HTML report)
* `output/<domain>/period-comparison-{slug}-{start_date}-to-{end_date}.html` (HTML report)

---

## How to Interpret the Period Comparison Report

This report tracks performance changes between a current period and a previous period of equal length.

### 1. Interactive Charts
* Visualise query-level deltas to quickly distinguish broad traffic changes from page-specific fluctuations.

### 2. Query Deltas (Clicks & Impressions)
* **Positive Delta (+)**: Marks search terms that have gained visibility and clicks ("Rising Stars").
* **Negative Delta (-)**: Highlights search terms that have lost traction ("Decaying Keywords").

### 3. Position Deltas
* **Negative Delta (-)**: Represents a positive change (ranking moved closer to position 1).
* **Positive Delta (+)**: Indicates ranking slippage.

### 4. Content Decay & Opportunity Analysis
* Sort by click delta descending to find the biggest winners.
* Sort by click delta ascending to locate decaying pages/queries that require content updates or backlink acquisition.
* Focus on queries with stable or rising impressions but falling clicks—this indicates a drop in snippet relevance or increased competitor ad spend.

---

## Recommendations and Best Practices

1. **Warm the Cache First**: Run `python utilities/cache_warmer.py --file site-lists/sites.txt` to populate GSC data locally before executing batch reports.
2. **Frequency**: Generate this report monthly to identify seasonal trends and monitor organic visibility performance.
3. **Bespoke Branding**: Custom logo, primary colours, and support links can be configured in `config/branding.json`.
