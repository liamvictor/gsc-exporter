"""
Generates a page-level report with key performance metrics and unique query counts.

This script fetches performance data for a specified date range and creates a CSV
and HTML report listing all pages along with their clicks, impressions, CTR, and
the number of unique queries driving traffic to each page.

Usage:
    python page-level-report.py <site_url> [date_range_flag]

Example:
    python page-level-report.py https://www.example.com --last-28-days
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

# --- Configuration ---
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'

def get_gsc_service():
    """Authenticates and returns a Google Search Console service object."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Could not load credentials from {TOKEN_FILE}. Error: {e}")
            print("Will attempt to re-authenticate.")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("Credentials have expired. Attempting to refresh...")
                creds.refresh(Request())
            except exceptions.RefreshError as e:
                print(f"Error refreshing token: {e}")
                print("The refresh token is expired or revoked. Deleting it and re-authenticating.")
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                creds = None
        
        if not creds:
            if not os.path.exists(CLIENT_SECRET_FILE):
                print(f"Error: {CLIENT_SECRET_FILE} not found. Please follow setup instructions in README.md.")
                return None
            
            print("A browser window will open for you to authorize access.")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            print("Authentication successful. Credentials saved.")

    return build('webmasters', 'v3', credentials=creds)

def get_page_query_data(service, site_url, start_date, end_date):
    """Fetches page and query performance data from GSC."""
    all_data = []
    start_row = 0
    row_limit = 25000 
    
    print(f"Fetching page and query data from {start_date} to {end_date}...")

    while True:
        try:
            request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['page', 'query'],
                'rowLimit': row_limit,
                'startRow': start_row
            }
            response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()

            if 'rows' in response:
                rows = response['rows']
                all_data.extend(rows)
                print(f"Retrieved {len(rows)} rows... (Total: {len(all_data)})")
                if len(rows) < row_limit:
                    break 
                start_row += row_limit
            else:
                break
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
            
    if not all_data:
        return pd.DataFrame()

    df = pd.DataFrame(all_data)
    df[['page', 'query']] = pd.DataFrame(df['keys'].tolist(), index=df.index)
    df = df.drop(columns=['keys'])
    
    for col in ['clicks', 'impressions', 'ctr', 'position']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
    return df

def create_html_report(df, report_title, period_str):
    """Generates an HTML report from the DataFrame."""
    
    df_html = df.copy()
    
    # Format numbers for readability
    df_html['clicks'] = df_html['clicks'].apply(lambda x: f"{int(x):,}")
    df_html['impressions'] = df_html['impressions'].apply(lambda x: f"{int(x):,}")
    df_html['query_count'] = df_html['query_count'].apply(lambda x: f"{int(x):,}")
    df_html['ctr'] = df_html['ctr'].apply(lambda x: f"{x:.2%}")
    
    report_body = df_html.to_html(classes="table table-striped table-hover", index=False, border=0)

    return f"""
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{report_title}</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<style>body{{padding:2rem;}}h1,h2{{border-bottom:2px solid #dee2e6;padding-bottom:.5rem;margin-top:2rem;}}.table thead th {{background-color: #434343;color: #ffffff;text-align: left;}}footer{{margin-top:3rem;text-align:center;color:#6c757d;}}</style></head>
<body><div class="container-fluid"><h1>{report_title}</h1><p class="text-muted">Analysis for the period: {period_str}</p>
<div class="table-responsive">{report_body}</div></div>
<footer><p><a href="https://github.com/liamdelahunty/gsc-exporter" target="_blank">gsc-exporter</a></p></footer></body></html>"""


