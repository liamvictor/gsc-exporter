# Sitemap Generator

Generates an XML sitemap and a discovery summary based on Google Search Console data.
Uses a long date range (default 16 months) to ensure maximum URL discovery.
Refactored for modular GSC Exporter.

---

## Command Line Usage

### Standard Example
```bash
python reports/sitemap_generator.py <site_url> --last-month
```

### Argument Reference
* **`site_url`** *(positional)*: The GSC property URL (e.g. `sc-domain:example.com` or `https://example.com/`).
* **`--start-date YYYY-MM-DD`**: Specify a custom start date for the analysis.
* **`--end-date YYYY-MM-DD`**: Specify a custom end date.
* **`--last-month`**: Automatically run the report for the last complete calendar month.
* **`--last-7-days`**: Run for the last 7 full days of available data.

### Optional Arguments

* **`--lookback-months`**: No description available. (default: `16`)
* **`--min-impressions`**: Minimum impressions to include a URL. (default: `0`)


---

## Expected Output Files

This report generates the following files in the output directory:

* `output/<domain>/sitemap-urls{file_prefix}.csv` (CSV dataset)
* `output/<domain>/sitemap-summary{file_prefix}.html` (HTML report)

---

## How to Interpret the Sitemap Generator Report

This tool discovers active URLs based on GSC historical query data and outputs a search-validated XML sitemap.

### 1. Active vs. Orphaned URLs
* Compares URLs in GSC that received impressions/clicks against your internal database.
* Identifies "active" pages that Google is currently crawling and serving.

### 2. Crawl Budget Efficiency
* Sitemap files generated from search-validated URLs ensure Google prioritises crawls on pages that actually generate search visibility, optimizing your crawl budget.
* Exclude low-impression, low-value pages to prevent Google from wasting crawl resources.

---

## Recommendations and Best Practices

1. **Warm the Cache First**: Run `python utilities/cache_warmer.py --file site-lists/sites.txt` to populate GSC data locally before executing batch reports.
2. **Frequency**: Generate this report monthly to identify seasonal trends and monitor organic visibility performance.
3. **Bespoke Branding**: Custom logo, primary colours, and support links can be configured in `config/branding.json`.
