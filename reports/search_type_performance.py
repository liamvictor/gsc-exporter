import pandas as pd
import os
from functools import reduce
from core.naming import get_output_dir
from core.cache import fetch_with_cache

SEARCH_TYPES = ['web', 'image', 'video', 'news', 'discover', 'googleNews']

def run_report(service, site_url, start_date, end_date):
    """
    Runs the search type performance report.
    """
    print(f"Running search type performance report for {site_url}")
    
    all_data_dfs = []
    
    # 1. Fetch data for each search type
    for st in SEARCH_TYPES:
        df = fetch_with_cache(service, site_url, start_date, end_date, dimensions=['date'], search_type=st)
        
        if not df.empty:
            # Rename columns to include search type
            rename_dict = {
                'clicks': f'{st}_clicks',
                'impressions': f'{st}_impressions',
                'ctr': f'{st}_ctr',
                'position': f'{st}_position'
            }
            df.rename(columns=rename_dict, inplace=True)
            all_data_dfs.append(df)
    
    if not all_data_dfs:
        print("No data found.")
        return

    # 2. Merge data
    merged_df = reduce(lambda left, right: pd.merge(left, right, on='date', how='outer'), all_data_dfs)
    merged_df.fillna(0, inplace=True)
    merged_df = merged_df.sort_values('date', ascending=False)
    
    # 3. Save output
    output_dir = get_output_dir(site_url)
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f"search-type-performance-{start_date}-to-{end_date}.csv")
    merged_df.to_csv(csv_path, index=False)
    print(f"Report saved to {csv_path}")
