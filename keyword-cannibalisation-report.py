"""
Generates a report that highlights keyword cannibalisation issues.

This script identifies keywords that multiple pages are ranking for, which
can cause SEO issues. It calculates the total potential clicks and impressions
a consolidated page could achieve.

The report is generated in HTML format, showing the top 100 cannibalised
keywords by impressions.

Usage:
    python keyword-cannibalisation-report.py <site_url> [--start-date <start_date>] [--end-date <end_date>]
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
import sys
import html
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
            
            print("A browser window will open for you to authorise access.")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            print("Authentication successful. Credentials saved.")

    return build('webmasters', 'v3', credentials=creds)

def get_latest_available_gsc_date(service, site_url, max_retries=5):
    """
    Determines the latest date for which GSC data is available by querying
    backwards from today.
    """
    current_date = date.today()
    for i in range(max_retries):
        check_date = current_date - timedelta(days=i)
        check_date_str = check_date.strftime('%Y-%m-%d')
        
        print(f"Checking for GSC data availability on: {check_date_str}...")
        try:
            request = {
                'startDate': check_date_str,
                'endDate': check_date_str,
                'dimensions': ['date'],
                'rowLimit': 1,
                'startRow': 0
            }
            response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
            
            if 'rows' in response and response['rows']:
                print(f"Latest available GSC data found for: {check_date_str}")
                return check_date
            else:
                print(f"No data for {check_date_str}, checking previous day.")
        except HttpError as e:
            if e.resp.status == 400:
                print(f"No data for {check_date_str}, checking previous day (HTTP 400).")
            else:
                print(f"An HTTP error occurred while checking date {check_date_str}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while checking date {check_date_str}: {e}")
            
    print(f"Could not determine latest available GSC date within {max_retries} days. Using today's date as a fallback.")
    return current_date

def get_performance_data(service, site_url, start_date, end_date):
    """Fetches pages and queries data from GSC for a given date range."""
    all_data = []
    start_row = 0
    row_limit = 25000
    print(f"Fetching data for {site_url} from {start_date} to {end_date}...")
    while True:
        try:
            request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['query', 'page'],
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
    return all_data

def create_html_report():
    # Placeholder for HTML report generation
    pass

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(
        description='Generates a report highlighting keyword cannibalisation issues.',
        epilog='Example Usage:
'
               '  python keyword-cannibalisation-report.py https://www.example.com --last-28-days
',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('site_url', help='The URL of the site to analyse.')
    
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument('--start-date', help='Start date in YYYY-MM-DD format.')
    date_group.add_argument('--last-24-hours', action='store_true', help='Set date range to the last 24 hours.')
    date_group.add_argument('--last-7-days', action='store_true', help='Set date range to the last 7 days.')
    date_group.add_argument('--last-28-days', action='store_true', help='Set date range to the last 28 days.')
    date_group.add_argument('--last-month', action='store_true', help='Set date range to the last calendar month.')
    date_group.add_argument('--last-quarter', action='store_true', help='Set date range to the last quarter.')
    date_group.add_argument('--last-3-months', action='store_true', help='Set date range to the last 3 months.')
    date_group.add_argument('--last-6-months', action='store_true', help='Set date range to the last 6 months.')
    date_group.add_argument('--last-12-months', action='store_true', help='Set date range to the last 12 months.')
    date_group.add_argument('--last-16-months', action='store_true', help='Set date range to the last 16 months.')
    
    parser.add_argument('--end-date', help='End date in YYYY-MM-DD format. Used only with --start-date.')

    args = parser.parse_args()

    service = get_gsc_service()
    if not service:
        return

    latest_available_date = get_latest_available_gsc_date(service, args.site_url)

    if not any([
        args.start_date, args.last_24_hours, args.last_7_days, args.last_28_days,
        args.last_month, args.last_quarter, args.last_3_months,
        args.last_6_months, args.last_12_months, args.last_16_months
    ]):
        args.last_28_days = True

    if args.start_date and args.end_date:
        start_date = args.start_date
        end_date = args.end_date
    elif args.last_24_hours:
        start_date = (latest_available_date - timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = (latest_available_date - timedelta(days=1)).strftime('%Y-%m-%d')
    elif args.last_7_days:
        start_date = (latest_available_date - timedelta(days=6)).strftime('%Y-%m-%d')
        end_date = latest_available_date.strftime('%Y-%m-%d')
    elif args.last_28_days:
        start_date = (latest_available_date - timedelta(days=27)).strftime('%Y-%m-%d')
        end_date = latest_available_date.strftime('%Y-%m-%d')
    elif args.last_month:
        first_day_of_current_month = latest_available_date.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
        start_date = last_day_of_previous_month.replace(day=1).strftime('%Y-%m-%d')
        end_date = last_day_of_previous_month.strftime('%Y-%m-%d')
    elif args.last_quarter:
        current_quarter = (latest_available_date.month - 1) // 3
        end_date_dt = datetime(latest_available_date.year, 3 * current_quarter + 1, 1).date() - timedelta(days=1)
        start_date_dt = end_date_dt.replace(day=1) - relativedelta(months=2)
        start_date = start_date_dt.strftime('%Y-%m-%d')
        end_date = end_date_dt.strftime('%Y-%m-%d')
    elif args.last_3_months:
        start_date = (latest_available_date - relativedelta(months=3) + timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = latest_available_date.strftime('%Y-%m-%d')
    elif args.last_6_months:
        start_date = (latest_available_date - relativedelta(months=6) + timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = latest_available_date.strftime('%Y-%m-%d')
    elif args.last_12_months:
        start_date = (latest_available_date - relativedelta(months=12) + timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = latest_available_date.strftime('%Y-%m-%d')
    elif args.last_16_months:
        start_date = (latest_available_date - relativedelta(months=16) + timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = latest_available_date.strftime('%Y-%m-%d')
    else: 
        start_date = args.start_date
        end_date = args.end_date

    site_url = args.site_url

    # Placeholder for the rest of the logic
    print(f"Analysing {site_url} from {start_date} to {end_date}")

    raw_data = get_performance_data(service, site_url, start_date, end_date)
    if not raw_data:
        print("No data found for the given site and date range.")
        return

    df = pd.DataFrame(raw_data)
    df[['query', 'page']] = pd.DataFrame(df['keys'].tolist(), index=df.index)
    df.drop(columns=['keys'], inplace=True)
    
    print(f"
Successfully downloaded {len(df)} rows of data.")
    print("Processing for cannibalisation issues...")
    # Cannibalisation logic will go here
    # HTML report generation will go here
    # File writing will go here

if __name__ == '__main__':
    main()
