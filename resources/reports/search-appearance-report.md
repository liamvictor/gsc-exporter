# Search Appearance Report

Generates a search appearance report for a single property or all properties in the account.
Exposes performance metrics (clicks, impressions, CTR, average position) segmented by Search Appearance.

---

## Command Line Usage

### Standard Example
```bash
python reports/search_appearance_report.py <site_url> --last-month
```

### Argument Reference
* **`site_url`** *(positional)*: The GSC property URL (e.g. `sc-domain:example.com` or `https://example.com/`).
* **`--start-date YYYY-MM-DD`**: Specify a custom start date for the analysis.
* **`--end-date YYYY-MM-DD`**: Specify a custom end date.
* **`--last-month`**: Automatically run the report for the last complete calendar month.
* **`--last-7-days`**: Run for the last 7 full days of available data.

### Optional Arguments

* **`--all-properties`**: Retrieve data for all properties in the GSC account.


---

## Expected Output Files

This report generates the following files in the output directory:

* `output/<domain>/{file_prefix}.csv` (CSV dataset)
* `output/<domain>/report-blank.html` (HTML report)
* `output/<domain>/{file_prefix}.html` (HTML report)

---

## How to Interpret the Search Appearance Report

Segment your performance metrics by Google Rich Result types (e.g. Review Snippets, FAQs, Videos, AMP, Products).

### 1. Rich Result Efficiency
* Compare CTRs of search appearances against standard web search. Rich results generally exhibit significantly higher CTR.

### 2. Schema Markup Verification
* If you deployed Structured Data (e.g. Product or FAQ Schema) but see zero impressions for that type, your schema may be invalid or not yet indexed by Google.
* Use this report to calculate the direct traffic ROI of your structured data implementation efforts.

---

## Recommendations and Best Practices

1. **Warm the Cache First**: Run `python utilities/cache_warmer.py --file site-lists/sites.txt` to populate GSC data locally before executing batch reports.
2. **Frequency**: Generate this report monthly to identify seasonal trends and monitor organic visibility performance.
3. **Bespoke Branding**: Custom logo, primary colours, and support links can be configured in `config/branding.json`.
