# Snapshot Report

Generates a single-period performance snapshot for a Google Search Console property.
Adapted for the modular GSC Exporter.

---

## Command Line Usage

### Standard Example
```bash
python reports/snapshot_report.py <site_url> --last-month
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

* `output/<domain>/{base_file_prefix}-pages.csv` (CSV dataset)
* `output/<domain>/{base_file_prefix}-devices.csv` (CSV dataset)
* `output/<domain>/{base_file_prefix}-countries.csv` (CSV dataset)
* `output/<domain>/{base_file_prefix}-report.html` (HTML report)

---

## How to Interpret the Snapshot Report

This report provides a multi-dimensional summary of a site's performance for a single period.

### 1. Overall Performance Summary
* **Clicks & Impressions**: Establish the absolute traffic and visibility baseline.
* **Average CTR**: High-level indicator of search snippet relevance and clickability.
* **Average Position**: The weighted average ranking position across all query impressions.

### 2. Top Pages by Clicks & Impressions
* Identify your **Top Traffic Drivers** (high clicks) and **Brand Visibility Leaders** (high impressions).
* A page with high impressions but low clicks indicates a major click-through rate optimization opportunity.

### 3. High Impressions, Low CTR Opportunities
* Lists pages with **>= 1,000 impressions** and **< 1% CTR**.
* **Actionable Insight**: These pages are highly visible in search results but fail to attract clicks. Prioritise them for search snippet optimization (rewriting title tags, improving meta descriptions, and adding structured schema).

### 4. Performance by Device
* **Mobile vs. Desktop vs. Tablet**: Evaluate the mobile-friendliness of your site. If mobile impressions are high but CTR/Position is low, check mobile page speed, rendering, and content presentation.

### 5. Performance by Country
* Analyse geographic traffic distribution. Useful for identifying international expansion opportunities or localising content for top-performing regions.

---

## Recommendations and Best Practices

1. **Warm the Cache First**: Run `python utilities/cache_warmer.py --file site-lists/sites.txt` to populate GSC data locally before executing batch reports.
2. **Frequency**: Generate this report monthly to identify seasonal trends and monitor organic visibility performance.
3. **Bespoke Branding**: Custom logo, primary colours, and support links can be configured in `config/branding.json`.
