"""
Generates a report using the Google Search Console URL Inspection API.
Adapted for the modular GSC Exporter.
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from datetime import datetime
from urllib.parse import urlparse
from core.naming import get_output_dir

def get_url_inspection_data(service, site_url, inspect_url):
    """Fetches URL inspection data for a given URL."""
    try:
        request = {
            'inspectionUrl': inspect_url,
            'siteUrl': site_url,
            'languageCode': 'en-US'
        }
        response = service.urlInspection().index().inspect(body=request).execute()
        return response.get('inspectionResult')
    except Exception as e:
        return {"error": str(e)}

def _format_inspection_data_for_csv(inspect_url, inspection_data, request_timestamp):
    """Flattens raw inspection data into a dictionary for CSV."""
    row = {'Request Timestamp': request_timestamp, 'URL': inspect_url}

    if inspection_data and inspection_data.get("error"):
        row['Error'] = inspection_data['error']
        return row
    elif not inspection_data:
        row['Error'] = 'No inspection data received.'
        return row
    
    index_status = inspection_data.get('indexStatusResult', {})
    mobile_usability = inspection_data.get('mobileUsability', {})
    rich_results = inspection_data.get('richResults', [])

    row.update({
        "Verdict": index_status.get('verdict', 'N/A'),
        "Indexing State": index_status.get('indexingState', 'N/A'),
        "Page Fetch State": index_status.get('pageFetchState', 'N/A'),
        "Last Crawl Time": index_status.get('lastCrawlTime', 'N/A'),
        "Google Canonical": index_status.get('googleCanonicalUrl', 'N/A'),
        "User Canonical": index_status.get('userCanonical', 'N/A'),
        "Robots.txt State": index_status.get('robotsTxtState', 'N/A'),
        "In Sitemap": index_status.get('sitemap', 'N/A'),
        "Crawled As": index_status.get('crawledAs', 'N/A'),
        "Coverage State": index_status.get('coverageState', 'N/A'),
        "Referring URLs": ', '.join(index_status.get('referringUrls', [])),
        "Mobile Usability Verdict": mobile_usability.get('verdict', 'N/A'),
        "Mobile Usability Issues": ', '.join([item.get('issueType', 'N/A') for item in mobile_usability.get('issues', [])]),
        "Rich Results Status": ', '.join([item.get('richResultType', 'N/A') + ' - ' + item.get('verdict', 'N/A') for item in rich_results])
    })
    return row

def run_report(service, urls, site_list_name="report"):
    """Executes the URL inspection report for a list of URLs."""
    print(f"Running URL Inspection Report for {len(urls)} URLs...")
    
    request_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_date_str = datetime.now().strftime("%Y-%m-%d")
    
    all_inspection_results = {}
    
    for url in urls:
        print(f"Inspecting: {url}")
        # Derive site URL for API
        parsed = urlparse(url)
        site_url = f"{parsed.scheme}://{parsed.netloc}/"
        
        inspection_data = get_url_inspection_data(service, site_url, url)
        all_inspection_results[url] = inspection_data
    
    # Paths
    # Using 'account' as a generic output directory for list-based reports
    output_dir = os.path.join(get_output_dir("account"), 'url-inspection')
    os.makedirs(output_dir, exist_ok=True)
    
    base_filename = f"inspection-{site_list_name}-{current_date_str}"
    csv_path = os.path.join(output_dir, f"{base_filename}.csv")
    
    # Save CSV
    formatted_data_list = [_format_inspection_data_for_csv(url, data, request_timestamp) for url, data in all_inspection_results.items()]
    pd.DataFrame(formatted_data_list).to_csv(csv_path, index=False, encoding='utf-8')
    
    print(f"Report completed: {csv_path}")
    return csv_path

if __name__ == '__main__':
    import argparse
    from core.client import get_gsc_service
    
    parser = argparse.ArgumentParser(description='Inspect URLs.')
    parser.add_argument('--url', help='Single URL.')
    parser.add_argument('--sites-file', help='File with URLs.')
    
    args = parser.parse_args()
    
    service = get_gsc_service() # Need searchconsole v1 service
    
    if service:
        urls = []
        if args.url:
            urls = [args.url]
            name = "single"
        elif args.sites_file:
            with open(args.sites_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            name = os.path.splitext(os.path.basename(args.sites_file))[0]
            
        run_report(service, urls, name)
