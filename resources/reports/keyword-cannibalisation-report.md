# Keyword Cannibalisation Report

Generates a report that highlights keyword cannibalisation issues.
Refactored for modular GSC Exporter.

---

## Command Line Usage

### Standard Example
```bash
python reports/keyword_cannibalisation_report.py <site_url> --last-month
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

* `output/<domain>/{file_prefix}.csv` (CSV dataset)
* `output/<domain>/{file_prefix}.html` (HTML report)

---

## How to Interpret the Keyword Cannibalisation Report

Keyword cannibalisation occurs when multiple pages on your site compete for the same search query.

### 1. Identifying Competitor Pages
* Look for queries where multiple URLs rank with similar average positions.
* If a query lists multiple ranking URLs with split clicks, it indicates search engines are confused about which page is most relevant.

### 2. Assessing the Impact
* **Diluted Authority**: Link equity and click-through rates are split across pages.
* **Rank Fluctuations**: Search engines may constantly alternate which page ranks, causing position instability.

### 3. Actions to Resolve Cannibalisation
* **Canonicalisation**: Set the canonical tag of the weaker page to point to the primary page if they serve the same intent.
* **301 Redirects**: Redirect the redundant page to the primary page and merge their content.
* **De-optimisation**: Remove the target keyword from the metadata and headings of the secondary page.
* **Content Restructuring**: Re-write the pages to target distinct search intents (e.g. informational vs. transactional).

---

## Recommendations and Best Practices

1. **Warm the Cache First**: Run `python utilities/cache_warmer.py --file site-lists/sites.txt` to populate GSC data locally before executing batch reports.
2. **Frequency**: Generate this report monthly to identify seasonal trends and monitor organic visibility performance.
3. **Bespoke Branding**: Custom logo, primary colours, and support links can be configured in `config/branding.json`.
