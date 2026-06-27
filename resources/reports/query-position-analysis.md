# Query Position Analysis

No overview description available.

---

## Command Line Usage

### Standard Example
```bash
python reports/query_position_analysis.py <site_url> --last-month
```

### Argument Reference
* **`site_url`** *(positional)*: The GSC property URL (e.g. `sc-domain:example.com` or `https://example.com/`).
* **`--start-date YYYY-MM-DD`**: Specify a custom start date for the analysis.
* **`--end-date YYYY-MM-DD`**: Specify a custom end date.
* **`--last-month`**: Automatically run the report for the last complete calendar month.
* **`--last-7-days`**: Run for the last 7 full days of available data.

### Optional Arguments

* **`--months`**: Number of months to analyse. (default: `16`)


---

## Expected Output Files

This report generates the following files in the output directory:

* `output/<domain>/query-position-analysis-{slug}-{start_date}-to-{end_date}.csv` (CSV dataset)
* `output/<domain>/query-position-analysis-{slug}-{start_date}-to-{end_date}.html` (HTML report)

---

## How to Interpret the Query Position Analysis Report

Tracks how your keywords are distributed across different ranking groups over time.

### 1. Position Buckets
* Monitors the count and trend of keywords ranking in:
  * **Top 3**: Primary traffic drivers.
  * **Positions 4-10**: Page 1 visibility; prime candidates for optimization to push into Top 3.
  * **Positions 11-20**: Page 2 visibility; requires content improvements or link additions to reach page 1.
  * **Positions 21-100**: Long-tail or low-relevance queries.

### 2. Trend Identification
* If Top 3 keywords are declining while Positions 11-20 are increasing, it indicates site-wide ranking deflation or increased competitor activity.

---

## Recommendations and Best Practices

1. **Warm the Cache First**: Run `python utilities/cache_warmer.py --file site-lists/sites.txt` to populate GSC data locally before executing batch reports.
2. **Frequency**: Generate this report monthly to identify seasonal trends and monitor organic visibility performance.
3. **Bespoke Branding**: Custom logo, primary colours, and support links can be configured in `config/branding.json`.
