# Discover Key Performance Metrics

Performs an analysis of Google Search Console Discover data, gathering key performance metrics.
Refactored for modular GSC Exporter.

---

## Command Line Usage

### Standard Example
```bash
python reports/discover_key_performance_metrics.py <site_url> --last-month
```

### Argument Reference
* **`site_url`** *(positional)*: The GSC property URL (e.g. `sc-domain:example.com` or `https://example.com/`).
* **`--start-date YYYY-MM-DD`**: Specify a custom start date for the analysis.
* **`--end-date YYYY-MM-DD`**: Specify a custom end date.
* **`--last-month`**: Automatically run the report for the last complete calendar month.
* **`--last-7-days`**: Run for the last 7 full days of available data.

### Optional Arguments

* **`--months`**: No description available. (default: `16`)


---

## Expected Output Files

This report generates the following files in the output directory:

* `output/<domain>/{file_prefix}.csv` (CSV dataset)
* `output/<domain>/{file_prefix}.html` (HTML report)

---

## How to Interpret the Google Discover Report

Google Discover is a query-less feed based on user interests rather than search intent.

### 1. Volatility and Spikes
* Discover traffic is notoriously spike-heavy and short-lived. Expect rapid impression surges followed by steep declines.

### 2. High CTR Expectations
* Discover CTRs are often much higher than standard organic web CTR (often 5% to 15%+).
* Analyse high-performing Discover topics to identify content themes that resonate with your target audience's interest feed.

---

## Recommendations and Best Practices

1. **Warm the Cache First**: Run `python utilities/cache_warmer.py --file site-lists/sites.txt` to populate GSC data locally before executing batch reports.
2. **Frequency**: Generate this report monthly to identify seasonal trends and monitor organic visibility performance.
3. **Bespoke Branding**: Custom logo, primary colours, and support links can be configured in `config/branding.json`.