def main():
    """Main function to run the page-level report."""
    parser = argparse.ArgumentParser(description='Generate a page-level report with clicks, impressions, CTR, and unique query counts.')
    parser.add_argument('site_url', help='The URL of the site to analyse. Use sc-domain: for a domain property.')

    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument('--start-date', help='Start date in YYYY-MM-DD format.')
    date_group.add_argument('--last-24-hours', action='store_true', help='Use the last 24 hours for the report.')
    date_group.add_argument('--last-7-days', action='store_true', help='Use the last 7 days for the report.')
    date_group.add_argument('--last-28-days', action='store_true', help='Use the last 28 days for the report.')
    date_group.add_argument('--last-month', action='store_true', help='Use the last calendar month for the report. (Default)')
    date_group.add_argument('--last-quarter', action='store_true', help='Use the last quarter for the report.')
    date_group.add_argument('--last-3-months', action='store_true', help='Use the last 3 months for the report.')
    date_group.add_argument('--last-6-months', action='store_true', help='Use the last 6 months for the report.')
    date_group.add_argument('--last-12-months', action='store_true', help='Use the last 12 months for the report.')
    date_group.add_argument('--last-16-months', action='store_true', help='Use the last 16 months for the report.')

    parser.add_argument('--end-date', help='End date in YYYY-MM-DD format. Used only with --start-date.')
    
    args = parser.parse_args()
    site_url = args.site_url

    # Set default date range if none is chosen
    if not any([
        args.start_date, args.last_24_hours, args.last_7_days, args.last_28_days,
        args.last_month, args.last_quarter, args.last_3_months,
        args.last_6_months, args.last_12_months, args.last_16_months
    ]):
        args.last_month = True

    today = date.today()
    
    if args.start_date and args.end_date:
        start_date = args.start_date
        end_date = args.end_date
        period_label = "custom-period"
    elif args.last_24_hours:
        start_date = (today - timedelta(days=2)).strftime('%Y-%m-%d')
        end_date = (today - timedelta(days=2)).strftime('%Y-%m-%d')
        period_label = "last-24-hours"
    elif args.last_7_days:
        start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        period_label = "last-7-days"
    elif args.last_28_days:
        start_date = (today - timedelta(days=28)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        period_label = "last-28-days"
    elif args.last_month:
        first_day_of_current_month = today.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
        start_date = last_day_of_previous_month.replace(day=1).strftime('%Y-%m-%d')
        end_date = last_day_of_previous_month.strftime('%Y-%m-%d')
        period_label = "last-month"
    elif args.last_quarter:
        start_date = (today - relativedelta(months=3)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        period_label = "last-quarter"
    elif args.last_3_months:
        start_date = (today - relativedelta(months=3)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        period_label = "last-3-months"
    elif args.last_6_months:
        start_date = (today - relativedelta(months=6)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        period_label = "last-6-months"
    elif args.last_12_months:
        start_date = (today - relativedelta(months=12)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        period_label = "last-12-months"
    elif args.last_16_months:
        start_date = (today - relativedelta(months=16)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        period_label = "last-16-months"
    
    print(f"Using date range: {start_date} to {end_date}")

    service = get_gsc_service()
    if not service:
        return

    df_raw = get_page_query_data(service, site_url, start_date, end_date)

    if df_raw.empty:
        print("No data found for the specified period. Exiting.")
        return

    # Process the data
    page_level_data = df_raw.groupby('page').agg(
        clicks=('clicks', 'sum'),
        impressions=('impressions', 'sum'),
        query_count=('query', 'nunique')
    ).reset_index()

    # Calculate CTR safely, avoiding division by zero
    page_level_data['ctr'] = page_level_data.apply(
        lambda row: row['clicks'] / row['impressions'] if row['impressions'] > 0 else 0,
        axis=1
    )

    # Sort by clicks
    page_level_data = page_level_data.sort_values(by='clicks', ascending=False)
    
    # --- Output Generation ---
    if site_url.startswith('sc-domain:'):
        host_plain = site_url.replace('sc-domain:', '')
    else:
        host_plain = urlparse(site_url).netloc
    
    host_dir = host_plain.replace('www.', '')
    output_dir = os.path.join('output', host_dir)
    os.makedirs(output_dir, exist_ok=True)
    host_for_filename = host_dir.replace('.', '-')

    file_prefix = f"page-level-report-{host_for_filename}-{period_label}-{start_date}-to-{end_date}"
    csv_output_path = os.path.join(output_dir, f"{file_prefix}.csv")
    html_output_path = os.path.join(output_dir, f"{file_prefix}.html")

    try:
        # Save CSV
        page_level_data.to_csv(csv_output_path, index=False, encoding='utf-8')
        print(f"\nSuccessfully exported page-level data to {csv_output_path}")

        # Generate and save HTML report
        html_output = create_html_report(
            df=page_level_data,
            report_title=f"Page-Level Report for {host_dir}",
            period_str=f"{start_date} to {end_date}"
        )
        with open(html_output_path, 'w', encoding='utf-8') as f:
            f.write(html_output)
        print(f"Successfully created HTML report at {html_output_path}")

    except Exception as e:
        print(f"An error occurred during file generation: {e}")

if __name__ == '__main__':
    main()
