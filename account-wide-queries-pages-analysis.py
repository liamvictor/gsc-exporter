"""
Performs an account-wide analysis of Google Search Console data, gathering key
performance metrics for each complete calendar month for every property in the account.

This script authenticates with the Google Search Console API, fetches a list of all
sites associated with the account, and then, for each site, retrieves the clicks,
impressions, CTR, average position, and counts of unique queries and pages for
each full calendar month over the last 16 months.

The aggregated data is then compiled into a single CSV file and a single HTML report,
providing a comprehensive overview of the account's performance over time.
"""

import os
import pandas as pd
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from urllib.parse import urlparse
import argparse
from functools import cmp_to_key

# --- Configuration ---
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'

def get_gsc_service():
    """Authenticates and returns a Google Search Console service object."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                print(f"Error: {CLIENT_SECRET_FILE} not found.")
                print("Please download your client secret from the Google API Console and place it in the root directory.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('webmasters', 'v3', credentials=creds)

def get_all_sites(service):
    """Fetches a list of all sites in the user's GSC account."""
    sites = []
    try:
        site_list = service.sites().list().execute()
        if 'siteEntry' in site_list:
            sites = [s['siteUrl'] for s in site_list['siteEntry']]
    except HttpError as e:
        print(f"An HTTP error occurred while fetching sites: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while fetching sites: {e}")
    return sites

def get_monthly_performance_data(service, site_url, start_date, end_date):
    """
    Fetches performance data from GSC for a given date range.
    This includes total clicks, impressions, CTR, and average position,
    as well as the number of unique queries and pages.
    Note: The count of unique queries and pages is capped at 5000 each
    due to API limitations. For sites with more than 5000 unique queries or
    pages per month, the reported number will be 5000.
    """
    try:
        # 1. Get total aggregated data (clicks, impressions, ctr, position)
        request_totals = {
            'startDate': start_date,
            'endDate': end_date
        }
        response_totals = service.searchanalytics().query(siteUrl=site_url, body=request_totals).execute()

        if 'rows' not in response_totals:
            print(f"    - No data for {site_url} for the period {start_date} to {end_date}.")
            return None

        totals_data = response_totals['rows'][0]

        # 2. Get unique query count
        unique_queries = 0
        try:
            request_queries = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['query'],
                'rowLimit': 5000
            }
            response_queries = service.searchanalytics().query(siteUrl=site_url, body=request_queries).execute()
            if 'rows' in response_queries:
                unique_queries = len(response_queries['rows'])
        except HttpError as e:
            print(f"    - Warning: Could not fetch unique query count for {site_url}: {e}")

        # 3. Get unique page count
        unique_pages = 0
        try:
            request_pages = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['page'],
                'rowLimit': 5000
            }
            response_pages = service.searchanalytics().query(siteUrl=site_url, body=request_pages).execute()
            if 'rows' in response_pages:
                unique_pages = len(response_pages['rows'])
        except HttpError as e:
            print(f"    - Warning: Could not fetch unique page count for {site_url}: {e}")

        return {
            'clicks': totals_data['clicks'],
            'impressions': totals_data['impressions'],
            'ctr': totals_data['ctr'],
            'position': totals_data['position'],
            'queries': unique_queries,
            'pages': unique_pages
        }

    except HttpError as e:
        if e.resp.status == 403:
            print(f"Warning: Insufficient permission for site {site_url}. Skipping further monthly data for this property.")
            return "PERMISSION_DENIED" # Special indicator
        # Handle cases where there is no data for the month, which can be a 400 or 404 error
        if e.resp.status in [400, 404]:
             print(f"    - No data available for {site_url} from {start_date} to {end_date}.")
        else:
            print(f"An HTTP error occurred for site {site_url} from {start_date} to {end_date}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred for site {site_url} from {start_date} to {end_date}: {e}")
    return None

