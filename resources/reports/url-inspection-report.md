# Url Inspection Report

Generates a report using the Google Search Console URL Inspection API.
Adapted for the modular GSC Exporter with intelligent property detection.

---

## Command Line Usage

### Standard Example
```bash
python reports/url_inspection_report.py --last-month
```

### Argument Reference
* **`site_url`** *(positional)*: The GSC property URL (e.g. `sc-domain:example.com` or `https://example.com/`).
* **`--start-date YYYY-MM-DD`**: Specify a custom start date for the analysis.
* **`--end-date YYYY-MM-DD`**: Specify a custom end date.
* **`--last-month`**: Automatically run the report for the last complete calendar month.
* **`--last-7-days`**: Run for the last 7 full days of available data.

### Optional Arguments

* **`site_url_or_prop`**: GSC property OR a specific URL to inspect.
* **`--url`**: No description available.
* **`--sites-file`**: File with a list of URLs to inspect.


---

## Expected Output Files

This report generates the following files in the output directory:

* `output/<domain>/{base_filename}.csv` (CSV dataset)
* `output/<domain>/{base_filename}.html` (HTML report)

---

## How to Interpret the Report Metrics

* **Clicks**: Represents the number of times a user clicked your search result to visit your site.
* **Impressions**: The number of times your search result appeared in search results.
* **CTR (Click-Through Rate)**: The percentage of impressions that resulted in a click (`Clicks / Impressions`). A low CTR indicates snippet styling or metadata needs improvement.
* **Average Position**: The average ranking position of your URLs for the queries. A lower position (closer to 1) is better. Monitor position trends to spot algorithm updates or competitor improvements.

---

## Recommendations and Best Practices

1. **Warm the Cache First**: Run `python utilities/cache_warmer.py --file site-lists/sites.txt` to populate GSC data locally before executing batch reports.
2. **Frequency**: Generate this report monthly to identify seasonal trends and monitor organic visibility performance.
3. **Bespoke Branding**: Custom logo, primary colours, and support links can be configured in `config/branding.json`.
