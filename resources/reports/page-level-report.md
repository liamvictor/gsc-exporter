# Page Level Report

Generates a page-level report with key performance metrics and unique query counts.
Adapted for the modular GSC Exporter.

---

## Command Line Usage

### Standard Example
```bash
python reports/page_level_report.py <site_url> --last-month
```

### Argument Reference
* **`site_url`** *(positional)*: The GSC property URL (e.g. `sc-domain:example.com` or `https://example.com/`).
* **`--start-date YYYY-MM-DD`**: Specify a custom start date for the analysis.
* **`--end-date YYYY-MM-DD`**: Specify a custom end date.
* **`--last-month`**: Automatically run the report for the last complete calendar month.
* **`--last-7-days`**: Run for the last 7 full days of available data.

### Optional Arguments

* **`--search-type`**: No description available. (default: `'web'`)
* **`--limit`**: Limit for HTML report. (default: `250`)
* **`--strip-query-strings`**: Remove query strings.


---

## Expected Output Files

This report generates the following files in the output directory:

* `output/<domain>/{file_prefix}.csv` (CSV dataset)
* `output/<domain>/{file_prefix}.html` (HTML report)

---

## How to Interpret the Page Level Report

A page-centric view of performance focusing on organic traffic distribution and query complexity.

### 1. Unique Query Counts (Query #)
* **Long-Tail Depth**: Pages with a high number of unique queries are successfully capturing long-tail search traffic.
* **Narrow Intent**: Pages with high clicks but a low unique query count typically rank highly for a single, high-volume keyword.

### 2. Traffic Skew
* Typically, 20% of your pages drive 80% of your traffic. Use this report to verify if traffic is diversified or heavily reliant on a single landing page.
* Check pages with high unique queries but low clicks—they may require small content expansions to move long-tail rankings from page 2 to page 1.

---

## Recommendations and Best Practices

1. **Warm the Cache First**: Run `python utilities/cache_warmer.py --file site-lists/sites.txt` to populate GSC data locally before executing batch reports.
2. **Frequency**: Generate this report monthly to identify seasonal trends and monitor organic visibility performance.
3. **Bespoke Branding**: Custom logo, primary colours, and support links can be configured in `config/branding.json`.
