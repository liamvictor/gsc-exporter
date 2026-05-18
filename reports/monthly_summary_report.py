"""
Generates a summary report of Google Search Console performance data for various date ranges.
Adapted for the modular GSC Exporter.
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from urllib.parse import urlparse
from core.naming import get_output_dir, get_filename_slug
from core.cache import fetch_with_cache

def get_sort_key(site_url):
    """Creates a sort key for a site URL."""
    if site_url.startswith('sc-domain:'):
        root_domain = site_url.replace('sc-domain:', '')
        order = 0
        subdomain = ''
    else:
        netloc = urlparse(site_url).netloc
        parts = netloc.split('.')
        if len(parts) > 2 and parts[-2] in ['co', 'com', 'org', 'net', 'gov', 'edu'] and len(parts[-3]) > 2:
            root_domain = '.'.join(parts[-3:])
        elif len(parts) > 2:
            root_domain = '.'.join(parts[-2:])
        else:
            root_domain = netloc
        if netloc.startswith('www.'):
            order = 1
            subdomain = ''
        else:
            order = 2
            subdomain = netloc.split('.')[0]
    return (root_domain, order, subdomain)

def create_summary_report_html(df, report_title, date_range_str, template_path='resources/report-blank.html'):
    """Generates a summary HTML report from a DataFrame using a template."""
    if not os.path.exists(template_path):
        # Fallback to a basic template if the specific one is missing
        print(f"Warning: Template file not found at {template_path}. Using basic layout.")
        template_html = """
        <!DOCTYPE html><html><head><title>{{ title }}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head><body><div class="container py-4">
        <h1>{{ title }}</h1><p>{{ date_range }}</p>
        {{ table|safe }}
        </div></body></html>
        """
    else:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_html = f.read()

    report_df = df.copy()
    report_df['sort_key'] = report_df['site_url'].apply(get_sort_key)
    report_df = report_df.sort_values(by=['sort_key', 'clicks'], ascending=[True, False]).drop(columns=['sort_key'])

    # Format numbers
    report_df['clicks'] = report_df['clicks'].apply(lambda x: f"{x:,.0f}")
    report_df['impressions'] = report_df['impressions'].apply(lambda x: f"{x:,.0f}")
    report_df['ctr'] = report_df['ctr'].apply(lambda x: f"{x:.2%}")
    report_df['position'] = report_df['position'].apply(lambda x: f"{x:,.2f}")
    if 'queries' in report_df.columns:
        report_df['queries'] = report_df['queries'].apply(lambda x: f"{x:,.0f}")
    if 'pages' in report_df.columns:
        report_df['pages'] = report_df['pages'].apply(lambda x: f"{x:,.0f}")

    report_df = report_df.rename(columns={
        'site_url': 'Property',
        'clicks': 'Total Clicks',
        'impressions': 'Impressions',
        'ctr': 'CTR',
        'position': 'Avg. Position',
        'queries': '# Queries',
        'pages': '# Pages'
    })

    cols = ['Property', 'Total Clicks', 'Impressions', 'CTR', 'Avg. Position']
    if '# Queries' in report_df.columns: cols.append('# Queries')
    if '# Pages' in report_df.columns: cols.append('# Pages')
    report_df = report_df[cols]
    
    table_html = report_df.to_html(classes="table table-striped table-hover", index=False, border=0)

    if '{{' in template_html: # Basic template
        return template_html.replace('{{ title }}', report_title).replace('{{ date_range }}', date_range_str).replace('{{ table|safe }}', table_html)

    # Themed template
    html_output = template_html.replace('This Report Name', report_title)
    html_output = html_output.replace('<span class="text-muted me-4">Domain name</span>', f'<span class="text-muted me-4">Account Summary</span>')
    html_output = html_output.replace('<span class="text-muted me-4">Date-range</span>', f'<span class="text-muted me-4">{date_range_str}</span>')
    html_output = html_output.replace('<a href="index.html">Resources</a>', '<a href="../../resources/index.html">Resources</a>')

    custom_css = """<style>
        html { height: 100%; }
        body { display: flex; flex-direction: column; min-height: 100vh; }
        .table th, .table td { text-align: right; vertical-align: middle; }
        .table th:first-child, .table td:first-child { text-align: left; }
    </style>"""
    html_output = html_output.replace("""<style>
        html {
            height: 100%;
        }
        body {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
    </style>""", custom_css)

    main_placeholder = """    <main class="container py-4 flex-grow-1">
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
    final_main = f"""    <main class="container py-4 flex-grow-1">
        <div class="table-responsive">
            {table_html}
        </div>
    </main>"""
    html_output = html_output.replace(main_placeholder, final_main)

    return html_output

def run_report(service, sites, start_date=None, end_date=None, report_label=None):
    """Executes the monthly summary report for a list of sites."""
    if isinstance(sites, str):
        sites = [sites]
    
    if not start_date or not end_date:
        today = date.today()
        end_date_dt = today.replace(day=1) - timedelta(days=1)
        start_date_dt = end_date_dt.replace(day=1)
        start_date = start_date_dt.strftime('%Y-%m-%d')
        end_date = end_date_dt.strftime('%Y-%m-%d')

    print(f"Running Monthly Summary Report for {len(sites)} sites ({start_date} to {end_date})...")
    
    all_data = []
    for site_url in sites:
        print(f"  - Processing {site_url}...")
        # Get overall totals
        df_totals = fetch_with_cache(service, site_url, start_date, end_date, [])
        if not df_totals.empty:
            row = df_totals.iloc[0].to_dict()
            # Get unique query and page counts
            df_queries = fetch_with_cache(service, site_url, start_date, end_date, ['query'])
            df_pages = fetch_with_cache(service, site_url, start_date, end_date, ['page'])
            row['queries'] = len(df_queries)
            row['pages'] = len(df_pages)
            row['site_url'] = site_url
            all_data.append(row)
            
    if not all_data:
        print("No data found for the given sites and period.")
        return None

    df = pd.DataFrame(all_data)
    
    # Define Output Paths
    if len(sites) == 1:
        output_dir = get_output_dir(sites[0])
        slug = get_filename_slug(sites[0])
        label = slug
    else:
        output_dir = os.path.join('output', 'account')
        label = report_label if report_label else "account-wide"
    
    os.makedirs(output_dir, exist_ok=True)
    file_prefix = f"monthly-summary-report-{label}-{start_date}-to-{end_date}"
    csv_path = os.path.join(output_dir, f"{file_prefix}.csv")
    html_path = os.path.join(output_dir, f"{file_prefix}.html")
    
    df.to_csv(csv_path, index=False)
    
    report_title = f"GSC Monthly Summary"
    if len(sites) == 1: report_title += f" for {sites[0]}"
    
    html_content = create_summary_report_html(df, report_title, f"{start_date} to {end_date}")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Report completed: {html_path}")
    return html_path

if __name__ == '__main__':
    import argparse
    from core.client import get_gsc_service
    
    parser = argparse.ArgumentParser(description='Run a monthly summary report.')
    parser.add_argument('site_url', nargs='?', help='The URL of the site to analyse.')
    parser.add_argument('--sites-file', help='Text file with site URLs.')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD).')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD).')
    
    args = parser.parse_args()
    
    sites = []
    if args.sites_file:
        with open(args.sites_file, 'r') as f:
            sites = [line.strip() for line in f if line.strip()]
    elif args.site_url:
        sites = [args.site_url]
    
    service = get_gsc_service()
    if service and sites:
        run_report(service, sites, args.start_date, args.end_date)
