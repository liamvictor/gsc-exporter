"""
Generates a monthly Google Search Console performance report by search type.

This script fetches performance data (clicks, impressions, CTR) for all available
search types (web, discover, Google News, image, video, news) for a given site.
It fetches data for the last 16 months, providing a monthly breakdown.
The output is a CSV file containing the aggregated monthly data.

Usage:
    python monthly-search-type-performance-report.py <site_url>

Example:
    python monthly-search-type-performance-report.py sc-domain:example.com
"""
import os
import pandas as pd
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth import exceptions
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from urllib.parse import urlparse
import argparse
from functools import reduce

# --- Configuration ---
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'
SEARCH_TYPES = ['web', 'image', 'video', 'news', 'discover', 'googleNews']

def get_gsc_service():
    """Authenticates and returns a Google Search Console service object."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Could not load credentials from {TOKEN_FILE}. Error: {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except exceptions.RefreshError as e:
                print(f"Error refreshing token: {e}")
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                creds = None
        
        if not creds:
            if not os.path.exists(CLIENT_SECRET_FILE):
                print(f"Error: {CLIENT_SECRET_FILE} not found.")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('webmasters', 'v3', credentials=creds)

def fetch_gsc_data(service, site_url, start_date, end_date, search_type):
    """Fetches GSC data for a given search type and date range."""
    print(f"Fetching {search_type} data for {site_url} from {start_date} to {end_date}...")
    try:
        request = {
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': ['date'],
            'searchType': search_type,
            'rowLimit': 25000,
            'aggregationType': 'byPage'
        }
        response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        return response.get('rows', [])
    except HttpError as e:
        print(f"An HTTP error occurred for {search_type} data: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred for {search_type} data: {e}")
        return []

def process_data_monthly(rows, search_type):
    """Processes the raw API data into a monthly pandas DataFrame."""
    if not rows:
        return pd.DataFrame()
    
    df = pd.DataFrame(rows)
    df['date'] = pd.to_datetime(df['keys'].apply(lambda x: x[0]))
    df['month'] = df['date'].dt.strftime('%Y-%m')
    
    df.rename(columns={
        'clicks': f'{search_type}_clicks',
        'impressions': f'{search_type}_impressions',
    }, inplace=True)
    
    monthly_df = df.groupby('month').agg({
        f'{search_type}_clicks': 'sum',
        f'{search_type}_impressions': 'sum'
    }).reset_index()
    
    monthly_df[f'{search_type}_ctr'] = monthly_df[f'{search_type}_clicks'] / monthly_df[f'{search_type}_impressions']
    
    return monthly_df

def get_latest_available_gsc_date(service, site_url, max_retries=5):
    """
    Determines the latest date for which GSC data is available by querying
    backwards from today.
    """
    current_date = date.today()
    for i in range(max_retries):
        check_date = current_date - timedelta(days=i + 2) # GSC data is usually delayed
        check_date_str = check_date.strftime('%Y-%m-%d')
        
        print(f"Checking for GSC data availability on: {check_date_str}...")
        try:
            request = {
                'startDate': check_date_str,
                'endDate': check_date_str,
                'dimensions': ['date'],
                'rowLimit': 1
            }
            response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
            
            if 'rows' in response and response['rows']:
                print(f"Latest available GSC data found for: {check_date_str}")
                return check_date
        except HttpError as e:
            if e.resp.status == 400:
                print(f"No data for {check_date_str}, checking previous day (HTTP 400).")
            else:
                print(f"An HTTP error occurred while checking date {check_date_str}: {e}")
            
    print(f"Could not determine latest available GSC date. Using two days ago as fallback.")
    return current_date - timedelta(days=2)

def create_search_type_report_html(df, report_title, date_range, site_url, template_path='resources/report-blank.html'):
    """Generates a search type performance HTML report from a DataFrame."""
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        return None

    with open(template_path, 'r', encoding='utf-8') as f:
        template_html = f.read()

    report_df = df.copy()

    # Format numeric columns
    for col in report_df.columns:
        if 'clicks' in col or 'impressions' in col:
            report_df[col] = report_df[col].apply(lambda x: f"{int(x):,}")
        elif 'ctr' in col:
            report_df[col] = report_df[col].apply(lambda x: f"{x:.2%}" if pd.notnull(x) and x != 0 else '0.00%')

    # Rename columns for presentation
    column_rename_map = {
        'month': 'Month',
        'web_clicks': 'Web Clicks', 'web_impressions': 'Web Impressions', 'web_ctr': 'Web CTR',
        'image_clicks': 'Image Clicks', 'image_impressions': 'Image Impressions', 'image_ctr': 'Image CTR',
        'video_clicks': 'Video Clicks', 'video_impressions': 'Video Impressions', 'video_ctr': 'Video CTR',
        'news_clicks': 'News Clicks', 'news_impressions': 'News Impressions', 'news_ctr': 'News CTR',
        'discover_clicks': 'Discover Clicks', 'discover_impressions': 'Discover Impressions', 'discover_ctr': 'Discover CTR',
        'googleNews_clicks': 'Google News Clicks', 'googleNews_impressions': 'Google News Impressions', 'googleNews_ctr': 'Google News CTR',
        'total_clicks': 'Total Clicks', 'total_impressions': 'Total Impressions', 'total_ctr': 'Total CTR',
    }
    
    # Only rename columns that actually exist in the DataFrame
    existing_columns_to_rename = {k: v for k, v in column_rename_map.items() if k in report_df.columns}
    report_df = report_df.rename(columns=existing_columns_to_rename)
    
    # Define the order of columns, keeping only those present in the report
    ordered_columns = [
        'Month', 'Total Clicks', 'Total Impressions', 'Total CTR',
        'Web Clicks', 'Web Impressions', 'Web CTR',
        'Image Clicks', 'Image Impressions', 'Image CTR',
        'Video Clicks', 'Video Impressions', 'Video CTR',
        'News Clicks', 'News Impressions', 'News CTR',
        'Discover Clicks', 'Discover Impressions', 'Discover CTR',
        'Google News Clicks', 'Google News Impressions', 'Google News CTR'
    ]
    
    final_columns = [col for col in ordered_columns if col in report_df.columns]
    report_df = report_df[final_columns]

    table_html = report_df.to_html(classes="table table-striped table-hover", index=False, border=0)

    html_output = template_html.replace('This Report Name', report_title)
    html_output = html_output.replace(
        '<span class="text-muted me-4">Domain name</span>',
        f'<span class="text-muted me-4">{site_url}</span>'
    )
    html_output = html_output.replace(
        '<span class="text-muted me-4">Date-range</span>',
        f'<span class="text-muted me-4">{date_range}</span>'
    )
    html_output = html_output.replace(
        '<a href="index.html">Resources</a>',
        '<a href="../../resources/index.html">Resources</a>'
    )
    
    custom_css = """<style>
        html {
            height: 100%;
        }
        body {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        .table th, .table td {
            text-align: right;
            vertical-align: middle;
        }
        .table th:first-child, .table td:first-child {
            text-align: left;
        }
    </style>"""
    html_output = html_output.replace(
        """<style>
        html {
            height: 100%;
        }
        body {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
    </style>""",
        custom_css
    )

    main_content_placeholder = """    <main class="container py-4 flex-grow-1">
        <h1>Hello</h1>
        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
            tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
            quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
            consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
            cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
        proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
        <div class="row">
            <div class="col">
                <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
                    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
                    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
                    consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
                    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
                proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
            </div>
            <div class="col">
                <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
                    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
                    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
                    consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
                    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
                proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
            </div>
        </div>
    </main>"""

    final_main_content = f"""    <main class="container py-4 flex-grow-1">
        <div class="table-responsive">
            {table_html}
        </div>
    </main>"""
    
    html_output = html_output.replace(main_content_placeholder, final_main_content)

    return html_output


def main():
    parser = argparse.ArgumentParser(description='Generate a monthly performance report by search type from Google Search Console.')
    parser.add_argument('site_url', help='The URL of the site to process (e.g., sc-domain:example.com).')
    
    args = parser.parse_args()
    site_url = args.site_url

    service = get_gsc_service()
    if not service:
        print("Failed to get GSC service.")
        return

    latest_available_date = get_latest_available_gsc_date(service, site_url)
    
    # GSC API has a 16-month data retention period.
    # We will fetch for the last 16 complete months.
    end_date = latest_available_date.replace(day=1) - timedelta(days=1)
    start_date = end_date.replace(day=1) - relativedelta(months=15)
    
    end_date_str = end_date.strftime('%Y-%m-%d')
    start_date_str = start_date.strftime('%Y-%m-%d')

    all_monthly_dfs = []
    for st in SEARCH_TYPES:
        data = fetch_gsc_data(service, site_url, start_date_str, end_date_str, st)
        monthly_df = process_data_monthly(data, st)
        if not monthly_df.empty:
            all_monthly_dfs.append(monthly_df)
    
    if not all_monthly_dfs:
        print("No data found for any search type in the given period.")
        return

    # Merge all dataframes on month
    merged_df = reduce(lambda left, right: pd.merge(left, right, on='month', how='outer'), all_monthly_dfs)

    merged_df.fillna(0, inplace=True)
    
    # Calculate totals
    for col_type in ['clicks', 'impressions']:
        cols_to_sum = [f'{st}_{col_type}' for st in SEARCH_TYPES if f'{st}_{col_type}' in merged_df.columns]
        merged_df[f'total_{col_type}'] = merged_df[cols_to_sum].sum(axis=1)

    merged_df['total_ctr'] = merged_df['total_clicks'] / merged_df['total_impressions']
    
    merged_df = merged_df.sort_values('month', ascending=False)
    
    # Define output paths
    if site_url.startswith('sc-domain:'):
        host_plain = site_url.replace('sc-domain:', '')
    else:
        host_plain = urlparse(site_url).netloc
    
    host_dir = host_plain.replace('www.', '')
    output_dir = os.path.join('output', host_dir)
    os.makedirs(output_dir, exist_ok=True)
    host_for_filename = host_dir.replace('.', '-')
    
    # CSV and HTML output
    file_prefix = f"monthly-search-type-performance-{host_for_filename}-{start_date.strftime('%Y-%m')}-to-{end_date.strftime('%Y-%m')}"
    csv_output_path = os.path.join(output_dir, f"{file_prefix}.csv")
    merged_df.to_csv(csv_output_path, index=False)
    print(f"Successfully exported CSV to {csv_output_path}")

    html_output_path = os.path.join(output_dir, f"{file_prefix}.html")
    report_title = f"Monthly Search Type Performance for {site_url}"
    date_range_str = f"{start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')}"
    
    try:
        html_output = create_search_type_report_html(merged_df, report_title, date_range_str, site_url)
        if html_output:
            with open(html_output_path, 'w', encoding='utf-8') as f:
                f.write(html_output)
            print(f"Successfully created HTML report at {html_output_path}")
    except Exception as e:
        print(f"An error occurred during HTML report generation: {e}")

if __name__ == '__main__':
    main()