def create_html_report(df, sorted_sites):
    """Generates an HTML report from the analysis dataframe."""
    
    # Generate the index of sites
    index_html = '<ul>'
    current_root_domain = None
    for site in sorted_sites:
        root_domain, order, subdomain = get_sort_key(site)
        
        # Determine if we need a new root domain heading
        if root_domain != current_root_domain:
            if current_root_domain is not None:
                index_html += '</ul></li>' # Close previous root domain's ul and li
            index_html += f'<li><strong>{root_domain}</strong><ul>' # Open new root domain's li and ul
            current_root_domain = root_domain

        # Create a URL-friendly anchor link
        anchor = site.replace('https://', '').replace('http://', '').replace(':', '-').replace('/', '-').replace('.', '-')
        
        if order == 0 or order == 1: # sc-domain or www
            # These are top-level within their root domain group
            index_html += f'<li><a href="#{anchor}">{site}</a></li>'
        else:
            # Other subdomains are indented
            index_html += f'<li>&nbsp;&nbsp;&nbsp;&nbsp;<a href="#{anchor}">{site}</a></li>'
            
    if current_root_domain is not None:
        index_html += '</ul></li>' # Close the last root domain's ul and li
    index_html += '</ul>'

    # Generate the individual site sections
    site_sections_html = generate_site_sections(df, sorted_sites)

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account-Wide GSC Performance Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ padding: 2rem; }}
        .table-responsive {{ max-height: 800px; overflow-y: auto; }}
        h1, h2, h3 {{ border-bottom: 2px solid #dee2e6; padding-bottom: 0.5rem; margin-top: 2rem; }}
        footer {{ margin-top: 3rem; text-align: center; color: #6c757d; }}
        .table thead th {{ text-align: center; }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <h1 class="mb-3" id="top">Account-Wide GSC Performance Report</h1>
        <h2>Index</h2>
        {index_html}
        {site_sections_html}
    </div>
    <footer>
        <p><a href="https://github.com/liamdelahunty/gsc-exporter" target="_blank">gsc-exporter</a></p>
    </footer>
</body>
</html>
"""
    return html_template

def generate_site_sections(df, sorted_sites):
    """Generates HTML sections for each site."""
    sections_html = ''
    for site in sorted_sites:
        anchor = site.replace('https://', '').replace('http://', '').replace(':', '-').replace('/', '-').replace('.', '-')
        sections_html += f'<h2 id="{anchor}" class="mt-5">{site}</h2>'
        
        site_df = df[df['site_url'] == site].drop(columns=['site_url'])
        
        if not site_df.empty:
            sections_html += '<div class="table-responsive">'
            sections_html += site_df.to_html(classes="table table-striped table-hover", index=False, border=0)
            sections_html += '</div>'
            sections_html += '<p><a href="#top">Back to Top</a></p>' # Added "Back to Top" link
        else:
            sections_html += '<p>No data available for this site.</p>'
            sections_html += '<p><a href="#top">Back to Top</a></p>' # Added "Back to Top" link
            
    return sections_html

def get_sort_key(site_url):
    """Creates a sort key for a site URL based on the specified sorting rules."""
    
    # Rule 1: Extract root domain for primary sorting
    if site_url.startswith('sc-domain:'):
        root_domain = site_url.replace('sc-domain:', '')
    else:
        netloc = urlparse(site_url).netloc
        parts = netloc.split('.')
        if len(parts) > 2 and parts[-2] in ['co', 'com', 'org', 'net', 'gov', 'edu'] and len(parts[-3]) > 2:
            root_domain = '.'.join(parts[-3:])
        elif len(parts) > 2:
            root_domain = '.'.join(parts[-2:])
        else:
            root_domain = netloc

    # Rule 2 & 3: Prioritise sc-domain and www
    if site_url.startswith('sc-domain:'):
        order = 0
        subdomain = ''
    elif urlparse(site_url).netloc.startswith('www.'):
        order = 1
        subdomain = ''
    else:
        order = 2
        subdomain = urlparse(site_url).netloc.split('.')[0]
        
    return (root_domain, order, subdomain)
    
def main():
    """Main function to run the account-wide analysis."""
    service = get_gsc_service()
    if not service:
        return

    sites = get_all_sites(service)
    if not sites:
        print("No sites found in your account.")
        return

    sites.sort(key=get_sort_key)

    all_data = []
    today = date.today()
    
    # Define the number of months to go back, e.g., 16 for the last 16 full months
    # The GSC API has a data retention of 16 months.
    # We fetch data for the last 16 complete calendar months.
    for site_url in sites:
        print(f"\nFetching data for site: {site_url}")
        # Loop from 1 to 17 to cover the last 16 full months.
        # i=1 is the previous month, i=16 is 16 months ago.
        for i in range(1, 17):
            # Calculate the end date of the month 'i' months ago
            end_of_month = today.replace(day=1) - relativedelta(months=i-1) - timedelta(days=1)
            # Calculate the start date of that same month
            start_of_month = end_of_month.replace(day=1)
            
            start_date_str = start_of_month.strftime('%Y-%m-%d')
            end_date_str = end_of_month.strftime('%Y-%m-%d')
            
            print(f"  - Fetching data for {start_of_month.strftime('%Y-%m')}...")
            data = get_monthly_performance_data(service, site_url, start_date_str, end_date_str)
            
            if data == "PERMISSION_DENIED":
                break # Stop processing this site
            elif data:
                all_data.append({
                    'site_url': site_url,
                    'month': start_of_month.strftime('%Y-%m'),
                    'clicks': data['clicks'],
                    'impressions': data['impressions'],
                    'ctr': data['ctr'],
                    'position': data['position'],
                    'queries': data.get('queries', 0),
                    'pages': data.get('pages', 0)
                })
    
    if not all_data:
        print("No performance data found for any site.")
        return
        
    df = pd.DataFrame(all_data)
    
    # Reorder columns for the final report
    column_order = ['site_url', 'month', 'clicks', 'impressions', 'ctr', 'position', 'queries', 'pages']
    df = df[column_order]
    
    output_dir = os.path.join('output', 'account')
    os.makedirs(output_dir, exist_ok=True)
    
    most_recent_month = (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m')

    # Update file names
    csv_file_name = f'account-wide-queries-pages-{most_recent_month}.csv'
    csv_output_path = os.path.join(output_dir, csv_file_name)

    html_file_name = f'account-wide-queries-pages-{most_recent_month}.html'
    html_output_path = os.path.join(output_dir, html_file_name)
    
    try:
        # Save the raw data to CSV before formatting for HTML
        df.to_csv(csv_output_path, index=False)
        print(f"\nSuccessfully exported CSV to {csv_output_path}")

        # Create a deep copy for HTML formatting
        html_df = df.copy()
        html_df['ctr'] = html_df['ctr'].apply(lambda x: f"{x:.2%}")
        html_df['position'] = html_df['position'].apply(lambda x: f"{x:.2f}")

        # Generate and save HTML report
        html_output = create_html_report(html_df, sites)
        with open(html_output_path, 'w', encoding='utf-8') as f:
            f.write(html_output)
        print(f"Successfully created HTML report at {html_output_path}")
    except PermissionError:
        print(f"\nError: Permission denied when trying to write to the output directory.")
        print(f"Please make sure you have write permissions for the directory: {output_dir}")
        print(f"Also, check if the file is already open in another program: {csv_file_name} or {html_file_name}")

if __name__ == '__main__':
    main()
